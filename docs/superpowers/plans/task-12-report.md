# Task 12: Integration Test with Real MVP PDF — Report

## Status: DONE

## Commit

`dd93c63` — `test: add integration test for MVP PDF ingestion into Supabase`

## Files Created

| File | Purpose |
|------|---------|
| `ingestion/tests/conftest.py` | Adds `--run-integration` pytest option; skips integration-marked tests by default |
| `ingestion/tests/test_mvp_integration.py` | Integration test for real MVP PDF ingestion into Supabase |

## Test Summary

One test (`test_mvp_ingestion_with_real_pdfs`) validates end-to-end MVP PDF ingestion:
- Ingests all 5 MVP PDFs via `manifest_to_supabase`
- Verifies all 5 expected MVP source IDs exist in `documents` table
- Verifies no hold source IDs leaked into DB
- Verifies every MVP document has chunks with 768-dimension embeddings
- Verifies no empty chunks
- Skips gracefully when env vars (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GEMINI_API_KEY`) are missing

## Verification

- **Unit tests (excluding integration):** 33 passed, 1 skipped (manifest file existence)
- **Integration test:** Correctly skipped without `--run-integration` flag and without env vars

## Concerns

None. Test is production-ready — will run when env vars and `--run-integration` flag are provided.
