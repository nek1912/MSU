"""Azure Cognitive Services voice provider (primary)."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AzureVoiceProvider:
    """Azure Speech Services for STT and TTS."""

    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY", "")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION", "centralindia")
        self.enabled = bool(self.speech_key)

        if not self.enabled:
            logger.info("Azure voice disabled: AZURE_SPEECH_KEY not set")

    async def speech_to_text(self, audio_bytes: bytes, language: str = "en") -> str:
        """Convert speech to text."""
        if not self.enabled:
            raise RuntimeError("Azure voice not configured")

        # TODO: Implement when AZURE_SPEECH_KEY is provided
        # Use azure-cognitiveservices-speech SDK
        raise NotImplementedError("Azure STT not yet implemented")

    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech."""
        if not self.enabled:
            raise RuntimeError("Azure voice not configured")

        # TODO: Implement when AZURE_SPEECH_KEY is provided
        raise NotImplementedError("Azure TTS not yet implemented")
