"""Static RAG service — encapsulates Supabase pgvector hybrid retrieval.

Provides a single entry point for the static retrieval pipeline:
  1. Hybrid retrieval (dense + lexical with RRF fusion)
  2. Optional Jina reranker (if enabled)
  3. Conversion to EvidenceChunk contracts
  4. Unified evidence gate validation
  5. Returns typed RAGResult
"""

from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.contracts import (
    AbstentionReason,
    ConfidenceBand,
    EvidenceChunk,
    RAGResult,
)
from app.db import get_supabase
from app.evidence_gate import evidence_gate
from app.hybrid_retrieval import retrieve_hybrid
from app.providers.reranker import JinaReranker
from app.retrieval import RetrievedChunk

logger = logging.getLogger(__name__)

_DOMAIN_MAP = {
    "pacs": "pacs_governance",
    "finlit": "financial_inclusion",
    "cooperative": "pacs_governance",
}


class StaticRAGService:
    """Encapsulates Supabase pgvector hybrid retrieval pipeline.

    Usage:
        service = StaticRAGService(settings)
        result = service.retrieve(
            embedding=[...],
            query="What is PMFBY?",
            domain="pmfby",
            state="gujarat",
        )
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def retrieve(
        self,
        embedding: list[float],
        query: str,
        domain: str,
        state: str | None,
        k: int | None = None,
    ) -> RAGResult:
        """Run static RAG pipeline and return typed result.

        Args:
            embedding: Query embedding vector.
            query: English query text.
            domain: Requested domain (raw, before _DOMAIN_MAP).
            state: Requested state filter (or None for central only).
            k: Number of chunks to retrieve. Defaults to 25 if reranker
               enabled, else 6.

        Returns:
            RAGResult with chunks, abstention info, and confidence band.
        """
        retrieval_domain = _DOMAIN_MAP.get(domain, domain)
        effective_k = k or (25 if self._settings.reranker_enabled else 6)

        # Step 1: Hybrid retrieval
        try:
            supabase = get_supabase()
            chunks = retrieve_hybrid(
                supabase, embedding, query, retrieval_domain, state, k=effective_k,
            )
        except Exception:
            logger.exception("Static RAG retrieval failed")
            return RAGResult(
                chunks=[],
                abstained=True,
                reason=AbstentionReason.PROVIDER_UNAVAILABLE,
                band=ConfidenceBand.LOW,
                domain=retrieval_domain,
            )

        # Step 2: Optional reranker
        if self._settings.reranker_enabled and chunks:
            chunks = self._apply_reranker(query, chunks)

        # Step 3: Convert to EvidenceChunk
        evidence_chunks = [self._to_evidence_chunk(c, retrieval_domain) for c in chunks]

        # Step 4: Evidence gate
        try:
            abstained, reason, band = evidence_gate(
                evidence_chunks,
                expected_domain=retrieval_domain,
                expected_state=state,
            )
        except Exception:
            logger.exception("Evidence gate failed")
            abstained, reason, band = True, AbstentionReason.CITATION_FAILURE, ConfidenceBand.LOW

        logger.info(
            "StaticRAGService result: chunks=%d abstained=%s reason=%s band=%s",
            len(evidence_chunks), abstained, reason, band,
        )

        return RAGResult(
            chunks=evidence_chunks,
            abstained=abstained,
            reason=reason,
            band=band,
            domain=retrieval_domain,
        )

    def _apply_reranker(
        self, query: str, chunks: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        """Apply Jina reranker to reorder chunks. Returns original on failure."""
        try:
            reranker = JinaReranker()
            docs_for_rerank = [
                {"chunk_id": c.chunk_id, "content": c.content} for c in chunks
            ]
            reranked = reranker.rerank(query, docs_for_rerank, top_n=6)
            chunks_by_id = {c.chunk_id: c for c in chunks}
            return [
                chunks_by_id[r["chunk_id"]]
                for r in reranked
                if r["chunk_id"] in chunks_by_id
            ]
        except Exception:
            logger.warning("Reranker failed, returning original chunks")
            return chunks

    @staticmethod
    def _to_evidence_chunk(chunk: RetrievedChunk, domain: str) -> EvidenceChunk:
        """Convert a RetrievedChunk to an EvidenceChunk contract."""
        return EvidenceChunk(
            chunk_id=chunk.chunk_id,
            content=chunk.content,
            source_type="static",
            title=chunk.title,
            url=chunk.source_url,
            page=chunk.page,
            section=chunk.section,
            domain=chunk.domain or domain,
            jurisdiction=chunk.jurisdiction,
            state=chunk.state,
            dense_score=chunk.similarity,
            metadata={
                "stable_chunk_id": chunk.stable_chunk_id,
                "document_id": chunk.document_id,
                "source_file": chunk.source_file,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "subsection": chunk.subsection,
                "clause": chunk.clause,
            },
        )
