"""Tests for eval source-ID bug fix.

Verifies that retrieve_live extracts document_id correctly and
resolve_source_ids maps document_id → source_id.
"""
from unittest.mock import MagicMock, patch


def test_retrieve_live_extracts_document_id():
    """Verify retrieve_live extracts document_id, not source_id."""
    from eval.run_retrieval_eval import retrieve_live

    mock_response = MagicMock()
    mock_response.data = [
        {"chunk_id": "abc", "document_id": "doc123", "title": "Test"}
    ]

    mock_client = MagicMock()
    mock_client.rpc.return_value.execute.return_value = mock_response

    env = {"SUPABASE_URL": "http://test", "SUPABASE_SERVICE_KEY": "test-key"}
    with patch.dict("os.environ", env):
        with patch("supabase.create_client", return_value=mock_client):
            with patch("app.providers.embeddings.get_embedding_provider") as mock_embed:
                mock_embed.return_value.embed_texts.return_value = [[0.1] * 768]
                result = retrieve_live("test question", "pacs", None)

                assert len(result) == 1
                assert result[0]["chunk_id"] == "abc"
                assert result[0]["document_id"] == "doc123"
                # Must NOT have source_id key from retrieval
                assert "source_id" not in result[0]


def test_resolve_source_ids_maps_correctly():
    """Verify resolve_source_ids maps document_id → source_id via documents table."""
    from eval.run_retrieval_eval import resolve_source_ids

    retrieved = [
        {"chunk_id": "chunk1", "document_id": "doc123"},
        {"chunk_id": "chunk2", "document_id": "doc456"},
    ]

    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
        {"id": "doc123", "source_id": "pacs_model_bylaws_2023"},
        {"id": "doc456", "source_id": "pmfby_operational_guidelines"},
    ]

    resolved = resolve_source_ids(retrieved, mock_supabase)

    assert resolved[0]["source_id"] == "pacs_model_bylaws_2023"
    assert resolved[1]["source_id"] == "pmfby_operational_guidelines"
    assert resolved[0]["chunk_id"] == "chunk1"
    assert resolved[1]["chunk_id"] == "chunk2"


def test_resolve_source_ids_handles_missing_document():
    """Verify resolve_source_ids returns empty source_id for unknown document_id."""
    from eval.run_retrieval_eval import resolve_source_ids

    retrieved = [
        {"chunk_id": "chunk1", "document_id": "doc_unknown"},
    ]

    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = []

    resolved = resolve_source_ids(retrieved, mock_supabase)

    assert resolved[0]["source_id"] == ""


def test_resolve_source_ids_deduplicates_document_ids():
    """Verify resolve_source_ids sends unique document_ids to the query."""
    from eval.run_retrieval_eval import resolve_source_ids

    retrieved = [
        {"chunk_id": "c1", "document_id": "doc123"},
        {"chunk_id": "c2", "document_id": "doc123"},
        {"chunk_id": "c3", "document_id": "doc456"},
    ]

    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.in_.return_value.execute.return_value.data = [
        {"id": "doc123", "source_id": "source_a"},
        {"id": "doc456", "source_id": "source_b"},
    ]

    resolved = resolve_source_ids(retrieved, mock_supabase)

    # Check that the in_ call received deduplicated IDs
    in_call = mock_supabase.table.return_value.select.return_value.in_
    called_ids = in_call.call_args[0][1]
    assert len(called_ids) == 2

    assert resolved[0]["source_id"] == "source_a"
    assert resolved[1]["source_id"] == "source_a"
    assert resolved[2]["source_id"] == "source_b"


def test_resolve_source_ids_empty_input():
    """Verify resolve_source_ids handles empty retrieval results."""
    from eval.run_retrieval_eval import resolve_source_ids

    mock_supabase = MagicMock()
    resolved = resolve_source_ids([], mock_supabase)

    assert resolved == []
    mock_supabase.table.assert_not_called()


def test_compute_recall_metrics_basic():
    """Verify compute_recall_metrics computes correct recall and MRR."""
    from eval.run_retrieval_eval import compute_recall_metrics

    results = [
        {
            "question": "What is PACS?",
            "relevant_source_ids": ["pacs_model_bylaws"],
            "relevant_chunk_ids": ["chunk_abc"],
            "retrieved": [
                {"chunk_id": "chunk_abc", "source_id": "pacs_model_bylaws"},
            ],
        },
    ]

    metrics = compute_recall_metrics(results)

    assert metrics["total"] == 1
    assert metrics["recall_at"]["r@1"] == 1.0
    assert metrics["recall_at"]["r@3"] == 1.0
    assert metrics["recall_at"]["r@5"] == 1.0
    assert metrics["mrr"] == 1.0


def test_compute_recall_metrics_no_match():
    """Verify recall is 0 when no relevant chunks are retrieved."""
    from eval.run_retrieval_eval import compute_recall_metrics

    results = [
        {
            "question": "What is PACS?",
            "relevant_source_ids": ["pacs_model_bylaws"],
            "relevant_chunk_ids": ["chunk_abc"],
            "retrieved": [
                {"chunk_id": "chunk_other", "source_id": "other_source"},
            ],
        },
    ]

    metrics = compute_recall_metrics(results)

    assert metrics["recall_at"]["r@5"] == 0.0
    assert metrics["mrr"] == 0.0


def test_compute_recall_metrics_empty():
    """Verify compute_recall_metrics handles empty results."""
    from eval.run_retrieval_eval import compute_recall_metrics

    metrics = compute_recall_metrics([])

    assert metrics["total"] == 0
    assert metrics["evaluated"] == 0
    assert metrics["mrr"] == 0.0
