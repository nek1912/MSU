# Sahakarita — Multilingual Cooperative Governance & Legal Assistance Chatbot

Evidence-grounded, multilingual (English + Hindi + Gujarati + Marathi + Bengali + Tamil)
citizen-assistance PWA for cooperative governance, legal guidance, schemes, PMFBY,
financial literacy, and grievance redressal.

> **Core principle:** the LLM is **never** the source of truth. Every factual
> answer must be grounded in retrieved official documents with verifiable
> citations. If retrieval confidence is low or no supporting chunk exists, the
> system **abstains** — it never guesses.

---

## What It Does

- Answers questions from official government sources with verifiable citations
- **6 languages**: English, Hindi, Gujarati, Marathi, Bengali, Tamil
- Routes queries across 7 domains: cooperative, PACS, schemes, PMFBY, agriculture,
  financial literacy, grievance
- Applies jurisdiction filtering (central + selected state — currently Gujarat)
- **Hybrid retrieval**: dense vector search (pgvector) + lexical search (RRF fusion)
- Abstains when evidence is insufficient — never guesses
- Prototype grievance workflow with follow-up questions and status lookup
  (`is_official_submission: false` — no real government integration)
- Voice input/output via Sarvam AI (Indic language support)
- Responsive PWA (desktop + mobile)

---

## Architecture

```
Next.js PWA ──▶ FastAPI API ──▶ Domain Router (keyword + anchor + LLM)
                                       │
                                       ├─▶ Hybrid retrieval (dense pgvector + lexical)
                                       │       └─▶ optional reranker (wired, OFF by default)
                                       ├─▶ Evidence gate (abstention if no citation)
                                       ├─▶ Citation verifier
                                       └─▶ Grounded LLM (Groq primary, Gemini fallback)
                                                └─▶ Answer / abstain + citations + confidence
                                       ▼
                                  Supabase Postgres + pgvector (HNSW)
```

The evidence gate runs **before** the LLM: the model can never upgrade a
low-confidence or uncited result into an answer.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16 + React 19 + Tailwind CSS 4, PWA |
| Backend | FastAPI (Python 3.11+) |
| Database | Supabase Postgres + pgvector (HNSW cosine index) |
| Embeddings | Jina Embeddings v3 (`jina-embeddings-v3`), 768d |
| LLM | Groq (Llama 3.3 70B) primary, Gemini 2.5 Flash fallback |
| Reranker | Gemini 2.5 Flash Lite (wired, disabled by default) |
| Voice | Sarvam AI (STT + TTS) primary, Azure fallback, text-only final |
| Document parsing | MinerU `content_list_v2.json` |
| Eval | Supabase-backed retrieval eval, pytest |

---

## Project Structure

```
backend/
  app/
    main.py              FastAPI entrypoint
    routes/chat.py       /chat pipeline (retrieve → rerank → evidence gate → LLM)
    domains.py           domain classifier (keyword rules + anchor store + LLM fallback)
    hybrid_retrieval.py  dense (match_chunks) + lexical fusion
    retrieval.py         legacy dense retrieval wrapper
    evidence_gate.py     abstention / confidence scoring
    citation_verifier.py citation→chunk→document→page resolution
    contracts.py         frozen API response contract
    generation.py        grounded answer generation
    llm_fallback.py      Groq → Gemini fallback chain
    config.py            all thresholds and settings
    providers/           llm, embeddings, reranker, voice adapters (timeout + fallback)
    rag/                 web-grounded RAG pipeline (Tavily + Gemini reranker)
    services/            voice_service.py (Sarvam → Azure → text-only)
    web_rag/             tavily_client.py (dual-key rotation)
    data/                keyword_rules.json, domain_anchors.json
  seed_parser.py         MinerU content_list_v2.json → canonical chunk JSONL
  ingest_seed.py         clear + Jina-v3 embed + insert into Supabase
  migrations/            0001_init.sql, 0005_rag_contracts.sql, combined_migration.sql
  tests/                 pytest (417 tests — domain routing, retrieval, evidence gate, citations)

frontend/                Next.js PWA (chat, grievance, citations UI, 6 languages)

corpus/
  seeds/
    json_files/          MinerU content_list_v2.json per source (input)
    chunks_jsonl/        canonical parsed chunks (page, heading_path, clause, tables)
    *.pdf                source documents
    *.md                 human-readable derived artifacts (NOT authoritative)
  manifests/mvp_sources.yaml

eval/
  gold_cases.yaml        golden evaluation cases (245; 40 answerable)
  run_retrieval_eval.py  Recall@1/3/5/10/20 + MRR vs live Supabase
  validate_retrieval.py  page/citation/metadata/taxonomy checks
  populate_gold_chunk_ids.py  localizes relevant chunk per query (retriever-anchored)

docs/                    foundation / repair / e2e reports
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase project (free tier) with pgvector
- API keys: Supabase, Jina (embeddings), Groq, Gemini, Sarvam AI

### Backend

```bash
cd backend
cp ../.env.example .env      # fill in API keys
pip install -e .
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

