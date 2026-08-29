from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    groq_api_key: str
    gemini_api_key: str
    jina_api_key: str = ""
    supabase_url: str
    supabase_service_key: str
    allowed_origins: str = "http://localhost:3000"
    selected_state: str | None = "gujarat"
    # Model IDs are deployment config, not code truth — Task 2 verifies the
    # current IDs against live docs and they are set via .env; defaults here
    # are best-known values only.
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.5-flash"
    embed_model: str = "gemini-embedding-2"
    jina_embed_model: str = "jina-embeddings-v3"
    # Reranker config (Phase 4/5) — disabled until curated eval proves value
    reranker_model: str = "jina-reranker-v2-base-multilingual"
    reranker_enabled: bool = False
    retrieval_strategy: str = "dense"  # dense | hybrid | hybrid_reranked
    # Azure Speech Services (PHASE 13 — voice I/O)
    azure_speech_key: str = ""
    azure_speech_region: str = ""
    # TTS voice names per language — configurable, not hardcoded
    azure_tts_voices: str = "en:en-IN-NeerjaNeural,hi:hi-IN-SwaraNeural,gu:gu-IN-DhwaniNeural"

    @property
    def tts_voices(self) -> dict[str, str]:
        """Parse azure_tts_voices into a dict."""
        result: dict[str, str] = {}
        for pair in self.azure_tts_voices.split(","):
            if ":" in pair:
                lang, voice = pair.split(":", 1)
                result[lang.strip()] = voice.strip()
        return result

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

EMBED_DIMS = 768
REQUEST_TIMEOUT_S = 30.0

# Retrieval gate thresholds (spec §2.4)
TOP1_THRESHOLD = 0.35
SECONDARY_THRESHOLD = 0.30
MIN_CHUNKS_ABOVE_SECONDARY = 2

@lru_cache
def get_settings() -> Settings:
    return Settings()
