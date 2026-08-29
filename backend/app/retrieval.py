from pydantic import BaseModel

from app.config import MIN_CHUNKS_ABOVE_SECONDARY, SECONDARY_THRESHOLD, TOP1_THRESHOLD


class RetrievedChunk(BaseModel):
    chunk_id: str            # internal database UUID (kept for citation matching)
    stable_chunk_id: str     # deterministic application-level ID
    document_id: str
    title: str
    page: int
    page_start: int
    page_end: int
    section: str
    subsection: str | None = None
    clause: str | None = None
    content: str
    similarity: float
    source_url: str
    source_file: str | None = None
    domain: str
    jurisdiction: str
    state: str | None = None


class GateResult(BaseModel):
    abstained: bool
    reason: str | None = None
    confidence: float = 0.0


def retrieve(supabase, query_embedding: list[float], domain: str,
             state: str | None, k: int = 6,
             as_of_date: str | None = None) -> list[RetrievedChunk]:
    params = {
        "query_embedding": query_embedding, "match_domain": domain,
        "match_state": state, "match_count": k,
    }
    if as_of_date is not None:
        params["as_of_date"] = as_of_date
    rows = supabase.rpc("match_chunks", params).execute().data or []
    return [RetrievedChunk(
        chunk_id=str(r.get("chunk_id") or r["id"]),
        stable_chunk_id=r.get("stable_chunk_id") or str(r.get("chunk_id") or r["id"]),
        document_id=str(r["document_id"]),
        title=r["title"],
        page=r.get("page") or 0,
        page_start=r.get("page_start") or r.get("page") or 0,
        page_end=r.get("page_end") or r.get("page") or 0,
        section=r.get("section") or "",
        subsection=r.get("subsection"),
        clause=r.get("clause"),
        content=r["content"],
        similarity=r["similarity"],
        source_url=r.get("source_url") or "",
        source_file=r.get("source_file"),
        domain=r.get("domain") or domain,
        jurisdiction=r.get("jurisdiction") or "central",
        state=r.get("state"),
    ) for r in rows]


def _jurisdiction_ok(chunk: RetrievedChunk, expected_state: str | None) -> bool:
    return chunk.jurisdiction == "central" or chunk.state == expected_state


def evidence_gate(chunks: list[RetrievedChunk], expected_domain: str | None = None,
                  expected_state: str | None = None) -> GateResult:
    if not chunks:
        return GateResult(abstained=True, reason="no_chunks")
    # Defense-in-depth (spec §2.4): SQL prefilter should guarantee these;
    # verify anyway so a bad filter can never surface cross-domain evidence.
    if expected_domain is not None and any(c.domain != expected_domain for c in chunks):
        return GateResult(abstained=True, reason="domain_mismatch_in_retrieval")
    if not all(_jurisdiction_ok(c, expected_state) for c in chunks):
        return GateResult(abstained=True, reason="jurisdiction_mismatch_in_retrieval")
    sims = sorted((c.similarity for c in chunks), reverse=True)
    if sims[0] < TOP1_THRESHOLD:
        return GateResult(abstained=True, reason="below_top1_threshold")
    strong = sum(1 for s in sims if s >= SECONDARY_THRESHOLD)
    if strong < MIN_CHUNKS_ABOVE_SECONDARY:
        return GateResult(abstained=True, reason="insufficient_supporting_chunks")
    # Retrieval-signal-based confidence (replaces arbitrary heuristic)
    base = sims[0] * 0.6
    coverage = min(strong / 3, 1.0) * 0.3
    domain_bonus = 0.1 if (expected_domain is not None and
                           all(c.domain == expected_domain for c in chunks)) else 0.0
    confidence = base + coverage + domain_bonus
    if sims[0] < 0.3:
        confidence = min(confidence, 0.4)
    confidence = round(min(confidence, 1.0), 2)
    return GateResult(abstained=False, reason=None, confidence=confidence)