See `.env.example`. Key variables:

```
SUPABASE_URL=             # Supabase project URL
SUPABASE_SERVICE_KEY=     # Supabase service role key
JINA_API_KEY=             # Jina embeddings
GROQ_API_KEY=             # Groq LLM
GEMINI_API_KEY=           # Gemini fallback LLM
SARVAM_API_KEY=           # Sarvam AI voice (STT + TTS)
TAVILY_API_KEY=           # Tavily web search (dynamic RAG)
RERANKER_ENABLED=false    # reranker is wired but OFF (see PROJECT_STATUS)
```

### Database Setup

Apply the migrations in `backend/migrations/` to your Supabase project
(e.g. via Supabase SQL editor, or `supabase db push`):

1. `0001_init.sql` — tables (`documents`, `chunks`, `sessions`, `grievances`,
   `feedback`) + **HNSW cosine index** on `chunks.embedding` + `match_chunks` RPC
   (domain + jurisdiction filtered, cosine distance).
2. `0005_rag_contracts.sql` / `combined_migration.sql` — response-contract and
   citation-supporting objects.

### Ingestion (corpus build)

Place each source's MinerU export at `corpus/seeds/json_files/<source>_content_list_v2.json`,
then:

```bash
python backend/seed_parser.py     # content_list_v2.json → chunks_jsonl/*.jsonl
python backend/ingest_seed.py     # embed (Jina v3) + insert into Supabase
```

Current frozen corpus: **5 documents, 2,188 embedded chunks (768d Jina v3)**.

---

## Supported Languages

| Language | Code | Status |
|---|---|---|
| English | `en` | Full support |
| Hindi | `hi` | Full support |
| Gujarati | `gu` | Full support |
| Marathi | `mr` | Full support |
| Bengali | `bn` | Full support |
| Tamil | `ta` | Full support |

All UI strings translated. Backend responds in the same language as the question.

---

## RAG Pipelines

### Static RAG (Retrieval-Augmented Generation)
- Hybrid retrieval: dense vector search (pgvector) + lexical search (RRF fusion)
- Domain + jurisdiction filtering before candidate ranking
- Evidence gate with configurable thresholds
- Citation verification against retrieved chunks
- Abstains when evidence insufficient

### Dynamic RAG (Web-Grounded)
- Tavily web search for current information
- Gemini reranker for semantic scoring
- Answer generation with `llama-3.3-70b-versatile`
- Language-matching: responds in same language as question

---

## Safety

- API keys are server-side only — never in frontend code (`NEXT_PUBLIC_*`).
- Every citation maps to a chunk actually retrieved in that request.
- Low retrieval confidence / no valid citation forces abstention.
- Jurisdiction + effective-date metadata on all legal/cooperative answers.
- Grievances are prototype-only (`is_official_submission: false`) — no real CPGRAMS.
- Structured logs without PII or secrets.

---

## License

Built for a hackathon. See repository for license details.
