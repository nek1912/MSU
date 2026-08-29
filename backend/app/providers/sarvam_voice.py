"""Sarvam AI voice provider (fallback for Indian languages)."""

import os
import logging

logger = logging.getLogger(__name__)


class SarvamVoiceProvider:
    """Sarvam AI for Indian language STT and TTS."""

    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY", "")
        self.base_url = "https://api.sarvam.ai"
        self.enabled = bool(self.api_key)

        if not self.enabled:
            logger.info("Sarvam voice disabled: SARVAM_API_KEY not set")

    async def speech_to_text(self, audio_bytes: bytes, language: str = "hi") -> str:
        """Convert speech to text."""
        if not self.enabled:
            raise RuntimeError("Sarvam voice not configured")

        # TODO: Implement when SARVAM_API_KEY is provided
        raise NotImplementedError("Sarvam STT not yet implemented")

    async def text_to_speech(self, text: str, language: str = "hi") -> bytes:
        """Convert text to speech."""
        if not self.enabled:
            raise RuntimeError("Sarvam voice not configured")

        # TODO: Implement when SARVAM_API_KEY is provided
        raise NotImplementedError("Sarvam TTS not yet implemented")

    async def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        """Convert text segments to multi-voice speech."""
        if not self.enabled:
            raise RuntimeError("Sarvam voice not configured")

        # TODO: Implement when SARVAM_API_KEY is provided
        raise NotImplementedError("Sarvam TTS not yet implemented")
