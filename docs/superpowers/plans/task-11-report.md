# Task 11 Report: Add Corpus Safety Invariant

**Status:** DONE_WITH_CONCERNS
**Date:** 2026-08-27
**Commit:** `85587ca` — `feat: add corpus safety invariant test (pytest.raises, v4.1 Patch 4)`

## What Was Done

Created `ingestion/tests/test_corpus_safety.py` with one integration test:

- **`test_existing_document_not_deleted_on_failure`** — Verifies the RPC transaction rollback guarantee: when a replacement with invalid data (wrong vector dimension 100 vs 768) fails, the original document and its chunks remain intact.

## Patch 4 Compliance

Applied the corrected test from v4.1 Patch 4:

| Requirement | Status |
|---|---|
| Uses `pytest.raises` instead of `except Exception: pass` | ✅ |
| Forces failure AFTER deletion attempt (invalid vector dim) | ✅ |
| Verifies original document still exists after failure | ✅ |
| Verifies original chunks still exist after failure | ✅ |
| Uses `@pytest.mark.integration` marker | ✅ |
| Cleans up test data after assertions | ✅ |

## Test Collection & Syntax

- ✅ Syntax validated via `ast.parse`
- ✅ Pytest collects the test (1 item collected)
- ✅ Import path matches existing tests: `from ingestion.ingest import atomic_replace_document`
- ✅ Source ID `"test_safety_doc"` is distinct from `"test_rollback_doc"` in `test_rpc_atomicity.py`

## Concerns

### 1. Integration tests cannot run locally (BLOCKING for CI)

The test requires:
1. **Live Supabase connection** — DNS resolution works from `ingestion/` CWD but not from `backend/` CWD
2. **Schema deployed** — Migrations 0001-0004 must be applied to the Supabase database (tables `documents`, `chunks` + `atomic_replace_document` RPC function)

Current state: connecting to Supabase succeeds but returns `PGRST205` ("Could not find the table 'public.documents' in the schema cache"). The schema smoke tests (`test_schema_smoke.py`) also fail with DNS resolution errors.

**Resolution needed:** Deploy migrations to Supabase, or run tests in a CI environment with proper network access.

### 2. Test correctness depends on RPC rollback behavior

The test asserts that `atomic_replace_document` rolls back on failure. This depends on the PostgreSQL function (migration 0004) being wrapped in a transaction. The migration SQL does NOT explicitly use `BEGIN/END` — it relies on PLpgsql's implicit transaction wrapping for the function body. This is correct behavior for PostgreSQL, but worth noting.

### 3. Non-integration tests unaffected

All existing unit tests (chunker, state normalization, extraction validation) pass without regression.

## Files

- **Created:** `ingestion/tests/test_corpus_safety.py` (61 lines)
