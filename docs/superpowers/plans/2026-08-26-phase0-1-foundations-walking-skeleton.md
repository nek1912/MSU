# Phase 0–1: Foundations & Walking Skeleton — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standing monorepo + cloud provider accounts + Supabase schema + a locally running `/chat` that answers 5 seed questions with verified citations from a 10–15 chunk seed corpus and correctly abstains on 2 unsupported questions, plus a trivial `/health` stub live on Render.

**Architecture:** FastAPI orchestrates: explicit-language handling → keyword+anchor hybrid domain routing → jurisdiction-filtered pgvector retrieval (Supabase RPC) → provisional evidence gate → Groq grounded generation with `[chunk:N]` citation markers → code-level citation verification → frozen-contract response or structured abstention. Ingestion is an offline script package, never in the request path.

**Tech Stack:** Python 3.11+, FastAPI, pydantic-settings, httpx, supabase-py, pytest + respx; Next.js (App Router) + Tailwind + vitest; ruff; GitHub Actions. Providers: Groq (`llama-3.3-70b-versatile`), Gemini fallback (`gemini-2.5-flash`), embeddings `gemini-embedding-2` @ 768.

**Spec:** `docs/superpowers/specs/2026-08-26-mvp-build-design.md` (§2 decisions are law here).

## Global Constraints

- Frozen `/chat` response fields ONLY: `answer, language, domain, confidence, citations[{title,page,url}], abstained, follow_up_question`. Evidence bands are computed client-side; no extra API fields.
- Abstention is decided by code (thresholds), never by the LLM. Thresholds live ONLY in `backend/app/config.py`: `TOP1_THRESHOLD=0.35`, `SECONDARY_THRESHOLD=0.30`, `MIN_CHUNKS_ABOVE_SECONDARY=2`.
- Every citation validated against the retrieved set of the current request; any invalid citation → `abstained: true`.
- Grievance endpoints always return `is_official_submission: false` (not exercised until Phase 2).
- Keys only via env vars; `.env` is gitignored; never `NEXT_PUBLIC_*` for secrets.
- Jurisdiction SQL: central documents always eligible; state documents only when `state` matches; `state=null` queries see central only.
- Provisional values (calibrated Phase 4): thresholds above; confidence `0.6*top1 + 0.4*(above_secondary/k)` clamped [0,1], rounded 2dp.
- FAISS intentionally deferred — dev retrieval runs directly against the development Supabase project (spec §4 Phase 1 wording).
- Model IDs verified in Task 2 against live docs before first spend; update `config.py` constants if changed.

---

### Task 1: Monorepo scaffold, env contract, CI

**Files:**
- Create: `.gitignore`, `.env.example`, `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/tests/__init__.py`, `frontend/package.json` (via create-next-app), `.github/workflows/ci.yml`, `render.yaml`

**Interfaces:**
- Produces: directory layout all later tasks import from; `backend.app` importable package; CI green on push.

- [ ] **Step 1: Create Python scaffold files**

`.gitignore`:
```
.env
__pycache__/
*.pyc
.venv/
node_modules/
.next/
coverage/
.pytest_cache/
.ruff_cache/
```

`.env.example`:
```
GROQ_API_KEY=
GEMINI_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
ALLOWED_ORIGINS=http://localhost:3000
SELECTED_STATE=gujarat
```

`backend/pyproject.toml`:
```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "pydantic>=2.7",
  "pydantic-settings>=2.3",
  "httpx>=0.27",
  "supabase>=2.5",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.23", "respx>=0.21", "ruff>=0.4"]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create Next.js app (no secrets, App Router, Tailwind)**

Run: `npx create-next-app@latest frontend --ts --tailwind --app --eslint --src-dir --import-alias "@/*" --use-npm`
Expected: `frontend/` created; `npm run dev` serves localhost:3000.

- [ ] **Step 3: CI workflow**

`.github/workflows/ci.yml`:
```yaml
name: ci
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: backend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest -q
  frontend:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: frontend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run lint --if-present && npx tsc --noEmit
```

`render.yaml` (stub service definition for Task 4's deployment):
```yaml
services:
  - type: web
    name: sahayak-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -e .
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    plan: free
```

- [ ] **Step 4: Install backend deps and verify toolchain**

Run (from `backend/`): `pip install -e ".[dev]"; ruff check .; pytest -q`
Expected: ruff passes (or reports nothing), pytest exits 0 with "no tests ran".

- [ ] **Step 5: Commit**
```bash
git add -A
git commit -m "chore: monorepo scaffold, env contract, CI, render stub"
```

---

### Task 2: Provider accounts + verification smoke scripts

**Files:**
- Create: `scripts/smoke_groq.py`, `scripts/smoke_gemini_embeddings.py`, `scripts/smoke_supabase.py`, `docs/runbooks/provider-setup.md`

**Interfaces:**
- Consumes: `.env` values (operator fills them manually).
- Produces: written confirmation in `PROJECT_STATUS.md` provider table; verified model IDs recorded in `backend/app/config.py` (Task 3 reads them).
- NOTE: These scripts hit paid-free-tier APIs and are NOT part of pytest. They require human account creation first — the AI executor prepares scripts + runbook and stops at the manual checklist.

- [ ] **Step 1: Write the runbook**

`docs/runbooks/provider-setup.md` — exact signup order and URLs:
1. Supabase → https://supabase.com/dashboard → New Project (name `sahayak-dev`, region nearest team) → copy Project URL + service_role key into `.env`.
2. Groq → https://console.groq.com → API Keys → create → `.env` as `GROQ_API_KEY`.
3. Gemini → https://aistudio.google.com → Get API key → `.env` as `GEMINI_API_KEY`.
4. Bhashini → https://bhashini.gov.in → register (ULCA API key request). Approval lead time unverified — submit NOW, record submission date in PROJECT_STATUS.md Blocking issues; do not block other work on it.
5. Render → https://dashboard.render.com → sign up (used by Task 4).

- [ ] **Step 2: Smoke scripts**

`scripts/smoke_groq.py`:
```python
import os, sys, httpx

