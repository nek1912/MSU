"""Sarvam AI chat completions provider (OpenAI-compatible API)."""
from __future__ import annotations

import httpx
import logging
import time
from typing import Generator

from app.config import Settings
from app.key_rotator import KeyRotator

logger = logging.getLogger(__name__)


class SarvamProviderError(Exception):
    """Dedicated exception for Sarvam provider failures.

    Subclasses distinguish retryable from non-retryable errors:
    - Retryable: 403 (invalid_api_key), 429, 500, 503, timeout
    - Non-retryable: 400, 422, malformed response, programming errors
    """

    def __init__(self, message: str, status_code: int | None = None, retryable: bool = True):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class SarvamChatProvider:
    """Sarvam-105B chat completions adapter.

    Uses the OpenAI-compatible endpoint at api.sarvam.ai.
    Auth: ``api-subscription-key: <key>`` header only.
    Reasoning is disabled (reasoning_effort=None) for latency-sensitive RAG.
    """

    def __init__(self, settings: Settings) -> None:
        keys = settings.sarvam_keys
        if not keys:
            raise ValueError("No Sarvam API keys configured")
        self._rotator = KeyRotator(keys, name="sarvam")
        self._model = settings.sarvam_chat_model
        self._url = settings.sarvam_chat_url

    def generate(
        self, system: str, user: str, temperature: float = 0.1
    ) -> str:
        """Non-streaming generation. Primary MVP path."""
        last_error: SarvamProviderError | None = None
        keys = self._rotator._keys  # noqa: SLF001
        for key in keys:
            try:
                return self._call_api(key, system, user, temperature)
            except SarvamProviderError as exc:
                last_error = exc
                if not exc.retryable:
                    raise  # 400, 422 — don't rotate keys
                # 429 → bounded backoff before trying next key
                if exc.status_code == 429:
                    time.sleep(1.0)
                continue
        raise last_error  # type: ignore[misc]

    def _call_api(
        self,
        key: str,
        system: str,
        user: str,
        temperature: float,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": key,
        }
        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "reasoning_effort": None,
            "max_tokens": 2048,
            "stream": False,
        }
        try:
            resp = httpx.post(self._url, json=body, headers=headers, timeout=(30.0, 120.0))
        except httpx.TimeoutException as exc:
            raise SarvamProviderError(f"Timeout: {exc}", retryable=True) from exc

        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if not choices or not choices[0].get("message", {}).get("content"):
                raise SarvamProviderError("Empty response from Sarvam", retryable=False)
            return choices[0]["message"]["content"]

        # Classify error
        if resp.status_code == 422:
            raise SarvamProviderError(
                f"Invalid request (422): {resp.text[:200]}", status_code=422, retryable=False
            )
        if resp.status_code == 400:
            raise SarvamProviderError(
                f"Bad request (400): {resp.text[:200]}", status_code=400, retryable=False
            )
        if resp.status_code == 403:
            # 403 can mean invalid key OR other forbidden error
            # Inspect error.code if available
            try:
                err_body = resp.json()
                err_code = err_body.get("error", {}).get("code", "")
                if err_code == "invalid_api_key":
                    raise SarvamProviderError(
                        f"Invalid API key (403)", status_code=403, retryable=True
                    )
            except (ValueError, KeyError):
                pass
            raise SarvamProviderError(
                f"Forbidden (403): {resp.text[:200]}", status_code=403, retryable=False
            )
        if resp.status_code in (429, 500, 503):
            raise SarvamProviderError(
                f"Provider error ({resp.status_code}): {resp.text[:200]}",
                status_code=resp.status_code,
                retryable=True,
            )
        raise SarvamProviderError(
            f"Unexpected status {resp.status_code}: {resp.text[:200]}",
            status_code=resp.status_code,
            retryable=False,
        )