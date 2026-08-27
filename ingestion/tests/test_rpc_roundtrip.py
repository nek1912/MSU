"""Test RPC round-trip: Python list → Supabase RPC → PostgreSQL vector → retrieval."""
import pytest


@pytest.mark.integration
def test_rpc_vector_roundtrip():
    """Test complete round-trip: Python list → RPC → vector(768) → retrieval.
    
    This verifies the entire boundary:
    1. Python list[768] → JSON serialization
    2. Supabase RPC → PostgreSQL jsonb → vector(768)
    3. Store chunk in database
    4. Retrieve chunk and verify dimension/content/document_id
    """
    from app.db import get_supabase
    from ingestion.ingest import atomic_replace_document

    supabase = get_supabase()

    # Test vector
    test_vector = [0.1] * 768
    test_content = "Test content for round-trip verification"

    # Insert document and chunk via RPC
    doc_id = atomic_replace_document(
        supabase,
        source_id="test_roundtrip_doc",
        doc_data={
            "source_id": "test_roundtrip_doc",
            "title": "Test Roundtrip",
            "organization": "Test",
            "jurisdiction": "central",
            "domain": "test",
            "document_type": "test",
            "source_url": "https://test.com",
            "effective_date": None,
            "document_date": None,
            "verified_date": "2026-08-27",
            "source_type": "test",
        },
        chunks_data=[
            {
                "content": test_content,
                "embedding": test_vector,
                "page": 1,
                "section": "Test Section",
            }
        ]
    )

    # Verify document was created
    assert doc_id is not None

    # Retrieve the chunk
    chunks = supabase.table("chunks").select("*").eq("document_id", doc_id).execute().data

    # Verify chunk exists
    assert len(chunks) == 1
    chunk = chunks[0]

    # Verify content
    assert chunk["content"] == test_content
    assert chunk["page"] == 1
    assert chunk["section"] == "Test Section"

    # Verify embedding dimension
    embedding = chunk["embedding"]
    # Supabase may return as list or as string representation
    if isinstance(embedding, str):
        # Parse string representation
        import json
        embedding = json.loads(embedding.replace("[", "[").replace("]", "]"))

    assert len(embedding) == 768

    # Verify embedding values (approximately)
    for i, val in enumerate(embedding):
        assert abs(val - 0.1) < 0.001, f"Embedding value at index {i} is {val}, expected 0.1"

    # Cleanup
    supabase.table("chunks").delete().eq("document_id", doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_roundtrip_doc").execute()