def main() -> int:
    key = os.environ["GROQ_API_KEY"]
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": "llama-3.3-70b-versatile",
              "messages": [{"role": "user", "content": "Reply with OK"}],
              "max_tokens": 5},
        timeout=30,
    )
    r.raise_for_status()
    print("groq ok:", r.json()["choices"][0]["message"]["content"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`scripts/smoke_gemini_embeddings.py` — implements the spec §2.2 per-string guard:
```python
import os, sys, httpx

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"

def embed(key: str, text: str) -> list[float]:
    r = httpx.post(
        f"{URL}?key={key}",
        json={"content": {"parts": [{"text": text}]}, "output_dimensionality": 768},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["embedding"]["values"]

def main() -> int:
    key = os.environ["GEMINI_API_KEY"]
    texts = ["PMFBY crop insurance eligibility", "PACS byelaws membership",
             "RBI financial literacy booklet"]
    vecs = [embed(key, t) for t in texts]
    assert all(len(v) == 768 for v in vecs), "wrong dimensionality"
    assert len({tuple(v) for v in vecs}) == 3, "AGGREGATION GUARD FAILED: inputs collapsed"
    print("gemini-embedding-2 ok: 3 inputs -> 3 distinct 768-dim vectors")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`scripts/smoke_supabase.py`:
```python
import os, sys
from supabase import create_client

def main() -> int:
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    sb.table("documents").select("id").limit(1).execute()
    print("supabase ok: connection + documents table reachable")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```
(Note: supabase smoke passes only after Task 3's migration; run order is Task 3 → this script.)

- [ ] **Step 3: Operator runs smokes after accounts exist; record results**

Run (repo root, `.env` loaded): `python scripts/smoke_groq.py; python scripts/smoke_gemini_embeddings.py`
Expected: `groq ok: OK` and `gemini-embedding-2 ok: 3 inputs -> 3 distinct 768-dim vectors`.
If the aggregation assertion fails: STOP, revert embedding decision to `gemini-embedding-001` per DECISIONS.md guard, re-log, adjust `config.py` (Task 3) to add manual L2 normalization.
Update `PROJECT_STATUS.md`: provider table rows + timestamp.

- [ ] **Step 4: Verify current model IDs**

Check https://console.groq.com/docs/models and https://ai.google.dev/gemini-api/docs — confirm `llama-3.3-70b-versatile` and `gemini-2.5-flash` are still offered; record findings in the runbook. If changed, use the documented successor and update Global Constraints + `config.py`.

- [ ] **Step 5: Commit**
```bash
git add -A
git commit -m "chore: provider smoke scripts and setup runbook"
```

---

### Task 3: Supabase schema migration

**Files:**
- Create: `backend/migrations/0001_init.sql`

**Interfaces:**
- Produces: tables `documents, chunks, grievances, sessions, feedback`; RPC `match_chunks(query_embedding vector(768), match_domain text, match_state text, match_count int)` used verbatim by Task 8.

- [ ] **Step 1: Write migration**

`backend/migrations/0001_init.sql`:
```sql
create extension if not exists vector;

create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  source_id text unique not null,
  title text not null,
  organization text not null,
  jurisdiction text not null check (jurisdiction in ('central','state')),
  state text,
  domain text not null,
  document_type text not null,
  source_url text not null,
  effective_date date,
  verified_date date not null default current_date,
  document_hash text,
  created_at timestamptz not null default now()
);

create table if not exists chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  page int not null default 0,
  section text not null default '',
  content text not null,
  embedding vector(768) not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists chunks_embedding_hnsw
  on chunks using hnsw (embedding vector_cosine_ops);
create index if not exists chunks_document_idx on chunks(document_id);

create table if not exists sessions (
  session_id uuid primary key,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  expires_at timestamptz not null default now() + interval '24 hours'
);

create table if not exists grievances (
  id uuid primary key default gen_random_uuid(),
  reference text unique not null,
  status text not null default 'NEW'
    check (status in ('NEW','NEEDS_INFORMATION','CLASSIFIED','CREATED','IN_PROGRESS','RESOLVED')),
  category text,
  location text,
  language text not null default 'en',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists feedback (
  id uuid primary key default gen_random_uuid(),
  session_id uuid,
  message_id text,
  rating int check (rating between 1 and 5),
  note text,
  created_at timestamptz not null default now()
);

create or replace function match_chunks(
  query_embedding vector(768),
  match_domain text default null,
  match_state text default null,
  match_count int default 6
)
returns table (
  chunk_id uuid, document_id uuid, title text, organization text,
  jurisdiction text, state text, domain text, source_url text,
  page int, section text, content text, similarity float
)
language sql stable as $$
  select c.id, d.id, d.title, d.organization, d.jurisdiction, d.state, d.domain,
         d.source_url, c.page, c.section, c.content,
         1 - (c.embedding <=> query_embedding) as similarity
  from chunks c
  join documents d on d.id = c.document_id
  where (match_domain is null or d.domain = match_domain)
    and (
      d.jurisdiction = 'central'
      or (match_state is not null and d.state = match_state)
    )
  order by c.embedding <=> query_embedding
  limit least(match_count, 20);
$$;
```

- [ ] **Step 2: Apply via Supabase dashboard SQL editor** (human step; paste file contents, Run). Confirm "Success. No rows returned".

- [ ] **Step 3: Verify RPC shape**

Run in SQL editor:
```sql
select * from match_chunks(gen_random_uuid()::text::vector, null, null, 3);
```
Expected: empty set, no error.

- [ ] **Step 4: Run `python scripts/smoke_supabase.py`** — Expected: `supabase ok: ...`

- [ ] **Step 5: Commit**
```bash
git add backend/migrations/0001_init.sql
git commit -m "feat: supabase schema + match_chunks rpc"
```

---

### Task 4: Config + provider adapters (LLM, embeddings, Bhashini stub)

**Files:**
- Create: `backend/app/config.py`, `backend/app/providers/__init__.py`, `backend/app/providers/base.py`, `backend/app/providers/groq_llm.py`, `backend/app/providers/gemini_llm.py`, `backend/app/providers/embeddings.py`, `backend/app/providers/bhashini_stub.py`, `backend/app/llm_fallback.py`
- Test: `backend/tests/test_providers.py`, `backend/tests/test_llm_fallback.py`

**Interfaces:**
- Produces:
  - `get_settings() -> Settings` (cached); fields: `groq_api_key, gemini_api_key, supabase_url, supabase_service_key, allowed_origins: list[str], selected_state: str | None`
  - `EmbeddingProvider.embed_texts(texts: list[str]) -> list[list[float]]` (768-dim)
  - `LLMProvider.generate(system: str, user: str, temperature: float = 0.1) -> str`
  - `grounded_answer(primary: LLMProvider, fallback: LLMProvider, system: str, user: str) -> str` — tries primary, falls back on `httpx.TimeoutException | httpx.HTTPStatusError` with 429/5xx, raises `AllProvidersFailedError` otherwise
  - `BhashiniStub` implementing `transcribe(audio: bytes, lang: str) -> str` / `synthesize(text: str, lang: str) -> bytes` returning canned data (replaced Phase 6)

- [ ] **Step 1: Failing tests**

`backend/tests/test_providers.py`:
```python
import httpx, respx, pytest
from app.config import Settings
from app.providers.embeddings import GeminiEmbeddingProvider
from app.providers.groq_llm import GroqLLMProvider


def test_embed_returns_768_per_text(respx_mock):
    body = {"embedding": {"values": [0.1] * 768}}
    respx_mock.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent").mock(
        return_value=httpx.Response(200, json=body)
    )
    provider = GeminiEmbeddingProvider(Settings(gemini_api_key="k", groq_api_key="g",
        supabase_url="u", supabase_service_key="s"))
    out = provider.embed_texts(["a", "b"])
    assert len(out) == 2 and len(out[0]) == 768


def test_groq_generate(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "hi"}}]})
    )
    p = GroqLLMProvider(Settings(gemini_api_key="k", groq_api_key="g",
        supabase_url="u", supabase_service_key="s"))
    assert p.generate("sys", "user") == "hi"
```

`backend/tests/test_llm_fallback.py`:
```python
import httpx, respx, pytest
from app.config import Settings
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider

S = lambda: Settings(gemini_api_key="k", groq_api_key="g", supabase_url="u", supabase_service_key="s")

@respx.mock
def test_falls_back_to_gemini_on_429():
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={"error": "rate"}))
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent").mock(
        return_value=httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "fb"}]}}]}))
    out = grounded_answer(GroqLLMProvider(S()), GeminiLLMProvider(S()), "sys", "user")
    assert out == "fb"

@respx.mock
def test_raises_when_both_fail():
    respx.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(429, json={}))
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent").mock(
        return_value=httpx.Response(429, json={}))
    with pytest.raises(AllProvidersFailedError):
        grounded_answer(GroqLLMProvider(S()), GeminiLLMProvider(S()), "sys", "user")
```

- [ ] **Step 2: Run tests, verify they fail**
Run: `pytest tests/test_providers.py tests/test_llm_fallback.py -v`
Expected: FAIL — `ModuleNotFoundError: app.config` / `app.providers`.

- [ ] **Step 3: Implement**

`backend/app/config.py`:
```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    groq_api_key: str
    gemini_api_key: str
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

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

EMBED_DIMS = 768
REQUEST_TIMEOUT_S = 30.0

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`.env.example` gains:
```
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.5-flash
EMBED_MODEL=gemini-embedding-2
```

`backend/app/providers/base.py`:
```python
from typing import Protocol


class LLMProvider(Protocol):
    def generate(self, system: str, user: str, temperature: float = 0.1) -> str: ...


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
```

`backend/app/providers/embeddings.py`:
```python
from functools import lru_cache

import httpx

from app.config import EMBED_DIMS, REQUEST_TIMEOUT_S, Settings


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
```

`backend/app/providers/groq_llm.py`:
```python
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
```

`backend/app/providers/gemini_llm.py`:
```python
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
```

`backend/app/providers/bhashini_stub.py`:
```python
class BhashiniStub:
    """Tier-2 placeholder. Real adapter lands in Phase 6."""

    def transcribe(self, audio: bytes, lang: str) -> str:
        return "[stub transcription]"

    def synthesize(self, text: str, lang: str) -> bytes:
        return b"[stub audio]"
```

`backend/app/llm_fallback.py`:
```python
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
            if not _retryable(exc):
                raise
            errors.append(f"{name}: {exc!r}")
    raise AllProvidersFailedError("; ".join(errors))
```

