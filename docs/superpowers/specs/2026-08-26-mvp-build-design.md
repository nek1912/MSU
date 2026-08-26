# MVP Build Design — Multilingual Cooperative Governance & Legal Assistance Chatbot

**Date:** 2026-08-26
**Status:** Approved design (all four chunks approved in brainstorming session)
**Supersedes operationally:** work-plan.md day numbering (demoted to background reference — see DECISIONS.md entry plan below)

## 1. Context

The frozen docs (CLAUDE.md, PRD.md, architecture.md, design.md, AGENT.md) define
*what* to build. This spec defines *how and in what order*, closing every gap that
would otherwise stall implementation. It was produced by reviewing all nine
planning files against five questions:

| Decision | Value |
|---|---|
| State coverage | **Gujarat** (Gujarat Co-operative Societies Act 1961, Rules 1965, Commissioner of Cooperation portal) |
| Execution model | Hybrid — tasks written owner-style but independently AI-executable |
| Timeline | MVP-first sprint, phase-gated; no calendar commitments |
| Provider accounts | Groq/Gemini/Supabase keys required at Phase 0 (needed for local dev); Vercel/Render hosting deferred to Phase 5; Bhashini registration submitted early (approval lead time unverified) |
| Build strategy | Walking skeleton first, then thicken; deployment last |

