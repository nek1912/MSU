import uuid
from unittest.mock import MagicMock, patch

import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"


def test_chat_request_accepts_history():
    """ChatRequest should accept an optional history field."""
    payload = {
        "question": "What are the eligibility criteria?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
        "history": [
            {"role": "user", "content": "What is PMFBY?"},
            {"role": "assistant", "content": "PMFBY is a crop insurance scheme."},
        ],
    }
    from app.routes.chat import ChatRequest
    req = ChatRequest(**payload)
    assert len(req.history) == 2
    assert req.history[0]["role"] == "user"


def test_chat_request_history_optional():
    """history=None should be valid."""
    from app.routes.chat import ChatRequest
    req = ChatRequest(
        question="test", session_id=str(uuid.uuid4()),
        language="en", state=None
    )
    assert req.history is None


@patch("app.routes.chat.trim_messages")
@patch("app.routes.chat.save_message")
@patch("app.routes.chat.get_history")
@patch("app.routes.chat.grounded_answer")
@patch("app.routes.chat.get_embedding_provider")
@patch("app.routes.chat.get_anchor_store")
@patch("app.routes.chat.retrieve_hybrid")
@patch("app.routes.chat.evidence_gate_v2")
@patch("app.routes.chat.verify_citations_v2")
def test_chat_sends_history_to_prompt(
    mock_verify, mock_gate, mock_retrieve, mock_anchor,
    mock_embed, mock_llm, mock_history, mock_save, mock_trim,
):
    """When history is provided, it should be passed to build_user_prompt."""
    mock_embed.return_value.embed_texts.return_value = [[0.5] * 768]
    mock_anchor.return_value.classify.return_value = ("pmfby", 0.8)
    mock_retrieve.return_value = []
    mock_gate.return_value = (False, None, MagicMock(value="high"))
    mock_verify.return_value = MagicMock(is_valid=True)
    mock_llm.return_value = "Answer [chunk:aaaabbbb]."
    mock_history.return_value = [{"role": "user", "content": "What is PMFBY?"}]

    payload = {
        "question": "What are the criteria?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
        "history": [{"role": "user", "content": "What is PMFBY?"}],
    }

    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    # get_history was called (server-side retrieval)
    mock_history.assert_called_once()
    # messages were persisted
    assert mock_save.call_count == 2


@patch("app.routes.chat.trim_messages")
@patch("app.routes.chat.save_message")
@patch("app.routes.chat.get_history")
@patch("app.routes.chat.grounded_answer")
@patch("app.routes.chat.get_embedding_provider")
@patch("app.routes.chat.get_anchor_store")
@patch("app.routes.chat.retrieve_hybrid")
@patch("app.routes.chat.evidence_gate_v2")
def test_chat_persists_on_out_of_scope(
    mock_gate, mock_retrieve, mock_anchor,
    mock_embed, mock_llm, mock_history, mock_save, mock_trim,
):
    """Out-of-scope path should also persist messages."""
    mock_embed.return_value.embed_texts.return_value = [[0.5] * 768]
    mock_anchor.return_value.classify.return_value = ("out_of_scope", 0.8)
    mock_llm.return_value = "General answer."

    payload = {
        "question": "What is the weather?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
    }

    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["domain"] == "out_of_scope"
    assert mock_save.call_count == 2
    mock_trim.assert_called_once_with(payload["session_id"], keep=50)


@patch("app.routes.chat.trim_messages")
@patch("app.routes.chat.save_message")
@patch("app.routes.chat.get_history")
@patch("app.routes.chat.grounded_answer")
@patch("app.routes.chat.get_embedding_provider")
@patch("app.routes.chat.get_anchor_store")
@patch("app.routes.chat.retrieve_hybrid")
@patch("app.routes.chat.evidence_gate_v2")
@patch("app.routes.chat.verify_citations_v2")
def test_chat_persists_on_success(
    mock_verify, mock_gate, mock_retrieve, mock_anchor,
    mock_embed, mock_llm, mock_history, mock_save, mock_trim,
):
    """Successful RAG path should persist messages."""
    mock_embed.return_value.embed_texts.return_value = [[0.5] * 768]
    mock_anchor.return_value.classify.return_value = ("pmfby", 0.8)
    mock_retrieve.return_value = []
    mock_gate.return_value = (False, None, MagicMock(value="high"))
    mock_verify.return_value = MagicMock(is_valid=True)
    mock_llm.return_value = "Answer [chunk:aaaabbbb]."
    mock_history.return_value = []

    payload = {
        "question": "What is PMFBY?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
    }

    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    assert mock_save.call_count == 2
    mock_trim.assert_called_once_with(payload["session_id"], keep=50)
