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

### Switched embedding model from gemini-embedding-001 to gemini-embedding-2
**Date:** 2026-08-26
**Changed by:** spec-review session (user review; verified against live docs)
**What:** Standardize on `gemini-embedding-2` with `output_dimensionality: 768`
for chunk and anchor embeddings. `gemini-embedding-001` demoted to approved
fallback. Phase 0 must smoke-test N inputs → N distinct 768-dim vectors before
any corpus ingestion; on violation, revert to `gemini-embedding-001` (manual
normalization at 768) and re-log.
**Why:** Live Google docs verified 2026-08-26: `gemini-embedding-2` is stable GA
(released 2026-04-22, no shutdown announced), documents per-string embeddings,
and auto-renormalizes truncated dimensions; it is Google's listed replacement
for `gemini-embedding-001`, whose shutdown is now announced for 2028-05-14. The
earlier rejection below targeted `embedding-2-preview` (shutdown 2026-08-10);
its aggregation behavior does not carry to the GA model per current official
docs and examples.
**Replaces:** "Reverted embedding model from gemini-embedding-2 to
gemini-embedding-001" (above).
**Doc updated:** yes — CLAUDE.md, SOURCES.md, spec §2.2
(docs/superpowers/specs/2026-08-26-mvp-build-design.md)

### Adopted implementation spec; work-plan demoted to reference
**Date:** 2026-08-26
**Changed by:** brainstorming/spec session
**What:** Adopted
`docs/superpowers/specs/2026-08-26-mvp-build-design.md` as the operational plan:
Gujarat selected as the state; phase-gated build (0–7) with an MVP gate (Phase 4)
and a PS-complete gate (Phase 7); cut order protects Hindi voice (a mandatory PS
requirement) instead of sacrificing it first; language handling switched to
explicit UI selection with optional heuristic consistency check (no IndicLID /
no detection-as-dependency); domain classification pinned to hybrid keyword +
anchor-embedding classifier; deployment staged (trivial `/health` stub early,
full integration in Phase 5); evidence thresholds explicitly provisional until
Phase 4 calibration; UI shows evidence bands, not raw confidence numbers;
sessions gain TTL; state-null questions ask for the state rather than assuming
Gujarat.
**Why:** Converts frozen-doc ambiguities into testable decisions before code
exists; aligns delivery bar with the problem statement's mandatory items.
**Replaces:** day-by-day sequencing in work-plan.md (now background info);
design.md's IndicLID/provider-native detection line; earlier voice-first-cut
order.
**Doc updated:** yes — spec is authoritative for sequencing; design.md/design
deviations itemized in spec §8.

### Adopted Phase 2A spec — Corpus & Retrieval Quality Gate
**Date:** 2026-08-26
**Changed by:** planning session
**What:** Phase 2A design spec finalized with 6 hard invariants, 245 gold
evaluation cases, 4 new evaluation scripts (retrieval, jurisdiction,
unsupported-query, citation), corpus snapshot versioning, Gate 2 report
generator, and gate2_config.yaml for frozen target T.
**Why:** Phase 0-1 code/integrity gate passed; next milestone is corpus quality
and retrieval accuracy measurement before adding new features.
**Replaces:** None — extends existing plan.
**Doc updated:** yes — docs/superpowers/specs/2026-08-26-phase2a-corpus-retrieval-quality-design.md

### Implemented GeminiReranker with real Gemini API calls
**Date:** 2026-09-02
**Changed by:** 7th session
**What:** Replaced stub GeminiReranker (passthrough scores) with real Gemini API
calls for pre-ranking and final reranking. Uses `gemini-2.5-flash-lite` model
with batch scoring prompts. Falls back to passthrough on API failure.
**Why:** Stub reranker was not providing real semantic ranking, making the
dynamic RAG pipeline's reranking step ineffective.
**Replaces:** Stub GeminiReranker that returned passthrough scores.
**Doc updated:** yes — PROJECT_STATUS.md

### Changed AnswerGenerator model from openai/gpt-oss-20b to llama-3.3-70b-versatile
**Date:** 2026-09-02
**Changed by:** 7th session
**What:** Updated DEFAULT_MODEL in `app/rag/answer_generator.py` from
`openai/gpt-oss-20b` (non-existent model) to `llama-3.3-70b-versatile`
(available on Groq API).
**Why:** The previous model ID was invalid and would cause API errors.
**Replaces:** `openai/gpt-oss-20b` model ID.
**Doc updated:** yes — PROJECT_STATUS.md

### Enabled Sarvam as primary voice provider
**Date:** 2026-09-02
**Changed by:** 7th session
**What:** Configured Sarvam AI as primary voice provider (STT + TTS) with API
key. Voice fallback chain: Sarvam → Azure → text-only.
**Why:** User provided Sarvam API key; Sarvam offers better Indic language
support than Azure for Hindi, Gujarati, Marathi, Bengali, Tamil.
**Replaces:** Previous state where both providers were disabled.
**Doc updated:** yes — PROJECT_STATUS.md