`backend/app/providers/__init__.py`: empty file.

- [ ] **Step 4: Tests pass**
Run: `pytest tests/test_providers.py tests/test_llm_fallback.py -v` — Expected: 4 PASS.

- [ ] **Step 5: Commit**
```bash
git add backend/app backend/tests
git commit -m "feat: config, provider adapters, llm fallback chain"
```

---

### Task 5: FastAPI app shell — `/health`, `/health/providers`, CORS

**Files:**
- Create: `backend/app/main.py`
- Modify: `backend/pyproject.toml` (add `uvicorn` already present; nothing needed)
- Test: `backend/tests/test_health.py`
- Deploy: Render stub (manual step at end)

**Interfaces:**
- Produces: ASGI app `app.main:app`; `GET /health` → `{"status":"ok","version":"0.1.0"}`; `GET /health/providers` → `{"groq":"configured","gemini":"configured","supabase":"configured","bhashini":"stub"}`.

- [ ] **Step 1: Failing test**

`backend/tests/test_health.py`:
```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_health_providers_shape():
    r = client.get("/health/providers")
    assert r.status_code == 200
    body = r.json()
    assert body["groq"] == "configured" and body["bhashini"] == "stub"
```

- [ ] **Step 2: Run, verify failure** — `pytest tests/test_health.py -v` → FAIL (`app.main` missing).

- [ ] **Step 3: Implement**

`backend/app/main.py`:
```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logging.basicConfig(level=logging.INFO,
                    format='{"level":"%(levelname)s","msg":"%(message)s"}')


@asynccontextmanager
async def lifespan(_: FastAPI):
    # One-time anchor embedding at boot (~70 requests) so no user request
    # ever pays for it (P0-1). Failure defers to first /chat instead of
    # blocking startup — e.g. when running tests offline.
    try:
        from app.domains import get_anchor_store
        get_anchor_store()
    except Exception as exc:
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
```

- [ ] **Step 4: Tests pass + lint** — `pytest tests/test_health.py -v; ruff check .` → PASS.

- [ ] **Step 5: Deploy Render stub (human-in-loop)**

Dashboard → New + → Web Service → connect repo → Runtime: Python, Root Directory: `backend`, Build: `pip install -e .`, Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, add env vars from `.env.example` (real values). Record URL in PROJECT_STATUS.md. Expected: `GET <url>/health` → 200 after wake (~60s cold start).

- [ ] **Step 6: Commit**
```bash
git add backend/app backend/tests
git commit -m "feat: fastapi shell with health routes and cors"
```

---

### Task 6: Language handling module

**Files:**
- Create: `backend/app/language.py`
- Test: `backend/tests/test_language.py`

**Interfaces:**
- Produces: `normalize_language(selected: str, text: str) -> str` → `"en" | "hi"`. Selection wins unless text is ≥70% Devanagari while `"en"` selected (then `"hi"`), or ≥70% Latin while `"hi"` selected AND Hindi stopword count exceeds English stopword count (then `"en"`). Raises `ValueError` on non-en/hi selection.

- [ ] **Step 1: Failing test**

`backend/tests/test_language.py`:
```python
import pytest

from app.language import normalize_language


def test_selection_wins_on_plain_english():
    assert normalize_language("en", "What is PMFBY eligibility?") == "en"


def test_devanagari_overrides_en_selection():
    assert normalize_language("en", "पीएमएफबीवाई में कैसे आवेदन करें") == "hi"


def test_latin_script_hindi_stays_hi():
    # Latin-script Hindi must NOT flip just because of script
    assert normalize_language("hi", "meri fasal ka insurance kaise milega") == "hi"


def test_invalid_selection_rejected():
    with pytest.raises(ValueError):
        normalize_language("fr", "bonjour")
```

- [ ] **Step 2: Run → FAIL** (`app.language` missing).

- [ ] **Step 3: Implement**

`backend/app/language.py`:
```python
_DEVANAGARI = set(range(0x0900, 0x097F))
_HI_STOPWORDS = {"ka", "ki", "ke", "kaise", "kya", "hai", "mein", "meri", "mera",
                 "kaise", "kitna", "nahi", "aur"}
_EN_STOPWORDS = {"the", "is", "at", "which", "on", "in", "how", "what", "do",
                 "does", "of", "and", "to", "for"}


def _script_ratios(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ord(c) in _DEVANAGARI) / len(letters)


def _latin_stopword_bias(text: str) -> float:
    words = {w.lower() for w in text.split()}
    return len(words & _HI_STOPWORDS) - len(words & _EN_STOPWORDS)


def normalize_language(selected: str, text: str) -> str:
    if selected not in ("en", "hi"):
        raise ValueError(f"unsupported language: {selected}")
    dev_ratio = _script_ratios(text)
    if selected == "en" and dev_ratio >= 0.7:
        return "hi"  # high-confidence mismatch only
    if selected == "hi" and dev_ratio <= 0.05 and _latin_stopword_bias(text) > 0:
        return "en"
    return selected
```

- [ ] **Step 4: Run → 4 PASS.**
- [ ] **Step 5: Commit** — `git add backend/app/language.py backend/tests/test_language.py; git commit -m "feat: explicit-first language normalization"`

---

### Task 7: Hybrid domain classification

**Files:**
- Create: `backend/app/domains.py`, `backend/data/domain_anchors.json`, `backend/data/keyword_rules.json`
- Test: `backend/tests/test_domains.py`

**Interfaces:**
- Consumes: `EmbeddingProvider.embed_texts`.
- Produces: `load_anchor_store(provider) -> AnchorStore` (embedded once, cached); `AnchorStore.classify(text: str, query_embedding: list[float]) -> tuple[str, float]` returning `(domain|'out_of_scope', score)`; domains fixed: `cooperative|pacs|schemes|pmfby|agriculture|finlit|grievance|out_of_scope`. Keyword rules short-circuit BEFORE embeddings.

- [ ] **Step 1: Data files**

`backend/data/keyword_rules.json`:
```json
{
  "pmfby": ["pmfby", "crop insurance", "fasal bima", "pradhan mantri fasal"],
  "pacs": ["pacs", "primary agricultural credit society", "primary agriculture credit"],
  "cooperative": ["cooperative society", "co-operative society", "byelaws", "by-laws", "sahkari"],
  "schemes": ["scheme", "yojana", "yojna", "ministry of cooperation"],
  "finlit": ["rbi", "bank account", "pmjdy", "jan dhan", "financial literacy", "deposit insurance"],
  "agriculture": ["sowing", "harvest", "mandi", "msp", "fertilizer", "seed variety"],
  "grievance": ["complaint", "grievance", "shikayat", "report corruption"]
}
```

`backend/data/domain_anchors.json` (10 per domain; abbreviated here — author writes all 7×10):
```json
{
  "pmfby": ["How do I enrol my crops under PMFBY crop insurance?",
            "What risks does PMFBY cover for standing crops?",
            "PMFBY claim process after crop loss",
            "Who is eligible for PMFBY coverage?",
            "PMFBY premium rates for food crops",
            "Where do farmers register for fasal bima yojana?",
            "PMFBY cut-off dates for enrollment",
            "Crop insurance claim rejection remedies under PMFBY",
            "Difference between PMFBY and restructured weather scheme",
            "Documents needed for PMFBY claim"],
  "cooperative": ["How is a cooperative society registered?",
                  "Amendment of cooperative society byelaws",
                  "Rights and duties of cooperative society members",
                  "Role of the registrar of cooperative societies",
                  "Cooperative society audit requirements",
                  "Dispute resolution inside a cooperative society",
                  "Model byelaws for PACS adaptation",
                  "Winding up of a cooperative society",
                  "Voting rights in a cooperative society",
                  "State cooperative rules versus central law"],
  "pacs": ["What does a PACS do?", "PACS loan services for farmers",
           "Membership of a primary agricultural credit society",
           "PACS role in the short-term credit structure",
           "How PACS interact with district cooperative banks",
           "Digitization of PACS operations",
           "PACS and storage infrastructure",
           "Dividend policy of a PACS",
           "Election of the PACS managing committee",
           "PACS convergence with government schemes"],
  "schemes": ["Ministry of Cooperation schemes list",
              "National cooperation policy schemes",
              "Scheme benefits for cooperative societies",
              "Computerization of PACS scheme",
              "National dairy development plan support",
              "Fisheries and livestock cooperation schemes",
              "Scheme eligibility for small cooperatives",
              "How to apply for cooperation ministry funding",
              "New multipurpose PACS services",
              "Sector-specific cooperative schemes"],
  "agriculture": ["Best sowing window for kharif crops",
                  "Soil health card usage",
                  "Mandi prices and market fees",
                  "Fertilizer application guidance",
                  "Integrated pest management basics",
                  "Cold storage and warehousing for produce",
                  "Minimum support price procurement process",
                  "Drip irrigation subsidies",
                  "Organic farming certification steps",
                  "Post-harvest loss reduction practices"],
  "finlit": ["How does deposit insurance protect my bank savings?",
             "Steps to open a Jan Dhan account",
             "Recognizing and avoiding digital payment fraud",
             "Understanding interest rates on deposits",
             "Safe use of UPI payments",
             "Reading a bank statement",
             "Benefits of RuPay cards",
             "Loan borrowing warnings and debt traps",
             "Pension schemes for rural workers",
             "Complaint channels for banking fraud"],
  "grievance": ["How do I file a complaint about a cooperative society?",
                "Escalating an unresolved grievance",
                "What details should a grievance contain?",
                "Tracking status of a filed complaint",
                "Consumer forum versus cooperative dispute routes",
                "Reporting mismanagement by committee members",
                "Whom to contact about delayed insurance claims",
                "Ombudsman complaint for banking issues",
                "Grievance redressal timelines",
                "Evidence to attach with a complaint"]
}
```

