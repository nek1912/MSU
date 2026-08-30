"""Voice service with provider fallback chain."""

import logging
from app.providers.azure_voice import AzureVoiceProvider
from app.providers.sarvam_voice import SarvamSTTProvider, SarvamTTSProvider

logger = logging.getLogger(__name__)


class VoiceService:
    """Manages voice providers with fallback chain.

    Fallback order: Sarvam → Azure → text-only
    """

    def __init__(self):
        self.stt_providers = [
            ("sarvam", SarvamSTTProvider()),
            ("azure", AzureVoiceProvider()),
        ]
        self.tts_providers = [
            ("sarvam", SarvamTTSProvider()),
            ("azure", AzureVoiceProvider()),
        ]

    async def speech_to_text(self, audio_bytes: bytes, language: str = "en") -> str:
        """Convert speech to text with fallback."""
        for name, provider in self.stt_providers:
            try:
                return await provider.transcribe(audio_bytes, language)
            except Exception as e:
                logger.warning(f"{name} STT failed: {e}")
                continue

        raise VoiceUnavailableError("No voice providers available. Please type your question.")

    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech with fallback."""
        for name, provider in self.tts_providers:
            try:
                return await provider.synthesize(text, language)
            except Exception as e:
                logger.warning(f"{name} TTS failed: {e}")
                continue

        raise VoiceUnavailableError("No voice providers available.")

    async def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        """Convert text segments to multi-voice speech with fallback."""
        for name, provider in self.providers:
            try:
                return await provider.text_to_speech_segments(segments)
            except Exception as e:
                logger.warning(f"{name} TTS segments failed: {e}")
                continue

        raise VoiceUnavailableError("No voice providers available.")


class VoiceUnavailableError(Exception):
    """Raised when all voice providers fail."""
    pass
