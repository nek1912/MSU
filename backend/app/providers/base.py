from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, system: str, user: str, temperature: float = 0.1) -> str: ...


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