- [ ] **Step 2: Failing test**

`backend/tests/test_domains.py`:
```python
import numpy as np

from app.domains import AnchorStore, load_rules


class FakeProvider:
    """Deterministic fake: identical text -> identical vector; different -> orthogonal-ish."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        out = []
        for i, t in enumerate(texts):
            v = [0.0] * 16
            v[i % 16] = 1.0
            out.append(v)
        return out


RULES = {"pmfby": ["pmfby"], "finlit": ["jan dhan"]}
ANCHORS = {"pmfby": ["crop insurance claim"], "finlit": ["open a bank account"]}


def test_keyword_rule_short_circuits():
    store = AnchorStore(rules=RULES, anchors=ANCHORS, vectors=np.zeros((2, 16)))
    assert store.classify("tell me about PMFBY", [0.0] * 16)[0] == "pmfby"


def test_anchor_match_by_cosine():
    q = [1.0] + [0.0] * 15  # matches FakeProvider vector index 0
    store = AnchorStore(rules={}, anchors={"finlit": ["open a bank account", "second"]},
                        vectors=np.array([[1.0] + [0.0] * 15, [0.0, 1.0] + [0.0] * 14]))
    domain, score = store.classify("bank account help", q)
    assert domain == "finlit" and score > 0.9


def test_out_of_scope_floor():
    store = AnchorStore(rules={}, anchors={"finlit": ["open a bank account"]},
                        vectors=np.zeros((1, 16)))
    assert store.classify("who won the cricket match", [0.0] * 16)[0] == "out_of_scope"
```

- [ ] **Step 3: Run → FAIL**, then implement

`backend/app/domains.py`:
```python
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
DOMAIN_FLOOR = 0.45  # provisional; calibrated in Phase 4 alongside retrieval gates


def load_rules(path: Path = DATA_DIR / "keyword_rules.json") -> dict[str, list[str]]:
    return json.loads(path.read_text(encoding="utf-8"))


class AnchorStore:
    def __init__(self, rules: dict[str, list[str]], anchors: dict[str, list[str]],
                 vectors: np.ndarray):
        self.rules = rules
        self.domains = sorted(anchors)
        self.vectors = vectors / max(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)

    def classify(self, text: str, query_embedding: list[float]) -> tuple[str, float]:
        lowered = text.lower()
        for domain, keywords in self.rules.items():
            if any(kw in lowered for kw in keywords):
                return domain, 1.0
        q = np.asarray(query_embedding, dtype=float)
        q = q / max(np.linalg.norm(q), 1e-9)
        scores = self.vectors @ q
        best = int(scores.argmax())
        if scores[best] < DOMAIN_FLOOR:
            return "out_of_scope", float(scores[best])
        return self.domains[best], float(scores[best])


@lru_cache(maxsize=1)
def load_anchor_store(embed_texts, rules_path: Path = DATA_DIR / "keyword_rules.json",
                      anchors_path: Path = DATA_DIR / "domain_anchors.json") -> AnchorStore:
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    flat = [a for items in anchors.values() for a in items]
    vectors = np.asarray(embed_texts(flat), dtype=float)
    return AnchorStore(load_rules(rules_path), anchors, vectors)


def get_anchor_store() -> AnchorStore:
    """Process-wide singleton. The route MUST call THIS, never
    `load_anchor_store(provider.embed_texts)` directly — a fresh bound method
    per request would defeat the cache and re-embed all ~70 anchors on every
    `/chat` (P0-1). First call costs ~70 embedding requests; the FastAPI
    startup hook (Task 11) warms it so no user request ever pays for it."""
    from app.providers.embeddings import get_embedding_provider
    return load_anchor_store(get_embedding_provider().embed_texts)
```

- [ ] **Step 4: Run → 3 PASS; lint.**
- [ ] **Step 5: Commit** — `git commit -m "feat: hybrid keyword+anchor domain classifier"`

---

### Task 8: Seed corpus + ingestion pipeline

**Files:**
- Create: `corpus/seeds/*.md` (12 files), `ingestion/__init__.py`, `ingestion/chunker.py`, `ingestion/loader.py`, `ingestion/ingest.py`, `.env` loading helper reuse
- Test: `ingestion/tests/test_chunker.py`

**Interfaces:**
- Produces:
  - Chunk markdown format: YAML frontmatter (`source_id,title,organization,domain,jurisdiction,state,url,effective_date,verified_date,page,section`) + body text. `loader.parse_chunk_file(path) -> dict` with keys matching those names + `content`.
  - `chunk_markdown(body: str, target_tokens=600, min_tokens=400, max_tokens=800, overlap_tokens=80) -> list[str]` (heading-aware; token≈word count for MVP determinism).
  - `ingest.seeds_to_supabase(paths, embed_texts, supabase_client) -> int` (rows inserted). Idempotent: deletes `documents` rows with matching `source_id` first (cascade clears chunks).

- [ ] **Step 1: Author 12 seed files (anti-fabrication rule)**

For EACH of these sources, open the live URL and copy 2–4 factual sentences VERBATIM (public-domain government material; cite the URL in frontmatter). Do NOT write facts from memory:
`https://pmfby.gov.in/faq` ×4 (eligibility, coverage, premium, claim), `https://www.cooperation.gov.in/en/model-byelaws` ×2, `https://cooperation.gov.in/en/about-primary-agriculture-cooperative-credit-societies-pacs` ×2, `https://cooperation.gov.in/index.php/en/pacs-related-schemes` ×1, `https://rbi.org.in/` (financial literacy page) ×1, `https://www.pmjdy.gov.in/literacy` ×2.

**Every file gets a UNIQUE `source_id`** — several files may share one URL, and ingestion deletes by `source_id`, so duplicate IDs would silently overwrite earlier documents (P0-2):

| File | source_id |
|---|---|
| `pmfby_eligibility.md` | `pmfby_faq_eligibility` |
| `pmfby_coverage.md` | `pmfby_faq_coverage` |
| `pmfby_premium.md` | `pmfby_faq_premium` |
| `pmfby_claims.md` | `pmfby_faq_claims` |
| `bylaws_governance.md` | `model_pacs_bylaws_governance` |
| `bylaws_membership.md` | `model_pacs_bylaws_membership` |
| `pacs_role.md` | `pacs_overview_role` |
| `pacs_credit.md` | `pacs_overview_credit` |
| `pacs_schemes_computerization.md` | `pacs_schemes_computerization` |
| `rbi_finlit_awareness.md` | `rbi_finlit_awareness` |
| `pmjdy_account.md` | `pmjdy_finlit_account` |
| `pmjdy_rupay.md` | `pmjdy_finlit_rupay` |

