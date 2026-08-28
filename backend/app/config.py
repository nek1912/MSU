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
    RERANKER_ENABLED: bool = False  # Feature flag, disabled by default

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
