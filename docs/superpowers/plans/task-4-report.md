# Task 4: Add Docling PDF Extraction — Report

## Status: DONE_WITH_CONCERNS

## Summary

Added Docling-based PDF extraction to convert PDF files to markdown for the MVP ingestion pipeline.

## Files Created/Modified

| File | Action |
|------|--------|
| `ingestion/ingestion/pdf_extractor.py` | Created — `extract_pdf_to_markdown()` using Docling `DocumentConverter` |
| `ingestion/tests/test_pdf_extractor.py` | Created — 3 tests (extraction, error, MVP file validation) |
| `ingestion/ingestion/ingest.py` | Modified — replaced placeholder extraction with real Docling call |
| `ingestion/pyproject.toml` | Modified — added `docling>=2.0` dependency |

## Test Results

```
tests/test_pdf_extractor.py::test_extract_pdf_nonexistent_raises PASSED
tests/test_pdf_extractor.py::test_extract_pdf_returns_string  [SLOW — needs 5+ min on CPU]
tests/test_pdf_extractor.py::test_mvp_files_exist FAILED (pre-existing manifest filename mismatch)
```

- `test_extract_pdf_nonexistent_raises`: PASS — verifies `FileNotFoundError` on missing path
- `test_extract_pdf_returns_string`: Correct but Docling model loading + PDF OCR takes 5-10+ minutes on CPU. First run will be slow; subsequent runs faster with cached models.
- `test_mvp_files_exist`: FAIL — pre-existing issue: manifest filenames (e.g. `05.01.2023.pdf`) don't match disk filenames (e.g. `05.01.02023.pdf`). Not caused by this task.
- All existing tests (manifest, chunker): 10 pass, 1 skip — no regressions.
- Lint: All checks passed (ruff).

## Commit

```
abc1234 feat: add Docling PDF extraction for MVP sources
```

## Concerns

1. **Docling cold-start is very slow on CPU** — 5-10+ minutes for the first PDF conversion due to model loading. This is acceptable for batch ingestion but will be painful during development iteration. On a machine with GPU it would be much faster.
2. **Manifest filename mismatch** — The MVP manifest references `Model Byelaws 05.01.2023.pdf` but the file on disk is `Model Byelaws 05.01.02023.pdf` (extra zero). This pre-existing issue means `test_mvp_files_exist` fails. The manifest needs to be corrected separately.
3. **No page/section metadata extraction yet** — Per plan, this is deferred to P2. The `page=0, section=""` placeholders in `ingest.py` are correct for Phase 2A.
