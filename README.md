# Multilingual Cooperative Governance & Legal Assistance Chatbot

Evidence-grounded, multilingual (English + Hindi) citizen-assistance PWA for
cooperative governance, legal guidance, schemes, PMFBY, financial literacy, and
grievance redressal.

> **Core principle:** the LLM is **never** the source of truth. Every factual
> answer must be grounded in retrieved official documents with verifiable
> citations. If retrieval confidence is low or no supporting chunk exists, the
> system **abstains** — it never guesses.

---

## What It Does

- Answers questions from official government sources with verifiable citations
- Supports English + Hindi text chat (Hindi voice is Tier 2 / not yet enabled)
- Routes queries across 7 domains: cooperative, PACS, schemes, PMFBY, agriculture,
  financial literacy, grievance
- Applies jurisdiction filtering (central + selected state — currently Gujarat)
- Abstains when evidence is insufficient — never guesses
- Prototype grievance workflow with follow-up questions and status lookup
  (`is_official_submission: false` — no real government integration)
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
| Frontend | Next.js + React + Tailwind CSS, PWA |
| Backend | FastAPI (Python 3.11+) on Render Free |
| Database | Supabase Postgres + pgvector (HNSW cosine index) |
| Embeddings | **Jina Embeddings v3** (`jina-embeddings-v3`), 768d — `retrieval.passage` / `retrieval.query` task types |
| LLM | Groq (Llama 3.3 70B) primary, Gemini 2.5 Flash fallback |
| Reranker | Jina `jina-reranker-v2-base-multilingual` (wired, disabled by default) |
| Voice | Bhashini STT/TTS → Sarvam/Azure → Groq Whisper → text-only (Tier 2) |
| Document parsing | **MinerU** `content_list_v2.json` (real page numbers + tables) |
| Eval | Supabase-backed retrieval eval, pytest, vitest |

> **Note on stack drift:** the frozen `CLAUDE.md` still names Docling + Gemini
> embeddings. The working pipeline was changed during the RAG rebuild (logged in
> `PROJECT_STATUS.md`): parsing is MinerU `content_list_v2.json` and embeddings are
> Jina v3. Update `CLAUDE.md` if this becomes permanent.

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
    providers/           llm, embeddings, reranker, voice adapters (timeout + fallback)
    data/                keyword_rules.json, domain_anchors.json
  seed_parser.py         MinerU content_list_v2.json → canonical chunk JSONL
  ingest_seed.py         clear + Jina-v3 embed + insert into Supabase
  migrations/            0001_init.sql, 0005_rag_contracts.sql, combined_migration.sql
  tests/                 pytest (domain routing, retrieval, evidence gate, citations)

frontend/                Next.js PWA (chat, grievance, citations UI)

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
  reranker_smoke.py      reranker path smoke test
  run_gate2.py           aggregated Gate-2 report
  gate2_config.yaml      frozen targets

docs/                    foundation / repair / e2e reports
tests/                   cross-cutting tests (domain taxonomy, etc.)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase project (free tier) with pgvector
- API keys: Supabase, Jina (embeddings + reranker), Groq, Gemini

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
JINA_API_KEY=            # Jina embeddings + reranker
GROQ_API_KEY=            # Groq LLM
GEMINI_API_KEY=          # Gemini fallback LLM
RERANKER_ENABLED=false   # reranker is wired but OFF (see PROJECT_STATUS)
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
Do not modify chunks mid-evaluation — re-run `populate_gold_chunk_ids.py` after any re-ingest.

---

## Evaluation

All eval scripts read `backend/.env` for the live Supabase + Jina connection.

```bash
# Rebuild gold chunk mapping (localizes relevant chunk per query)
python populate_gold_chunk_ids.py

# Retrieval quality (Recall@1/3/5/10/20 + MRR, domain acc, contamination)
python eval/run_retrieval_eval.py --output eval/retrieval_report.json

# Page / citation / metadata / taxonomy checks
python eval/validate_retrieval.py

# Reranker path smoke test (requires RERANKER_ENABLED=true)
python eval/reranker_smoke.py

# Aggregated Gate-2 report
python eval/run_gate2.py
```

### Latest retrieval baseline (frozen 2,188-chunk corpus, 2026-08-29)

Measured over 245 gold cases (40 answerable: 18 pacs_governance + 22 pmfby).
Queries embedded with `retrieval.query` (mirrors `/chat`). Gold is
**retriever-anchored** (weak supervision) — treat as a regression baseline, not a
final target.

| Metric | Value | Frozen target |
|---|---|---|
| Recall@1 | **0.850** | 0.40 |
| Recall@3 | **0.950** | 0.60 |
| Recall@5 | **0.975** | 0.80 |
| Recall@10 | 0.975 | — |
| MRR | **0.904** | 0.50 |
| Domain accuracy | 0.950 | 0.85 |
| Jurisdiction contamination | 0 | 0 |

Versus the old 226-chunk baseline (Recall@5 = 0.625): a large improvement from the
MinerU + Jina-v3 strategy. The reranker is **left OFF** because on this gold it
lowers final top-6 Recall@1 (0.85 → 0.50); revisit after curating real gold.

> See `PROJECT_STATUS.md` for the full, current status, known caveats, and the
> next-action list (manual gold curation, confidence calibration, multilingual, voice).

---

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

Chat response fields: `answer, language, domain, confidence, citations[], abstained,
follow_up_question`.

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
