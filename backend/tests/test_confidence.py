"""PHASE 9: Confidence behavior tests.

Verifies that confidence is exposed as an internal diagnostic, not a probability.
Tests the confidence_level field and calibration data collection.
"""
import uuid

import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app
from app.confidence_eval import (
    ConfidenceEvalRecord,
    compute_calibration_stats,
)

client = TestClient(app)
EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
RPC_PATH = "/rest/v1/rpc/match_chunks"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _mock_chunks(similarities: list[float] | None = None) -> list[dict]:
    sims = similarities or [0.72, 0.51, 0.35]
    return [
        {
            "chunk_id": f"aaaaaaaa-{i:04d}-2222-3333-444444444444",
            "stable_chunk_id": f"pmfby-faq:p{i+1}:c0",
            "document_id": f"dddd{i:04d}-2222-3333-4444-555555555555",
            "title": "PMFBY FAQ",
            "page": i + 1,
            "page_start": i + 1,
            "page_end": i + 1,
            "section": "Eligibility",
            "subsection": None,
            "clause": None,
            "content": "Eligible farmers are covered.",
            "similarity": sim,
            "source_url": "https://pmfby.gov.in/faq",
            "source_file": "faq.pdf",
            "domain": "pmfby",
            "jurisdiction": "central",
            "state": None,
        }
        for i, sim in enumerate(sims)
    ]


def _payload(**overrides) -> dict:
    base = {
        "question": "What is PMFBY?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
    }
    base.update(overrides)
    return base


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE LEVEL FIELD
# ═══════════════════════════════════════════════════════════════════════════

class TestConfidenceLevel:
    """confidence_level must be present and correct in all responses."""

    @respx.mock
    def test_confidence_level_in_answered_response(self, respx_mock):
        respx_mock.post(EMBED_URL).mock(
            return_value=httpx.Response(200, json={"embedding": {"values": [0.5] * 768}}))
        respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
            return_value=httpx.Response(200, json=_mock_chunks([0.82, 0.65, 0.48])))
        respx_mock.post(GROQ_URL).mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {
                "content": "PMFBY covers crops [chunk:aaaaaaaa]."}}]}))

        r = client.post("/chat", json=_payload())
        body = r.json()

        assert "confidence_level" in body
        assert body["confidence_level"] in ("high", "moderate", "low", "none")
        assert body["abstained"] is False
        assert body["confidence"] > 0.0

    @respx.mock
    def test_confidence_level_in_abstained_response(self, respx_mock):
        respx_mock.post(EMBED_URL).mock(
            return_value=httpx.Response(200, json={"embedding": {"values": [0.5] * 768}}))
        respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
            return_value=httpx.Response(200, json=[]))

        r = client.post("/chat", json=_payload())
        body = r.json()

        assert body["confidence_level"] == "none"
        assert body["confidence"] == 0.0
        assert body["abstained"] is True

    @respx.mock
    def test_confidence_level_matches_score(self, respx_mock):
        """confidence_level must be consistent with confidence score."""
        respx_mock.post(EMBED_URL).mock(
            return_value=httpx.Response(200, json={"embedding": {"values": [0.5] * 768}}))
        respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
            return_value=httpx.Response(200, json=_mock_chunks([0.82, 0.65, 0.48])))
        respx_mock.post(GROQ_URL).mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {
                "content": "PMFBY covers crops [chunk:aaaaaaaa]."}}]}))

        r = client.post("/chat", json=_payload())
        body = r.json()

        conf = body["confidence"]
        level = body["confidence_level"]
        if conf >= 0.7:
            assert level == "high"
        elif conf >= 0.5:
            assert level == "moderate"
        elif conf > 0.0:
            assert level == "low"
        else:
            assert level == "none"


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE AS DIAGNOTIC (NOT PROBABILITY)
# ═══════════════════════════════════════════════════════════════════════════

class TestConfidenceDiagnostic:
    """Confidence is an internal diagnostic, not a user-facing probability."""

    @respx.mock
    def test_confidence_not_presented_as_percentage(self, respx_mock):
        """The response should not contain percentage strings like '92%'."""
        respx_mock.post(EMBED_URL).mock(
            return_value=httpx.Response(200, json={"embedding": {"values": [0.5] * 768}}))
        respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
            return_value=httpx.Response(200, json=_mock_chunks()))
        respx_mock.post(GROQ_URL).mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {
                "content": "Answer [chunk:aaaaaaaa]."}}]}))

        r = client.post("/chat", json=_payload())
        body = r.json()

        # confidence should be a float, not a percentage string
        assert isinstance(body["confidence"], float)
        assert 0.0 <= body["confidence"] <= 1.0
        # answer should not contain percentage-based confidence claims
        assert "%" not in body["answer"]


