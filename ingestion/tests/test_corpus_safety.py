"""Corpus safety invariant: existing documents must not be deleted if ingestion fails.

Uses the RPC transaction rollback guarantee to verify atomicity.
"""
import pytest


@pytest.mark.integration
def test_existing_document_not_deleted_on_failure():
    """Verify existing document is not deleted if new ingestion fails."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    # Insert a test document with chunks
    test_doc = supabase.table("documents").insert({
        "source_id": "test_safety_doc",
        "title": "Test Safety",
        "organization": "Test",
        "jurisdiction": "central",
        "domain": "test",
        "document_type": "test",
        "source_url": "https://test.com",
        "verified_date": "2026-08-27",
        "source_type": "test",
    }).execute().data[0]

    original_doc_id = test_doc["id"]

    # Insert a chunk
    supabase.table("chunks").insert({
        "document_id": original_doc_id,
        "page": 1,
        "section": "Test",
        "content": "Test content",
        "embedding": [0.1] * 768,
    }).execute()

    # Try to replace with invalid data (should fail after deletion)
    # Use invalid vector dimension to force failure
    with pytest.raises(Exception):
        atomic_replace_document(
            supabase,
            source_id="test_safety_doc",
            doc_data={"title": "Test Safety"},
            chunks_data=[{"content": "chunk1", "embedding": [0.1] * 100}]  # Wrong dimension
        )

    # Verify original document still exists (transaction rolled back)
    result = supabase.table("documents").select("id").eq("source_id", "test_safety_doc").execute()
    assert len(result.data) == 1
    assert result.data[0]["id"] == original_doc_id

    # Verify original chunks still exist
    chunks = supabase.table("chunks").select("*").eq("document_id", original_doc_id).execute()
    assert len(chunks.data) == 1

    # Cleanup
    supabase.table("chunks").delete().eq("document_id", original_doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_safety_doc").execute()
