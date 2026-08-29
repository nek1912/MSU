"""PHASE 8: Citation correctness validation tests.

Verifies that the citation chain is enforced in backend code:
citation → retrieved chunk → stable_chunk_id → source document → source page

Must reject:
- Citation to non-retrieved chunk (fabricated)
- Citation to wrong document
- Citation to wrong page
- Malformed citations

Enforced in backend code, not just prompt instructions.
"""
import pytest

from app.generation import CitationError, validate_citation_chain, verify_citations
from app.retrieval import RetrievedChunk


def _chunk(
    chunk_id: str = "aaaaaaaa-1111-2222-3333-444444444444",
    stable_chunk_id: str = "pmfby-faq:p1:c0",
    document_id: str = "doc-001",
    title: str = "PMFBY FAQ",
    page: int = 1,
    section: str = "Eligibility",
    content: str = "Eligible farmers are covered.",
    domain: str = "pmfby",
    jurisdiction: str = "central",
    state: str | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        stable_chunk_id=stable_chunk_id,
        document_id=document_id,
        title=title,
        page=page,
        page_start=page,
        page_end=page,
        section=section,
        content=content,
        similarity=0.8,
        source_url=f"https://pmfby.gov.in/{stable_chunk_id}",
        domain=domain,
        jurisdiction=jurisdiction,
        state=state,
    )


