"""Azure Speech Services — STT adapter.

Converts audio bytes to text using Azure Cognitive Services Speech SDK.
Falls back gracefully if SDK is unavailable or credentials are missing.
"""
import logging

from app.config import Settings

_log = logging.getLogger(__name__)


class AzureSTTProvider:
    """Speech-to-text via Azure Cognitive Services."""

    def __init__(self, settings: Settings) -> None:
        self._key = getattr(settings, "azure_speech_key", "")
        self._region = getattr(settings, "azure_speech_region", "")

    @property
    def configured(self) -> bool:
        return bool(self._key and self._region)

    def transcribe(self, audio: bytes, language: str = "en-IN") -> str:
        """Transcribe audio bytes to text.

        Args:
            audio: Raw audio data (WAV, WEBM, OGG, MP3, etc.)
            language: BCP-47 language code (e.g., "en-IN", "hi-IN", "gu-IN")

        Returns:
            Transcribed text, or empty string on failure.
        """
        if not self.configured:
            _log.warning("Azure STT not configured — returning empty")
            return ""

        try:
            import importlib
            speechsdk = importlib.import_module("azure.cognitiveservices.speech")
        except (ImportError, ModuleNotFoundError):
            _log.warning("azure-cognitiveservices-speech SDK not installed")
            return ""

        try:
            config = speechsdk.SpeechConfig(
                subscription=self._key, region=self._region
            )
            config.speech_recognition_language = language

            # Use push stream for arbitrary audio input
            stream = speechsdk.audio.PushAudioInputStream()
            config = speechsdk.audio.AudioConfig(stream=stream)

            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speechsdk.SpeechConfig(
                    subscription=self._key, region=self._region
                ),
                audio_config=config,
            )

            # Push audio data
            stream.write(audio)
            stream.close()

            # Recognize and wait for result
            result = recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text
            if result.reason == speechsdk.ResultReason.NoMatch:
                _log.info("Azure STT: no speech recognized")
                return ""
            if result.reason == speechsdk.ResultReason.Canceled:
                _log.warning("Azure STT canceled: %s", result.cancellation_details)
                return ""
            return ""
        except Exception as exc:
            _log.warning("Azure STT failed: %r", exc)
            return ""
