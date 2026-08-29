import uuid

import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PAYLOAD = {"question": "Who is eligible under PMFBY?", "session_id": str(uuid.uuid4()),
           "language": "en", "state": None}
EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
RPC_PATH = "/rest/v1/rpc/match_chunks"


@respx.mock
def test_answered_with_valid_citation(respx_mock):
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[{
            "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
            "stable_chunk_id": "pmfby-faq:p1:c0",
            "document_id": "dddd1111-2222-3333-4444-555555555555",
            "title": "PMFBY FAQ", "page": 1, "page_start": 1, "page_end": 1,
            "section": "Eligibility", "subsection": None, "clause": None,
            "content": "Eligible farmers are covered.", "similarity": 0.72,
            "source_url": "https://pmfby.gov.in/faq", "source_file": "pmfby.gov.in/faq",
            "domain": "pmfby", "jurisdiction": "central", "state": None}, {
            "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
            "stable_chunk_id": "pmfby-guidelines:p4:c0",
            "document_id": "eeee1111-2222-3333-4444-555555555555",
            "title": "PMFBY Guidelines", "page": 4, "page_start": 4, "page_end": 4,
            "section": "Coverage", "subsection": None, "clause": None,
            "content": "Coverage extends to notified crops.", "similarity": 0.51,
            "source_url": "https://pmfby.gov.in/guidelines",
            "source_file": "pmfby.gov.in/guidelines",
            "domain": "pmfby", "jurisdiction": "central", "state": None}]))
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": "Farmers growing notified crops are eligible [chunk:aaaaaaaa]."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is False and body["confidence"] > 0
    assert body["citations"][0]["title"] == "PMFBY FAQ"
    assert set(body) == {"answer", "language", "domain", "intent", "entities",
                         "confidence", "confidence_level", "citations",
                         "abstained", "follow_up_question"}


@respx.mock
def test_answered_with_fullwidth_citation(respx_mock):
    """Groq often emits full-width 【ID】 markers; these must be normalised
    to [chunk:ID] and accepted when the ID matches retrieved evidence."""
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[{
            "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
            "stable_chunk_id": "pmfby-faq:p1:c0",
            "document_id": "dddd1111-2222-3333-4444-555555555555",
            "title": "PMFBY FAQ", "page": 1, "page_start": 1, "page_end": 1,
            "section": "Eligibility", "subsection": None, "clause": None,
            "content": "Eligible farmers are covered.", "similarity": 0.72,
            "source_url": "https://pmfby.gov.in/faq", "source_file": "pmfby.gov.in/faq",
            "domain": "pmfby", "jurisdiction": "central", "state": None}, {
            "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
            "stable_chunk_id": "pmfby-guidelines:p4:c0",
            "document_id": "eeee1111-2222-3333-4444-555555555555",
            "title": "PMFBY Guidelines", "page": 4, "page_start": 4, "page_end": 4,
            "section": "Coverage", "subsection": None, "clause": None,
            "content": "Coverage extends to notified crops.", "similarity": 0.51,
            "source_url": "https://pmfby.gov.in/guidelines",
            "source_file": "pmfby.gov.in/guidelines",
            "domain": "pmfby", "jurisdiction": "central", "state": None}]))
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": "Farmers growing notified crops are eligible 【aaaaaaaa】."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is False
    assert body["citations"][0]["title"] == "PMFBY FAQ"


@respx.mock
def test_abstains_on_fullwidth_non_retrieved_citation(respx_mock):
    """Full-width 【ID】 that is NOT in retrieved evidence must still be
    rejected (never silently accepted)."""
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[{
            "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
            "stable_chunk_id": "pmfby-faq:p1:c0",
            "document_id": "dddd1111-2222-3333-4444-555555555555",
            "title": "PMFBY FAQ", "page": 1, "page_start": 1, "page_end": 1,
            "section": "Eligibility", "subsection": None, "clause": None,
            "content": "Eligible farmers are covered.", "similarity": 0.72,
            "source_url": "https://pmfby.gov.in/faq", "source_file": "pmfby.gov.in/faq",
            "domain": "pmfby", "jurisdiction": "central", "state": None}, {
            "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
            "stable_chunk_id": "pmfby-guidelines:p4:c0",
            "document_id": "eeee1111-2222-3333-4444-555555555555",
            "title": "PMFBY Guidelines", "page": 4, "page_start": 4, "page_end": 4,
            "section": "Coverage", "subsection": None, "clause": None,
            "content": "Coverage extends to notified crops.", "similarity": 0.51,
            "source_url": "https://pmfby.gov.in/guidelines",
            "source_file": "pmfby.gov.in/guidelines",
            "domain": "pmfby", "jurisdiction": "central", "state": None}]))
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": "Something about farmers 【ffffffff】."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is True
    assert body["citations"] == []


@respx.mock
def test_abstains_when_retrieval_below_threshold(respx_mock):
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.01] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[]))
    r = client.post("/chat", json=PAYLOAD)
    body = r.json()
    assert body["abstained"] is True and body["citations"] == []
    assert body["answer"]  # safe message present


@respx.mock
def test_abstains_when_both_llms_fail(respx_mock):
    """Both LLMs down → safe abstention, not 500."""
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[{
            "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
            "stable_chunk_id": "pmfby-faq:p1:c0",
            "document_id": "dddd1111-2222-3333-4444-555555555555",
            "title": "PMFBY FAQ", "page": 1, "page_start": 1, "page_end": 1,
            "section": "Eligibility", "subsection": None, "clause": None,
            "content": "Eligible farmers are covered.", "similarity": 0.72,
            "source_url": "https://pmfby.gov.in/faq", "source_file": "pmfby.gov.in/faq",
            "domain": "pmfby", "jurisdiction": "central", "state": None}, {
            "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
            "stable_chunk_id": "pmfby-guidelines:p4:c0",
            "document_id": "eeee1111-2222-3333-4444-555555555555",
            "title": "PMFBY Guidelines", "page": 4, "page_start": 4, "page_end": 4,
            "section": "Coverage", "subsection": None, "clause": None,
            "content": "Coverage extends to notified crops.", "similarity": 0.51,
            "source_url": "https://pmfby.gov.in/guidelines",
            "source_file": "pmfby.gov.in/guidelines",
            "domain": "pmfby", "jurisdiction": "central", "state": None}]))
    # Both LLMs return 429
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"}))
    respx_mock.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent").mock(
        return_value=httpx.Response(429, json={"error": "rate limited"}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is True
    assert body["citations"] == []
    assert body["answer"]  # safe message present


@respx.mock
def test_abstains_on_supabase_failure(respx_mock):
    """Supabase connection failure → safe abstention, not 503."""
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    # Supabase RPC returns500
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(500, json={"error": "internal error"}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is True
    assert body["citations"] == []
    assert body["answer"]  # safe message present
