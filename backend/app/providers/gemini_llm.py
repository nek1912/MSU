import httpx

from app.config import REQUEST_TIMEOUT_S, Settings


class GeminiLLMProvider:
    def __init__(self, settings: Settings):
        self._key = settings.gemini_api_key
        self._url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                     f"{settings.gemini_model}:generateContent")

    def generate(self, system: str, user: str, temperature: float = 0.1) -> str:
        r = httpx.post(f"{self._url}?key={self._key}", json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature}},
            timeout=REQUEST_TIMEOUT_S)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
