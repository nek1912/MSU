# Task 11: Integration Test — End-to-End Flow

## What Was Implemented

Created `tests/test_integration_sarvam.py` with two integration tests:

1. **`test_strip_citations_removes_all_formats`** — Verifies `strip_citations()` removes all `[chunk:xxx]` formats from answers, including standard IDs, web-sourced IDs, multiple citations, and edge cases like empty IDs.

2. **`test_evidence_assessment_flow`** — Tests the full assessment flow from `RAGResult` → `EvidenceController.assess_evidence()` → `EvidenceAssessment`, verifying source role determination (`WEB_PRIMARY` for current/dynamic queries), sufficiency check, and assessment text generation.

## Test Results

Both tests passed:
```
tests/test_integration_sarvam.py::test_strip_citations_removes_all_formats PASSED
tests/test_integration_sarvam.py::test_evidence_assessment_flow PASSED
2 passed in 9.20s
```

## Files Changed

- **Created:** `backend/tests/test_integration_sarvam.py`

## Commit

- `04a83a4` — test: add integration tests for Sarvam migration end-to-end flow
