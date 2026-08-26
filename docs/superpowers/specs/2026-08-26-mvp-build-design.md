# MVP Build Design — Multilingual Cooperative Governance & Legal Assistance Chatbot

**Date:** 2026-08-26
**Status:** Approved design; revised same-day per detailed user review (14 points) — embedding model swapped with live-doc verification, explicit language selection, staged deployment, PS-complete gate added, voice protected in cut order
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
| Provider accounts | Groq/Gemini/Supabase keys required at Phase 0 (needed for local dev); full hosting integration deferred to Phase 5; Bhashini registration + smoke test at Phase 0 (approval lead time unverified — external risk retired early) |
| Build strategy | Walking skeleton first, then thicken; trivial `/health` deployment at Phase 0/1, production-like deployment at Phase 5 |
| Success bar | Two gates: **MVP gate** (Phase 4, reliable text core) and **PS-complete gate** (Phase 7, all mandatory problem-statement requirements incl. Hindi voice) |

**Gujarat language note:** Gujarati-speaking state with English-language official
texts. Hindi flagship demos run via Bhashini translation over English sources —
works, but the alignment rationale must be logged. Gujarati becomes the natural
post-MVP second language (replacing "Marathi" in work-plan.md's backlog).

## 2. Gap-closing technical decisions

These resolve every "or" / blank left in the frozen docs. Each gets a DECISIONS.md
entry when implemented.

### 2.1 Language handling — explicit UI selection, optional auto-check
English/Hindi is **selected in the UI**; the selection is authoritative for text
and is passed directly to Bhashini STT for voice requests. A lightweight
script-ratio heuristic runs only as a consistency check on text input and may
override the selection only on high-confidence mismatch (e.g., >70% Devanagari
while `en` selected).
Rationale: heuristics-as-primary fail on common cases — Latin-script Hindi
("meri fasal ka insurance kaise milega"), Hindi terms inside English sentences,
and code-mixed queries. A two-language MVP does not need language *detection*
as a mandatory routing dependency. No dedicated language-detection model.
**Deviation from design.md ("IndicLID or provider-native").**

### 2.2 Domain classification — keyword rules + embedding anchors (hybrid)
High-precision keyword/rule signals fire first (e.g., "PMFBY", "crop insurance",
"PACS", "cooperative society", "RBI", "grievance") and short-circuit to their
domain deterministically. Everything else falls to embedding anchors: ~10 anchor
phrases per domain embedded once at ingest time with `gemini-embedding-2` at
`output_dimensionality: 768`, cached; each turn makes one query-embedding call;
cosine vs anchors picks the domain; max similarity below calibrated floor →
`out_of_scope`. Keyword rules double as the offline fallback when Gemini is
unavailable.

**Embedding model:** `gemini-embedding-2` (stable GA since 2026-04-22; official
replacement for `gemini-embedding-001`, which shuts down 2028-05-14). Verified
against live Google docs 2026-08-26: per-string embeddings with automatic
renormalization at reduced dimensions. The earlier DECISIONS.md rejection
targeted `embedding-2-preview`, whose behavior does not carry to GA.
**Guard:** the Phase 0 smoke test must empirically confirm N input strings → N
distinct 768-dim vectors; on violation, fall back to `gemini-embedding-001`
(manual normalization required) and re-log the decision.

### 2.3 Jurisdiction & sessions — server-side, TTL'd, ask-don't-assume
`sessions(session_id UUID PK (client-generated), state JSONB, updated_at,
expires_at)`. Frontend sends `session_id` + selected state (`null | "gujarat"`)
per `/chat`. Grievance slot-filling progress lives server-side. `expires_at =
updated_at + 24h`; expired rows are purged lazily on upsert — no scheduler
needed.
**Jurisdiction rule:** if a question requires state-specific legal/cooperative
information and `state == null`, the system asks the user for the state
(offering Gujarat) instead of silently assuming one.

### 2.4 Evidence gate & confidence — provisional numbers, banded display
Initial values are **provisional, not validated truths**: answer only if
`top1_cosine >= 0.35` AND at least 2 chunks score `>= 0.30`; otherwise abstain.
The gate additionally confirms **domain match and jurisdiction match** of the
retrieved chunks — defense-in-depth on top of metadata pre-filtering.
Confidence = `0.6·top1 + 0.4·(chunks_above_0.30 / k)` clamped [0,1] — again
provisional. Phase 4 calibrates: top1 threshold, secondary-chunk threshold,
confidence weights, against golden-set runs.
**Display rule:** the API keeps the numeric `confidence` field (frozen
contract), but the UI renders evidence **bands** — "Strong source support" /
"Moderate source support" / "Weak source support" — never a bare percentage.
An uncalibrated number invites the question "how do you know 86% means 86%?"

### 2.5 Chunking — structure-aware, citation-ready
Docling → Markdown → split on heading boundaries, then token-length split
(target ~600 tokens, hard range 400–800) with 80-token overlap. Page number and
**section heading stored separately** on every chunk (schema columns `page`,
`section`). Citations render as
`PMFBY Operational Guidelines — §5.2 — p. 14`, not a bare page number. Same
pipeline for seed and real corpus so seed→real swap costs nothing.

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
| **0 — Foundations** | Groq/Gemini/Supabase accounts + keys in `.env` (never committed); Bhashini registration **and smoke-test script** (key → pipeline config → Hindi STT → Hindi TTS — script-level, no UI); current Groq/Gemini model IDs verified against live provider docs; git init + monorepo scaffold; `.env.example`; CI workflow (ruff + pytest + vitest); Gujarat sources verified & added to `sources.yaml`; Supabase migrations (`documents`, `chunks vector(768)` + HNSW, `grievances`, `sessions`, `feedback`); embedding per-string guard test (§2.2); trivial Render `/health` stub deployed (platform quirks discovered early) | Schema applied; smoke calls succeed against Groq, Gemini, Supabase; embedding guard passes; Bhashini smoke passed **or** tracked as an open blocking issue; `/health` stub reachable on Render |
| **1 — Walking skeleton** | 10–15 hand-written seed chunks from real `sources.yaml` URLs → ingest script → `/chat` full path (UI-selected language + consistency check → keyword/anchor hybrid domain routing → jurisdiction filter → pgvector top-k → evidence gate → Groq grounded generation → citation verification → abstain path) → minimal text chat UI with citations/confidence bands/abstention display; `LanguageProvider` + `BhashiniProvider` adapter stubs with mocked audio/text | 5 seed questions answered with valid citations; 2 unsupported questions correctly abstain — local application against the development Supabase project |
| **2 — Grievance** | State machine NEW→NEEDS_INFORMATION→CLASSIFIED→CREATED→IN_PROGRESS→RESOLVED; LLM slot extraction; missing-field follow-ups; `DEMO-<DOMAIN>-<#####>` references; status lookup; form/status UI with prototype warning (`is_official_submission: false` always) | Full create→follow-up→reference→lookup green in pytest + manual UI run |
| **3 — Real corpus + Gujarat** | Docling ingestion of all `sources.yaml` documents + Gujarat Act/Rules; complete jurisdiction metadata; state/domain filters enforced pre-vector-search; PRD's 8–15 schemes coverage | Corpus auditable from `sources.yaml`; Gujarat-specific question returns state-filtered citations |
| **4 — Eval & hardening — MVP GATE** | ~140 golden cases (20 per domain, floor 10/domain under pressure); threshold calibration (§2.4 values are provisional until here); Groq→Gemini fallback + timeout/429 handling; structured logging; error-state UX; Playwright smoke suite; **citation-support negative test** — inject a fabricated citation and assert answer rejection → abstention | Text-mode PRD Definition-of-Done met locally. Voice implementation begins after this gate |
| **5 — Deployment** | Render backend + Vercel frontend; CORS allow-list; env config; cold-start playbook incl. explicit **Supabase resume checklist**: resume project → migrations applied → HNSW index exists → documents/chunks present → health query passes. Never assume "it worked yesterday" | Deployed PWA meets PRD DoD end-to-end |
| **6 — Voice (Tier 2)** | Wire the Phase-1 stubs to real Bhashini STT/TTS → Groq Whisper STT fallback → text-only fallback; `/voice/transcribe`, `/voice/speak`; recording UI; provider health states | Hindi voice question → cited Hindi answer (flagship demo #1) |
| **7 — PS-complete verification** | Run the full problem-statement checklist end-to-end: multilingual conversation (EN/HI), cooperative laws/by-laws with jurisdiction metadata, Ministry schemes, PMFBY/agriculture workflows, financial literacy, grievance prototype workflow, Hindi voice, responsive web/mobile PWA, evidence citations, abstention | Every mandatory PS item demonstrably working. Only now does the enhancement backlog open |

### Gate semantics
**MVP gate (Phase 4)** = reliable text core. **PS-complete gate (Phase 7)** = all
mandatory problem-statement requirements including Hindi voice. The team must
not declare success at Phase 4 while an explicit PS requirement is absent.

### Cut order under pressure
1. Languages beyond English + Hindi
2. Schemes beyond the PRD minimum of 8
3. States beyond Gujarat
4. Agriculture workflows beyond the core set
5. Eval cases beyond the 10-per-domain floor
6. UI polish, admin conveniences

**Never cut:** Hindi voice, citations + citation verification, abstention,
jurisdiction filtering, grievance prototype workflow + prototype labeling.

Sequencing note: voice *development* still starts after the Phase 4 gate so the
reliable text core lands first — but voice can no longer be the first thing
sacrificed, because PS completion requires it. Bhashini risk is instead retired
in Phase 0 via early registration + smoke testing.

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
2. **Language handling: explicit UI selection replaces IndicLID/provider-native/heuristic-primary** (§2.1) — updates design.md.
3. **Embedding model: `gemini-embedding-2` @ 768 supersedes `gemini-embedding-001`**, verified against live Google docs 2026-08-26, with a Phase 0 per-string empirical guard and 001 as approved fallback — supersedes the earlier DECISIONS.md entry rejecting `embedding-2-preview`.
4. **Deployment staged**: trivial `/health` stub at Phase 0/1 (platform risk retired early), production-like integration at Phase 5 — supersedes work-plan Day-1 "create Vercel/Render projects" timing.
5. **Domain classification pinned to hybrid keyword + anchor-embedding classifier** (§2.2) — resolves design.md's "or"; keywords promoted from failure-fallback to first-class signal.
6. **Phase structure re-gated around two success bars** — MVP gate (Phase 4) and PS-complete gate (Phase 7); cut order now protects Hindi voice because voice is a mandatory PS requirement, not an enhancement.
7. **Gujarat selected as state** — fills sources.yaml placeholder; language-alignment rationale recorded; Gujarati = natural post-MVP second language.
8. **Evidence display: banded strength in UI, numeric confidence kept only in API** (§2.4); thresholds explicitly provisional until Phase 4 calibration.

## 9. Non-goals honored

Everything on PRD.md's non-goals list stays out. Voice is Tier 2 gated behind
the Phase 4 MVP gate. No native apps, WhatsApp, blockchain, custom training,
self-hosted GPU, multi-agent frameworks, complex auth, analytics dashboards,
real CPGRAMS integration, or nationwide legal coverage.
