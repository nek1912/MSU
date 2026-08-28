"""Voice service with provider fallback chain."""

import logging
from typing import Optional
from app.providers.azure_voice import AzureVoiceProvider
from app.providers.sarvam_voice import SarvamVoiceProvider

logger = logging.getLogger(__name__)


class VoiceService:
    """Manages voice providers with fallback chain.

    Fallback order: Azure → Sarvam → text-only
    """

    def __init__(self):
        self.providers = [
            ("azure", AzureVoiceProvider()),
            ("sarvam", SarvamVoiceProvider()),
        ]

    async def speech_to_text(self, audio_bytes: bytes, language: str = "en") -> str:
        """Convert speech to text with fallback."""
        for name, provider in self.providers:
            try:
                return await provider.speech_to_text(audio_bytes, language)
            except Exception as e:
                logger.warning(f"{name} STT failed: {e}")
                continue

        raise VoiceUnavailableError("No voice providers available. Please type your question.")

    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech with fallback."""
        for name, provider in self.providers:
            try:
                return await provider.text_to_speech(text, language)
            except Exception as e:
                logger.warning(f"{name} TTS failed: {e}")
                continue

        raise VoiceUnavailableError("No voice providers available.")


class VoiceUnavailableError(Exception):
    """Raised when all voice providers fail."""
    pass