### Aligned evidence gate thresholds with test expectations
**Date:** 2026-09-02
**Changed by:** 7th session
**What:** Updated `app/config.py` thresholds: `TOP1_THRESHOLD=0.25` (was 0.20),
`SECONDARY_THRESHOLD=0.30` (was 0.15), `MIN_CHUNKS_ABOVE_SECONDARY=2` (was 1).
Updated `evidence_gate_v2` to read thresholds from config instead of hardcoded
defaults.
**Why:** Tests expected these threshold values; the previous values were too
permissive and allowed weak evidence through.
**Replaces:** Previous threshold values.
**Doc updated:** yes — PROJECT_STATUS.md

### Added language-matching rule to dynamic RAG prompts
**Date:** 2026-09-02
**Changed by:** 7th session
**What:** Added explicit language-matching instruction to dynamic RAG system
prompt: "You MUST respond in the same language as the user's question." Added
Tamil language support to generation.py. Added conflicting evidence handling
guidance to prompt_builder.py.
**Why:** Dynamic RAG pipeline was not language-aware; responses would default
to English regardless of question language. Tamil was missing from supported
languages.
**Replaces:** No language matching rule in dynamic RAG prompts.
**Doc updated:** yes — PROJECT_STATUS.md

### Added Hindi keywords to QueryClassifier and domain mapping
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Added Hindi keywords to QueryClassifier DOMAIN_KEYWORDS (PMFBY,
cooperative, schemes, agriculture, finlit, grievance). Added `_DOMAIN_MAP` in
chat.py to map QueryClassifier domains to AnchorStore domains (pacs→pacs_governance,
finlit→financial_inclusion, cooperative→pacs_governance). Added `pacs_computerization`
as separate domain with its own keywords.
**Why:** Hindi queries were not matching any keywords and falling through to
"general" domain. Domain name mismatch between QueryClassifier and _STATIC_DOMAINS
caused incorrect routing to web RAG.
**Replaces:** English-only keywords in QueryClassifier; mismatched domain names.
**Doc updated:** yes — PROJECT_STATUS.md

### Out-of-scope questions now abstain instead of generating general answers
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Changed out_of_scope handling in chat.py to return abstain text instead
of generating a general answer with disclaimer. When AnchorStore classifies a
query as "out_of_scope", the system now returns `abstained: True` with no citations.
**Why:** The previous behavior answered out-of-scope questions (like "What is the
capital of France?") with a general answer + disclaimer, which violated the
principle that the LLM is never the source of truth. Out-of-scope queries should
abstain, not guess.
**Replaces:** General answer with disclaimer for out-of-scope queries.
**Doc updated:** yes — PROJECT_STATUS.md

### Added Tamil to ChatRequest.language literal
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Updated `ChatRequest.language` field in chat.py from
`Literal["en", "hi", "gu", "mr", "bn"]` to include `"ta"` for Tamil support.
**Why:** Tamil was added to the frontend i18n but was missing from the backend
request schema, causing 422 errors for Tamil queries.
**Replaces:** `Literal["en", "hi", "gu", "mr", "bn"]`
**Doc updated:** yes — PROJECT_STATUS.md

### Improved RAG system prompt to reduce INSUFFICIENT_EVIDENCE responses
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Rewrote `build_system_prompt()` in generation.py to explicitly instruct
the LLM to use the provided context chunks. Added clearer citation format
instructions and explicit guidance to only say INSUFFICIENT_EVIDENCE when chunks
truly contain no relevant information.
**Why:** The previous prompt was causing Groq Llama 3.3 70B to return
INSUFFICIENT_EVIDENCE despite having good chunks, resulting in empty citations
and general answers with disclaimers.
**Replaces:** Previous system prompt that was too restrictive.
**Doc updated:** yes — PROJECT_STATUS.md

### Added fallback citation logic for LLM non-compliance
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Added `_append_citations()` function in chat.py that automatically
adds citation markers from top chunks when the LLM doesn't include them. This
handles cases where the LLM ignores citation instructions.
**Why:** Even with improved prompts, some LLMs may not always include citations.
Fallback logic ensures citations are always present when the evidence gate passes.
**Replaces:** No fallback citation logic.
**Doc updated:** yes — PROJECT_STATUS.md

### Added Sarvam translator for Indian languages
**Date:** 2026-09-02
**Changed by:** 8th session
**What:** Created `SarvamTranslator` provider using Sarvam's Mayura v2 translation
model. Updated chat.py to use Sarvam as primary translator for Indian languages,
with Azure as fallback.
**Why:** Sarvam handles Indian languages better than Azure Translator. User
confirmed Sarvam is better for Indian language translation.
**Replaces:** Azure-only translation.
**Doc updated:** yes — PROJECT_STATUS.md
