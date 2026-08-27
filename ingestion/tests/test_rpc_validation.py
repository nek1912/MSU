"""RPC validation tests for atomic_replace_document."""
import pytest


@pytest.mark.integration
def test_rpc_rejects_null_chunks():
    """Verify RPC rejects NULL p_chunks_data."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    with pytest.raises(Exception) as exc_info:
        atomic_replace_document(
            supabase,
            source_id="test_validation",
            doc_data={"title": "Test"},
            chunks_data=None
        )

    assert "p_chunks_data must not be NULL" in str(exc_info.value)


@pytest.mark.integration
def test_rpc_rejects_non_array_chunks():
    """Verify RPC rejects non-array p_chunks_data."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    # Pass a dict instead of a list
    with pytest.raises(Exception) as exc_info:
        supabase.rpc(
            "atomic_replace_document",
            {
                "p_source_id": "test_validation",
                "p_doc_data": {"title": "Test"},
                "p_chunks_data": {"content": "not an array"},  # Wrong type
            }
        ).execute()

    assert "p_chunks_data must be a JSON array" in str(exc_info.value)


@pytest.mark.integration
def test_rpc_rejects_empty_array():
    """Verify RPC rejects empty p_chunks_data array."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    with pytest.raises(Exception) as exc_info:
        atomic_replace_document(
            supabase,
            source_id="test_validation",
            doc_data={"title": "Test"},
            chunks_data=[]
        )

    assert "p_chunks_data must contain at least one chunk" in str(exc_info.value)


@pytest.mark.integration
def test_rpc_accepts_valid_input():
    """Verify RPC accepts valid input."""
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    doc_id = atomic_replace_document(
        supabase,
        source_id="test_validation_valid",
        doc_data={
            "title": "Test Document",
            "organization": "Test Org",
            "jurisdiction": "central",
            "domain": "test",
            "document_type": "test",
            "source_url": "https://test.com",
            "verified_date": "2026-08-27",
            "source_type": "test",
        },
        chunks_data=[
            {"content": "Test content", "embedding": [0.1] * 768, "page": 1, "section": "Test"}
        ]
    )

    assert doc_id is not None

    # Cleanup
    supabase.table("chunks").delete().eq("document_id", doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_validation_valid").execute()