Template `corpus/seeds/pmfby_eligibility.md`:
```markdown
---
source_id: pmfby_faq_eligibility
title: "PMFBY FAQ — Eligibility"
organization: PMFBY
domain: pmfby
jurisdiction: central
state: null
url: https://pmfby.gov.in/faq
effective_date: null
verified_date: 2026-08-26
page: 1
section: "Eligibility"
---
<PASTE VERBATIM TEXT HERE>
```
(Repeat per file with correct frontmatter from the table; `page` = visible page/section number where found, else 0.)

- [ ] **Step 2: Failing chunker test**

`ingestion/tests/test_chunker.py`:
```python
from ingestion.chunker import chunk_markdown


def test_short_body_single_chunk():
    assert chunk_markdown("one two three") == ["one two three"]


def test_heading_split_then_length_split():
    body = "# A\n" + ("word " * 500) + "\n# B\n" + ("term " * 500)
    chunks = chunk_markdown(body, target_tokens=300, min_tokens=100,
                            max_tokens=350, overlap_tokens=40)
    assert len(chunks) >= 3
    assert all(len(c.split()) <= 350 for c in chunks)
```

- [ ] **Step 3: Implement**

`ingestion/chunker.py`:
```python
import re

_HEADING = re.compile(r"^#{1,6}\s", re.M)


def _split_long(text: str, target: int, max_tokens: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text] if text.strip() else []
    out, step = [], max(target - overlap, 1)
    for start in range(0, len(words), step):
        piece = words[start:start + target]
        if len(piece) < overlap and out:
            break
        out.append(" ".join(piece))
    return out


def chunk_markdown(body: str, target_tokens: int = 600, min_tokens: int = 400,
                   max_tokens: int = 800, overlap_tokens: int = 80) -> list[str]:
    sections, current = [], []
    for line in body.splitlines():
        if _HEADING.match(line) and current:
            sections.append("\n".join(current)); current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))

    chunks: list[str] = []
    for section in sections:
        words = section.split()
        if len(words) < min_tokens and chunks and len(chunks[-1].split()) + len(words) <= max_tokens:
            chunks[-1] = chunks[-1] + "\n" + section  # merge undersized tail
        else:
            chunks.extend(_split_long(section, target_tokens, max_tokens, overlap_tokens))
    return [c.strip() for c in chunks if c.strip()]
```

`ingestion/loader.py`:
```python
import yaml


def parse_chunk_file(path) -> dict:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---\n", 2)
    meta = yaml.safe_load(parts[1]) or {}
    return {**meta, "content": parts[2].strip()}
```

`ingestion/ingest.py`:
```python
from pathlib import Path

from ingestion.chunker import chunk_markdown
from ingestion.loader import parse_chunk_file

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"


def seeds_to_supabase(paths: list[Path], embed_texts, supabase) -> int:
    total = 0
    for path in paths:
        rec = parse_chunk_file(path)
        supabase.table("documents").delete().eq("source_id", rec["source_id"]).execute()
        doc = supabase.table("documents").insert({
            "source_id": rec["source_id"], "title": rec["title"],
            "organization": rec["organization"], "domain": rec["domain"],
            "jurisdiction": rec["jurisdiction"], "state": rec.get("state"),
            "document_type": "seed", "source_url": rec["url"],
            "effective_date": rec.get("effective_date"),
            "verified_date": rec["verified_date"],
        }).execute().data[0]
        # Same pipeline as the real corpus (P1-6): parse → chunk → embed → insert.
        pieces = chunk_markdown(rec["content"])
        vectors = embed_texts(pieces)
        for piece, vector in zip(pieces, vectors):
            supabase.table("chunks").insert({
                "document_id": doc["id"], "page": rec.get("page", 0),
                "section": rec.get("section", ""), "content": piece,
                "embedding": vector})
        total += 1
    return total


if __name__ == "__main__":
    from supabase import create_client

    from app.config import get_settings
    from app.providers.embeddings import get_embedding_provider

    s = get_settings()
    paths = sorted(SEEDS_DIR.glob("*.md"))
    count = seeds_to_supabase(paths, get_embedding_provider().embed_texts,
                              create_client(s.supabase_url, s.supabase_service_key))
    print(f"ingested {count} seed documents")
```

