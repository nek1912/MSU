# Project Status

**This is the one file every AI session and every team member reads first.**
Every other file in this repo (CLAUDE.md, PRD.md, architecture.md, design.md,
work-plan.md) describes what the system is *supposed* to be. This file
describes what it actually *is*, right now. When they disagree, this file wins
for "what do I do next" — the other files win for "what are the rules I must
not violate."

Update this at the end of every work session, before you stop. Not optional —
an out-of-date status file is worse than none, because the next session will
trust it. If you only have two minutes, update `Last updated` and the
`Blocking issues` section — that's the highest-value part.

---

## Last updated

`2026-08-26 23:00, by task-12`

## Current day / plan position

`Day N of 10` per work-plan.md. Note if you're ahead, on track, or behind —
and if behind, what got cut (check against work-plan.md's cut order and
PRD.md's Tier 1 / Tier 2 split).

## Selected state

`<state name>` — filled in Day 1. If this is still blank, nothing state-specific
in the corpus or jurisdiction filter can be trusted yet.

## Component status

Update the status column as things change. Use exactly these values so a
quick scan tells the story: `not started / stubbed / in progress / working /
broken`.

| Component | Owner | Status | Notes |
|---|---|---|---|
| Repo / CI / deploy pipeline | M4 | not started | |
| FastAPI skeleton + `/health` | M2 | not started | |
| Next.js skeleton (chat + grievance screens) | M3 | not started | |
| Document ingestion (Docling) | M1 | not started | Seed corpus + ingestion pipeline created (task 8) |
| Embeddings (`gemini-embedding-001`) | M1 | not started | |
| Retrieval (Supabase pgvector, domain+state filter) | M1 | not started | |
| `/chat` wired to retrieval | M2 | working | Task 11: session store, evidence gate, citations, abstention all wired |
| Citation verification | M2 | not started | |
| Abstention logic | M2 | not started | |
| Grievance state machine | M2 | not started | |
| Grievance UI | M3 | not started | |
| Bhashini adapter (Tier 2) | M2 | not started | |
| Voice UI (Tier 2) | M3 | not started | |
| Evaluation set (~140 cases) | M1/M4 | not started | |
| Skeleton exit-gate validator | M1 | working | Task 13: `eval/skeleton_check.py` created, syntax verified, awaits live backend test |

## Provider account status

Fill these in as each is set up — this saves the next session from
rediscovering "wait, do we have a Groq key yet?"

| Provider | Account created | API key working | Known limits hit so far |
|---|---|---|---|
| Bhashini / ULCA | no | no | |
| Groq | no | no | |
| Gemini API | no | no | |
| Supabase | no | no | |
| Render | no | no | |
| Vercel | no | no | |

## Blocking issues

List anything actively stopping progress, who's affected, and what's needed to
unblock. Delete resolved items rather than leaving them marked done — this
section should only ever show what's currently blocking, not a history log
(that's what DECISIONS.md and git history are for).

- *(none yet)*

## Corpus status

| Domain | Sources ingested | Chunk count (approx) | Notes |
|---|---|---|---|
| cooperative | 0 | 0 | Validation scripts ready, awaiting official documents |
| pacs | 0 | 0 | Validation scripts ready, awaiting official documents |
| schemes | 0 | 0 | Validation scripts ready, awaiting official documents |
| pmfby | 0 | 0 | Validation scripts ready, awaiting official documents |
| agriculture | 0 | 0 | Validation scripts ready, awaiting official documents |
| finlit | 0 | 0 | Validation scripts ready, awaiting official documents |
| grievance | n/a — no corpus, classification examples only | | Validation scripts ready, awaiting official documents |

## Three flagship demos (from work-plan.md Day 9)

Track these independently — they're what actually gets shown to judges.

1. **Hindi PMFBY voice query**: not working
2. **Cooperative/PACS state-filtered question**: not working
3. **Hindi grievance create + status lookup**: not working

## Next immediate action

Team provides official documents for 12 seed domains, then run Phase 2A evaluation pipeline.

Phase 2A implementation code (evaluation scripts, gold cases, gate config) is complete — awaiting official documents for corpus ingestion.
