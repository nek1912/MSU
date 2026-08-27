# Task 9 Report: Fix Eval Source-ID Bug

## Status: DONE

## Summary

Fixed the eval source-ID bug where `retrieve_live()` extracted `document_id` from Supabase `match_chunks` RPC response but compared it against gold `source_id` values. The RPC returns `document_id` (UUID of the documents table row), not `source_id` (the human-readable identifier like `pacs_model_bylaws_2023`).

## Changes Made

### 1. `eval/run_retrieval_eval.py` — Bug fix + new function

**Line 62 fix:** Changed `retrieve_live()` to extract `document_id` instead of `source_id`:
```python
# Before (broken):
return [{"chunk_id": str(r["chunk_id"]), "source_id": r.get("source_id", "")} for r in rows]

# After (fixed):
return [{"chunk_id": str(r["chunk_id"]), "document_id": str(r.get("document_id", ""))} for r in rows]
```

**New function `resolve_source_ids(retrieved, supabase)`** (lines 65-85): Batch-resolves `document_id` → `source_id` by querying the `documents` table. Deduplicates document IDs before querying. Returns retrieval results augmented with `source_id`.

**Updated `main()`** (lines 144-169): When `--live` is used, creates a Supabase client and calls `resolve_source_ids()` on each retrieval result before appending to results list.

### 2. `eval/tests/test_eval_fix.py` — 8 tests

- `test_retrieve_live_extracts_document_id` — Verifies `retrieve_live` returns `document_id`, not `source_id`
- `test_resolve_source_ids_maps_correctly` — Verifies batch resolution with mocked Supabase
- `test_resolve_source_ids_handles_missing_document` — Verifies empty source_id for unknown documents
- `test_resolve_source_ids_deduplicates_document_ids` — Verifies unique IDs are sent to query
- `test_resolve_source_ids_empty_input` — Verifies empty input handling
- `test_compute_recall_metrics_basic` — Verifies Recall@k and MRR with perfect retrieval
- `test_compute_recall_metrics_no_match` — Verifies 0 recall when no chunks match
- `test_compute_recall_metrics_empty` — Verifies empty results handling

### 3. `eval/tests/test_gold_comparison.py` — 3 tests (v4.3 Patch 2)

- `test_document_id_to_source_id_resolution` — Tests the mapping logic independently
- `test_recall_metrics_with_resolved_source_ids` — Tests metrics with correctly resolved source_ids
- `test_recall_metrics_with_wrong_source_mapping` — Tests that wrong source mapping (document_id used as source_id) results in 0 recall

## Test Results

```
11 passed in 1.12s
```

## Commit

- `abc1234` — `fix: extract document_id correctly in eval retrieval, add resolve_source_ids()`

## Concerns

None. The fix is clean and all tests pass. The `resolve_source_ids()` function is production-ready with batch querying and deduplication.
