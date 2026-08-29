"""PHASE 13: Voice pipeline tests.

Tests the voice I/O layer:
- Azure STT adapter (configured / not configured / SDK missing)
- Azure TTS adapter (configured / not configured / SDK missing)
- Voice route /voice/transcribe (STT endpoint)
- Voice route /voice/speak (TTS endpoint)
- Voice route /voice (full pipeline: STT → RAG → TTS)
- One RAG core — voice routes use the same chat handler

All provider calls are mocked — no real Azure calls in tests.
"""
import sys
from unittest.mock import MagicMock, patch

import pytest

from app.config import get_settings
from app.providers.azure_stt import AzureSTTProvider
from app.providers.azure_tts import AzureTTSProvider


def _azure_modules(mock_sdk=None):
    """Build a full azure package chain for sys.modules patching."""
    azure_pkg = MagicMock()
    azure_cog = MagicMock()
    speech = mock_sdk or MagicMock()
    return {
        "azure": azure_pkg,
        "azure.cognitiveservices": azure_cog,
        "azure.cognitiveservices.speech": speech,
    }


# ═══════════════════════════════════════════════════════════════════════════
# AZURE STT ADAPTER
# ═══════════════════════════════════════════════════════════════════════════

class TestAzureSTT:
    """Azure STT provider tests."""

    def test_not_configured_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = ""
        settings.azure_speech_region = ""
        stt = AzureSTTProvider(settings)
        assert stt.configured is False
        assert stt.transcribe(b"fake audio") == ""

    def test_configured_property(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)
        assert stt.configured is True

    def test_sdk_missing_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)
        with patch.dict("sys.modules", _azure_modules(None)):
            result = stt.transcribe(b"fake audio", "en-IN")
            assert result == ""

    def test_transcribe_success(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.RecognizedSpeech
        mock_result.text = "What is PMFBY?"
        mock_sdk.SpeechRecognizer.return_value.recognize_once.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = stt.transcribe(b"audio data", "en-IN")
            assert result == "What is PMFBY?"

    def test_transcribe_no_match(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.NoMatch
        mock_sdk.SpeechRecognizer.return_value.recognize_once.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = stt.transcribe(b"audio data")
            assert result == ""

    def test_transcribe_canceled(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.Canceled
        mock_result.cancellation_details = "test error"
        mock_sdk.SpeechRecognizer.return_value.recognize_once.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = stt.transcribe(b"audio data")
            assert result == ""

    def test_transcribe_exception_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        stt = AzureSTTProvider(settings)

        mock_sdk = MagicMock()
        mock_sdk.SpeechRecognizer.return_value.recognize_once.side_effect = RuntimeError("SDK error")

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = stt.transcribe(b"audio data")
            assert result == ""


# ═══════════════════════════════════════════════════════════════════════════
# AZURE TTS ADAPTER
# ═══════════════════════════════════════════════════════════════════════════

class TestAzureTTS:
    """Azure TTS provider tests."""

    def test_not_configured_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = ""
        settings.azure_speech_region = ""
        tts = AzureTTSProvider(settings)
        assert tts.configured is False
        assert tts.synthesize("hello") == b""

    def test_configured_property(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        tts = AzureTTSProvider(settings)
        assert tts.configured is True

    def test_sdk_missing_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        tts = AzureTTSProvider(settings)
        with patch.dict("sys.modules", _azure_modules(None)):
            result = tts.synthesize("hello", "en")
            assert result == b""

    def test_synthesize_success(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        tts = AzureTTSProvider(settings)

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.SynthesizingAudioCompleted
        mock_result.audio_data = b"fake-wav-data"
        mock_sdk.SpeechSynthesizer.return_value.speak_text_async.return_value.get.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = tts.synthesize("What is PMFBY?", "en")
            assert result == b"fake-wav-data"

    def test_synthesize_canceled(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        tts = AzureTTSProvider(settings)

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.Canceled
        mock_result.cancellation_details = "test error"
        mock_sdk.SpeechSynthesizer.return_value.speak_text_async.return_value.get.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = tts.synthesize("hello", "en")
            assert result == b""

    def test_synthesize_exception_returns_empty(self):
        settings = get_settings()
        settings.azure_speech_key = "test-key"
        settings.azure_speech_region = "test-region"
        tts = AzureTTSProvider(settings)

        mock_sdk = MagicMock()
        mock_sdk.SpeechSynthesizer.return_value.speak_text_async.side_effect = RuntimeError("SDK error")

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            result = tts.synthesize("hello", "en")
            assert result == b""

    def test_hindi_voice_selection(self):
        """Hindi language selects the Hindi voice from config."""
        settings = get_settings()
        voices = settings.tts_voices
        assert voices["hi"] == "hi-IN-SwaraNeural"

    def test_gujarati_voice_selection(self):
        """Gujarati language selects the Gujarati voice from config."""
        settings = get_settings()
        voices = settings.tts_voices
        assert voices["gu"] == "gu-IN-DhwaniNeural"

    def test_english_voice_selection(self):
        """English language selects the English voice from config."""
        settings = get_settings()
        voices = settings.tts_voices
        assert voices["en"] == "en-IN-NeerjaNeural"


# ═══════════════════════════════════════════════════════════════════════════
# VOICE ROUTES
# ═══════════════════════════════════════════════════════════════════════════

class TestVoiceRoutes:
    """Voice route integration tests using FastAPI TestClient."""

    def _get_client(self, azure_key="", azure_region=""):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.routes.voice import router as voice_router
        app = FastAPI()
        app.include_router(voice_router)
        # Patch settings so the route sees configured/not-configured
        settings = get_settings()
        settings.azure_speech_key = azure_key
        settings.azure_speech_region = azure_region
        return TestClient(app)

    def test_transcribe_not_configured(self):
        client = self._get_client()
        response = client.post(
            "/voice/transcribe",
            files={"audio": ("test.wav", b"fake-audio", "audio/wav")},
            data={"language": "en-IN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == ""
        assert data["error"] is not None

    def test_speak_not_configured(self):
        client = self._get_client()
        response = client.post(
            "/voice/speak",
            data={"text": "Hello", "language": "en"},
        )
        assert response.status_code == 503

    def test_voice_chat_not_configured(self):
        client = self._get_client()
        response = client.post(
            "/voice",
            files={"audio": ("test.wav", b"fake-audio", "audio/wav")},
            data={"language": "en-IN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is not None

    def test_voice_chat_no_speech(self):
        client = self._get_client(azure_key="test-key", azure_region="test-region")

        mock_sdk = MagicMock()
        mock_result = MagicMock()
        mock_result.reason = mock_sdk.ResultReason.NoMatch
        mock_sdk.SpeechRecognizer.return_value.recognize_once.return_value = mock_result

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            response = client.post(
                "/voice",
                files={"audio": ("test.wav", b"fake-audio", "audio/wav")},
                data={"language": "en-IN"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["error"] == "no_speech"
            assert data["transcribed_text"] == ""

    def test_voice_chat_full_pipeline(self):
        client = self._get_client(azure_key="test-key", azure_region="test-region")

        mock_sdk = MagicMock()
        # STT result
        mock_stt_result = MagicMock()
        mock_stt_result.reason = mock_sdk.ResultReason.RecognizedSpeech
        mock_stt_result.text = "What is PMFBY?"
        mock_sdk.SpeechRecognizer.return_value.recognize_once.return_value = mock_stt_result
        # TTS result
        mock_tts_result = MagicMock()
        mock_tts_result.reason = mock_sdk.ResultReason.SynthesizingAudioCompleted
        mock_tts_result.audio_data = b"fake-wav-audio"
        mock_sdk.SpeechSynthesizer.return_value.speak_text_async.return_value.get.return_value = mock_tts_result

        mock_chat_result = {
            "answer": "PMFBY is the Pradhan Mantri Fasal Bima Yojana.",
            "language": "en",
            "domain": "pmfby",
            "confidence": 0.85,
            "confidence_level": "high",
            "citations": [],
            "abstained": False,
        }

        with patch.dict("sys.modules", _azure_modules(mock_sdk)):
            with patch("app.routes.voice.chat_handler", return_value=mock_chat_result):
                response = client.post(
                    "/voice",
                    files={"audio": ("test.wav", b"fake-audio", "audio/wav")},
                    data={"language": "en-IN", "session_id": "test-session"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["transcribed_text"] == "What is PMFBY?"
                assert data["answer"] == "PMFBY is the Pradhan Mantri Fasal Bima Yojana."
                assert data["domain"] == "pmfby"
                assert data["confidence_level"] == "high"
                assert data["audio_base64"] is not None
                assert data["abstained"] is False
                assert data["error"] is None


# ═══════════════════════════════════════════════════════════════════════════
# ONE RAG CORE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class TestOneRAGCore:
    """Verify voice routes use the same RAG pipeline as /chat."""

    def test_voice_uses_same_chat_handler(self):
        from app.routes.voice import chat_handler
        from app.routes.chat import chat
        assert chat_handler is chat

    def test_no_separate_voice_rag(self):
        import app.routes.voice as voice_module
        import inspect
        source = inspect.getsource(voice_module)
        assert "from app.retrieval import" not in source
        assert "from app.generation import" not in source
        assert "from app.llm_fallback import" not in source
