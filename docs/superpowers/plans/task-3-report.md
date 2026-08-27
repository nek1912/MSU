# Task 3: Manifest-Driven File Discovery with Fail-Loud - Implementation Report

## Status: DONE

## Summary

Implemented manifest-driven file discovery that fails loudly if any MVP file is missing. Added dry-run and preflight modes for safe testing.

## Files Created/Modified

### Created
- `ingestion/ingestion/manifest.py` - Manifest loading and validation module
- `ingestion/tests/test_manifest.py` - Comprehensive tests for manifest module

### Modified
- `ingestion/ingestion/ingest.py` - Added `manifest_to_supabase()` function with dry-run/preflight modes

## Implementation Details

### manifest.py
- `load_mvp_manifest(manifest_path)` - Load MVP sources from YAML manifest
- `load_hold_manifest(manifest_path)` - Load hold sources from YAML manifest
- `validate_manifest_files(sources, base_dir)` - Validate file existence on disk
- `validate_manifest_fields(source)` - Validate required fields for DB insertion

### ingest.py
- `manifest_to_supabase(manifest_path, embed_texts, supabase, dry_run, preflight)` - Main ingestion function with:
  - Fail-loud behavior for missing files or invalid manifest fields
  - `dry_run=True` - Report what would be done without embeddings or DB writes
  - `preflight=True` - Run full pipeline including embeddings but no DB writes
  - `dry_run` and `preflight` are mutually exclusive

## Test Results

```
14 passed, 1 skipped
```

The skipped test (`test_validate_manifest_files_all_exist`) is expected - it validates that MVP PDF files exist on disk, but they haven't been added to `corpus/seeds/` yet.

## Linting

All ruff checks pass.

## Concerns

1. **MVP PDFs not yet present**: The test `test_validate_manifest_files_all_exist` is skipped because the actual MVP PDF files haven't been added to `corpus/seeds/` yet. This is expected behavior - the test validates the manifest structure, not file existence.

2. **Placeholder extraction**: The `manifest_to_supabase()` function uses a placeholder for PDF extraction (Task 4 will implement Docling extraction). The current implementation reads file metadata but doesn't extract actual content.

3. **Placeholder atomic replacement**: The function uses simple insert/delete instead of the atomic RPC transaction (Task 10 will implement this).

## Next Steps

- Task 4: Add Docling PDF Extraction
- Task 5: Add Per-File Error Isolation
- Task 10: Add Atomic DB Replacement via RPC Transaction

## Commits

Pending - will commit after review.