**Gujarat language note:** Gujarati-speaking state with English-language official
texts. Hindi flagship demos run via Bhashini translation over English sources —
works, but the alignment rationale must be logged. Gujarati becomes the natural
post-MVP second language (replacing "Marathi" in work-plan.md's backlog).

## 2. Gap-closing technical decisions

These resolve every "or" / blank left in the frozen docs. Each gets a DECISIONS.md
entry when implemented.

### 2.1 Language detection — script/token heuristics (not IndicLID)
Binary hi/en decision: Devanagari Unicode-range ratio ≥ ~30% → `hi`; else `en`;
mixed-script edge cases resolved by Hindi-vs-English stopword counting.
Rationale: two-language problem does not justify self-hosted PyTorch on Render
Free's memory budget. **Deviation from design.md ("IndicLID or provider-native").**

### 2.2 Domain classification — embedding anchors
~10 anchor phrases per domain embedded once with `gemini-embedding-001` at ingest
time, cached. Per turn: one embedding call, cosine vs anchors, max-similarity
below floor → `out_of_scope`. Keyword rules as offline fallback when Gemini is
unavailable. No extra infrastructure beyond what retrieval already uses.

### 2.3 Jurisdiction & session ownership — server-side sessions table
`sessions(session_id UUID PK (client-generated), state JSONB, updated_at)`.
Frontend sends `session_id` + selected state (`null | "gujarat"`) per `/chat`
call. Grievance slot-filling progress lives server-side in session state.
Stateless request handlers survive Render restarts without cleanup logic.

### 2.4 Evidence threshold & confidence — starting values, eval-tuned
- Abstain if `top1_cosine < 0.35` OR fewer than 2 chunks above `0.30`.
- Confidence = `0.6·top1 + 0.4·(chunks_above_0.30 / k)`, clamped [0,1].
- Values live in a single config module; tuned by Phase 4 golden-set runs.

### 2.5 Chunking — structure-aware
Docling → Markdown → split on heading boundaries, then token-length split
(target ~600 tokens, hard range 400–800) with 80-token overlap. Page numbers
carried from Docling page breaks onto every chunk. Identical pipeline for seed
and real corpus so seed→real swap costs nothing.

## 3. Repo layout

```
├── docs/                  # existing planning docs (unchanged locations)
│   └── superpowers/specs/ # this spec + implementation plans
├── backend/               # FastAPI: routes/, services/, providers/, adapters/, tests/
├── ingestion/             # offline batch: Docling parse → chunk → embed → upsert
├── corpus/seeds/          # seed markdown chunks (Phase 1) → real extractions (Phase 3)
├── frontend/              # Next.js PWA
├── eval/                  # golden cases + runner (JSON report output)
├── sources.yaml           # manifest; Gujarat entries verified & added in Phase 0, ingested in Phase 3
└── .github/workflows/     # CI: lint + tests only until Phase 5
```

Ingestion stays out of `backend/` because Render's filesystem is ephemeral and
ingestion is an offline batch job — this structurally prevents anyone wiring it
into the request path. `eval/` is separate because it targets both FAISS-local
and Supabase retrieval.

## 4. Phase plan

Phases are gate-gated, not calendar-gated. A phase starts when the previous
gate passes. Falling back one phase on a discovered blocker is normal and gets
logged in PROJECT_STATUS.md — it is not a plan failure.

| Phase | Contents | Exit gate |
|---|---|---|
| **0 — Foundations** | Groq/Gemini/Supabase accounts + keys in `.env` (never committed); Bhashini registration submitted; git init + monorepo scaffold; `.env.example`; CI workflow (ruff + pytest + vitest); Gujarat sources verified & added to `sources.yaml`; Supabase migrations (`documents`, `chunks vector(768)` + HNSW, `grievances`, `sessions`, `feedback`) | Schema applied; smoke call succeeds against Groq, Gemini, Supabase |
| **1 — Walking skeleton** | 10–15 hand-written seed chunks from real `sources.yaml` URLs → ingest script → `/chat` full local path (lang heuristic → domain anchors → jurisdiction filter → pgvector top-k → evidence gate → Groq grounded generation → citation verification → abstain path) → minimal text chat UI with citations/confidence/abstention display | 5 seed questions answered with valid citations; 2 unsupported questions correctly abstain — all local |
| **2 — Grievance** | State machine NEW→NEEDS_INFORMATION→CLASSIFIED→CREATED→IN_PROGRESS→RESOLVED; LLM slot extraction; missing-field follow-ups; `DEMO-<DOMAIN>-<#####>` references; status lookup; form/status UI with prototype warning (`is_official_submission: false` always) | Full create→follow-up→reference→lookup green in pytest + manual UI run |
| **3 — Real corpus + Gujarat** | Docling ingestion of all `sources.yaml` documents + Gujarat Act/Rules; complete jurisdiction metadata; state/domain filters enforced pre-vector-search; PRD's 8–15 schemes coverage | Corpus auditable from `sources.yaml`; Gujarat-specific question returns state-filtered citations |
| **4 — Eval & hardening — MVP GATE** | ~140 golden cases (20 per domain); threshold calibration; Groq→Gemini fallback + timeout/429 handling; structured logging; error-state UX; Playwright smoke suite | Text-mode PRD Definition-of-Done met locally. Voice may start **only** after this gate |
| **5 — Deployment** | Render backend + Vercel frontend; CORS allow-list; env config; cold-start/Supabase-pause playbook; live smoke suite | Deployed PWA meets PRD DoD end-to-end |
| **6 — Voice (Tier 2)** | Bhashini STT/TTS adapter → Groq Whisper STT fallback → text-only fallback; `/voice/transcribe`, `/voice/speak`; recording UI; provider health states | Hindi voice question → cited Hindi answer (flagship demo #1) |

### Cut order under pressure
1. Phase 6 (voice) entirely
2. Phase 3 breadth — shrink scheme count toward PRD minimum of 8
3. Phase 4 eval size — floor 10 cases per domain

**Never cut:** abstention logic, citation verification, prototype-only grievance
labeling, jurisdiction filtering.

## 5. Testing strategy

Maps to CLAUDE.md's mandated test areas: domain routing, jurisdiction filtering,
retrieval, citation validity, abstention, grievance workflow, provider fallback,
API failure handling.

- **Backend:** pytest + pytest-asyncio; providers mocked with respx; no bare excepts; Pydantic models on every request/response body.
- **Frontend:** vitest + React Testing Library — citation display, confidence bar, abstention state, grievance form validation.
- **E2E:** Playwright smoke (chat happy path, abstain path, grievance path) built during Phase 4.
- **Eval:** `eval/run_eval.py` emits JSON quality report (domain accuracy, abstention correctness, citation validity, groundedness spot checks). Eval-time only, never a runtime dependency.
- **CI:** ruff + pytest + vitest on every push; deploy jobs added at Phase 5.

## 6. Error handling

Every external call (Groq, Gemini, Supabase, later Bhashini) goes through an
adapter with explicit timeout and typed failures. Fallback chains per
architecture.md §11: LLM Groq→Gemini→safe response; STT Bhashini→Whisper→text-only.
Both LLMs failing returns a contract-valid response (`abstained: true`, safe
message, `follow_up_question: null`) — never a raw 500 to end users. Frontend
supports every error state listed in design.md.

## 7. Security & privacy

- API keys server-side only; never in frontend code, never `NEXT_PUBLIC_*`, never committed.
- CORS allow-list: localhost + eventual Vercel origin.
- Structured logs without keys, tokens, or full grievance PII.
- Synthetic data only for grievances during demo/testing (PRD safety req. 7).
- Grievances always labeled prototype; `is_official_submission` hardcoded `false`.

## 8. Deviations to log in DECISIONS.md (at implementation time)

1. **work-plan.md demoted to background reference** — operational sequencing lives here; day numbers are not commitments.
2. **Language detection: heuristics replace IndicLID/provider-native** (§2.1) — updates design.md.
3. **Deployment deferred to Phase 5** — supersedes work-plan Day 1 "create Vercel/Render projects" timing; accounts still created before demos need them.
4. **Gujarat selected as state** — fills sources.yaml placeholder; language-alignment rationale recorded.
5. **Domain classification pinned to anchor embeddings** (§2.2) — resolves design.md's "or".

## 9. Non-goals honored

Everything on PRD.md's non-goals list stays out. Voice is Tier 2 gated behind
the Phase 4 MVP gate. No native apps, WhatsApp, blockchain, custom training,
self-hosted GPU, multi-agent frameworks, complex auth, analytics dashboards,
real CPGRAMS integration, or nationwide legal coverage.
