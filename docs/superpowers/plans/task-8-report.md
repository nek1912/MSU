# Task 8 Report: Fix Citation Verification Bug

## Status: DONE

## Summary

Fixed the citation verification bug where `grounded_answer()` in `chat.py` bypassed `verify_citations()`, allowing invalid LLM citations to be returned to users with `abstained: false`.

## Root Cause

In `backend/app/routes/chat.py:70-72`, the chat route called:
1. `grounded_answer()` → returns raw LLM text (no citation verification)
2. `_citations_from(answer, chunks)` → called `verify_citations()` but silently discarded invalid citations, only returning valid ones

The response was returned with `abstained: False` even when invalid citations existed.

## Fix Applied

**`backend/app/routes/chat.py`** — Added explicit `verify_citations()` check after `grounded_answer()` (line 72):
```python
_valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
if invalid:
    return _abstain(lang, "invalid_citations")
```

This matches the behavior already implemented in `generate_answer()` (generation.py:60-62), which was not being called from the chat route.

## Files Created

### `backend/tests/test_citation_fix.py` (6 tests)
Helper function unit tests:
- `test_citations_from_filters_invalid` — `_citations_from()` discards invalid citations
- `test_citations_from_accepts_valid` — `_citations_from()` preserves valid citations
- `test_citations_from_empty_when_no_markers` — returns empty list for no markers
- `test_verify_citations_rejects_invalid` — rejects unknown chunk prefixes
- `test_verify_citations_accepts_valid` — accepts matching chunk prefixes
- `test_verify_citations_rejects_mixed` — flags mixed valid/invalid as invalid

### `backend/tests/test_chat_citation_route.py` (3 tests)
Route-level tests using `respx` HTTP mocking (matching existing test patterns):
- `test_abstains_on_invalid_citations` — LLM returns `[chunk:deadbeef1]` → abstained=True
- `test_passes_on_valid_citations` — LLM returns `[chunk:aaaaaaaa]` matching retrieved chunk → abstained=False, 1 citation
- `test_abstains_on_mixed_valid_and_invalid_citations` — mixed → abstained=True

**Note:** Each route test provides 2+ chunks with similarity >= 0.51 to pass `evidence_gate` (MIN_CHUNKS_ABOVE_SECONDARY=2).

## Test Results

- 9 new tests: all PASSED
- 95/97 total backend tests: PASSED
- 2 pre-existing failures: `test_schema_smoke.py` (integration tests requiring live Supabase — not related to this task)

## Design Decisions

1. **Abstain on ANY invalid citation** — per spec: "we never silently discard bad citations." This matches `generate_answer()` behavior.
2. **Used `respx` over `unittest.mock.patch`** — consistent with existing `test_chat_route.py` patterns. Tests the actual HTTP call path rather than patching provider classes.
3. **`generation.py` unchanged** — `verify_citations()` already works correctly; the bug was only that `chat.py` wasn't acting on invalid results.

## Commit

- **94bb4ef** — `fix: validate citations before returning answer in chat route`
