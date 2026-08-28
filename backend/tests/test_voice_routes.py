"""Tests for voice routes (transcribe and speak)."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.voice_service import VoiceUnavailableError

client = TestClient(app)


def test_voice_routes_import():
    """Test that voice routes can be imported without errors."""
    from app.routes.voice import router, voice_service
    assert router is not None
    assert voice_service is not None


def test_transcribe_returns_503_when_no_providers():
    """Test that /voice/transcribe returns 503 when no voice providers are configured."""
    r = client.post("/voice/transcribe", json={"audio": "dGVzdA==", "language": "en"})
    assert r.status_code == 503
    body = r.json()
    assert "No voice providers available" in body["detail"]


def test_speak_returns_503_when_no_providers():
    """Test that /voice/speak returns 503 when no voice providers are configured."""
    r = client.post("/voice/speak", json={"text": "Hello world", "language": "en"})
    assert r.status_code == 503
    body = r.json()
    assert "No voice providers available" in body["detail"]


def test_transcribe_returns_503_when_all_providers_fail():
    """Test that /voice/transcribe returns 503 when all providers fail."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.speech_to_text = AsyncMock(side_effect=VoiceUnavailableError("No voice providers available"))
        r = client.post("/voice/transcribe", json={"audio": "dGVzdA==", "language": "en"})
        assert r.status_code == 503
        assert "No voice providers available" in r.json()["detail"]


def test_speak_returns_503_when_all_providers_fail():
    """Test that /voice/speak returns 503 when all providers fail."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.text_to_speech = AsyncMock(side_effect=VoiceUnavailableError("No voice providers available"))
        r = client.post("/voice/speak", json={"text": "Hello world", "language": "en"})
        assert r.status_code == 503
        assert "No voice providers available" in r.json()["detail"]


def test_transcribe_returns_text_on_success():
    """Test that /voice/transcribe returns transcribed text on success."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.speech_to_text = AsyncMock(return_value="recognized text")
        r = client.post("/voice/transcribe", json={"audio": "dGVzdA==", "language": "en"})
        assert r.status_code == 200
        body = r.json()
        assert body["text"] == "recognized text"
        assert body["language"] == "en"


def test_speak_returns_audio_on_success():
    """Test that /voice/speak returns audio hex on success."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.text_to_speech = AsyncMock(return_value=b"\x00\x01\x02")
        r = client.post("/voice/speak", json={"text": "Hello world", "language": "en"})
        assert r.status_code == 200
        body = r.json()
        assert body["audio"] == "000102"
        assert body["language"] == "en"


def test_transcribe_default_language():
    """Test that /voice/transcribe defaults language to 'en'."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.speech_to_text = AsyncMock(return_value="text")
        r = client.post("/voice/transcribe", json={"audio": "dGVzdA=="})
        assert r.status_code == 200
        assert r.json()["language"] == "en"


def test_speak_default_language():
    """Test that /voice/speak defaults language to 'en'."""
    with patch("app.routes.voice.voice_service") as mock_vs:
        mock_vs.text_to_speech = AsyncMock(return_value=b"\x00")
        r = client.post("/voice/speak", json={"text": "Hello"})
        assert r.status_code == 200
        assert r.json()["language"] == "en"
