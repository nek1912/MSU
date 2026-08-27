import time
from functools import lru_cache

import httpx

from app.config import EMBED_DIMS, REQUEST_TIMEOUT_S, Settings, get_settings

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class GeminiEmbeddingProvider:
    def __init__(self, settings: Settings):
        self._key = settings.gemini_api_key
        self._endpoint = ("https://generativelanguage.googleapis.com/v1beta/models/"
                          f"{settings.embed_model}:embedContent")
        self._max_attempts = 3
        self._base_delay = 1.0

    def _embed_single(self, text: str, client: httpx.Client) -> list[float]:
        last_exc: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                r = client.post(
                    f"{self._endpoint}?key={self._key}",
                    json={
                        "content": {"parts": [{"text": text}]},
                        "output_dimensionality": EMBED_DIMS,
                    },
                )
                r.raise_for_status()
                values = r.json()["embedding"]["values"]
                if len(values) != EMBED_DIMS:
                    raise ValueError(f"unexpected dims {len(values)}")
                return values
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code not in _RETRYABLE_STATUS:
                    raise
                if attempt < self._max_attempts - 1:
                    time.sleep(self._base_delay * (2 ** attempt))
        raise last_exc  # type: ignore[misc]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
            for text in texts:
                out.append(self._embed_single(text, client))
        return out


@lru_cache(maxsize=1)
def get_embedding_provider() -> GeminiEmbeddingProvider:
    """Process-wide singleton. The route MUST use this — constructing a fresh
    provider per request would defeat the anchor-store cache (P0-1)."""
    return GeminiEmbeddingProvider(get_settings())
