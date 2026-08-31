from collections.abc import Generator

import httpx

from app.providers.base import LLMProvider


class AllProvidersFailedError(Exception): ...


def _retryable(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in (429, 500, 502, 503, 504)


def grounded_answer(primary: LLMProvider, fallback: LLMProvider,
                    system: str, user: str) -> str:
    errors: list[str] = []
    for name, provider in (("groq", primary), ("gemini", fallback)):
        try:
            return provider.generate(system, user)
        except Exception as exc:
            errors.append(f"{name}: {exc!r}")
    raise AllProvidersFailedError("; ".join(errors))


def grounded_answer_stream(primary: LLMProvider, fallback: LLMProvider,
                           system: str, user: str) -> Generator[str, None, None]:
    """Yield tokens from primary; fall back to secondary on failure."""
    errors: list[str] = []
    for name, provider in (("groq", primary), ("gemini", fallback)):
        try:
            yield from provider.generate_stream(system, user)
            return
        except Exception as exc:
            errors.append(f"{name}: {exc!r}")
    raise AllProvidersFailedError("; ".join(errors))
