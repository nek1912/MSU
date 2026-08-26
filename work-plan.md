# 10-Day Work Plan — organized by ownership, not phases

This is the plan as frozen on Day 1. It will drift — that's expected. When it
does, don't silently deviate: log the deviation in DECISIONS.md and update
PROJECT_STATUS.md so the next session (yours or a teammate's) knows the plan
below is aspirational history, not current truth.

## Ownership

- **M1 — AI / RAG / Governance**: document ingestion, source curation, chunking,
  embeddings, retrieval, grounding, citation validation, confidence, abstention,
  evaluation.
- **M2 — Backend / Grievance Workflow**: FastAPI, API contracts, domain routing,
  grievance state machine, provider adapters, database integration, backend
  deployment.
- **M3 — Frontend / Voice**: Next.js PWA, chat UI, citation UI, confidence/
  abstention UI, grievance UI, voice controls, Bhashini UX, mobile usability.
- **M4 — DevOps / Testing / Data / Demo**: GitHub, CI, Render/Vercel/Supabase
  setup, environment configuration, regression testing, source-manifest support,
  quota/latency tests, deployment verification, demo rehearsal.

## Day 1 — Architecture and contract lock (ALL)

- Freeze MVP scope (PRD.md). Select ONE state. Freeze API contracts.
- Create GitHub repo, Supabase project, Render service, Vercel project.
- Register for Bhashini access (do this first — approval time unverified).
- Test Gemini, Groq, and Bhashini access with a real API key each.
- Verify all four members can clone and run the project locally.

**Exit criterion:** all four members can run the basic system locally.

## Day 2 — Skeleton systems

- M1: document metadata schema, `sources.yaml` started, test Docling extraction,
  test embedding generation against `gemini-embedding-001`.
- M2: FastAPI app, `/health` route, all API route stubs, Supabase connection,
  mocked responses.
- M3: Next.js app, chat screen, grievance screen, language selector.
- M4: GitHub Actions, deploy frontend + backend skeletons, `.env.example`,
  document required environment variables.

**Exit criterion:** deployed frontend can call deployed backend.

## Day 3 — Data and retrieval

- M1: ingest first official documents, parse with Docling, chunk, generate
  embeddings, store in Supabase, add metadata filters, implement top-k retrieval.
- M2: connect `/chat` to retrieval, implement domain routing, structured
  answer schema, provider abstraction.
- M3: display answer, citations, confidence, build abstention UI.
- M4: sample question set, retrieval latency testing, failure tracking,
  validate deployed APIs.

**Exit criterion:** a text question produces a cited answer from the real corpus.

## Day 4 — Grounding and safety

- M1: citation validation, evidence thresholds, jurisdiction filters, source
  metadata.
- M2: grounded generation, unsupported-question handling, LLM fallback,
  provider timeouts.
- M3: answer readability, source expansion panel, clear abstention UI.
- M4: evaluation set started; test fabricated citations, unsupported questions,
  wrong domain, wrong state, irrelevant documents.

**Exit criterion:** system abstains instead of guessing when evidence is inadequate.

## Day 5 — Grievance workflow

- M1: grievance-related source material, grievance classification examples.
- M2: grievance state machine, missing-information detection, follow-up logic,
  prototype reference creation, status lookup.
- M3: grievance form, status-lookup screen, prototype-warning display.
- M4: test full grievance path, database persistence, backup/export.

**Exit criterion:** describe issue → answer follow-ups → prototype reference →
look up status.

## Day 6 — Hindi voice (Tier 2 begins)

- M1: test Hindi query retrieval and answer quality, fix language/domain issues.
- M2: Bhashini adapter, Groq Whisper fallback, text-only fallback, provider
  health states.
- M3: recording control, audio playback, browser permission handling, loading/
  error states.
- M4: voice latency and quota testing, provider-failure testing, record a
  backup voice demo video (used if live Bhashini calls are slow/down at
  presentation time).

**Exit criterion:** a Hindi voice question produces a cited Hindi answer.

## Day 7 — Corpus completion (ALL)

Complete remaining domains: cooperative law, PACS, Ministry schemes, PMFBY,
agriculture, financial literacy, grievance. Every source needs: official URL,
organization, domain, jurisdiction, state, effective date, verified date,
page-level citation data.

**Exit criterion:** complete demo corpus is auditable — someone unfamiliar with
the project could open `sources.yaml` and understand where every answer's
evidence comes from.

## Day 8 — Quality and resilience

- M1: run retrieval evaluation, fix weak chunks/metadata, tune evidence thresholds.
- M2: timeout handling, 429 handling, provider fallback, improve API errors.
- M3: mobile UI polish, loading/empty/error states.
- M4: regression tests, clean-browser test, cloud-deployment test, free-tier
  limit test, restart/cold-start behavior test.

**Exit criterion:** stable end-to-end cloud system.

## Day 9 — Demo optimization (ALL)

Select exactly three flagship demonstrations:

1. Hindi PMFBY voice question — voice → STT → routing → RAG → cited answer →
   Hindi TTS
2. Cooperative/PACS question — question → state selection → jurisdiction
   filtering → source-backed answer
3. Hindi grievance — voice/text complaint → classification → follow-up →
   prototype reference → status lookup

Then: optimize latency, remove broken features, improve UI, prepare
architecture diagram, prepare a limitations slide, prepare a cost/free-tier
slide, prepare open-source attribution, record a backup demo video.

**Exit criterion:** a reliable five-minute demonstration.

## Day 10 — Freeze and presentation (ALL)

Freeze code. Deploy final. Run smoke tests. Verify provider health, database,
citations, grievance flow, Hindi voice. Record final backup demo. Prepare
README, API documentation, architecture explanation. Rehearse failure/fallback
scenarios out loud, not just in code.

**Exit criterion:** reproducible deployed submission plus backup demo.

## Post-MVP backlog (only after core is stable — do not pull these forward)

1. Marathi / additional state language
2. Document download/share
3. Conversation history
4. Feedback buttons
5. Admin source management
6. More states
7. Analytics
8. Human escalation
9. Source-freshness automation
10. CI governance checks
