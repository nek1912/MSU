import json
from collections.abc import Generator

import httpx

from app.config import REQUEST_TIMEOUT_S, Settings


class GeminiLLMProvider:
    def __init__(self, settings: Settings):
        self._key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                     f"{self._model}:generateContent")
        self._stream_url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                            f"{self._model}:streamGenerateContent")

    def generate(self, system: str, user: str, temperature: float = 0.1) -> str:
        r = httpx.post(f"{self._url}?key={self._key}", json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature}},
            timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def generate_stream(self, system: str, user: str,
                        temperature: float = 0.1) -> Generator[str, None, None]:
        """Yield text tokens as they arrive from Gemini's streaming API."""
        with httpx.stream(
            "POST", f"{self._stream_url}?key={self._key}",
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"temperature": temperature},
            },
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0),
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    candidates = chunk.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            text = part.get("text")
                            if text:
                                yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