# ═══════════════════════════════════════════════════════════════════════════
# CALIBRATION DATA SCHEMA
# ═══════════════════════════════════════════════════════════════════════════

class TestCalibrationDataSchema:
    """Evaluation record schema must be valid."""

    def test_valid_record_creation(self):
        record = ConfidenceEvalRecord(
            request_id="req-001",
            question="What is PMFBY?",
            language="en",
            domain="pmfby",
            state="gujarat",
            retrieval_scores=[0.82, 0.65, 0.48],
            retrieval_rank=1,
            num_chunks_retrieved=3,
            num_agreeing_chunks=3,
            domain_match=True,
            metadata_valid=True,
            gate_result="pass",
            gate_confidence=0.72,
            answerable=True,
            human_correctness="correct",
        )
        assert record.request_id == "req-001"
        assert record.gate_result == "pass"
        assert record.human_correctness == "correct"

    def test_abstain_record(self):
        record = ConfidenceEvalRecord(
            request_id="req-002",
            question="Unknown topic",
            language="en",
            domain="unknown",
            retrieval_scores=[],
            retrieval_rank=0,
            num_chunks_retrieved=0,
            num_agreeing_chunks=0,
            domain_match=False,
            metadata_valid=False,
            gate_result="abstain",
            gate_reason="no_chunks",
            gate_confidence=0.0,
            answerable=False,
            human_correctness="abstain_correct",
        )
        assert record.gate_result == "abstain"
        assert record.human_correctness == "abstain_correct"


# ═══════════════════════════════════════════════════════════════════════════
# CALIBRATION STATS COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════

class TestCalibrationStats:
    """Calibration stats must be computed correctly."""

    def test_empty_records(self):
        stats = compute_calibration_stats([])
        assert stats.total_records == 0
        assert stats.precision == 0.0
        assert stats.recall == 0.0

    def test_all_correct(self):
        records = [
            ConfidenceEvalRecord(
                request_id=f"req-{i}", question="Q", language="en",
                domain="pmfby", retrieval_scores=[0.8], retrieval_rank=1,
                num_chunks_retrieved=1, num_agreeing_chunks=1,
                domain_match=True, metadata_valid=True,
                gate_result="pass", gate_confidence=0.7,
                answerable=True, human_correctness="correct",
            )
            for i in range(5)
        ]
        stats = compute_calibration_stats(records)
        assert stats.total_records == 5
        assert stats.true_positive == 5
        assert stats.false_positive == 0
        assert stats.precision == 1.0
        assert stats.recall == 1.0
        assert stats.f1 == 1.0

    def test_mixed_results(self):
        records = [
            # TP: answerable + pass
            ConfidenceEvalRecord(
                request_id="req-1", question="Q", language="en",
                domain="pmfby", retrieval_scores=[0.8], retrieval_rank=1,
                num_chunks_retrieved=1, num_agreeing_chunks=1,
                domain_match=True, metadata_valid=True,
                gate_result="pass", gate_confidence=0.7,
                answerable=True, human_correctness="correct",
            ),
            # TN: unanswerable + abstain
            ConfidenceEvalRecord(
                request_id="req-2", question="Q", language="en",
                domain="unknown", retrieval_scores=[], retrieval_rank=0,
                num_chunks_retrieved=0, num_agreeing_chunks=0,
                domain_match=False, metadata_valid=False,
                gate_result="abstain", gate_reason="no_chunks",
                gate_confidence=0.0, answerable=False,
                human_correctness="abstain_correct",
            ),
            # FP: unanswerable + pass (hallucination risk)
            ConfidenceEvalRecord(
                request_id="req-3", question="Q", language="en",
                domain="pmfby", retrieval_scores=[0.5], retrieval_rank=1,
                num_chunks_retrieved=1, num_agreeing_chunks=1,
                domain_match=True, metadata_valid=True,
                gate_result="pass", gate_confidence=0.5,
                answerable=False, human_correctness="incorrect",
            ),
            # FN: answerable + abstain (missed answer)
            ConfidenceEvalRecord(
                request_id="req-4", question="Q", language="en",
                domain="pmfby", retrieval_scores=[0.2], retrieval_rank=1,
                num_chunks_retrieved=1, num_agreeing_chunks=0,
                domain_match=True, metadata_valid=True,
                gate_result="abstain", gate_reason="below_top1_threshold",
                gate_confidence=0.0, answerable=True,
                human_correctness="abstain_incorrect",
            ),
        ]
        stats = compute_calibration_stats(records)
        assert stats.true_positive == 1
        assert stats.true_negative == 1
        assert stats.false_positive == 1
        assert stats.false_negative == 1
        assert stats.precision == 0.5
        assert stats.recall == 0.5
        assert stats.f1 == 0.5
