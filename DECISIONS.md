# Decisions Log

CLAUDE.md, PRD.md, architecture.md, and design.md are frozen specs — that's
deliberate, so a new AI session or teammate has a stable target instead of a
moving one. But a 10-day build with four people will deviate from them
sometimes, for good reasons. When it does, log it here instead of either (a)
silently drifting, which makes the frozen docs actively misleading, or (b)
blindly following a spec that's turned out to be wrong just because it's
"frozen."

**Rule: if you deviate from a frozen doc, add an entry here in the same
session, and update the relevant doc if the deviation is permanent.** A
deviation that isn't logged didn't happen as far as the next session is
concerned — it'll just look like an unexplained inconsistency between the docs
and the code.

Each entry: what changed, why, what it replaced, who/when.

---

## Template

```
### <short title>
**Date:** YYYY-MM-DD
**Changed by:** <name/session>
**What:** <the actual change>
**Why:** <the reason — what problem this solved or avoided>
**Replaces:** <what the frozen doc said before, if anything>
**Doc updated:** <yes/no — which file, or "pending">
```

---

## Log

### Reverted embedding model from gemini-embedding-2 to gemini-embedding-001
**Date:** 2026-08-26
**Changed by:** consolidation session
**What:** Standardized on `gemini-embedding-001` (768 dims) for all chunk
embeddings, rejecting an earlier draft's switch to `gemini-embedding-2`.
**Why:** `gemini-embedding-2` is preview-status and, per Google's own docs,
aggregates multiple input strings into a single embedding rather than
returning one embedding per string. This RAG pipeline needs one vector per
chunk. Using it as drafted would have silently produced the wrong embedding
shape for retrieval. `gemini-embedding-001` is stable, supports per-string
embeddings, and its output dimension is configurable via MRL down to 768,
which is lighter on Supabase's free-tier storage.
**Replaces:** A prior draft's recommendation to use `gemini-embedding-2`.
**Doc updated:** yes — CLAUDE.md, SOURCES.md

### Dropped NyayaSetu-Offline-Multilingual-AI as a dependency
**Date:** 2026-08-26
**Changed by:** consolidation session
**What:** Removed this repo from the planned open-source reuse list entirely.
**Why:** Could not be verified via web search — no stars, forks, or discussion
anywhere, despite an earlier research pass citing it as a major grievance-
workflow foundation with "80+ endpoints." Building critical-path grievance
logic on an unverifiable citation is a risk not worth taking in a 10-day
hackathon.
**Replaces:** Earlier plan to reuse its grievance CRUD/lifecycle/SLA patterns.
**Doc updated:** yes — SOURCES.md

### Consolidated vector store and relational DB into Supabase pgvector
**Date:** 2026-08-26
**Changed by:** consolidation session
**What:** Single Supabase Postgres + pgvector instance for both structured
data (grievances, feedback) and embeddings, replacing an earlier two-service
split (separate Qdrant Cloud + separate Postgres).
**Why:** One free-tier service to provision, monitor, and keep from idling out
instead of two. Fewer moving parts for a 4-person, 10-day build.
**Replaces:** Earlier architecture using Qdrant Cloud for vectors and a
separate Postgres instance for relational data.
**Doc updated:** yes — architecture.md, CLAUDE.md
