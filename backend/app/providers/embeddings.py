import time
from functools import lru_cache

import httpx

from app.config import EMBED_DIMS, REQUEST_TIMEOUT_S, Settings, get_settings

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class JinaEmbeddingProvider:
    def __init__(self, settings: Settings):
        self._key = settings.jina_api_key
        self._endpoint = "https://api.jina.ai/v1/embeddings"
        self._model = settings.jina_embed_model
        self._max_attempts = 3
        self._base_delay = 1.0

    def _embed_batch(self, texts: list[str], client: httpx.Client, task: str = "retrieval.passage") -> list[list[float]]:
        last_exc: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                r = client.post(
                    self._endpoint,
                    headers={
                        "Authorization": f"Bearer {self._key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "input": texts,
                        "dimensions": EMBED_DIMS,
                        "task": task,
                    },
                )
                r.raise_for_status()
                data = r.json()["data"]
                # Sort by index to maintain order
                data.sort(key=lambda x: x["index"])
                values = [item["embedding"] for item in data]
                return values
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code not in _RETRYABLE_STATUS:
                    raise
                if attempt < self._max_attempts - 1:
                    time.sleep(self._base_delay * (2 ** attempt))
        raise last_exc  # type: ignore[misc]

    def embed_texts(self, texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:
        if not texts:
            return []
        # Jina supports batch embedding - process in chunks of 100
        all_embeddings = []
        with httpx.Client(timeout=60.0) as client:
            for i in range(0, len(texts), 100):
                batch = texts[i:i+100]
                embeddings = self._embed_batch(batch, client, task=task)
                all_embeddings.extend(embeddings)
                if i + 100 < len(texts):
                    time.sleep(0.5)  # Small delay between batches
        return all_embeddings


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

    def embed_texts(self, texts: list[str], task: str = "retrieval.passage") -> list[list[float]]:
        out: list[list[float]] = []
        with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
            for text in texts:
                out.append(self._embed_single(text, client))
        return out


@lru_cache(maxsize=1)
def get_embedding_provider():
    """Process-wide singleton. The route MUST use this — constructing a fresh
    provider per request would defeat the anchor-store cache (P0-1)."""
    settings = get_settings()
    # Prefer Jina if API key is available, fall back to Gemini
    if settings.jina_api_key:
        return JinaEmbeddingProvider(settings)
    return GeminiEmbeddingProvider(settings)