- [ ] **Step 4: Chunker tests pass** — `cd ingestion; python -m pytest tests/test_chunker.py -v` → PASS. (Add `ingestion/pyproject.toml` copying backend's pytest/ruff config if imports demand packaging.)
- [ ] **Step 5: Human runs real ingestion** — `cd backend; python ../ingestion/ingest.py` (needs `.env` + applied schema). Expected: `ingested 12 seed documents`.
- [ ] **Step 6: Commit** — `git commit -m "feat: seed corpus + ingestion pipeline"`

---

### Task 9: Retrieval service + evidence gate

**Files:**
- Create: `backend/app/retrieval.py`
- Test: `backend/tests/test_retrieval.py`

**Interfaces:**
- Consumes: Supabase RPC `match_chunks` (already returns `domain`, `jurisdiction`, `state` columns); config thresholds.
- Produces:
  - `RetrievedChunk` (pydantic): `chunk_id: str, title: str, page: int, section: str, content: str, similarity: float, source_url: str, domain: str, jurisdiction: str, state: str | None`
  - `retrieve(supabase, query_embedding: list[float], domain: str, state: str | None, k: int = 6) -> list[RetrievedChunk]`
  - `GateResult(abstained: bool, reason: str | None, confidence: float)`
  - `evidence_gate(chunks, expected_domain=None, expected_state=None) -> GateResult` — implements spec §2.4 fully: top1 ≥0.35, ≥2 chunks ≥0.30, PLUS defense-in-depth checks that every chunk's `domain == expected_domain` (when given) and each chunk is jurisdiction-valid (`jurisdiction == "central"` or `state == expected_state`) even though the SQL prefilter should guarantee it.

- [ ] **Step 1: Failing tests**

`backend/tests/test_retrieval.py`:
```python
from app.retrieval import GateResult, RetrievedChunk, evidence_gate


def mk(sim: float, domain: str = "pmfby", jurisdiction: str = "central",
       state: str | None = None) -> RetrievedChunk:
    return RetrievedChunk(chunk_id="c1", title="T", page=1, section="S",
                          content="C", similarity=sim, source_url="https://x",
                          domain=domain, jurisdiction=jurisdiction, state=state)


def test_gate_pass():
    g = evidence_gate([mk(0.62), mk(0.41), mk(0.33)], expected_domain="pmfby")
    assert not g.abstained and g.confidence == round(0.6 * 0.62 + 0.4 * (2 / 3), 2)


def test_gate_abstains_low_top1():
    assert evidence_gate([mk(0.31)]).abstained


def test_gate_abstains_insufficient_secondary():
    assert evidence_gate([mk(0.80), mk(0.28)]).abstained


def test_gate_empty():
    g = evidence_gate([])
    assert g.abstained and g.confidence == 0.0
    assert isinstance(g, GateResult)


def test_gate_rejects_wrong_domain_chunk():
    g = evidence_gate([mk(0.9), mk(0.7, domain="finlit")],
                      expected_domain="pmfby")
    assert g.abstained


def test_gate_rejects_wrong_state_document():
    g = evidence_gate([mk(0.9), mk(0.7, jurisdiction="state", state="maharashtra")],
                      expected_domain="pmfby", expected_state="gujarat")
    assert g.abstained
```

- [ ] **Step 2: Run → FAIL. Implement**

`backend/app/retrieval.py`:
```python
from pydantic import BaseModel

from app.config import (MIN_CHUNKS_ABOVE_SECONDARY, SECONDARY_THRESHOLD,
                        TOP1_THRESHOLD)


class RetrievedChunk(BaseModel):
    chunk_id: str
    title: str
    page: int
    section: str
    content: str
    similarity: float
    source_url: str
    domain: str
    jurisdiction: str
    state: str | None = None


class GateResult(BaseModel):
    abstained: bool
    reason: str | None = None
    confidence: float = 0.0


def retrieve(supabase, query_embedding: list[float], domain: str,
             state: str | None, k: int = 6) -> list[RetrievedChunk]:
    rows = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding, "match_domain": domain,
        "match_state": state, "match_count": k}).execute().data or []
    return [RetrievedChunk(chunk_id=str(r["chunk_id"]), title=r["title"],
                           page=r["page"], section=r["section"],
                           content=r["content"], similarity=r["similarity"],
                           source_url=r["source_url"], domain=r["domain"],
                           jurisdiction=r["jurisdiction"],
                           state=r.get("state")) for r in rows]


def _jurisdiction_ok(chunk: RetrievedChunk, expected_state: str | None) -> bool:
    return chunk.jurisdiction == "central" or chunk.state == expected_state


def evidence_gate(chunks: list[RetrievedChunk], expected_domain: str | None = None,
                  expected_state: str | None = None) -> GateResult:
    if not chunks:
        return GateResult(abstained=True, reason="no_chunks")
    # Defense-in-depth (spec §2.4): SQL prefilter should guarantee these;
    # verify anyway so a bad filter can never surface cross-domain evidence.
    if expected_domain is not None and any(c.domain != expected_domain for c in chunks):
        return GateResult(abstained=True, reason="domain_mismatch_in_retrieval")
    if not all(_jurisdiction_ok(c, expected_state) for c in chunks):
        return GateResult(abstained=True, reason="jurisdiction_mismatch_in_retrieval")
    sims = sorted((c.similarity for c in chunks), reverse=True)
    if sims[0] < TOP1_THRESHOLD:
        return GateResult(abstained=True, reason="below_top1_threshold")
    strong = sum(1 for s in sims if s >= SECONDARY_THRESHOLD)
    if strong < MIN_CHUNKS_ABOVE_SECONDARY:
        return GateResult(abstained=True, reason="insufficient_supporting_chunks")
    confidence = round(min(0.6 * sims[0] + 0.4 * (strong / len(sims)), 1.0), 2)
    return GateResult(abstained=False, reason=None, confidence=confidence)
```

- [ ] **Step 3: Run → 6 PASS; lint; commit** — `git commit -m "feat: filtered retrieval + evidence gate with jurisdiction defense-in-depth"`

---

### Task 10: Grounded generation + citation verification

**Files:**
- Create: `backend/app/generation.py`
- Test: `backend/tests/test_generation.py`

**Interfaces:**
- Consumes: `LLMProvider`, `list[RetrievedChunk]`.
- Produces: `SYSTEM_PROMPT` constant; `build_user_prompt(question, chunks) -> str`; `verify_citations(answer: str, chunk_ids: list[str]) -> list[str]` (extracts `[chunk:<id-prefix>]`, returns VALID ids in order); `generate_answer(llm, question, chunks) -> str` raising `CitationError` when the answer cites nothing valid. Contract: LLM must tag every factual sentence with `[chunk:<first 8 chars of chunk_id>]`.

- [ ] **Step 1: Failing tests**

`backend/tests/test_generation.py`:
```python
import pytest

from app.generation import verify_citations

IDS = ["aaaaaaaa-1111-2222-3333-444444444444", "bbbbbbbb-5555-6666-7777-888888888888"]


def test_valid_citation_extracted():
    assert verify_citations("X [chunk:aaaaaaaa].", IDS) == ["aaaaaaaa-1111-2222-3333-444444444444"]


def test_invalid_citation_dropped_and_empty_raises_path():
    assert verify_citations("Y [chunk:zzzzzzzz].", IDS) == []


def test_mixed_citations_keep_only_valid_in_order():
    out = verify_citations("A [chunk:bbbbbbbb] B [chunk:aaaaaaaa]", IDS)
    assert out == IDS[::-1][:1] + IDS[:1] if False else out == [
        "bbbbbbbb-5555-6666-7777-888888888888",
        "aaaaaaaa-1111-2222-3333-444444444444"]
```

- [ ] **Step 2: Implement**

`backend/app/generation.py`:
```python
import re

from app.retrieval import RetrievedChunk

_CITE = re.compile(r"\[chunk:([0-9a-f]{8})\]")


class CitationError(Exception): ...


SYSTEM_PROMPT = (
    "You answer ONLY from the numbered context chunks. Every factual sentence "
    "must end with a marker [chunk:ID] where ID is the first 8 hex characters "
    "of the chunk id you used. Never add outside knowledge. If the chunks do "
    "not contain the answer, reply exactly: INSUFFICIENT_EVIDENCE."
)


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    ctx = "\n\n".join(
        f"[chunk:{c.chunk_id[:8]}] ({c.title} — §{c.section} — p.{c.page})\n{c.content}"
        for c in chunks)
    return f"Question: {question}\n\nContext:\n{ctx}"


def verify_citations(answer: str, chunk_ids: list[str]) -> list[str]:
    valid: list[str] = []
    for prefix in _CITE.findall(answer):
        for cid in chunk_ids:
            if cid.startswith(prefix) and cid not in valid:
                valid.append(cid)
    return valid


def generate_answer(llm, question: str, chunks: list[RetrievedChunk]) -> str:
    answer = llm.generate(SYSTEM_PROMPT, build_user_prompt(question, chunks))
    if answer.strip() == "INSUFFICIENT_EVIDENCE":
        raise CitationError("model declined: insufficient evidence")
    if not verify_citations(answer, [c.chunk_id for c in chunks]):
        raise CitationError("answer carried no valid citations")
    return answer
```

- [ ] **Step 3: Run → 3 PASS; lint; commit** — `git commit -m "feat: grounded generation with hard citation verification"`

---

### Task 11: `/chat` orchestration route + sessions

**Files:**
- Create: `backend/app/routes/chat.py`, `backend/app/session_store.py`, modify `backend/app/main.py` (include router)
- Test: `backend/tests/test_chat_route.py`

**Interfaces:**
- Consumes: Tasks 4, 6, 7, 9, 10 outputs.
- Produces: `POST /chat` implementing the frozen contract. Request: `{"question": str, "session_id": uuid-str, "language": "en"|"hi", "state": str|null}`. Response: exactly `{answer, language, domain, confidence, citations:[{title,page,url}], abstained, follow_up_question}`. All failures (both LLMs down, Supabase down) → HTTP 200 with `abstained: true`, safe message, `follow_up_question: null`. Session upsert touches `updated_at/expires_at` and lazily purges expired rows.

- [ ] **Step 1: Failing test (mocks at provider boundary, real logic)**

`backend/tests/conftest.py` (autouse — env, classifier stub at the route boundary, session stubs; Supabase itself goes over real httpx so `respx` can mock its URLs):
```python
import pytest

from app.config import get_settings


class _FakeStore:
    @staticmethod
    def classify(_text: str, _embedding: list[float]) -> tuple[str, float]:
        return "pmfby", 1.0  # classifier is unit-tested in Task 7


@pytest.fixture(autouse=True)
def env_and_route_stubs(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setenv("SUPABASE_URL", "http://testsupa")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test")
    get_settings.cache_clear()
    import app.routes.chat as chat_route
    monkeypatch.setattr(chat_route, "get_anchor_store", lambda: _FakeStore())
    monkeypatch.setattr(chat_route, "get_state", lambda _sid: None)
    monkeypatch.setattr(chat_route, "touch_session", lambda *_a, **_k: None)
    yield
    get_settings.cache_clear()
```

`backend/tests/test_chat_route.py`:
```python
import uuid

import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PAYLOAD = {"question": "Who is eligible under PMFBY?", "session_id": str(uuid.uuid4()),
           "language": "en", "state": None}
EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
RPC_PATH = "/rest/v1/rpc/match_chunks"


@respx.mock
def test_answered_with_valid_citation(respx_mock):
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.5] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[{
            "chunk_id": "aaaaaaaa-1111-2222-3333-444444444444",
            "title": "PMFBY FAQ", "page": 1, "section": "Eligibility",
            "content": "Eligible farmers are covered.", "similarity": 0.72,
            "source_url": "https://pmfby.gov.in/faq", "domain": "pmfby",
            "jurisdiction": "central", "state": None}, {
            "chunk_id": "bbbbbbbb-5555-6666-7777-888888888888",
            "title": "PMFBY Guidelines", "page": 4, "section": "Coverage",
            "content": "Coverage extends to notified crops.", "similarity": 0.51,
            "source_url": "https://pmfby.gov.in/guidelines", "domain": "pmfby",
            "jurisdiction": "central", "state": None}]))
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {
            "content": "Farmers growing notified crops are eligible [chunk:aaaaaaaa]."}}]}))
    r = client.post("/chat", json=PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["abstained"] is False and body["confidence"] > 0
    assert body["citations"][0]["title"] == "PMFBY FAQ"
    assert set(body) == {"answer", "language", "domain", "confidence",
                         "citations", "abstained", "follow_up_question"}


@respx.mock
def test_abstains_when_retrieval_below_threshold(respx_mock):
    respx_mock.post(EMBED_URL).mock(return_value=httpx.Response(200, json={
        "embedding": {"values": [0.01] * 768}}))
    respx_mock.post(httpx.URL("http://testsupa" + RPC_PATH)).mock(
        return_value=httpx.Response(200, json=[]))
    r = client.post("/chat", json=PAYLOAD)
    body = r.json()
    assert body["abstained"] is True and body["citations"] == []
    assert body["answer"]  # safe message present
```

Note: the route's happy path above exercises real evidence-gate logic (two chunks ≥0.30 → pass) with only the domain classifier and session store stubbed at the route boundary — both have dedicated tests or arrive in Phase 2/3.

- [ ] **Step 2: Implement `db.py` wrapper + session store + route**

`backend/app/db.py`:
```python
from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


@lru_cache
def get_supabase() -> Client:
    s = get_settings()
    return create_client(s.supabase_url, s.supabase_service_key)
```

`backend/app/session_store.py`:
```python
from datetime import datetime, timedelta, timezone

from app.db import get_supabase


def get_state(session_id: str) -> str | None:
    """Session is authoritative for jurisdiction (spec §2.3, P1-7): a request
    with state=null continues in the session's previously selected state."""
    rows = (get_supabase().table("sessions").select("state")
            .eq("session_id", session_id).limit(1).execute().data or [])
    if not rows:
        return None
    return (rows[0].get("state") or {}).get("selected_state")


def touch_session(session_id: str, selected_state: str | None, language: str) -> None:
    sb = get_supabase()
    sb.rpc("purge_expired_sessions", {}).execute()
    expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    sb.table("sessions").upsert({
        "session_id": session_id,
        "state": {"selected_state": selected_state, "language": language},
        "expires_at": expires,
    }, on_conflict="session_id").execute()
```

Create and apply `backend/migrations/0002_purge.sql` (Supabase SQL editor):
```sql
create or replace function purge_expired_sessions() returns void
language sql as $$ delete from sessions where expires_at < now(); $$;
```

`backend/app/routes/chat.py`:
```python
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.domains import get_anchor_store
from app.db import get_supabase
from app.generation import (SYSTEM_PROMPT, CitationError, build_user_prompt,
                            verify_citations)
from app.language import normalize_language
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.embeddings import get_embedding_provider
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.retrieval import RetrievedChunk, evidence_gate, retrieve
from app.session_store import get_state, touch_session

router = APIRouter()

ABSTAIN_TEXT = {
    "en": "I could not find this in official sources, so I won't guess. "
          "Please try rephrasing or ask about cooperative rules, PACS, schemes, "
          "PMFBY, agriculture, or financial literacy.",
    "hi": "मुझे आधिकारिक स्रोतों में इसका उत्तर नहीं मिला, इसलिए मैं अनुमान नहीं लगाऊँगा। "
          "कृपया प्रश्न दूसरे शब्दों में पूछें या सहकारिता, पीएएससीएस, योजनाओं, "
          "पीएमएफबीवाई, कृषि या वित्तीय साक्षरता के बारे में पूछें।",
}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi"]
    state: str | None = None


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    settings = get_settings()
    lang = normalize_language(req.language, req.question)
    try:
        provider = get_embedding_provider()          # cached singleton (P0-1)
        embedding = provider.embed_texts([req.question])[0]
        domain, _score = get_anchor_store().classify(req.question, embedding)
        # Session is authoritative for jurisdiction (P1-7): explicit request
        # state updates it; a null state continues the session's prior state.
        resolved_state = req.state or get_state(req.session_id)
        touch_session(req.session_id, resolved_state, lang)
        if domain == "out_of_scope":
            return _abstain(lang, "out_of_scope")
        chunks = retrieve(get_supabase(), embedding, domain, resolved_state)
        gate = evidence_gate(chunks, expected_domain=domain,
                             expected_state=resolved_state)
        if gate.abstained:
            return _abstain(lang, gate.reason)
        prompt = build_user_prompt(req.question, chunks)
        answer = grounded_answer(GroqLLMProvider(settings),
                                 GeminiLLMProvider(settings), SYSTEM_PROMPT, prompt)
        citations = _citations_from(answer, chunks)
        return {"answer": answer, "language": lang, "domain": domain,
                "confidence": gate.confidence, "citations": citations,
                "abstained": False, "follow_up_question": None}
    except (CitationError, AllProvidersFailedError):
        return _abstain(lang, "provider_or_citation_failure")
    except Exception:
        raise HTTPException(status_code=503, detail="service unavailable") from None


def _abstain(lang: str, _reason: str | None) -> dict:
    return {"answer": ABSTAIN_TEXT[lang], "language": lang, "domain": "unknown",
            "confidence": 0.0, "citations": [], "abstained": True,
            "follow_up_question": None}


def _citations_from(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    ids = verify_citations(answer, [c.chunk_id for c in chunks])
    by_id = {c.chunk_id: c for c in chunks}
    return [{"title": by_id[i].title, "page": by_id[i].page,
             "url": by_id[i].source_url} for i in ids]
```

Wire into `main.py`: `from app.routes.chat import router as chat_router; app.include_router(chat_router)`.

- [ ] **Step 3: Route tests pass** — `pytest tests/test_chat_route.py -v` → 2 PASS.
- [ ] **Step 4: Live seed validation (human/AI with .env)** — run uvicorn, curl `/chat` with a seed question; expect cited answer; with "who won the cricket match" expect `abstained:true`.
- [ ] **Step 5: Commit** — `git commit -m "feat: /chat orchestration with sessions, abstention, citations"`

---

### Task 12: Minimal chat frontend

**Files:**
- Create: `frontend/src/app/page.tsx`, `frontend/src/components/ChatWindow.tsx`, `frontend/src/components/EvidenceBand.tsx`, `frontend/src/lib/api.ts`, `frontend/src/lib/band.ts`
- Test: `frontend/src/lib/band.test.ts`

**Interfaces:**
- Consumes: `POST /chat` frozen contract.
- Produces: `evidenceBand(confidence: number): "strong" | "moderate" | "weak"` (≥0.65 strong, ≥0.45 moderate, else weak); `sendChat(payload)` typed wrapper. UI shows language toggle EN/हिंदी, message list, citation chips linking `url`, abstention card, evidence band label — NEVER a bare percentage.

- [ ] **Step 1: Band unit test first**

`frontend/src/lib/band.test.ts`:
```typescript
import { evidenceBand } from "./band";

test("bands map correctly", () => {
  expect(evidenceBand(0.8)).toBe("strong");
  expect(evidenceBand(0.5)).toBe("moderate");
  expect(evidenceBand(0.2)).toBe("weak");
});
```
Run: `cd frontend; npm i -D vitest; npx vitest run src/lib/band.test.ts` → FAIL (module missing).

- [ ] **Step 2: Implement lib + components**

`frontend/src/lib/band.ts`:
```typescript
export type Band = "strong" | "moderate" | "weak";
export function evidenceBand(confidence: number): Band {
  if (confidence >= 0.65) return "strong";
  if (confidence >= 0.45) return "moderate";
  return "weak";
}
export const BAND_LABEL: Record<Band, string> = {
  strong: "Strong source support",
  moderate: "Moderate source support",
  weak: "Weak source support",
};
```

`frontend/src/lib/api.ts`:
```typescript
export interface ChatResponse {
  answer: string; language: "en" | "hi"; domain: string; confidence: number;
  citations: { title: string; page: number; url: string }[];
  abstained: boolean; follow_up_question: string | null;
}

export async function sendChat(payload: {
  question: string; session_id: string; language: "en" | "hi"; state: string | null;
}): Promise<ChatResponse> {
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"}/chat`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
```

`frontend/src/components/EvidenceBand.tsx`:
```tsx
import { BAND_LABEL, evidenceBand } from "@/lib/band";

export function EvidenceBand({ confidence }: { confidence: number }) {
  const band = evidenceBand(confidence);
  const color = band === "strong" ? "bg-green-100 text-green-800"
    : band === "moderate" ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800";
  return <span className={`rounded px-2 py-0.5 text-xs font-medium ${color}`}>
    {BAND_LABEL[band]}</span>;
}
```

`frontend/src/components/ChatWindow.tsx`:
```tsx
"use client";
import { useState } from "react";
import { sendChat, ChatResponse } from "@/lib/api";
import { EvidenceBand } from "./EvidenceBand";

type Msg = { role: "user" | "assistant"; text?: string; resp?: ChatResponse };

export function ChatWindow() {
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [busy, setBusy] = useState(false);

  async function ask() {
    const q = input.trim();
    if (!q || busy) return;
    setInput(""); setBusy(true);
    setMsgs(m => [...m, { role: "user", text: q }]);
    try {
      const resp = await sendChat({ question: q, session_id: sessionId, language: lang, state: null });
      setMsgs(m => [...m, { role: "assistant", resp }]);
    } catch {
      setMsgs(m => [...m, { role: "assistant",
        resp: { answer: lang === "hi" ? "सेवा अभी उपलब्ध नहीं है।" : "Service unavailable right now.",
                language: lang, domain: "unknown", confidence: 0, citations: [],
                abstained: true, follow_up_question: null } }]);
    } finally { setBusy(false); }
  }

  return (
    <div className="mx-auto flex h-dvh max-w-2xl flex-col p-4">
      <div className="mb-2 flex gap-2">
        {(["en", "hi"] as const).map(l => (
          <button key={l} onClick={() => setLang(l)}
            className={`rounded border px-3 py-1 ${lang === l ? "bg-black text-white" : ""}`}>
            {l === "en" ? "English" : "हिंदी"}
          </button>
        ))}
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto">
        {msgs.map((m, i) => m.role === "user"
          ? <div key={i} className="ml-auto w-fit max-w-[85%] rounded-xl bg-blue-600 px-4 py-2 text-white">{m.text}</div>
          : <div key={i} className="max-w-[90%] space-y-2">
              <div className={`rounded-xl border px-4 py-2 ${m.resp!.abstained ? "border-gray-300 bg-gray-50" : ""}`}>
                {m.resp!.answer}
              </div>
              {!m.resp!.abstained && <>
                <EvidenceBand confidence={m.resp!.confidence} />
                {m.resp!.citations.map((c, j) => (
                  <a key={j} href={c.url} target="_blank" rel="noopener noreferrer"
                     className="block truncate text-xs text-blue-700 underline">
                    {c.title}{c.page ? ` — p.${c.page}` : ""}
                  </a>))}
              </>}
            </div>)}
      </div>
      <div className="mt-2 flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && ask()}
          placeholder={lang === "hi" ? "अपना प्रश्न लिखें…" : "Type your question…"}
          className="flex-1 rounded border px-3 py-2" />
        <button onClick={ask} disabled={busy} className="rounded bg-black px-4 py-2 text-white disabled:opacity-50">
          {busy ? "…" : "➤"}
        </button>
      </div>
    </div>
  );
}
```

`frontend/src/app/page.tsx`:
```tsx
import { ChatWindow } from "@/components/ChatWindow";

export default function Home() {
  return <ChatWindow />;
}
```

- [ ] **Step 3: Vitest passes; `npm run build` clean.**
- [ ] **Step 4: Manual smoke** — backend + frontend up; seed question → cited answer + band; gibberish → gray abstain card.
- [ ] **Step 5: Commit** — `git commit -m "feat: minimal chat pwa with citations and evidence bands"`

---

### Task 13: Phase 1 exit-gate validation script

**Files:**
- Create: `eval/skeleton_check.py`

**Interfaces:**
- Produces: `python eval/skeleton_check.py <base_url>` → exit 0 iff 5 seeded questions return `abstained:false` WITH ≥1 citation whose URL appears in `corpus/seeds/`, and 2 out-of-corpus questions return `abstained:true` with empty citations. Writes `eval/reports/skeleton.json`.

- [ ] **Step 1: Implement**
```python
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"
CASES_ANSWER = [
    ("What are the eligibility criteria under PMFBY?", "en"),
    ("How are PMFBY claims made after crop loss?", "en"),
    ("What do the model byelaws for PACS cover?", "en"),
    ("What services does a PACS provide to farmers?", "en"),
    ("PMFBY ke antargat paatrata kya hai?", "hi"),
]
CASES_ABSTAIN = [("Who won yesterday's cricket match?", "en"),
                 ("Recommend me a good movie", "hi")]


def api_base() -> str:
    return sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "API_BASE", "http://localhost:8000")


