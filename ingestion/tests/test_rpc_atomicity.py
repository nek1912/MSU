"""Integration tests for RPC transaction atomicity."""
import pytest


@pytest.mark.integration
def test_rpc_atomicity_rollback():
    """Test that RPC transaction rolls back on failure.
    
    This test verifies that if the RPC fails (e.g., wrong vector dimension),
    the original document and chunks are preserved.
    """
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    # Insert a test document first
    test_doc = supabase.table("documents").insert({
        "source_id": "test_rollback_doc",
        "title": "Test Rollback",
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
            source_id="test_rollback_doc",
            doc_data={"title": "Test Rollback"},
            chunks_data=[{"content": "chunk1", "embedding": [0.1] * 100}]  # Wrong dimension
        )

    # Verify original document still exists (transaction rolled back)
    result = supabase.table("documents").select("id").eq("source_id", "test_rollback_doc").execute()
    assert len(result.data) == 1
    assert result.data[0]["id"] == original_doc_id

    # Verify original chunks still exist
    chunks = supabase.table("chunks").select("*").eq("document_id", original_doc_id).execute()
    assert len(chunks.data) == 1

    # Cleanup
    supabase.table("chunks").delete().eq("document_id", original_doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_rollback_doc").execute()


@pytest.mark.integration
def test_rpc_atomicity_success():
    """Test that successful RPC replaces document and chunks atomically."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    # Insert initial document
    initial_doc = supabase.table("documents").insert({
        "source_id": "test_atomic_success",
        "title": "Initial Title",
        "organization": "Test Org",
        "jurisdiction": "central",
        "domain": "test",
        "document_type": "test",
        "source_url": "https://test.com",
        "verified_date": "2026-08-27",
        "source_type": "test",
    }).execute().data[0]

    initial_doc_id = initial_doc["id"]

    # Insert initial chunk
    supabase.table("chunks").insert({
        "document_id": initial_doc_id,
        "page": 1,
        "section": "Initial",
        "content": "Initial content",
        "embedding": [0.1] * 768,
    }).execute()

    # Replace with new data
    new_doc_id = atomic_replace_document(
        supabase,
        source_id="test_atomic_success",
        doc_data={
            "title": "Updated Title",
            "organization": "Updated Org",
            "jurisdiction": "central",
            "domain": "test",
            "document_type": "test",
            "source_url": "https://test.com/updated",
            "verified_date": "2026-08-27",
            "source_type": "test",
        },
        chunks_data=[
            {"content": "New chunk 1", "embedding": [0.2] * 768, "page": 1, "section": "S1"},
            {"content": "New chunk 2", "embedding": [0.3] * 768, "page": 2, "section": "S2"},
        ]
    )

    # Verify new document exists
    assert new_doc_id is not None
    doc_result = supabase.table("documents").select("*").eq("id", new_doc_id).execute()
    assert len(doc_result.data) == 1
    assert doc_result.data[0]["title"] == "Updated Title"

    # Verify new chunks exist
    chunks = supabase.table("chunks").select("*").eq("document_id", new_doc_id).execute()
    assert len(chunks.data) == 2

    # Verify old document is gone
    old_doc = supabase.table("documents").select("id").eq("id", initial_doc_id).execute()
    assert len(old_doc.data) == 0

    # Cleanup
    supabase.table("chunks").delete().eq("document_id", new_doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_atomic_success").execute()