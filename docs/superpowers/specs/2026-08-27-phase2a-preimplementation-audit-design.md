# Phase 2A Pre-Implementation Audit — Design

**Date:** 2026-08-27
**Status:** Approved
**Supersedes:** None
**Purpose:** Identify all gaps between current code and MVP manifest requirements before implementation

## 1. Scope

This audit identifies gaps between the current codebase and the requirements for ingesting the 5 MVP PDF sources defined in `corpus/manifests/mvp_sources.yaml`. The audit follows a data-flow approach, tracing the path from manifest → PDF discovery → extraction → chunking → embedding → storage → retrieval → generation → citations.

**Entry condition:** Phase 0-1 code/integrity gate passed (80/80 tests passing).

**Exit condition:** Complete audit report with all gaps identified, severity-rated, and evidence-cited.

**Primary output:** `docs/phase2a_preimplementation_audit.md`

## 2. Audit Goal

Identify all gaps between current code and MVP manifest requirements. This audit does NOT include implementation details — those will be defined in the writing-plans phase after the audit is complete.

## 3. Audit Approach: Data-Flow

Following the data path through the entire pipeline:

```
MVP Manifest (mvp_sources.yaml)
    ↓
PDF Discovery (filesystem)
    ↓
PDF Extraction (Docling)
    ↓
Chunking (chunker.py)
    ↓
Metadata Enrichment
    ↓
Embedding (Gemini API)
    ↓
Storage (Supabase)
    ↓
Retrieval (match_chunks RPC)
    ↓
Generation (LLM + citations)
    ↓
Evaluation (gold_cases.yaml)
```

For each stage, the audit will:
1. Read the actual code — not assumptions
2. Answer the brainstorming questions from the task specification
3. Compare against MVP manifest requirements
4. Identify gaps with severity and evidence
5. Note cross-component dependencies

## 4. Output Structure

**File:** `docs/phase2a_preimplementation_audit.md`

**Sections:**

1. Current ingestion architecture
2. Current PDF-processing behavior
3. Current chunking behavior
4. Current metadata model
5. Current embedding behavior
6. Current Supabase ingestion behavior
7. Current retrieval behavior
8. Current citation behavior
9. Current failure handling
10. Resource/memory risks
11. Security risks
12. Production-vs-evaluation inconsistencies
13. Missing functionality
14. Bugs discovered
15. Recommended minimal changes
16. Files that would need modification
17. Tests that should be added
18. Dependencies/blockers

## 5. Severity Definitions

| Severity | Definition |
|---|---|
| P0 | Blocks MVP — must be fixed before any ingestion |
| P1 | Degrades quality — should be fixed for Gate 2 pass |
| P2 | Nice-to-have — can be deferred if time-constrained |

## 6. Evidence Format

Every finding must cite:
- File path
- Function/class name
- Line numbers (where relevant)
- Test coverage (if applicable)

## 7. Key Audit Checks

### 7.1 Manifest → Filesystem Consistency
- Every MVP manifest file exists on disk
- No hold file is ingested
- Manifest paths are accurate

### 7.2 Source ID Consistency End-to-End
- Manifest source_id → document source_id → chunk document_id → retrieval chunk_id → citation chunk_id → evaluation source_id/chunk_id

### 7.3 Corpus Replacement Behavior
- Old placeholder documents/chunks cannot remain after MVP ingestion
- Idempotent ingestion: re-running produces same result

### 7.4 Empty/Failed Extraction Behavior
- Failed PDF extraction must fail loudly
- Never create embeddings from empty/failed extraction
- No silent ingestion of corrupted data

### 7.5 MVP Scope Enforcement
- Ingestion must not silently fall back to `corpus/seeds/*.md`
- Only manifest-approved files are ingestible

## 8. Files to Inspect

| Pipeline Stage | Files |
|---|---|
| Manifest | `corpus/manifests/mvp_sources.yaml`, `corpus/manifests/hold_sources.yaml` |
| Ingestion | `ingestion/ingestion/ingest.py`, `ingestion/ingestion/loader.py` |
| Chunking | `ingestion/ingestion/chunker.py` |
| Embeddings | `backend/app/providers/embeddings.py` |
| Storage | `backend/migrations/0001_init.sql`, `backend/app/db.py` |
| Retrieval | `backend/app/retrieval.py`, `backend/app/routes/chat.py` |
| Citations | `backend/app/generation.py` |
| Evaluation | `eval/corpus_check.py`, `eval/gold_cases.yaml`, `eval/run_retrieval_eval.py` |
| Domain Classification | `backend/app/domains.py`, `backend/data/keyword_rules.json` |
| Seed Files | `corpus/seeds/*.md` (12 files) |

## 9. Preliminary Findings (Require Verification)

**Important Rule:** Do not treat these as established facts. Each finding must be verified against the actual repository and cited with file/function/test evidence.

### 9.1 Ingestion Pipeline Gap (P0 — verify)
- Current: `ingestion/ingestion/ingest.py` may only process `.md` files from `corpus/seeds/`
- Required: Process 5 PDF sources from `corpus/manifests/mvp_sources.yaml`
- **Verification needed:** Confirm `ingest.py` implementation actually processes only `.md` files

### 9.2 Gold Cases Source ID Mismatch (P0 — verify)
- Current: `eval/gold_cases.yaml` may reference source_ids that don't match `mvp_sources.yaml`
- Required: Source_ids must align end-to-end: manifest → document → chunk → retrieval → citation → evaluation
- **Verification needed:** Compare actual source_ids in both files

### 9.3 Seed File Content Quality (P0)
- Current: `corpus/seeds/*.md` files contain `wikipedia_proxy` placeholders and `TODO` markers
- Required: Verified official government text
- Impact: Invariant 1 (no placeholder/invalid corpus) will fail — directly blocks corpus-quality gate

### 9.4 Metadata Model Gap (P0 or P1 — verify against Gate 2 invariants)
- Current: Seed files have minimal metadata
- Required: MVP manifest has additional fields
- **Verification needed:** Determine if missing metadata is required by existing Gate 2 invariants

### 9.5 Chunking Compatibility (P2 — preliminary)
- Current: `chunk_markdown()` assumes markdown input
- Required: PDFs parsed via Docling will produce markdown
- Gap: Need to verify Docling output format matches chunker expectations

## 10. Success Criteria

Another engineer can read the resulting audit and know exactly:
- What already works
- What does not work
- What must change
- Why it must change
- Which files are affected
- How it will be tested
- How to verify that the implementation did not break the foundation

## 11. Implementation Principle

After the audit, implementation should follow:
```
existing architecture
    ↓
minimal changes
    ↓
tests
    ↓
small ingestion trial
    ↓
verification
    ↓
full MVP ingestion
    ↓
retrieval evaluation
```

**Do NOT:**
- rewrite the RAG architecture
- introduce LangChain unless a concrete gap requires it
- add new providers
- add new product features
- ingest hold sources
- add OCR during this task
- add dynamic/cron ingestion during this task
- add grievance functionality
