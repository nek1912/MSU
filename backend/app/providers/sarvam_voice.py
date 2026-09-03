"""Sarvam AI voice provider — Saaras v4 STT + Bulbul v3 TTS.

Supports multiple API keys — tries each on failure.
"""

import io
import logging
import base64
import aiohttp
from app.config import get_settings

logger = logging.getLogger(__name__)

_SARVAM_BASE = "https://api.sarvam.ai"
_TIMEOUT = aiohttp.ClientTimeout(total=30)

# BCP-47 language code mapping for Sarvam
_LANG_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "gu": "gu-IN",
    "bn": "bn-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "od": "od-IN",
    "pa": "pa-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "ne": "ne-IN",
    "kok": "kok-IN",
    "ks": "ks-IN",
    "sd": "sd-IN",
    "sa": "sa-IN",
    "sat": "sat-IN",
    "mni": "mni-IN",
    "brx": "brx-IN",
    "mai": "mai-IN",
    "doi": "doi-IN",
}


def _bcp(lang: str) -> str:
    """Convert short code like 'hi' to BCP-47 'hi-IN'."""
    if lang in _LANG_MAP:
        return _LANG_MAP[lang]
    if lang in _LANG_MAP.values():
        return lang
    return "hi-IN"


class SarvamSTTProvider:
    """Sarvam Saaras v4 — Speech to Text with key rotation."""

    def __init__(self):
        settings = get_settings()
        self._keys = settings.sarvam_keys
        self.enabled = bool(self._keys)

    async def transcribe(self, audio_bytes: bytes, language: str = "hi") -> str:
        if not self.enabled:
            raise RuntimeError("Sarvam STT not configured")

        lang_code = _bcp(language)
        last_exc: Exception | None = None

        for key in self._keys:
            form = aiohttp.FormData()
            form.add_field("file", audio_bytes, filename="audio.wav", content_type="audio/wav")
            form.add_field("model", "saaras:v4")
            form.add_field("language_code", lang_code)
            form.add_field("mode", "transcribe")
            form.add_field("sample_rate", "16000")

            try:
                async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                    async with session.post(
                        f"{_SARVAM_BASE}/speech-to-text",
                        headers={"api-subscription-key": key},
                        data=form,
                    ) as resp:
                        if resp.status != 200:
                            body = await resp.text()
                            raise RuntimeError(f"Sarvam STT {resp.status}: {body}")
                        data = await resp.json()
                        return data.get("transcript", "")
            except Exception as e:
                last_exc = e
                logger.warning("Sarvam STT key failed: %s — trying next", str(e)[:200])

        raise last_exc  # type: ignore[misc]


class SarvamTTSProvider:
    """Sarvam Bulbul v3 — Text to Speech with key rotation."""

    def __init__(self):
        settings = get_settings()
        self._keys = settings.sarvam_keys
        self.enabled = bool(self._keys)

    async def synthesize(self, text: str, language: str = "hi") -> bytes:
        if not self.enabled:
            raise RuntimeError("Sarvam TTS not configured")

        lang_code = _bcp(language)
        payload = {
            "text": text,
            "target_language_code": lang_code,
            "speaker": "shubh",
            "model": "bulbul:v3",
            "pace": 1,
            "speech_sample_rate": 22050,
            "output_audio_codec": "mp3",
        }

        last_exc: Exception | None = None

        for key in self._keys:
            try:
                async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                    async with session.post(
                        f"{_SARVAM_BASE}/text-to-speech",
                        headers={
                            "api-subscription-key": key,
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    ) as resp:
                        if resp.status != 200:
                            body = await resp.text()
                            raise RuntimeError(f"Sarvam TTS {resp.status}: {body}")
                        data = await resp.json()
                        audios = data.get("audios", [])
                        if not audios:
                            raise RuntimeError("Sarvam TTS returned no audio")
                        return base64.b64decode(audios[0])
            except Exception as e:
                last_exc = e
                logger.warning("Sarvam TTS key failed: %s — trying next", str(e)[:200])

        raise last_exc  # type: ignore[misc]

    async def text_to_speech(self, text: str, language: str = "hi") -> bytes:
        """Convert text to speech."""
        return await self.synthesize(text, language)

    async def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        """Convert text segments to multi-voice speech."""
        combined_text = " ".join(s.get("text", "") for s in segments if s.get("text"))
        lang = segments[0].get("lang", "hi") if segments else "hi"
        return await self.synthesize(combined_text, lang)