# ═══════════════════════════════════════════════════════════════════════════
# VALID CITATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestValidCitations:
    """Valid citations must resolve through the full chain."""

    def test_single_valid_citation(self):
        chunks = [_chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444")]
        answer = "Farmers are eligible [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert len(result) == 1
        assert result[0]["chunk_id"] == "pmfby-faq:p1:c0"
        assert result[0]["document_id"] == "doc-001"
        assert result[0]["page"] == 1

    def test_multiple_valid_citations(self):
        chunks = [
            _chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
                   stable_chunk_id="doc1:p1:c0", page=1),
            _chunk(chunk_id="bbbbbbbb-5555-6666-7777-888888888888",
                   stable_chunk_id="doc2:p4:c0", page=4,
                   document_id="doc-002", title="Guidelines"),
        ]
        answer = "Fact A [chunk:aaaaaaaa]. Fact B [chunk:bbbbbbbb]."
        result = validate_citation_chain(answer, chunks)
        assert len(result) == 2
        assert result[0]["page"] == 1
        assert result[1]["page"] == 4

    def test_duplicate_citation_deduplicated(self):
        chunks = [_chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444")]
        answer = "X [chunk:aaaaaaaa] and Y [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert len(result) == 1

    def test_no_citations_returns_empty(self):
        chunks = [_chunk()]
        answer = "No citations here."
        result = validate_citation_chain(answer, chunks)
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════
# FABRICATED CITATIONS (non-retrieved chunks)
# ═══════════════════════════════════════════════════════════════════════════

class TestFabricatedCitations:
    """Citations to non-retrieved chunks must be rejected."""

    def test_fabricated_chunk_rejected(self):
        chunks = [_chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444")]
        answer = "Something [chunk:11111111] happened."
        with pytest.raises(CitationError, match="fabricated citation"):
            validate_citation_chain(answer, chunks)

    def test_all_fabricated_rejected(self):
        chunks = [_chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444")]
        answer = "X [chunk:11111111] and Y [chunk:22222222]."
        with pytest.raises(CitationError, match="fabricated citation"):
            validate_citation_chain(answer, chunks)

    def test_mixed_valid_and_fabricated_rejected(self):
        chunks = [_chunk(chunk_id="aaaaaaaa-1111-2222-3333-444444444444")]
        answer = "Good [chunk:aaaaaaaa] and bad [chunk:11111111]."
        with pytest.raises(CitationError, match="fabricated citation"):
            validate_citation_chain(answer, chunks)


# ═══════════════════════════════════════════════════════════════════════════
# MALFORMED CITATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestMalformedCitations:
    """Malformed citation syntax must be rejected."""

    def test_non_hex_content_rejected(self):
        chunks = [_chunk()]
        answer = "Something [chunk:not-hex] happened."
        with pytest.raises(CitationError, match="malformed citation"):
            validate_citation_chain(answer, chunks)

    def test_empty_citation_rejected(self):
        chunks = [_chunk()]
        answer = "Something [chunk:] happened."
        with pytest.raises(CitationError, match="malformed citation"):
            validate_citation_chain(answer, chunks)

    def test_too_short_prefix_rejected(self):
        chunks = [_chunk()]
        answer = "Something [chunk:abc] happened."
        with pytest.raises(CitationError, match="malformed citation"):
            validate_citation_chain(answer, chunks)


# ═══════════════════════════════════════════════════════════════════════════
# CITATION WITHOUT CHUNKS
# ═══════════════════════════════════════════════════════════════════════════

class TestCitationWithoutChunks:
    """Citations when no chunks were retrieved must be rejected."""

    def test_citation_with_empty_chunks(self):
        answer = "Something [chunk:aaaaaaaa] happened."
        with pytest.raises(CitationError, match="no chunks retrieved"):
            validate_citation_chain(answer, [])

    def test_no_citation_with_empty_chunks_ok(self):
        answer = "No citations here."
        result = validate_citation_chain(answer, [])
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════
# CITATION METADATA INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════

class TestCitationMetadataIntegrity:
    """Citation must resolve to correct document and page."""

    def test_citation_resolves_to_correct_document(self):
        chunks = [_chunk(
            chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
            document_id="doc-999",
            stable_chunk_id="special-doc:p1:c0",
        )]
        answer = "Fact [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert result[0]["document_id"] == "doc-999"
        assert result[0]["chunk_id"] == "special-doc:p1:c0"

    def test_citation_resolves_to_correct_page(self):
        chunks = [_chunk(
            chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
            page=42,
        )]
        answer = "Fact [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert result[0]["page"] == 42

    def test_citation_resolves_to_correct_title(self):
        chunks = [_chunk(
            chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
            title="Official Gazette Notification",
        )]
        answer = "Fact [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert result[0]["title"] == "Official Gazette Notification"

    def test_citation_resolves_to_correct_url(self):
        chunks = [_chunk(
            chunk_id="aaaaaaaa-1111-2222-3333-444444444444",
            stable_chunk_id="doc:p1:c0",
        )]
        answer = "Fact [chunk:aaaaaaaa]."
        result = validate_citation_chain(answer, chunks)
        assert result[0]["url"] == "https://pmfby.gov.in/doc:p1:c0"


# ═══════════════════════════════════════════════════════════════════════════
# EXISTING verify_citations COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════════

class TestVerifyCitationsCompat:
    """verify_citations still works for backward compatibility."""

    def test_valid_citation_extracted(self):
        IDS = ["aaaaaaaa-1111-2222-3333-444444444444"]
        valid, invalid = verify_citations("X [chunk:aaaaaaaa].", IDS)
        assert valid == ["aaaaaaaa-1111-2222-3333-444444444444"]
        assert invalid == []

    def test_invalid_citation_detected(self):
        IDS = ["aaaaaaaa-1111-2222-3333-444444444444"]
        valid, invalid = verify_citations("Y [chunk:zzzzzzzz].", IDS)
        assert valid == []
        assert invalid == ["zzzzzzzz"]

    def test_mixed_citations(self):
        IDS = ["aaaaaaaa-1111-2222-3333-444444444444",
               "bbbbbbbb-5555-6666-7777-888888888888"]
        valid, invalid = verify_citations(
            "A [chunk:aaaaaaaa] B [chunk:zzzzzzzz]", IDS)
        assert valid == ["aaaaaaaa-1111-2222-3333-444444444444"]
        assert invalid == ["zzzzzzzz"]
