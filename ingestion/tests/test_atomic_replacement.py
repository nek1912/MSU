"""Unit tests for atomic document replacement via RPC."""
from unittest.mock import MagicMock

import pytest


def test_atomic_replace_uses_rpc():
    """Verify atomic_replace_document calls the RPC correctly."""
    from ingestion.ingest import atomic_replace_document

    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.return_value = MagicMock(data="doc123")

    doc_id = atomic_replace_document(
        mock_supabase,
        source_id="test",
        doc_data={"title": "Test", "organization": "Org"},
        chunks_data=[{"content": "chunk1", "embedding": [0.1] * 768, "page": 1, "section": "S1"}],
    )

    mock_supabase.rpc.assert_called_once()
    call_args = mock_supabase.rpc.call_args
    assert call_args[0][0] == "atomic_replace_document"
    params = call_args[0][1]
    assert params["p_source_id"] == "test"
    assert params["p_doc_data"] == {"title": "Test", "organization": "Org"}
    assert isinstance(params["p_chunks_data"], list)
    assert len(params["p_chunks_data"]) == 1
    assert doc_id == "doc123"


def test_atomic_replace_returns_document_id():
    """Verify the function returns the document ID from RPC."""
    from ingestion.ingest import atomic_replace_document

    mock_supabase = MagicMock()
    expected_id = "abc-123-def-456"
    mock_supabase.rpc.return_value.execute.return_value = MagicMock(data=expected_id)

    doc_id = atomic_replace_document(
        mock_supabase,
        source_id="test",
        doc_data={"title": "Test"},
        chunks_data=[{"content": "chunk1", "embedding": [0.0] * 768}],
    )

    assert doc_id == expected_id


def test_atomic_replace_multiple_chunks():
    """Verify multiple chunks are passed to RPC correctly."""
    from ingestion.ingest import atomic_replace_document

    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.return_value = MagicMock(data="doc456")

    chunks = [
        {"content": "chunk1", "embedding": [0.1] * 768, "page": 1, "section": "S1"},
        {"content": "chunk2", "embedding": [0.2] * 768, "page": 2, "section": "S2"},
        {"content": "chunk3", "embedding": [0.3] * 768, "page": 3, "section": "S3"},
    ]

    atomic_replace_document(
        mock_supabase,
        source_id="test-multi",
        doc_data={"title": "Multi Chunk"},
        chunks_data=chunks,
    )

    call_args = mock_supabase.rpc.call_args
    params = call_args[0][1]
    assert len(params["p_chunks_data"]) == 3
    assert params["p_chunks_data"][0]["content"] == "chunk1"
    assert params["p_chunks_data"][1]["content"] == "chunk2"
    assert params["p_chunks_data"][2]["content"] == "chunk3"


def test_atomic_replace_handles_missing_optional_fields():
    """Verify function handles chunks without optional page/section fields."""
    from ingestion.ingest import atomic_replace_document

    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.return_value = MagicMock(data="doc789")

    chunks = [{"content": "chunk1", "embedding": [0.1] * 768}]

    atomic_replace_document(
        mock_supabase,
        source_id="test-optional",
        doc_data={"title": "Optional Fields"},
        chunks_data=chunks,
    )

    call_args = mock_supabase.rpc.call_args
    params = call_args[0][1]
    chunk_param = params["p_chunks_data"][0]
    assert chunk_param["page"] == 0
    assert chunk_param["section"] == ""


def test_atomic_replace_rpc_error_propagates():
    """Verify RPC errors are propagated, not swallowed."""
    from ingestion.ingest import atomic_replace_document

    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.side_effect = Exception("RPC failed")

    with pytest.raises(Exception, match="RPC failed"):
        atomic_replace_document(
            mock_supabase,
            source_id="test",
            doc_data={"title": "Test"},
            chunks_data=[{"content": "chunk1", "embedding": [0.1] * 768}],
        )