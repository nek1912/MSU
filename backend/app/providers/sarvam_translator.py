"""Sarvam AI translation provider — Mayura v2 translation model.

Sarvam supports translation between Indian languages and English.
This is used as primary translator for Indian languages, with Azure as fallback.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import httpx

from app.config import REQUEST_TIMEOUT_S, get_settings

logger = logging.getLogger(__name__)

_SARVAM_BASE = "https://api.sarvam.ai"

# Sarvam language code mapping
_SARVAM_LANG_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "gu": "gu-IN",
    "bn": "bn-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "od": "od-IN",
    "pa": "pa-IN",
    "as": "as-IN",
    "ur": "ur-IN",
    "ne": "ne-IN",
}


def _to_sarvam_lang(lang: str) -> str:
    """Convert short code to Sarvam BCP-47 format."""
    if lang in _SARVAM_LANG_MAP:
        return _SARVAM_LANG_MAP[lang]
    if lang in _SARVAM_LANG_MAP.values():
        return lang
    return "hi-IN"


class SarvamTranslatorError(RuntimeError):
    pass


@lru_cache(maxsize=1024)
def _cached_translate(api_key: str, text: str, source_lang: str, target_lang: str) -> str:
    """Translate with cache; returns original text on failure."""
    if not text.strip():
        return text

    payload = {
        "input": text,
        "source_language_code": _to_sarvam_lang(source_lang),
        "target_language_code": _to_sarvam_lang(target_lang),
        "model": "mayura:v2",
        "mode": "formal",
    }

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
            resp = client.post(
                f"{_SARVAM_BASE}/translate",
                headers={
                    "api-subscription-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            translated = data.get("translated_text", "")
            return translated if translated else text
    except (httpx.HTTPError, KeyError, ValueError) as e:
        logger.warning(f"Sarvam translation failed: {e}")
        return text


class SarvamTranslator:
    """Sarvam Mayura v2 translator for Indian languages."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.sarvam_api_key)

    def translate(self, text: str, to: str = "en", source: str | None = None) -> str:
        if not self.configured:
            return text
        # Sarvam uses "en-IN" not just "en"
        target = "en" if to in ("en", "en-IN") else to
        source = source or "hi"  # default to Hindi
        return _cached_translate(self.settings.sarvam_api_key, text, source, target)
