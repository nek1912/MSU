import os
from pathlib import Path

import pytest

MANIFEST_PATH = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"

_HOLD_MANIFEST_PATH = MANIFEST_PATH.parent / "hold_sources.yaml"

_EXPECTED_MVP_IDS = {
    "pacs_model_bylaws_2023",
    "pacs_computerization_guidelines",
    "pacs_computerization_corrigendum_2023_06_12",
    "pmfby_operational_guidelines",
    "nsfi_2025_30",
}


@pytest.mark.integration
def test_mvp_ingestion_with_real_pdfs():
    """Integration test: ingest real MVP PDFs into Supabase.

    Requires:
        1. Real MVP PDF files in corpus/seeds/
        2. Supabase connection (SUPABASE_URL, SUPABASE_SERVICE_KEY env vars)
        3. Gemini API key (GEMINI_API_KEY env vars)
    """
    missing = [v for v in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "GEMINI_API_KEY") if not os.environ.get(v)]
    if missing:
        pytest.skip(f"Missing env vars: {missing}")

    from app.db import get_supabase
    from app.providers.embeddings import get_embedding_provider
    from ingestion.ingestion.ingest import manifest_to_supabase
    from ingestion.ingestion.manifest import load_hold_manifest, load_mvp_manifest

    embed_provider = get_embedding_provider()
    supabase = get_supabase()

    # Ingest MVP PDFs into Supabase
    result = manifest_to_supabase(MANIFEST_PATH, embed_provider.embed_texts, supabase)

    # Verify manifest source count
    sources = load_mvp_manifest(MANIFEST_PATH)
    expected_ids = {s["source_id"] for s in sources}
    assert len(expected_ids) == len(_EXPECTED_MVP_IDS), (
        f"Manifest has {len(expected_ids)} sources, expected {len(_EXPECTED_MVP_IDS)}"
    )

    # All MVP documents should have been ingested
    assert len(result["succeeded"]) == len(expected_ids), (
        f"Expected {len(expected_ids)} succeeded, got {len(result['succeeded'])}"
    )
    assert len(result["failed"]) == 0, f"Expected 0 failed, got {result['failed']}"

    # Verify all expected MVP source IDs exist in the documents table
    docs = supabase.table("documents").select("id, source_id").execute().data
    actual_ids = {d["source_id"] for d in docs}
    missing_ids = expected_ids - actual_ids
    assert not missing_ids, f"Missing MVP sources: {missing_ids}"

    # Verify no hold source IDs exist
    if _HOLD_MANIFEST_PATH.exists():
        hold_sources = load_hold_manifest(_HOLD_MANIFEST_PATH)
        hold_ids = {s["source_id"] for s in hold_sources}
        leaked = actual_ids & hold_ids
        assert not leaked, f"Hold sources found in DB: {leaked}"

    # Verify every MVP document has chunks and correct embedding dimension
    for doc in docs:
        if doc["source_id"] not in expected_ids:
            continue
        chunks = (
            supabase.table("chunks")
            .select("*")
            .eq("document_id", doc["id"])
            .execute()
            .data
        )
        assert len(chunks) > 0, f"Document {doc['source_id']} has no chunks"

        # Embedding dimension must be 768
        assert len(chunks[0]["embedding"]) == 768, (
            f"Document {doc['source_id']} has wrong embedding dimension: {len(chunks[0]['embedding'])}"
        )

        # No empty chunks
        for chunk in chunks:
            assert chunk["content"].strip(), f"Empty chunk in {doc['source_id']}"
