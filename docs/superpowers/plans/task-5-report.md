# Task 5: Per-File Error Isolation — Report

## Status: DONE

## What was done

### 1. Broadened exception handling in `manifest_to_supabase()`
- **Before:** `except (FileNotFoundError, ValueError, KeyError)` — only caught 3 specific types
- **After:** `except Exception` — catches any processing error (corrupt PDF, Docling crash, DB timeout, etc.)
- Failed files are isolated: their error is logged and appended to `failed[]`, then processing continues

### 2. Added structured logging
- Added `import logging` and `logger = logging.getLogger(__name__)` to `ingestion/ingestion/ingest.py`
- Replaced all `print()` calls with appropriate log levels:
  - `logger.error()` for file processing failures (includes source_id, exception type, message)
  - `logger.info()` for successful ingestions and dry-run/preflight summaries
  - `logger.warning()` for listing failed sources in the summary
  - `logger.info()` for the overall summary line

### 3. Created `ingestion/tests/test_error_isolation.py` — 6 tests

| Test | What it verifies |
|------|-----------------|
| `test_one_bad_file_others_succeed` | One file raising doesn't prevent others from completing |
| `test_all_fail_gracefully` | If every file raises, all appear in `failed[]` with no crash |
| `test_exception_types_isolated` | Different exception types (FileNotFoundError, KeyError, PermissionError) are all caught |
| `test_db_not_called_for_failed_files` | Failed files never reach the DB layer (delete/insert ops only for succeeded files) |
| `test_structured_log_on_failure` | ERROR log entry contains source_id and exception class name |
| `test_summary_logged` | Summary line logged with correct succeeded/failed counts |

## Files changed
- `ingestion/ingestion/ingest.py` — added logging, broadened except clause
- `ingestion/tests/test_error_isolation.py` — new file, 6 tests

## Test results
- 20 passed, 1 skipped (MVP PDFs not on disk)
- All existing tests unaffected

## Concerns
- The `validate_manifest_files` mock in tests patches `ingestion.ingest.validate_manifest_files`, which works because the installed package resolves correctly. However, the outer `ingestion/` directory also contains `ingestion/ingestion/` — this could cause confusion if someone runs tests from the wrong directory.
- The `print()` in `if __name__ == "__main__"` block was left as-is (not converted to logging) since it's a CLI entry point.
