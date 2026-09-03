"""Sarvam AI translation provider — Mayura v2 translation model.

Sarvam supports translation between Indian languages and English.
This is used as primary translator for Indian languages, with Azure as fallback.

Supports multiple API keys via KeyRotator — tries each key on failure.
"""
from __future__ import annotations

import logging

import httpx

from app.config import REQUEST_TIMEOUT_S, get_settings
from app.key_rotator import KeyRotator

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


_translate_cache: dict[tuple[str, str, str, str], str] = {}


def _raw_translate(api_key: str, text: str, source_lang: str, target_lang: str) -> str:
    """Make a single Sarvam translate API call. Raises on failure."""
    payload = {
        "input": text,
        "source_language_code": _to_sarvam_lang(source_lang),
        "target_language_code": _to_sarvam_lang(target_lang),
        "model": "mayura:v1",
        "numerals_format": "native",
        "mode": "formal",
    }

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


class SarvamTranslator:
    """Sarvam Mayura v2 translator for Indian languages with key rotation."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        keys = self.settings.sarvam_keys
        self._rotator = KeyRotator(keys, name="sarvam") if keys else None

    @property
    def configured(self) -> bool:
        return self._rotator is not None

    def translate(self, text: str, to: str = "en", source: str | None = None) -> str:
        if not self.configured or not text.strip():
            return text
        target = "en" if to in ("en", "en-IN") else to
        source = source or "hi"

        cache_key = (text, source, target)
        if cache_key in _translate_cache:
            return _translate_cache[cache_key]

        try:
            result = self._rotator.try_keys(  # type: ignore[union-attr]
                lambda key: _raw_translate(key, text, source, target)
            )
            _translate_cache[cache_key] = result
            return result
        except Exception as e:
            logger.warning("Sarvam translation failed with all keys: %s", e)
            return text
