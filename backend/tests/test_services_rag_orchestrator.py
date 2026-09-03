"""Tests for RAGOrchestrator — dual-pipeline RAG with evidence merging."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.citation_verifier import VerificationResult
from app.config import Settings
from app.contracts import (
    AbstentionReason,
    ConfidenceBand,
    EvidenceChunk,
    RAGResponse,
    RAGResult,
)
from app.llm_fallback import AllProvidersFailedError
from app.services.rag_orchestrator import RAGOrchestrator
from app.web_rag.query_classifier import QueryClassification


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_settings(**overrides) -> Settings:
    defaults = {
        "groq_api_key": "test-groq-key",
        "gemini_api_key": "test-gemini-key",
        "jina_api_key": "test-jina-key",
        "supabase_url": "https://test.supabase.co",
        "supabase_service_key": "test-key",
        "reranker_enabled": False,
    }
    defaults.update(overrides)
    return Settings(**defaults)


def _make_evidence_chunk(
    chunk_id: str = "chunk-abc12345",
    content: str = "PMFBY provides crop insurance to farmers.",
    source_type: str = "static",
    title: str = "PMFBY Guidelines",
    section: str = "Overview",
    page: int = 1,
    url: str = "https://pmfby.gov.in",
    domain: str = "pmfby",
    jurisdiction: str = "central",
    state: str | None = None,
    dense_score: float = 0.75,
) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        content=content,
        source_type=source_type,
        title=title,
        url=url,
        page=page,
        section=section,
        domain=domain,
        jurisdiction=jurisdiction,
        state=state,
        dense_score=dense_score,
    )


def _make_rag_result(
    chunks: list[EvidenceChunk] | None = None,
    abstained: bool = False,
    reason: AbstentionReason | None = None,
    band: ConfidenceBand | None = None,
    domain: str = "pmfby",
) -> RAGResult:
    return RAGResult(
        chunks=chunks or [],
        abstained=abstained,
        reason=reason,
        band=band,
        domain=domain,
    )


def _make_classification(
    domain: str = "pmfby",
    jurisdiction: str = "central",
    state: str | None = None,
    intent: str = "INFORMATIONAL",
    confidence: float = 0.85,
) -> QueryClassification:
    return QueryClassification(
        domain=domain,
        jurisdiction=jurisdiction,
        state=state,
        intent=intent,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestInitialization:
    def test_creates_with_default_settings(self):
        with patch("app.services.rag_orchestrator.get_settings") as mock_settings:
            mock_settings.return_value = _make_settings()
            orch = RAGOrchestrator()
            assert orch._settings is not None

    def test_creates_with_provided_settings(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        assert orch._settings is settings

    def test_initializes_static_and_web_services(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        assert orch._static_rag is not None
        assert orch._web_rag is not None


# ---------------------------------------------------------------------------
# Pipeline parallelism
# ---------------------------------------------------------------------------

class TestPipelineParallelism:
    def test_both_pipelines_called(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_result = _make_rag_result(
            chunks=[_make_evidence_chunk()],
            band=ConfidenceBand.HIGH,
        )
        web_result = _make_rag_result(
            chunks=[_make_evidence_chunk(source_type="web")],
            band=ConfidenceBand.MEDIUM,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result) as mock_static, \
             patch.object(orch._web_rag, "retrieve", return_value=web_result) as mock_web, \
             patch("app.services.rag_orchestrator.grounded_answer", return_value="Answer about PMFBY [chunk:chunk-abc12345]"):

            response = orch.run(
                query="What is PMFBY?",
                english_query="What is PMFBY?",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-1",
            )

            mock_static.assert_called_once()
            mock_web.assert_called_once()
            assert isinstance(response, RAGResponse)


# ---------------------------------------------------------------------------
# Abstention
# ---------------------------------------------------------------------------

class TestAbstention:
    def test_both_pipelines_abstained_returns_abstain(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)

        static_result = _make_rag_result(
            abstained=True,
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            band=ConfidenceBand.LOW,
        )
        web_result = _make_rag_result(
            abstained=True,
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            band=ConfidenceBand.LOW,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result):

            response = orch.run(
                query="What is the weather?",
                english_query="What is the weather?",
                embedding=[0.1] * 768,
                domain="general",
                state=None,
                classification=None,
                history=None,
                lang="en",
                session_id="sess-2",
            )

            assert response.abstained is True
            assert response.confidence == 0.0
            assert response.citations == []
            assert response.answer

    def test_static_abstained_web_has_chunks_proceeds(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_result = _make_rag_result(
            abstained=True,
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            band=ConfidenceBand.LOW,
        )
        web_result = _make_rag_result(
            chunks=[_make_evidence_chunk(source_type="web")],
            abstained=False,
            band=ConfidenceBand.MEDIUM,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer", return_value="Web answer [chunk:chunk-abc12345]"), \
             patch("app.services.rag_orchestrator.verify_citations", return_value=VerificationResult(is_valid=True)):

            response = orch.run(
                query="Tell me about PMFBY",
                english_query="Tell me about PMFBY",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-3",
            )

            assert response.abstained is False
            assert response.mode == "web"

    def test_web_abstained_static_has_chunks_proceeds(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_result = _make_rag_result(
            chunks=[_make_evidence_chunk()],
            abstained=False,
            band=ConfidenceBand.HIGH,
        )
        web_result = _make_rag_result(
            abstained=True,
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            band=ConfidenceBand.LOW,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer", return_value="Static answer [chunk:chunk-abc12345]"), \
             patch("app.services.rag_orchestrator.verify_citations", return_value=VerificationResult(is_valid=True)):

            response = orch.run(
                query="PMFBY details",
                english_query="PMFBY details",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-4",
            )

            assert response.abstained is False
            assert response.mode == "static"


# ---------------------------------------------------------------------------
# Evidence merging
# ---------------------------------------------------------------------------

class TestEvidenceMerging:
    def test_merge_evidence_preserves_order(self):
        orch = RAGOrchestrator(_make_settings())
        static_chunks = [_make_evidence_chunk(chunk_id="static-1", source_type="static")]
        web_chunks = [_make_evidence_chunk(chunk_id="web-1", source_type="web")]

        merged = orch._merge_evidence(static_chunks, web_chunks)

        assert len(merged) == 2
        assert merged[0].chunk_id == "static-1"
        assert merged[1].chunk_id == "web-1"

    def test_merge_empty_lists(self):
        orch = RAGOrchestrator(_make_settings())
        merged = orch._merge_evidence([], [])
        assert merged == []

    def test_merge_static_only(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [_make_evidence_chunk(chunk_id="s1"), _make_evidence_chunk(chunk_id="s2")]
        merged = orch._merge_evidence(chunks, [])
        assert len(merged) == 2

    def test_merge_web_only(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [_make_evidence_chunk(chunk_id="w1", source_type="web")]
        merged = orch._merge_evidence([], chunks)
        assert len(merged) == 1
        assert merged[0].source_type == "web"


# ---------------------------------------------------------------------------
# Context building
# ---------------------------------------------------------------------------

class TestBuildContext:
    def test_build_context_with_static_chunks(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [
            _make_evidence_chunk(
                chunk_id="abc12345def67890",
                title="PMFBY Guide",
                section="Premium",
                page=5,
                content="Premium is 2% for kharif.",
            ),
        ]
        context = orch._build_context(chunks, None, "PMFBY premium")
        assert "abc12345" in context
        assert "Premium is 2% for kharif" in context
        assert "PMFBY Guide" in context

    def test_build_context_with_web_chunks(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [
            _make_evidence_chunk(
                chunk_id="web12345",
                source_type="web",
                title="Web Article",
                url="https://example.com",
                content="PMFBY coverage details.",
            ),
        ]
        context = orch._build_context(chunks, None, "PMFBY coverage")
        assert "web12345" in context
        assert "Web Article" in context
        assert "https://example.com" in context

    def test_build_context_empty_chunks(self):
        orch = RAGOrchestrator(_make_settings())
        context = orch._build_context([], None, "query")
        assert context == "No evidence available."

    def test_build_context_with_history(self):
        orch = RAGOrchestrator(_make_settings())
        history = [
            {"role": "user", "content": "What is PMFBY?"},
            {"role": "assistant", "content": "PMFBY is a crop insurance scheme."},
        ]
        chunks = [_make_evidence_chunk()]
        context = orch._build_context(chunks, history, "Tell me more")
        assert "PMFBY" in context


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_prompt_contains_question(self):
        orch = RAGOrchestrator(_make_settings())
        prompt = orch._build_prompt("What is PMFBY?", "context", None, 1, 0)
        assert "What is PMFBY?" in prompt

    def test_prompt_contains_context(self):
        orch = RAGOrchestrator(_make_settings())
        prompt = orch._build_prompt("q", "some context text", None, 0, 0)
        assert "some context text" in prompt

    def test_prompt_contains_source_counts(self):
        orch = RAGOrchestrator(_make_settings())
        prompt = orch._build_prompt("q", "ctx", None, 3, 2)
        assert "3 chunks from official documents" in prompt
        assert "2 chunks from web sources" in prompt

    def test_prompt_contains_history(self):
        orch = RAGOrchestrator(_make_settings())
        history = [{"role": "user", "content": "previous question"}]
        prompt = orch._build_prompt("q", "ctx", history, 0, 0)
        assert "previous question" in prompt

    def test_prompt_no_history(self):
        orch = RAGOrchestrator(_make_settings())
        prompt = orch._build_prompt("q", "ctx", None, 0, 0)
        assert "Previous conversation" not in prompt


# ---------------------------------------------------------------------------
# Citation auto-append
# ---------------------------------------------------------------------------

class TestAutoAppendCitations:
    def test_existing_citations_not_appended(self):
        orch = RAGOrchestrator(_make_settings())
        answer = "PMFBY provides insurance [chunk:abc12345]"
        chunks = [_make_evidence_chunk(chunk_id="abc12345def67890")]
        result = orch._auto_append_citations(answer, chunks)
        assert result == answer

    def test_missing_citations_appended(self):
        orch = RAGOrchestrator(_make_settings())
        answer = "PMFBY provides crop insurance."
        chunks = [_make_evidence_chunk(chunk_id="abc12345def67890")]
        result = orch._auto_append_citations(answer, chunks)
        assert "[chunk:abc12345]" in result
        assert result.startswith("PMFBY provides crop insurance.")

    def test_no_chunks_no_append(self):
        orch = RAGOrchestrator(_make_settings())
        answer = "Some answer."
        result = orch._auto_append_citations(answer, [])
        assert result == answer

    def test_max_three_citations_appended(self):
        orch = RAGOrchestrator(_make_settings())
        answer = "Answer text."
        chunks = [
            _make_evidence_chunk(chunk_id=f"aaaa{i:04d}bbbbcccc")
            for i in range(5)
        ]
        result = orch._auto_append_citations(answer, chunks)
        citation_count = result.count("[chunk:")
        assert citation_count == 3


# ---------------------------------------------------------------------------
# Citation building
# ---------------------------------------------------------------------------

class TestBuildCitations:
    def test_build_citations_static(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [
            _make_evidence_chunk(
                chunk_id="abc12345def67890",
                title="PMFBY Guide",
                source_type="static",
                page=10,
                section="Premium",
            ),
        ]
        citations = orch._build_citations(chunks)
        assert len(citations) == 1
        assert citations[0]["chunk_id"] == "abc12345"
        assert citations[0]["source"] == "static"
        assert citations[0]["source_label"] == "Official Document"
        assert citations[0]["page"] == 10
        assert citations[0]["section"] == "Premium"

    def test_build_citations_web(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [
            _make_evidence_chunk(
                chunk_id="web12345",
                source_type="web",
                title="Web Article",
                url="https://example.com",
            ),
        ]
        citations = orch._build_citations(chunks)
        assert len(citations) == 1
        assert citations[0]["source"] == "web"
        assert citations[0]["source_label"] == "Web Source"
        assert citations[0]["url"] == "https://example.com"

    def test_build_citations_deduplicates(self):
        orch = RAGOrchestrator(_make_settings())
        chunks = [
            _make_evidence_chunk(chunk_id="abc12345def67890"),
            _make_evidence_chunk(chunk_id="abc12345def67890"),  # duplicate
        ]
        citations = orch._build_citations(chunks)
        assert len(citations) == 1

    def test_build_citations_empty(self):
        orch = RAGOrchestrator(_make_settings())
        citations = orch._build_citations([])
        assert citations == []


# ---------------------------------------------------------------------------
# Confidence calculation
# ---------------------------------------------------------------------------

class TestCalculateConfidence:
    def test_dual_source_high_band(self):
        orch = RAGOrchestrator(_make_settings())
        static = _make_rag_result(band=ConfidenceBand.HIGH)
        web = _make_rag_result(band=ConfidenceBand.HIGH)
        conf, band = orch._calculate_confidence(static, web, True, True)
        assert conf >= 0.7
        assert band == ConfidenceBand.HIGH

    def test_dual_source_medium_band(self):
        orch = RAGOrchestrator(_make_settings())
        static = _make_rag_result(band=ConfidenceBand.MEDIUM)
        web = _make_rag_result(band=ConfidenceBand.MEDIUM)
        conf, band = orch._calculate_confidence(static, web, True, True)
        # (0.7 + 0.7) / 2 + 0.10 = 0.80
        assert conf == 0.8
        assert band == ConfidenceBand.HIGH

    def test_static_only_high(self):
        orch = RAGOrchestrator(_make_settings())
        static = _make_rag_result(band=ConfidenceBand.HIGH)
        web = _make_rag_result(band=ConfidenceBand.LOW, abstained=True)
        conf, band = orch._calculate_confidence(static, web, True, False)
        assert conf == 0.9
        assert band == ConfidenceBand.HIGH

    def test_web_only_medium(self):
        orch = RAGOrchestrator(_make_settings())
        static = _make_rag_result(band=ConfidenceBand.LOW, abstained=True)
        web = _make_rag_result(band=ConfidenceBand.MEDIUM)
        conf, band = orch._calculate_confidence(static, web, False, True)
        assert conf == 0.7
        assert band == ConfidenceBand.HIGH  # 0.7 >= 0.7 threshold

    def test_neither_source_zero(self):
        orch = RAGOrchestrator(_make_settings())
        static = _make_rag_result(abstained=True)
        web = _make_rag_result(abstained=True)
        conf, band = orch._calculate_confidence(static, web, False, False)
        assert conf == 0.0
        assert band == ConfidenceBand.LOW


# ---------------------------------------------------------------------------
# Abstain response
# ---------------------------------------------------------------------------

class TestAbstainResponse:
    def test_abstain_response_structure(self):
        orch = RAGOrchestrator(_make_settings())
        response = orch._abstain_response(
            lang="en",
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            domain="pmfby",
            session_id="sess-1",
        )
        assert isinstance(response, RAGResponse)
        assert response.abstained is True
        assert response.confidence == 0.0
        assert response.citations == []
        assert response.mode == "dual_rag"
        assert response.conversation_id == "sess-1"
        assert response.answer

    def test_abstain_response_hindi(self):
        orch = RAGOrchestrator(_make_settings())
        response = orch._abstain_response(
            lang="hi",
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
            domain="pmfby",
            session_id="sess-2",
        )
        assert response.language == "hi"
        assert response.abstained is True


# ---------------------------------------------------------------------------
# LLM failure handling
# ---------------------------------------------------------------------------

class TestLLMFailure:
    def test_all_providers_failed_returns_abstain(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_result = _make_rag_result(
            chunks=[_make_evidence_chunk()],
            band=ConfidenceBand.HIGH,
        )
        web_result = _make_rag_result(
            abstained=True,
            reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer", side_effect=AllProvidersFailedError("all failed")):

            response = orch.run(
                query="PMFBY",
                english_query="PMFBY",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-5",
            )

            assert response.abstained is True
            assert response.confidence == 0.0


# ---------------------------------------------------------------------------
# Full pipeline integration
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_dual_rag_successful_flow(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_chunks = [
            _make_evidence_chunk(
                chunk_id="static-abc12345def67890",
                content="PMFBY premium is 2% for kharif crops.",
                source_type="static",
                title="PMFBY Guidelines",
                section="Premium",
                page=5,
            ),
        ]
        web_chunks = [
            _make_evidence_chunk(
                chunk_id="web-abc12345def67890",
                content="PMFBY covers all food crops.",
                source_type="web",
                title="PMFBY Overview",
                url="https://pmfby.gov.in",
            ),
        ]

        static_result = _make_rag_result(
            chunks=static_chunks,
            band=ConfidenceBand.HIGH,
        )
        web_result = _make_rag_result(
            chunks=web_chunks,
            band=ConfidenceBand.MEDIUM,
        )

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="PMFBY provides crop insurance with 2% premium [chunk:static-abc12345] and covers all food crops [chunk:web-abc12345]"), \
             patch("app.services.rag_orchestrator.verify_citations", return_value=VerificationResult(is_valid=True)):

            response = orch.run(
                query="What is PMFBY?",
                english_query="What is PMFBY?",
                embedding=[0.1] * 768,
                domain="pmfby",
                state="gujarat",
                classification=classification,
                history=[],
                lang="en",
                session_id="sess-full-1",
            )

            assert isinstance(response, RAGResponse)
            assert response.abstained is False
            assert response.mode == "dual_rag"
            assert response.domain == "pmfby"
            assert response.language == "en"
            assert response.confidence > 0.0
            assert len(response.citations) > 0
            assert response.speech_text
            assert response.conversation_id == "sess-full-1"

    def test_hindi_response_flow(self):
        settings = _make_settings()
        orch = RAGOrchestrator(settings)

        static_chunks = [_make_evidence_chunk()]
        static_result = _make_rag_result(
            chunks=static_chunks,
            band=ConfidenceBand.HIGH,
        )
        web_result = _make_rag_result(abstained=True)

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="PMFBY is a crop insurance scheme [chunk:chunk-abc12345]"), \
             patch("app.services.rag_orchestrator.verify_citations", return_value=VerificationResult(is_valid=True)):

            response = orch.run(
                query="PMFBY क्या है?",
                english_query="What is PMFBY?",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=None,
                history=None,
                lang="hi",
                session_id="sess-hindi-1",
            )

            assert response.language == "hi"
            assert response.abstained is False


# ---------------------------------------------------------------------------
# Citation verification integration
# ---------------------------------------------------------------------------

class TestCitationVerification:
    def test_valid_citations_pass_verification(self):
        """Valid citations from evidence pass verification and return normal response."""
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_chunks = [
            _make_evidence_chunk(
                chunk_id="chunk-abc12345",
                content="PMFBY premium is 2%.",
                source_type="static",
            ),
        ]
        static_result = _make_rag_result(chunks=static_chunks, band=ConfidenceBand.HIGH)
        web_result = _make_rag_result(abstained=True)

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="PMFBY premium is 2% [chunk:chunk-abc12345]"), \
             patch("app.services.rag_orchestrator.verify_citations") as mock_verify:
            mock_verify.return_value = VerificationResult(
                is_valid=True,
                valid_citations=[],
            )

            response = orch.run(
                query="PMFBY premium",
                english_query="PMFBY premium",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-cite-1",
            )

            assert response.abstained is False
            mock_verify.assert_called_once()

    def test_invalid_citations_return_abstained(self):
        """Invalid citations cause verification failure and return abstained response."""
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_chunks = [
            _make_evidence_chunk(chunk_id="chunk-abc12345"),
        ]
        static_result = _make_rag_result(chunks=static_chunks, band=ConfidenceBand.HIGH)
        web_result = _make_rag_result(abstained=True)

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="Some answer [chunk:fffffffffff]"), \
             patch("app.services.rag_orchestrator.verify_citations") as mock_verify:
            mock_verify.return_value = VerificationResult(
                is_valid=False,
                invalid_prefixes=["ffffffff"],
                reason=AbstentionReason.CITATION_FAILURE,
            )

            response = orch.run(
                query="test query",
                english_query="test query",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-cite-2",
            )

            assert response.abstained is True
            assert response.confidence == 0.0
            assert response.citations == []

    def test_verification_receives_all_chunk_ids(self):
        """Verification receives chunk IDs from all evidence chunks."""
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_chunks = [
            _make_evidence_chunk(chunk_id="static-aaa11111"),
            _make_evidence_chunk(chunk_id="static-bbb22222"),
        ]
        web_chunks = [
            _make_evidence_chunk(chunk_id="web-ccc33333", source_type="web"),
        ]
        static_result = _make_rag_result(chunks=static_chunks, band=ConfidenceBand.HIGH)
        web_result = _make_rag_result(chunks=web_chunks, band=ConfidenceBand.MEDIUM)

        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="Answer [chunk:static-aaa11111] [chunk:web-ccc33333]"), \
             patch("app.services.rag_orchestrator.verify_citations") as mock_verify:
            mock_verify.return_value = VerificationResult(is_valid=True)

            orch.run(
                query="test",
                english_query="test",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-cite-3",
            )

            call_args = mock_verify.call_args
            chunk_ids = call_args[0][1]
            assert "static-aaa11111" in chunk_ids
            assert "static-bbb22222" in chunk_ids
            assert "web-ccc33333" in chunk_ids

    def test_auto_appended_citations_verified(self):
        """Auto-appended citations also go through verification."""
        settings = _make_settings()
        orch = RAGOrchestrator(settings)
        classification = _make_classification()

        static_chunks = [
            _make_evidence_chunk(chunk_id="chunk-abc12345"),
        ]
        static_result = _make_rag_result(chunks=static_chunks, band=ConfidenceBand.HIGH)
        web_result = _make_rag_result(abstained=True)

        # LLM returns no citations, auto-append adds them, then verify
        with patch.object(orch._static_rag, "retrieve", return_value=static_result), \
             patch.object(orch._web_rag, "retrieve", return_value=web_result), \
             patch("app.services.rag_orchestrator.grounded_answer",
                   return_value="PMFBY is crop insurance."), \
             patch("app.services.rag_orchestrator.verify_citations") as mock_verify:
            mock_verify.return_value = VerificationResult(is_valid=True)

            response = orch.run(
                query="PMFBY",
                english_query="PMFBY",
                embedding=[0.1] * 768,
                domain="pmfby",
                state=None,
                classification=classification,
                history=None,
                lang="en",
                session_id="sess-cite-4",
            )

            # Verify was called with the auto-appended citation in the answer
            call_args = mock_verify.call_args
            answer_arg = call_args[0][0]
            # Auto-append truncates chunk_id to 8 chars: chunk-abc12345 -> chunk-ab
            assert "[chunk:chunk-ab]" in answer_arg
            assert response.abstained is False
