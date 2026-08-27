# Multilingual Cooperative Governance & Legal Assistance Chatbot

Evidence-grounded, multilingual (English + Hindi) citizen-assistance PWA for
cooperative governance, legal guidance, schemes, PMFBY, financial literacy, and
grievance redressal.

## What It Does

- Answers questions from official government sources with verifiable citations
- Supports English + Hindi text chat (Hindi voice via Bhashini — Tier 2)
- Routes queries across 7 domains: cooperative, PACS, schemes, PMFBY, agriculture, financial literacy, grievance
- Applies jurisdiction filtering (central + Gujarat state-specific)
- Abstains when evidence is insufficient — never guesses
- Prototype grievance workflow with follow-up questions and status lookup
- Responsive PWA (desktop + mobile)

## Architecture

```
Next.js PWA → FastAPI API → Domain Router → Supabase pgvector (RAG)
                                           → LLM (Groq primary, Gemini fallback)
                                           → Citation verification → Answer or abstain
```

**Key principle:** The LLM is never the source of truth. Every factual answer must
be grounded in retrieved official documents with verifiable citations.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 + React 19 + Tailwind CSS, PWA |
| Backend | FastAPI (Python 3.11+) on Render Free |
| Database | Supabase Postgres + pgvector (HNSW index) |
| Embeddings | Gemini `gemini-embedding-2` (768 dims) |
| LLM | Groq (Llama 3.3 70B) primary, Gemini 2.5 Flash fallback |
| Voice | Bhashini STT/TTS → Groq Whisper fallback → text-only |
| Document parsing | Docling |
| Eval | FAISS (local), pytest, vitest |

## Project Structure

```
backend/          FastAPI app (routes, services, providers, adapters)
frontend/         Next.js PWA (chat, grievance, citations UI)
ingestion/        Offline batch: Docling → chunk → embed → Supabase
corpus/seeds/     Seed markdown files (→ real extractions after ingestion)
eval/             Golden cases, evaluation scripts, Gate 2 reports
sources.yaml      Source manifest (verified official documents)
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase project (free tier)
- API keys: Gemini, Groq (optional: Bhashini)

### Setup

```bash
# Clone
git clone https://github.com/nek1912/MSU.git
cd MSU

# Backend
cd backend
cp ../.env.example .env  # Fill in API keys
pip install -e ../ingestion
pip install -e .
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

### Environment Variables

See `.env.example` for the full list. Key variables:

```
SUPABASE_URL=         # Your Supabase project URL
SUPABASE_SERVICE_KEY= # Supabase service role key
GEMINI_API_KEY=       # Google Gemini API key
GROQ_API_KEY=         # Groq API key
```

### Database Setup

Run the migrations in `backend/migrations/` against your Supabase project:

1. `0001_init.sql` — Creates tables (documents, chunks, sessions, grievances, feedback) + HNSW index + `match_chunks` RPC
2. `0002_purge.sql` — Creates `purge_expired_sessions()` RPC

### Ingestion

```bash
cd ingestion
python -m ingestion.ingest
```

## Evaluation

```bash
# Corpus quality check
python eval/corpus_check.py

# Domain classifier evaluation
python eval/run_domain_eval.py

# Corpus snapshot
python eval/corpus_version.py

# Retrieval evaluation (requires live Supabase)
python eval/run_retrieval_eval.py --live

# Jurisdiction contamination
python eval/run_jurisdiction_eval.py --live

# Unsupported-query safety (requires running backend)
python eval/run_unsupported_eval.py

# Citation provenance (requires running backend)
python eval/run_citation_eval.py

# Gate 2 report (requires all above)
python eval/run_gate2.py
```

## Current Status

See `PROJECT_STATUS.md` for the live project status. Phase 0-1 (foundation + walking skeleton)
is complete with 80 tests passing. Phase 2A (corpus & retrieval quality) implementation is
complete — awaiting official document provision for ingestion.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/chat` | POST | Text chat with RAG, citations, abstention |
| `/voice/transcribe` | POST | Audio → text (Tier 2) |
| `/voice/speak` | POST | Text → audio (Tier 2) |
| `/grievances` | POST | Create grievance |
| `/grievances/{reference}` | GET | Lookup grievance status |
| `/sources/{id}` | GET | Source metadata |
| `/health` | GET | Health check |
| `/health/providers` | GET | Provider status |

## Safety

- API keys are server-side only — never in frontend code
- Every citation maps to a retrieved chunk from that request
- Low retrieval confidence forces abstention
- Jurisdiction metadata on all legal/cooperative answers
- Grievances are prototype-only (`is_official_submission: false`)
- Structured logs without PII

## License

This project is built for a hackathon. See repository for license details.
