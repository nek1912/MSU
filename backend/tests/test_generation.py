from unittest.mock import MagicMock

import pytest

from app.generation import CitationError, generate_answer, verify_citations
from app.retrieval import RetrievedChunk

IDS = ["aaaaaaaa-1111-2222-3333-444444444444", "bbbbbbbb-5555-6666-7777-888888888888"]


def test_valid_citation_extracted():
    valid, invalid = verify_citations("X [chunk:aaaaaaaa].", IDS)
    assert valid == ["aaaaaaaa-1111-2222-3333-444444444444"]
    assert invalid == []


def test_invalid_citation_detected():
    valid, invalid = verify_citations("Y [chunk:zzzzzzzz].", IDS)
    assert valid == []
    assert invalid == ["zzzzzzzz"]


def test_mixed_citations_valid_and_invalid():
    valid, invalid = verify_citations("A [chunk:aaaaaaaa] B [chunk:zzzzzzzz]", IDS)
    assert valid == ["aaaaaaaa-1111-2222-3333-444444444444"]
    assert invalid == ["zzzzzzzz"]


def test_mixed_citations_keep_only_valid_in_order():
    valid, invalid = verify_citations("A [chunk:bbbbbbbb] B [chunk:aaaaaaaa]", IDS)
    assert valid == [
        "bbbbbbbb-5555-6666-7777-888888888888",
        "aaaaaaaa-1111-2222-3333-444444444444"]
    assert invalid == []


def test_generate_answer_raises_on_no_citations():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "The answer is unclear."
    chunks = [RetrievedChunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
                             stable_chunk_id="test:p1:c0",
                             document_id="dddd1111-2222-3333-4444-555555555555",
                             title="T", page=1, page_start=1, page_end=1,
                             section="S", content="C", similarity=0.8,
                             source_url="https://x", domain="pmfby",
                             jurisdiction="central", state=None)]
    with pytest.raises(CitationError):
        generate_answer(mock_llm, "test question", chunks)


def test_generate_answer_raises_on_invalid_citations():
    """Any invalid citation must cause abstention, not just missing valid ones."""
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Fact A [chunk:aaaaaaaa]. Fact B [chunk:zzzzzzzz]."
    chunks = [RetrievedChunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
                             stable_chunk_id="test:p1:c0",
                             document_id="dddd1111-2222-3333-4444-555555555555",
                             title="T", page=1, page_start=1, page_end=1,
                             section="S", content="C", similarity=0.8,
                             source_url="https://x", domain="pmfby",
                             jurisdiction="central", state=None)]
    with pytest.raises(CitationError, match="invalid citations"):
        generate_answer(mock_llm, "test question", chunks)


def test_generate_answer_returns_answer_with_valid_citation():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Farmers are eligible [chunk:aaaaaaaa]."
    chunks = [RetrievedChunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
                             stable_chunk_id="test:p1:c0",
                             document_id="dddd1111-2222-3333-4444-555555555555",
                             title="T", page=1, page_start=1, page_end=1,
                             section="S", content="C", similarity=0.8,
                             source_url="https://x", domain="pmfby",
                             jurisdiction="central", state=None)]
    result = generate_answer(mock_llm, "test question", chunks)
    assert "eligible" in result
