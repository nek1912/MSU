"""Jina reranker adapter — Phase 4.

Calls Jina Reranker v2 API to re-score candidate chunks.
Falls back to identity (no reranking) on any failure.
"""
from __future__ import annotations

import httpx

from app.config import REQUEST_TIMEOUT_S, get_settings


class JinaReranker:
    """Thin wrapper around Jina Reranker v2 API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._key = settings.jina_api_key
        self._model = settings.reranker_model
        self._endpoint = "https://api.jina.ai/v1/rerank"

    def rerank(self, query: str, documents: list[dict],
               top_n: int | None = None) -> list[dict]:
        """Re-score documents by relevance to query.

        Args:
            query: The user query string.
            documents: List of dicts with at least 'content' or 'text' key.
            top_n: If set, return only top_n results.

        Returns:
            List of dicts sorted by reranker score (descending).
            Each dict gains a 'reranker_score' key.
            On failure, returns documents unchanged (identity fallback).
        """
        if not documents:
            return []

        # Build document list for Jina API
        docs_for_jina = []
        for i, doc in enumerate(documents):
            text = doc.get("content") or doc.get("text") or ""
            docs_for_jina.append({"text": text, "index": i})

        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
                resp = client.post(
                    self._endpoint,
                    headers={
                        "Authorization": f"Bearer {self._key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "query": query,
                        "documents": [d["text"] for d in docs_for_jina],
                        "top_n": top_n or len(documents),
                        "return_documents": False,
                    },
                )
                resp.raise_for_status()
                results = resp.json().get("results", [])

            # Map reranker results back to original documents
            reranked = []
            for r in results:
                idx = r.get("index", 0)
                score = r.get("relevance_score", 0.0)
                doc = dict(documents[idx])
                doc["reranker_score"] = score
                reranked.append(doc)

            return reranked

        except Exception:
            # Identity fallback: return original docs with original scores
            return documents
