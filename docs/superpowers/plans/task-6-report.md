# Task 6 Report: Extraction Validation (Fail-Loud)

## Status: DONE

## What was done

Added `validate_extraction()` to the PDF extraction pipeline that fails loudly when extracted content is empty, whitespace-only, or shorter than 50 characters.

## Files modified

| File | Change |
|------|--------|
| `ingestion/ingestion/pdf_extractor.py` | Added `validate_extraction(content, filename, min_length=50)` function |
| `ingestion/ingestion/ingest.py` | Added import + validation call after `extract_pdf_to_markdown` |
| `ingestion/tests/test_extraction_validation.py` | **Created** — 4 new tests |
| `ingestion/tests/test_error_isolation.py` | Updated mock returns to pass 50-char minimum |

## Tests added (4)

- `test_validate_extraction_empty_raises` — empty string raises ValueError
- `test_validate_extraction_too_short_raises` — content < 50 chars raises ValueError
- `test_validate_extraction_valid` — valid content passes through
- `test_validate_extraction_whitespace_only_raises` — whitespace-only raises ValueError

## Commit

`2f21255` — `feat: add extraction validation with fail-loud behavior`

## Test summary

All 26 tests pass (1 skipped: MVP files not present; 2 deselected: slow PDF extraction tests).

## Concerns

None. The existing `test_error_isolation.py` tests needed minor updates because their mocks returned very short strings (e.g. `"# content"`, `"# ok"`) which now correctly fail validation. This is the intended behavior — the validation is doing its job.
