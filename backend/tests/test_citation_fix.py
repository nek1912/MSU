"""Tests for citation verification helper functions."""
from app.generation import verify_citations
from app.retrieval import RetrievedChunk
from app.routes.chat import _citations_from


CHUNK_ID = "abc1234567890abcdef1234567890abcd"


def _chunks():
    return [
        RetrievedChunk(
            chunk_id=CHUNK_ID, title="T", page=1, section="S",
            content="C", similarity=0.9, source_url="https://x",
            domain="pacs", jurisdiction="central", state=None),
    ]


def test_citations_from_filters_invalid():
    chunks = _chunks()
    answer = "This is about PACS [chunk:abc12345] but also [chunk:deadbeef]"
    citations = _citations_from(answer, chunks)
    assert len(citations) == 1
    assert citations[0]["title"] == "T"


def test_citations_from_accepts_valid():
    chunks = _chunks()
    answer = "This is about PACS [chunk:abc12345]"
    citations = _citations_from(answer, chunks)
    assert len(citations) == 1
    assert citations[0]["title"] == "T"


def test_citations_from_empty_when_no_markers():
    chunks = _chunks()
    answer = "This has no citation markers."
    citations = _citations_from(answer, chunks)
    assert citations == []


def test_verify_citations_rejects_invalid():
    chunks = _chunks()
    answer = "This is about PACS [chunk:deadbeef]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 0
    assert len(invalid) == 1


def test_verify_citations_accepts_valid():
    chunks = _chunks()
    answer = "This is about PACS [chunk:abc12345]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 1
    assert len(invalid) == 0


def test_verify_citations_rejects_mixed():
    chunks = _chunks()
    answer = "PACS [chunk:abc12345] and also [chunk:deadbeef]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 1
    assert len(invalid) == 1
