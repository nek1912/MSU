"""Groq LLM provider with API key rotation."""

import json
from collections.abc import Generator

import httpx

from app.config import REQUEST_TIMEOUT_S, Settings
from app.key_rotator import KeyRotator

_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqLLMProvider:
    def __init__(self, settings: Settings):
        keys = settings.groq_keys
        self._rotator = KeyRotator(keys, name="groq") if keys else None
        self._key = settings.groq_api_key  # fallback for single-key compat
        self._model = settings.groq_model

    def _get_key(self) -> str:
        return self._rotator.current_key if self._rotator else self._key

    def generate(self, system: str, user: str, temperature: float = 0.1) -> str:
        if self._rotator:
            return self._rotator.try_keys(lambda key: self._do_generate(key, system, user, temperature))
        return self._do_generate(self._key, system, user, temperature)

    def _do_generate(self, key: str, system: str, user: str, temperature: float) -> str:
        r = httpx.post(_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": self._model, "temperature": temperature,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": user}]},
            timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def generate_stream(self, system: str, user: str,
                        temperature: float = 0.1) -> Generator[str, None, None]:
        """Yield text tokens as they arrive from Groq's streaming API."""
        key = self._get_key()
        try:
            yield from self._do_stream(key, system, user, temperature)
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
            if not self._rotator:
                raise
            # Try next key
            for key in self._rotator._keys:
                if key == self._get_key():
                    continue
                try:
                    yield from self._do_stream(key, system, user, temperature)
                    return
                except Exception:
                    continue
            raise

    def _do_stream(self, key: str, system: str, user: str,
                   temperature: float) -> Generator[str, None, None]:
        with httpx.stream(
            "POST", _URL,
            headers={"Authorization": f"Bearer {key}"},
            json={"model": self._model, "temperature": temperature, "stream": True,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": user}]},
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0),
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta", {})
                    text = delta.get("content")
                    if text:
                        yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
