"""Rebuild gold chunk-ID mapping against the frozen 2,188-chunk Jina-v3 corpus.

The previous version just grabbed the first 3 chunk IDs of the whole document,
which is meaningless for Recall measurement. This version:

1. Translates the gold ``relevant_source_ids`` (old slug scheme) to the
   ``source_id`` values actually stored by ``backend/ingest_seed.py``.
2. For each answerable case, localizes the genuinely relevant chunk(s) by
   embedding the question (Jina ``retrieval.query``) and ranking ALL chunks of
   the expected document by cosine similarity, then records the top-2 as
   ``relevant_chunk_ids``.

NOTE: this is *retriever-anchored* (weak) supervision — the same embed model is
used to define the gold as to evaluate it, so Recall will be optimistic. It is a
baseline, not a target. Manual curation of gold answer spans is still required
before trusting these numbers as a pass/fail gate (see PROJECT_STATUS.md).
"""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv("backend/.env", override=True)

from supabase import create_client
from app.providers.embeddings import get_embedding_provider

# Old gold slug -> source_id stored by ingest_seed.py
SOURCE_ID_MAP = {
    "pacs_model_bylaws_2023": "Model Byelaws 05.01.2023",
    "pmfby_operational_guidelines": "operational_guidelines_pmfby",
    "nsfi_2025_30": "NSFI_2025_30",
    "pacs_computerization_guidelines": "Revised Scheme guidelines (Computerization of PACS project)",
    "corrigendum_letter_2023": "Corrigendum and letter Jun 12, 2023",
}

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
embed_provider = get_embedding_provider()


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


_DOC_CHUNK_CACHE: dict[str, list[tuple[str, list[float], str]]] = {}


def _doc_chunks(source_id: str) -> list[tuple[str, list[float], str]]:
    if source_id in _DOC_CHUNK_CACHE:
        return _DOC_CHUNK_CACHE[source_id]
    import json as _json
    doc = supabase.table("documents").select("id").eq("source_id", source_id).execute().data
    if not doc:
        _DOC_CHUNK_CACHE[source_id] = []
        return []
    doc_uuid = doc[0]["id"]
    rows = (
        supabase.table("chunks")
        .select("id, chunk_id, embedding, content")
        .eq("document_id", doc_uuid)
        .execute()
        .data or []
    )
    out = []
    for r in rows:
        emb = r.get("embedding")
        if not emb:
            continue
        if isinstance(emb, str):
            emb = _json.loads(emb)
        # match_chunks returns c.id (uuid) as `chunk_id`; gold must use the same
        # identifier so retrieval-eval recall aligns with what the retriever returns.
        out.append((r["id"], [float(x) for x in emb], r.get("content", "")[:60]))
    _DOC_CHUNK_CACHE[source_id] = out
    return out


def localize(question: str, source_id: str, top_n: int = 2) -> list[str]:
    """Return the most relevant chunk IDs for ``question`` within ``source_id``."""
    rows = _doc_chunks(source_id)
    if not rows:
        return []
    q_emb = embed_provider.embed_texts([question], task="retrieval.query")[0]
    scored = [(cosine(q_emb, emb), cid, _c) for cid, emb, _c in rows]
    scored.sort(key=lambda x: -x[0])
    return [c[1] for c in scored[:top_n]]


def main() -> None:
    gold_path = Path("eval/gold_cases.yaml")
    cases = yaml.safe_load(gold_path.read_text(encoding="utf-8"))

    updated = 0
    skipped = 0
    for case in cases:
        if not case.get("answerable", False):
            case["relevant_chunk_ids"] = []
            continue
        source_ids = case.get("relevant_source_ids") or []
        if not source_ids:
            skipped += 1
            continue
        # Translate to current source_ids.
        mapped = [SOURCE_ID_MAP.get(s, s) for s in source_ids]
        relevant = []
        for sid in mapped:
            relevant.extend(localize(case["question"], sid))
        if relevant:
            case["relevant_chunk_ids"] = relevant
            case["corpus_snapshot"] = "jina-v3-mineru-v2-2188"
            updated += 1
        else:
            skipped += 1

    gold_path.write_text(yaml.safe_dump(cases, default_flow_style=False, allow_unicode=True), encoding="utf-8")
    total_ans = sum(1 for c in cases if c.get("answerable", False))
    print(f"Updated {updated} answerable gold cases with localized chunk IDs")
    print(f"Total answerable: {total_ans}, skipped (no localization): {skipped}")


if __name__ == "__main__":
    main()
