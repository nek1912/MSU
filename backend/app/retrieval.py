from pydantic import BaseModel

from app.config import MIN_CHUNKS_ABOVE_SECONDARY, SECONDARY_THRESHOLD, TOP1_THRESHOLD


class RetrievedChunk(BaseModel):
    chunk_id: str
    title: str
    page: int
    section: str
    content: str
    similarity: float
    source_url: str
    domain: str
    jurisdiction: str
    state: str | None = None


class GateResult(BaseModel):
    abstained: bool
    reason: str | None = None
    confidence: float = 0.0


def retrieve(supabase, query_embedding: list[float], domain: str,
             state: str | None, k: int = 6) -> list[RetrievedChunk]:
    rows = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding, "match_domain": domain,
        "match_state": state, "match_count": k}).execute().data or []
    return [RetrievedChunk(chunk_id=str(r["chunk_id"]), title=r["title"],
                           page=r["page"], section=r["section"],
                           content=r["content"], similarity=r["similarity"],
                           source_url=r["source_url"], domain=r["domain"],
                           jurisdiction=r["jurisdiction"],
                           state=r.get("state")) for r in rows]


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
    confidence = round(min(0.6 * sims[0] + 0.4 * (strong / len(sims)), 1.0), 2)
    return GateResult(abstained=False, reason=None, confidence=confidence)
