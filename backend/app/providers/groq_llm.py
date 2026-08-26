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
