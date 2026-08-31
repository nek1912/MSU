import json
from collections.abc import Generator

import httpx

from app.config import REQUEST_TIMEOUT_S, Settings

_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqLLMProvider:
    def __init__(self, settings: Settings):
        self._key = settings.groq_api_key
        self._model = settings.groq_model

    def generate(self, system: str, user: str, temperature: float = 0.1) -> str:
        r = httpx.post(_URL,
            headers={"Authorization": f"Bearer {self._key}"},
            json={"model": self._model, "temperature": temperature,
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": user}]},
            timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def generate_stream(self, system: str, user: str,
                        temperature: float = 0.1) -> Generator[str, None, None]:
        """Yield text tokens as they arrive from Groq's streaming API."""
        with httpx.stream(
            "POST", _URL,
            headers={"Authorization": f"Bearer {self._key}"},
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
