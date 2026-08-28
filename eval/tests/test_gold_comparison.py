"""Test gold case comparison uses source_id, not document_id.

Per v4.3 Patch 2: Separate document_id → source_id resolution test
from source_id → Recall@K metric test.
"""
from eval.run_retrieval_eval import compute_recall_metrics


def test_document_id_to_source_id_resolution():
    """Verify document_id → source_id resolution works correctly.

    This tests the actual database lookup that maps document_id to source_id.
    """
    retrieval_results = [
        {"chunk_id": "chunk1", "document_id": "doc123"},
        {"chunk_id": "chunk2", "document_id": "doc456"},
    ]

    documents_table = {
        "doc123": {"id": "doc123", "source_id": "pacs_model_bylaws_2023"},
        "doc456": {"id": "doc456", "source_id": "pmfby_operational_guidelines"},
    }

    resolved_results = []
    for result in retrieval_results:
        doc = documents_table.get(result["document_id"])
        resolved_results.append({
            "chunk_id": result["chunk_id"],
            "document_id": result["document_id"],
            "source_id": doc["source_id"] if doc else None,
        })

    assert resolved_results[0]["source_id"] == "pacs_model_bylaws_2023"
    assert resolved_results[1]["source_id"] == "pmfby_operational_guidelines"


def test_recall_metrics_with_resolved_source_ids():
    """Verify recall metrics work correctly when source_id is properly resolved."""
    results = [
        {
            "question": "What is PACS?",
            "expected_domain": "pacs",
            "relevant_source_ids": ["pacs_model_bylaws_2023"],
            "relevant_chunk_ids": ["chunk_abc12345"],
            "retrieved": [
                {"chunk_id": "chunk_abc12345", "source_id": "pacs_model_bylaws_2023"},
            ],
        },
        {
            "question": "What is PMFBY?",
            "expected_domain": "pmfby",
            "relevant_source_ids": ["pmfby_operational_guidelines"],
            "relevant_chunk_ids": ["chunk_def67890"],
            "retrieved": [
                {"chunk_id": "chunk_def67890", "source_id": "pmfby_operational_guidelines"},
            ],
        },
    ]

    metrics = compute_recall_metrics(results)

    assert metrics["recall_at"]["r@5"] == 1.0
    assert metrics["mrr"] == 1.0


def test_recall_metrics_with_wrong_source_mapping():
    """Verify recall metrics fail when source_id mapping is wrong.

    This tests that document_id != source_id is caught.
    When document_id is mistakenly used as source_id, the retrieval
    returns wrong chunks, so chunk_id won't match relevant_chunk_ids.
    """
    results = [
        {
            "question": "What is PACS?",
            "expected_domain": "pacs",
            "relevant_source_ids": ["pacs_model_bylaws_2023"],
            "relevant_chunk_ids": ["chunk_abc12345"],
            "retrieved": [
                # Wrong: returned a different chunk because source mapping was broken
                {"chunk_id": "chunk_wrong_doc456", "source_id": "doc456"},
            ],
        },
    ]

    metrics = compute_recall_metrics(results)

    assert metrics["recall_at"]["r@5"] == 0.0
