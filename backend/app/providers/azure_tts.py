"""Azure Speech Services — TTS adapter.

Converts text to speech audio using Azure Cognitive Services Speech SDK.
Falls back gracefully if SDK is unavailable or credentials are missing.

Voice names are configured via Settings.azure_tts_voices — not hardcoded.
"""
import logging

from app.config import Settings

_log = logging.getLogger(__name__)


class AzureTTSProvider:
    """Text-to-speech via Azure Cognitive Services."""

    def __init__(self, settings: Settings) -> None:
        self._key = getattr(settings, "azure_speech_key", "")
        self._region = getattr(settings, "azure_speech_region", "")
        self._voices = settings.tts_voices  # config-driven, not hardcoded

    @property
    def configured(self) -> bool:
        return bool(self._key and self._region)

    def synthesize(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech audio (WAV format).

        Args:
            text: Text to speak.
            language: Language code ("en", "hi", "gu").

        Returns:
            WAV audio bytes, or empty bytes on failure.
        """
        if not self.configured:
            _log.warning("Azure TTS not configured — returning empty")
            return b""

        try:
            import importlib
            speechsdk = importlib.import_module("azure.cognitiveservices.speech")
        except (ImportError, ModuleNotFoundError):
            _log.warning("azure-cognitiveservices-speech SDK not installed")
            return b""

        try:
            # Config-driven voice selection — falls back to first configured voice
            default_voice = next(iter(self._voices.values()), "en-IN-NeerjaNeural")
            voice = self._voices.get(language, default_voice)
            config = speechsdk.SpeechConfig(
                subscription=self._key, region=self._region
            )
            config.speech_synthesis_voice_name = voice

            # Use default speaker output (in-memory)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=config, audio_config=None
            )

            result = synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            if result.reason == speechsdk.ResultReason.Canceled:
                _log.warning("Azure TTS canceled: %s", result.cancellation_details)
                return b""
            return b""
        except Exception as exc:
            _log.warning("Azure TTS failed: %r", exc)
            return b""
