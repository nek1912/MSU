"""Sarvam AI voice provider — Saaras v3 STT + Bulbul v3 TTS."""

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
    """Sarvam Saaras v3 — Speech to Text."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.sarvam_api_key
        self.enabled = bool(self.api_key)

    async def transcribe(self, audio_bytes: bytes, language: str = "hi") -> str:
        if not self.enabled:
            raise RuntimeError("Sarvam STT not configured")

        lang_code = _bcp(language)
        form = aiohttp.FormData()
        form.add_field("file", audio_bytes, filename="audio.wav", content_type="audio/wav")
        form.add_field("model", "saaras:v3")
        form.add_field("language_code", lang_code)
        form.add_field("mode", "transcribe")

        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{_SARVAM_BASE}/speech-to-text",
                headers={"api-subscription-key": self.api_key},
                data=form,
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(f"Sarvam STT {resp.status}: {body}")
                data = await resp.json()
                return data.get("transcript", "")


class SarvamTTSProvider:
    """Sarvam Bulbul v3 — Text to Speech."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.sarvam_api_key
        self.enabled = bool(self.api_key)

    async def synthesize(self, text: str, language: str = "hi") -> bytes:
        if not self.enabled:
            raise RuntimeError("Sarvam TTS not configured")

        lang_code = _bcp(language)
        payload = {
            "text": text,
            "language_code": lang_code,
            "model": "bulbul:v3",
            "speaker": "shubh",
            "speech_sample_rate": 24000,
            "output_audio_codec": "wav",
        }

        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(
                f"{_SARVAM_BASE}/text-to-speech",
                headers={
                    "api-subscription-key": self.api_key,
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

    async def text_to_speech(self, text: str, language: str = "hi") -> bytes:
        """Convert text to speech."""
        return await self.synthesize(text, language)

    async def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        """Convert text segments to multi-voice speech."""
        combined_text = " ".join(s.get("text", "") for s in segments if s.get("text"))
        lang = segments[0].get("lang", "hi") if segments else "hi"
        return await self.synthesize(combined_text, lang)