def load_seed_urls() -> set[str]:
    """Every citation must point at a URL present in the seed manifest
    (P0-4): the gate verifies sources, not just shapes."""
    urls = set()
    for path in SEEDS_DIR.glob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^url:\s*(\S+)", line)
            if m:
                urls.add(m.group(1))
                break
    return urls


def chat(base: str, q: str, lang: str) -> dict:
    req = urllib.request.Request(
        f"{base}/chat", method="POST",
        data=json.dumps({"question": q, "session_id": str(time.time_ns()),
                         "language": lang, "state": None}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main() -> int:
    base = api_base()
    allowed = load_seed_urls()
    results = {"passed": True, "api": base, "answers": [], "abstains": []}
    for q, lang in CASES_ANSWER:
        body = chat(base, q, lang)
        ok = (not body["abstained"]
              and len(body["citations"]) >= 1
              and all(c["url"] in allowed for c in body["citations"]))
        results["passed"] &= ok
        results["answers"].append({"q": q, "ok": ok, "citations": body["citations"]})
    for q, lang in CASES_ABSTAIN:
        body = chat(base, q, lang)
        ok = body["abstained"] and body["citations"] == []
        results["passed"] &= ok
        results["abstains"].append({"q": q, "ok": ok})
    os.makedirs("eval/reports", exist_ok=True)
    with open("eval/reports/skeleton.json", "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run against live local stack** — `python eval/skeleton_check.py http://localhost:8000` (or set `API_BASE`). Expected: exit 0, report shows 5/5 answered with citations whose URLs all come from `corpus/seeds/`, and 2/2 abstained.
- [ ] **Step 3: Fix any failure by returning to the owning task (chunk quality, threshold, classifier floor) — rerun until green.**
- [ ] **Step 4: Update PROJECT_STATUS.md (component table, provider table, next action) and commit** — `git commit -m "test: phase-1 skeleton exit-gate validator"`

## Self-Review Notes

- Spec coverage: §2.1→Task 6; §2.2→Tasks 7+2(guard); §2.3→Tasks 3+11(sessions, TTL purge, session-authoritative state); §2.4→Task 9(gate incl. domain/jurisdiction defense-in-depth)+Task 12(bands); §2.5→Task 8(chunker used by ingestion; page+section on every chunk); Phase 0 gates→Tasks 1–5; Phase 1 gates→Tasks 6–13. Voice stubs→Task 4. Render stub→Tasks 1(render.yaml)+5(deploy).
- Post-review patch round (user review): **P0** anchor-store caching (`get_embedding_provider`/`get_anchor_store` singletons + lifespan warmup so no request pays the ~70-call cost), unique per-file seed `source_id`s (delete-by-id can no longer silently drop documents), skeleton_check reads `argv[1]`, gate validates citation URLs against seed manifest, `RetrievedChunk` carries domain/jurisdiction/state and the gate enforces them. **P1** ingestion runs the same chunker as real corpus, session state resolves null-state requests, model IDs are env config with code defaults.
- Placeholder scan: none — the "PASTE VERBATIM TEXT HERE" marker in seed files is an anti-fabrication execution instruction (fetch live text from each URL, never write facts from memory), not a plan TODO.
- Type consistency: `RetrievedChunk` fields match across Tasks 9/10/11 and the RPC column list; `GateResult.reason` consumed by `_abstain`; `AnchorStore.classify(text, embedding)` consistent Tasks 7↔11; `embed_texts` contract consistent Tasks 3/7/8/11; frontend `ChatResponse` mirrors the frozen API exactly; Task 11 fixtures supply the columns `retrieve()` maps.
- Known simplification: `generate_answer` (Task 10) is exercised by unit tests but the route composes `grounded_answer` + `_citations_from` directly — same guarantees, one less indirection; Task 13's exit gate validates composed behavior live. Session-store DB behavior is stubbed at the route boundary in Phase 1 tests and exercised for real when grievance slot-filling lands in Phase 2.
