import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logging.basicConfig(level=logging.INFO,
                    format='{"level":"%(levelname)s","msg":"%(message)s"}')


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        from app.domains import get_anchor_store
        get_anchor_store()
    except Exception as exc:  # noqa: BLE001 – catch-all is intentional
        logging.getLogger(__name__).warning("anchor warmup deferred: %r", exc)
    yield


app = FastAPI(title="Sahayak API", version="0.1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware,
                   allow_origins=get_settings().origins,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": app.version}


@app.get("/health/providers")
def health_providers() -> dict:
    s = get_settings()
    return {
        "groq": "configured" if s.groq_api_key else "missing",
        "gemini": "configured" if s.gemini_api_key else "missing",
        "supabase": "configured" if s.supabase_url else "missing",
        "bhashini": "stub",
    }
