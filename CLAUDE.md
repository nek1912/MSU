# Project: Multilingual Cooperative Governance & Legal Assistance Chatbot

You are assisting a 4-person team building an evidence-grounded, multilingual
(English + Hindi) citizen-assistance PWA over 10 days, at zero cost, cloud-only,
with no personal GPU.

**Before doing anything else in a new session: read `PROJECT_STATUS.md`.** It
tells you what's actually built, what's stubbed, what's broken, and what the
next action is. This file (CLAUDE.md) tells you the rules that don't change.
PROJECT_STATUS.md tells you where things stand right now. Don't confuse the two.

If you're working in Cursor instead of Claude Code, `.cursorrules` in this repo
root is a duplicate of this file's rules section — keep them in sync if you edit
either.

## Non-negotiable principles

- The LLM is NEVER the source of truth. Every factual answer must be grounded in
  retrieved official documents with verifiable citations.
- If retrieval confidence is low or no supporting chunk exists, set `abstained: true`.
  Do not guess. Do not let the LLM override this in code.
- Never fabricate eligibility, amounts, dates, deadlines, legal clauses, or contacts.
- Grievances are PROTOTYPE references only. Always return `is_official_submission: false`.
  Never claim real government registration or a real CPGRAMS integration — there is
  no public CPGRAMS API to integrate with.
- Central and state law can differ. Always attach jurisdiction + effective-date
  metadata. Never present a national/model rule as universally applicable across states.
- Every citation must map to a chunk ID that was actually retrieved in that request.

## Scope discipline

Read `PRD.md` for full scope. Summary:

**MVP (Tier 1):** English + Hindi text chat, central cooperative info + ONE
selected state's rules, 8-15 curated schemes, PMFBY, 5-10 agriculture workflows,
RBI/PMJDY financial literacy, grievance workflow (text), citations, confidence,
abstention, responsive PWA, cloud deployment.

**Tier 2 (only after MVP is stable):** Hindi voice (Bhashini), remaining domains,
richer grievance follow-up.

**Do NOT add before the core is stable and demo-ready:** native Android/iOS,
WhatsApp integration, blockchain, custom model training, self-hosted GPU inference,
multi-agent frameworks, complex authentication, analytics dashboard, real government
grievance submission, nationwide legal coverage.

If you're asked to build something on this "do not add" list, push back and point
to this file rather than silently doing it.

## Stack (do not change without a logged decision — see DECISIONS.md)

- Frontend: Next.js + React + Tailwind, PWA, hosted on Vercel Hobby (Render Static
  Site is the fallback if Vercel eligibility becomes an issue)
- Backend: FastAPI (Python) on Render Free
- DB + vectors: Supabase Postgres + pgvector (HNSW index)
- Embeddings: Gemini API, model `gemini-embedding-001`, 768 dimensions.
  Do NOT use `gemini-embedding-2` / `gemini-embedding-2-preview` — it aggregates
  multiple inputs into a single vector rather than returning one embedding per
  input string, which is the wrong behavior for per-chunk retrieval, and it's
  preview-status with a larger default dimension that costs more free-tier storage
  for no benefit here. This was tried and reverted — see DECISIONS.md.
- LLM: provider abstraction, Groq primary (Llama 3.3 70B or similar), Gemini
  2.5 Flash fallback
- Voice: Bhashini primary → Groq Whisper STT fallback → text-only fallback
- Document parsing: Docling
- Local retrieval testing: FAISS

## API contracts (frozen Day 1 — do not break without updating PROJECT_STATUS.md
## and telling the whole team)

```
POST /chat
POST /voice/transcribe
POST /voice/speak
POST /grievances
GET  /grievances/{reference}
GET  /sources/{id}
GET  /health
GET  /health/providers
```

Chat response fields: `answer, language, domain, confidence, citations[], abstained,
follow_up_question`.

## Coding conventions

- Python: type hints everywhere, Pydantic models for all request/response bodies,
  no bare `except`.
- Every external provider call (Bhashini, Groq, Gemini, Supabase) goes through an
  adapter with explicit timeout and fallback handling — never call a provider SDK
  directly from route handlers.
- Never put API keys in frontend code, commit them, or expose them via
  `NEXT_PUBLIC_*`. Backend environment variables only.
- Structured logs. Never log API keys, auth tokens, or full grievance PII.
- Write tests for: domain routing, jurisdiction filtering, retrieval, citation
  validity, abstention, grievance workflow, provider fallback, API failure handling.

## When unsure

- Prefer reusing referenced open-source patterns (see SOURCES.md) over building
  from scratch — but read the actual repo before depending on it. Don't assume a
  cited repo does what a summary claims; verify against the real code/docs.
- Push back on scope creep, out loud, citing this file.
- State assumptions explicitly rather than silently picking one.
- Never invent facts, APIs, repositories, capabilities, or free-tier limits you
  haven't verified. If you're not sure whether a claim in these docs is still
  accurate (free-tier quotas change), say so and suggest checking the live source.
- At the end of every working session, update `PROJECT_STATUS.md` before you stop.
  This is not optional — it's the only thing that makes the next session (yours or
  a teammate's) start from reality instead of from the original plan.
