"""Test citation verification at the route level.

Tests the actual call path:
chat() → grounded_answer() → LLM returns answer with citations →
verify_citations() catches invalid → route abstains

Requires 2+ chunks per test to pass evidence_gate (MIN_CHUNKS_ABOVE_SECONDARY=2).
"""
import uuid

import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
RPC_PATH = "/rest/v1/rpc/match_chunks"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PAYLOAD = {"question": "What is PACS?", "session_id": str(uuid.uuid4()),
           "language": "en", "state": None}

CHUNK_A = {
    "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
    "title": "PMFBY FAQ", "page": 1, "section": "Eligibility",
    "content": "PACS membership rules.", "similarity": 0.72,
    "source_url": "https://pmfby.gov.in/faq", "domain": "pmfby",
    "jurisdiction": "central", "state": None,
}
CHUNK_B = {
    "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
    "title": "PMFBY Guidelines", "page": 4, "section": "Coverage",
    "content": "Coverage extends to notified crops.", "similarity": 0.51,
    "source_url": "https://pmfby.gov.in/guidelines", "domain": "pmfby",
    "jurisdiction": "central", "state": None,
}
VALID_PREFIX_A = "aaaaaaaa"


def _mock_embeddings_and_retrieval(respx_mock):
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[CHUNK_A, CHUNK_B]))


@respx.mock
def test_abstains_on_invalid_citations(respx_mock):
    """Chat route must abstain when LLM produces invalid citations."""
    _mock_embeddings_and_retrieval(respx_mock)
    respx_mock.post(GROQ_URL).mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": "PACS requires membership [chunk:deadbeef1]."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is True
    assert body["confidence"] == 0.0
    assert body["citations"] == []


@respx.mock
def test_passes_on_valid_citations(respx_mock):
    """Chat route must succeed when LLM produces valid citations."""
    _mock_embeddings_and_retrieval(respx_mock)
    respx_mock.post(GROQ_URL).mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": f"PACS requires membership [chunk:{VALID_PREFIX_A}]."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is False
    assert body["confidence"] > 0
    assert len(body["citations"]) == 1
    assert body["citations"][0]["title"] == "PMFBY FAQ"


@respx.mock
def test_abstains_on_mixed_valid_and_invalid_citations(respx_mock):
    """Chat route must abstain when answer mixes valid and invalid citations."""
    _mock_embeddings_and_retrieval(respx_mock)
    respx_mock.post(GROQ_URL).mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": f"PACS [chunk:{VALID_PREFIX_A}] and also [chunk:deadbeef1]."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is True
    assert body["confidence"] == 0.0
    assert body["citations"] == []
