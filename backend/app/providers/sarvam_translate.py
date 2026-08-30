"""Sarvam AI Translation provider — Mayura v1."""

import logging
import aiohttp
from app.config import get_settings

logger = logging.getLogger(__name__)

_SARVAM_BASE = "https://api.sarvam.ai"
_TIMEOUT = aiohttp.ClientTimeout(total=15)


def _bcp(lang: str) -> str:
    """Convert short code like 'hi' to BCP-47 'hi-IN'."""
    _MAP = {
        "en": "en-IN", "hi": "hi-IN", "gu": "gu-IN", "bn": "bn-IN",
        "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "od": "od-IN",
        "pa": "pa-IN", "ta": "ta-IN", "te": "te-IN",
    }
    if lang in _MAP:
        return _MAP[lang]
    if lang in _MAP.values():
        return lang
    return "hi-IN"


class SarvamTranslationProvider:
    """Sarvam Mayura v1 — text translation between Indian languages."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.sarvam_api_key
        self.enabled = bool(self.api_key)

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        """Translate text. Returns translated text or original on failure."""
        if not self.enabled:
            logger.warning("Sarvam translate disabled: no API key")
            return text

        src = _bcp(source_lang)
        tgt = _bcp(target_lang)
        if src == tgt:
            return text

        payload = {
            "input": text,
            "source_language_code": src,
            "target_language_code": tgt,
            "model": "mayura:v1",
            "mode": "modern-colloquial",
        }

        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(
                    f"{_SARVAM_BASE}/translate",
                    headers={
                        "api-subscription-key": self.api_key,
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.warning("Sarvam translate %s: %s", resp.status, body)
                        return text
                    data = await resp.json()
                    return data.get("translated_text", text)
        except Exception as exc:
            logger.warning("Sarvam translate failed: %s", exc)
            return text
