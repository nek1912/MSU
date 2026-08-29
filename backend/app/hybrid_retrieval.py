"""Hybrid retrieval: dense + lexical with deterministic RRF fusion.

Implements Stage 5 of the RAG refactor:
- Filters INSIDE both candidate queries before ranking
- Deterministic Reciprocal Rank Fusion
- Stable tie-breaking
- Per-candidate diagnostics

Live retrieval via Supabase: dense (pgvector) + lexical (ILIKE) + RRF.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.contracts import (
    ConfidenceBand,
    HardFilter,
    RetrievalCandidate,
)
from app.retrieval import RetrievedChunk


def reciprocal_rank_fusion(
    dense_candidates: list[RetrievalCandidate],
    lexical_candidates: list[RetrievalCandidate],
    k: int = 60,
    dense_weight: float = 0.6,
    lexical_weight: float = 0.4,
) -> list[RetrievalCandidate]:
    """Fuse dense and lexical results using deterministic weighted RRF.

    RRF score = weight / (k + rank)

    Tie-breaking order (deterministic):
    1. fused_score DESC
    2. best_component_rank ASC
    3. document_id ASC
    4. chunk_id ASC

    Args:
        dense_candidates: Ranked dense retrieval results
        lexical_candidates: Ranked lexical retrieval results
        k: RRF constant (higher = less weight to top ranks)
        dense_weight: Weight for dense component
        lexical_weight: Weight for lexical component

    Returns:
        Fused, deduplicated, deterministically ranked candidates
    """
    # Build rank lookup: chunk_id -> rank (1-indexed)
    dense_ranks = {c.chunk_id: i + 1 for i, c in enumerate(dense_candidates)}
    lexical_ranks = {c.chunk_id: i + 1 for i, c in enumerate(lexical_candidates)}

    # Build candidate lookup
    all_candidates: dict[str, RetrievalCandidate] = {}
    for c in dense_candidates:
        all_candidates[c.chunk_id] = c
    for c in lexical_candidates:
        if c.chunk_id not in all_candidates:
            all_candidates[c.chunk_id] = c

    # Calculate fused scores
    fused: list[tuple[float, int, str, str, RetrievalCandidate]] = []
    for chunk_id, candidate in all_candidates.items():
        dense_rank = dense_ranks.get(chunk_id)
        lexical_rank = lexical_ranks.get(chunk_id)

        dense_score = dense_weight / (k + dense_rank) if dense_rank else 0.0
        lexical_score = lexical_weight / (k + lexical_rank) if lexical_rank else 0.0
        fused_score = dense_score + lexical_score

        # Best component rank for tie-breaking
        component_ranks = [r for r in [dense_rank, lexical_rank] if r is not None]
        best_rank = min(component_ranks) if component_ranks else k

        fused.append((fused_score, best_rank, candidate.document_id,
                       candidate.chunk_id, candidate))

    # Deterministic sort
    fused.sort(key=lambda x: (-x[0], x[1], x[2], x[3]))

    # Assign final ranks and fused scores
    result = []
    for rank, (score, _, _, _, candidate) in enumerate(fused, 1):
        candidate.fused_score = round(score, 8)
        candidate.final_rank = rank
        result.append(candidate)

    return result


def deduplicate_candidates(candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
    """Deduplicate by chunk_id, keeping the first (highest-ranked) occurrence."""
    seen: set[str] = set()
    result = []
    for c in candidates:
        if c.chunk_id not in seen:
            seen.add(c.chunk_id)
            result.append(c)
    return result


def apply_hard_filters(
    candidates: list[RetrievalCandidate],
    filters: HardFilter,
) -> list[RetrievalCandidate]:
    """Apply hard filters to candidates.

    Filters are applied INSIDE the candidate set (not before ranking).
    Returns only candidates that pass all filters.
    """
    result = []
    for c in candidates:
        # Domain filter
        if filters.domain and c.filter_decisions.get("domain") is False:
            continue
        # Status filter
        if filters.status and c.filter_decisions.get("active") is False:
            continue
        result.append(c)
    return result


# ---------------------------------------------------------------------------
# Live retrieval via Supabase
# ---------------------------------------------------------------------------

def _dense_retrieve(supabase, query_embedding: list[float], domain: str,
                    state: str | None, k: int = 10) -> list[RetrievedChunk]:
    """Dense retrieval via match_chunks RPC."""
    rows = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_domain": domain,
        "match_state": state,
        "match_count": k,
    }).execute().data or []
    return [
        RetrievedChunk(
            chunk_id=str(r["chunk_id"]),
            title=r["title"],
            page=r["page"],
            section=r["section"],
            content=r["content"],
            similarity=r["similarity"],
            source_url=r["source_url"],
            domain=r["domain"],
            jurisdiction=r["jurisdiction"],
            state=r.get("state"),
        )
        for r in rows
    ]


def _lexical_retrieve(supabase, query_text: str, domain: str,
                      state: str | None, k: int = 10) -> list[RetrievedChunk]:
    """Lexical retrieval via term-overlap on chunks.content.

    Domain and jurisdiction/state filters are applied INSIDE candidate
    selection (same logic as the ``match_chunks`` RPC) so hybrid fusion can
    never surface cross-domain or cross-jurisdiction evidence.
    """
    # 1. Determine eligible document ids (central OR state match).
    doc_rows = (
        supabase.table("documents")
        .select("id, jurisdiction, state, domain")
        .execute()
        .data or []
    )
    eligible = {
        d["id"]
        for d in doc_rows
        if d.get("domain") == domain and (
            d.get("jurisdiction") == "central"
            or (state is not None and d.get("state") == state)
        )
    }
    if not eligible:
        return []

    # 2. Fetch candidate chunks for eligible documents.
    rows = (
        supabase.table("chunks")
        .select("id, content, document_id, page, section")
        .in_("document_id", list(eligible))
        .limit(2000)
        .execute()
        .data or []
    )

    # 3. Score by query term overlap.
    query_terms = set(query_text.lower().split())
    scored = []
    for row in rows:
        content_lower = row["content"].lower()
        matches = sum(1 for t in query_terms if t in content_lower)
        if matches > 0:
            scored.append((matches, row))

    scored.sort(key=lambda x: -x[0])

    # 4. Attach document metadata for top results.
    doc_meta = {d["id"]: d for d in doc_rows}
    results = []
    for _, row in scored[:k]:
        d = doc_meta.get(row["document_id"])
        if not d:
            continue
        results.append(RetrievedChunk(
            chunk_id=str(row["id"]),
            title=d["title"],
            page=row.get("page") or 0,
            section=row.get("section") or "",
            content=row["content"][:200],
            similarity=0.0,
            source_url=d.get("source_url", ""),
            domain=d["domain"],
            jurisdiction=d["jurisdiction"],
            state=d.get("state"),
        ))
    return results


def _enrich_chunks(supabase, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """Attach the stable application chunk_id + provenance metadata (Task 2).

    ``RetrievedChunk.chunk_id`` stays the internal DB uuid (used for the
    ``[chunk:id]`` citation markers and citation verification). This adds the
    deterministic, re-ingestion-safe ``stable_chunk_id`` and the fields needed
    to resolve a citation deterministically to a source page.
    """
    if not chunks:
        return chunks
    uuids = [c.chunk_id for c in chunks]
    try:
        rows = (
            supabase.table("chunks")
            .select("id, chunk_id, document_id, section, metadata")
            .in_("id", uuids)
            .execute()
            .data or []
        )
    except Exception:  # noqa: BLE001
        return chunks
    by_id = {str(r["id"]): r for r in rows}
    for c in chunks:
        r = by_id.get(c.chunk_id)
        if not r:
            continue
        meta = r.get("metadata") or {}
        c.stable_chunk_id = r.get("chunk_id")
        c.document_id = r.get("document_id")
        c.source_file = meta.get("source_file", "") or ""
        c.page_start = meta.get("page_start") or c.page
        c.page_end = meta.get("page_end") or c.page
        c.subsection = meta.get("subsection", "") or ""
        c.clause = meta.get("clause", "") or ""
    return chunks


def retrieve_hybrid(supabase, query_embedding: list[float], query_text: str,
                    domain: str, state: str | None,
                    k: int = 6) -> list[RetrievedChunk]:
    """Hybrid retrieval: dense + lexical with RRF fusion.

    Returns top-k chunks after deterministic fusion.
    Falls back to dense-only if lexical fails.
    """
    # Dense retrieval
    dense_chunks = _dense_retrieve(supabase, query_embedding, domain, state, k=k)

    # Lexical retrieval
    try:
        lexical_chunks = _lexical_retrieve(supabase, query_text, domain, state, k=k)
    except Exception:  # noqa: BLE001
        lexical_chunks = []

    # If no lexical results, fall back to dense-only
    if not lexical_chunks:
        return _enrich_chunks(supabase, dense_chunks)

    # Convert to RetrievalCandidate for fusion
    dense_candidates = []
    for i, chunk in enumerate(dense_chunks):
        dense_candidates.append(RetrievalCandidate(
            chunk_id=chunk.chunk_id,
            document_id="",
            source_id="",
            dense_rank=i + 1,
            dense_score=chunk.similarity,
            filter_decisions={"domain": True, "active": True},
        ))

    lexical_candidates = []
    for i, chunk in enumerate(lexical_chunks):
        lexical_candidates.append(RetrievalCandidate(
            chunk_id=chunk.chunk_id,
            document_id="",
            source_id="",
            lexical_rank=i + 1,
            lexical_score=0.5,
            filter_decisions={"domain": True, "active": True},
        ))

    # RRF fusion
    fused = reciprocal_rank_fusion(dense_candidates, lexical_candidates)

    # Map back to RetrievedChunk
    chunk_map = {c.chunk_id: c for c in dense_chunks + lexical_chunks}
    result = []
    for candidate in fused[:k]:
        chunk = chunk_map.get(candidate.chunk_id)
        if chunk:
            # Boost similarity with RRF signal
            chunk.similarity = max(chunk.similarity, candidate.fused_score or 0.0)
            result.append(chunk)

    return _enrich_chunks(supabase, result)
