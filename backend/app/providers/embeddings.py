from functools import lru_cache

import httpx

from app.config import EMBED_DIMS, REQUEST_TIMEOUT_S, Settings, get_settings


class GeminiEmbeddingProvider:
    def __init__(self, settings: Settings):
        self._key = settings.gemini_api_key
        self._endpoint = ("https://generativelanguage.googleapis.com/v1beta/models/"
                          f"{settings.embed_model}:embedContent")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
            for text in texts:  # one request per string: per-string guarantee
                r = client.post(f"{self._endpoint}?key={self._key}", json={
                    "content": {"parts": [{"text": text}]},
                    "output_dimensionality": EMBED_DIMS})
                r.raise_for_status()
                values = r.json()["embedding"]["values"]
                if len(values) != EMBED_DIMS:
                    raise ValueError(f"unexpected dims {len(values)}")
                out.append(values)
        return out


@lru_cache(maxsize=1)
def get_embedding_provider() -> GeminiEmbeddingProvider:
    """Process-wide singleton. The route MUST use this — constructing a fresh
    provider per request would defeat the anchor-store cache (P0-1)."""
    return GeminiEmbeddingProvider(get_settings())
