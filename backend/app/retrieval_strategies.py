"""Retrieval strategies — Phase 4.

Three strategies for comparison:
  A. Dense:           Jina/Gemini embedding → pgvector cosine search
  B. Hybrid:          Dense + Postgres FTS → Reciprocal Rank Fusion
  C. Hybrid+Reranker: Hybrid → Jina Reranker v2 → final ranking

All strategies share the same corpus (2,188 chunks) and domain pre-filter.
The corpus is NOT modified between experiments.
"""
from __future__ import annotations

import math

from app.retrieval import RetrievedChunk


# ---------------------------------------------------------------------------
# Strategy A: Dense (current default)
# ---------------------------------------------------------------------------

def retrieve_dense(supabase, query_embedding: list[float], domain: str,
                   state: str | None, k: int = 6,
                   as_of_date: str | None = None) -> list[RetrievedChunk]:
    """Pure pgvector cosine similarity retrieval (current implementation)."""
    from app.retrieval import retrieve
    return retrieve(supabase, query_embedding, domain, state, k, as_of_date)


# ---------------------------------------------------------------------------
# Strategy B: Hybrid (dense + lexical via RRF)
# ---------------------------------------------------------------------------

def _rrf_fuse(dense_results: list[RetrievedChunk],
              lexical_results: list[RetrievedChunk],
              k: int = 60) -> list[RetrievedChunk]:
    """Reciprocal Rank Fusion of two result lists.

    RRF score = sum(1 / (k + rank)) for each list where doc appears.
    k=60 is the standard constant from the original RRF paper.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, RetrievedChunk] = {}

    for rank, chunk in enumerate(dense_results):
        cid = chunk.chunk_id
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
        doc_map[cid] = chunk

    for rank, chunk in enumerate(lexical_results):
        cid = chunk.chunk_id
        scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
        if cid not in doc_map:
            doc_map[cid] = chunk

    # Sort by fused score descending
    sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
    return [doc_map[cid] for cid in sorted_ids[:k]]


def _retrieve_lexical(supabase, query_text: str, domain: str,
                      state: str | None, k: int = 6,
                      as_of_date: str | None = None) -> list[RetrievedChunk]:
    """Postgres full-text search with domain/jurisdiction pre-filter."""
    # Use plainto_tsquery for safe query parsing
    rpc_result = supabase.rpc("match_chunks_lexical", {
        "query_text": query_text,
        "match_domain": domain,
        "match_state": state,
        "match_count": k,
        "as_of_date": as_of_date,
    }).execute().data or []
    return [_row_to_chunk(r) for r in rpc_result]


def retrieve_hybrid(supabase, query_embedding: list[float], query_text: str,
                    domain: str, state: str | None,
                    k: int = 6, as_of_date: str | None = None) -> list[RetrievedChunk]:
    """Hybrid retrieval: dense cosine + lexical FTS, fused via RRF.

    Retrieves 2x candidates from each strategy, then fuses to top-k.
    """
    oversample = min(k * 2, 20)
    dense = retrieve_dense(supabase, query_embedding, domain, state, oversample, as_of_date)
    lexical = _retrieve_lexical(supabase, query_text, domain, state, oversample, as_of_date)
    return _rrf_fuse(dense, lexical, k)[:k]


# ---------------------------------------------------------------------------
# Strategy C: Hybrid + Reranker
# ---------------------------------------------------------------------------

def retrieve_hybrid_reranked(supabase, query_embedding: list[float],
                             query_text: str, query_full: str,
                             domain: str, state: str | None,
                             k: int = 6, as_of_date: str | None = None) -> list[RetrievedChunk]:
    """Hybrid retrieval + Jina Reranker v2 re-ranking.

    1. Get hybrid candidates (oversampled)
    2. Re-rank with Jina Reranker v2
    3. Return top-k
    """
    from app.providers.reranker import JinaReranker

    oversample = min(k * 3, 20)
    candidates = retrieve_hybrid(supabase, query_embedding, query_text,
                                 domain, state, oversample, as_of_date)

    if not candidates:
        return []

    # Rerank
    reranker = JinaReranker()
    docs = [{"content": c.content, "chunk_id": c.chunk_id} for c in candidates]
    reranked = reranker.rerank(query_full, docs, top_n=k)

    # Map back to RetrievedChunk
    chunk_map = {c.chunk_id: c for c in candidates}
    results = []
    for r in reranked:
        cid = r.get("chunk_id")
        if cid and cid in chunk_map:
            chunk = chunk_map[cid]
            # Attach reranker score for analysis
            chunk.similarity = r.get("reranker_score", chunk.similarity)
            results.append(chunk)
    return results[:k]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_chunk(r: dict) -> RetrievedChunk:
    """Convert a Supabase RPC row to RetrievedChunk."""
    return RetrievedChunk(
        chunk_id=str(r["chunk_id"]),
        stable_chunk_id=r.get("stable_chunk_id", ""),
        document_id=str(r.get("document_id", "")),
        title=r["title"],
        page=r["page"],
        page_start=r.get("page_start", r["page"]),
        page_end=r.get("page_end", r["page"]),
        section=r["section"],
        subsection=r.get("subsection"),
        clause=r.get("clause"),
        content=r["content"],
        similarity=r["similarity"],
        source_url=r["source_url"],
        source_file=r.get("source_file"),
        domain=r["domain"],
        jurisdiction=r["jurisdiction"],
        state=r.get("state"),
    )
