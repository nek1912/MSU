# System Architecture

## 1. Overview

Evidence-grounded, multilingual citizen-assistance platform. Official documents
→ extraction → chunking + metadata → embeddings → Supabase pgvector →
domain/jurisdiction-filtered retrieval → evidence validation → grounded LLM
generation → citation verification → answer or abstention.

**The LLM is not the source of truth.** It only rephrases retrieved chunks into
an answer and is not trusted to supply facts on its own.

## 2. High-level diagram

```
                        USER
                          |
                          v
             +------------------------+
             |     Next.js PWA        |
             |  chat / voice /        |
             |  grievance / status    |
             +-----------+------------+
                          |
                        HTTPS
                          |
                          v
             +------------------------+
             |      FastAPI API       |
             +-----------+------------+
                          |
          +---------------+----------------+
          |                |                |
          v                v                v
  +----------------+ +---------------+ +----------------+
  | Language Layer  | | Domain Router | | Grievance      |
  | Bhashini STT/MT | | cooperative   | | Workflow       |
  | /TTS            | | pacs/schemes  | | classify+slot- |
  | Groq Whisper     | | pmfby/agri    | | fill+ticket    |
  | fallback         | | finlit/       | |                |
  +--------+---------+ | grievance     | +-------+--------+
           |            +-------+-------+         |
           |                    |                 |
           |                    v                 |
           |         +--------------------+        |
           |         | Retrieval Service  |        |
           |         +---------+----------+        |
           |                   |                    |
           |                   v                    |
           |        +----------------------+        |
           +------->| Supabase Postgres    |<-------+
                     | + pgvector (HNSW)    |
                     | documents / chunks   |
                     | grievances / feedback|
                     +----------+-----------+
                                |
                                v
                     +--------------------+
                     | LLM Provider       |
                     | Groq (primary)     |
                     | Gemini (fallback)  |
                     +---------+----------+
                                |
                                v
                     Answer + citation
                     + confidence + abstention
```

## 3. Request flow (text)

```
question → language detection → domain classification → jurisdiction
resolution → hybrid retrieval (dense vector + lexical, RRF fusion,
domain + state filter applied before candidate ranking) → [reranker if
enabled, currently OFF] → evidence gate v2 (abstain if insufficient) →
grounded LLM generation → citation verification (every [chunk:id] must map
to a retrieved chunk) → structured response
```

Out-of-scope queries return a controlled scope response (no factual LLM
answer). The frontend `/api/chat` proxy has NO static fallback — a backend
failure returns 502/503, never an ungrounded answer.

## 4. Domain taxonomy

`pacs_governance | pacs_computerization | pmfby | financial_inclusion | schemes | agriculture | grievance | out_of_scope`

## 5. Jurisdiction

Legal and cooperative answers must carry `jurisdiction, state, effective_date,
verified_date`. Hierarchy where applicable:

```
Central policy/law → State Act → State Rules → State notification
→ PACS-specific by-law
```

Do not treat the Model PACS Byelaws as universal law — the Ministry itself says
they must be adapted per state Cooperative Societies Act/Rules.

## 6. Components

### 6.1 Frontend
Next.js + React + Tailwind, responsive PWA, hosted on Vercel Hobby (Render
Static Site as fallback). Features: text chat, EN/HI selector, voice recording +
playback, citation display, confidence display, abstention UI, grievance form,
grievance status lookup.

### 6.2 Backend
FastAPI (Python) on Render Free. Routes per the frozen API contract in PRD.md.
Responsibilities: routing, orchestration, retrieval, citation validation, LLM
integration, language-provider integration, grievance workflow, error handling,
fallbacks.

### 6.3 Language layer
Primary: Bhashini (Hindi STT, Hindi↔English translation, Hindi TTS). Fallback:
Groq Whisper for STT. Final fallback: text-only mode. This is a Tier 2 (post-MVP)
component — the MVP ships text-only.

### 6.4 Retrieval layer
Supabase Postgres + pgvector, HNSW index (cosine). Retrieval is **hybrid**:
dense vector search (`match_chunks` RPC, 768-d Jina embeddings) fused with
Postgres lexical search via weighted Reciprocal Rank Fusion (RRF). Domain and
jurisdiction/state filters are applied *inside* both candidate queries before
ranking to prevent cross-domain matches (contamination = 0). A Jina reranker
is wired but **disabled** (`RERANKER_ENABLED=false`) until a curated eval shows
it helps.

### 6.5 LLM layer
Provider abstraction — application logic must not depend directly on one
provider:
```
LLMProvider
  ├── GroqProvider   (primary)
  └── GeminiProvider (fallback)
```

### 6.6 Database schema

```
documents
---------
id, title, organization, jurisdiction, state, domain, document_type,
url, effective_date, verified_date, document_hash

chunks
------
id, document_id, page, section, content, embedding vector(768), metadata

grievances
----------
id, reference, status, category, location, language, payload,
created_at, updated_at

feedback
--------
id, session_id, message_id, rating, note, created_at
```

## 7. Data flow: chat
```
question → language detection → domain classification → jurisdiction
resolution → domain+state filter → top-k retrieval → evidence threshold
→ LLM → citation verification → answer / abstention
```

## 8. Data flow: voice (Tier 2)
```
audio → Bhashini STT → text → normal chat pipeline → answer → Bhashini TTS → audio
```
Fallback: `Bhashini STT (failure) → Groq Whisper (failure) → text input`

## 9. Data flow: grievance
```
user description → classification → entity extraction → missing-field
detection → follow-up questions → prototype reference creation → status lookup
```
Grievance submission always contains `is_official_submission: false`.

## 10. Citation flow

Retrieved chunks carry a stable application `chunk_id` (e.g.
`operational_guidelines_pmfby_00012`) plus the internal DB `id`, `document_id`,
`source_file`, `page_start`, `page_end`, `section`, `subsection`, `clause`, and
`text`. The LLM returns `[chunk:<id>]` markers. Backend validates: `citation
chunk exists AND was retrieved this turn` (stable `chunk_id` resolves
deterministically to the row → document → source page). Invalid/fabricated
citation → `ABSTAIN`. Confidence is an internal diagnostic, not a stated
probability.

## 11. Fallback chains

```
STT:  Bhashini → Groq Whisper → text-only
LLM:  Groq → Gemini → safe "unavailable" response
```

## 12. Non-functional requirements

No personal GPU. Free-tier/cloud-only. External providers require explicit
timeout handling. Render cold starts expected. Free-tier 429/rate limits
expected. Supabase may pause after inactivity — check and reactivate before
demos. Minimal PII. No secrets in frontend or source control.
