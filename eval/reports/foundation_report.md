# Foundation Hardening Report

**Date:** 2026-08-26
**Branch:** feat/phase-0-1
**Status:** FOUNDATION-HARDENED

## Executive Summary

The Phase 0-1 foundation has been hardened with two critical correctness fixes, 49 new invariant/contract/failure-injection tests, automated corpus and security checks, and a domain classifier evaluation. The foundation is now ready for Phase 2.

## Test Results

| Category | Count | Status |
|---|---|---|
| Unit tests (original) | 31 | All pass |
| Contract tests | 13 | All pass |
| Evidence gate boundary tests | 18 | All pass |
| LLM failure injection tests | 18 | All pass |
| **Total** | **80** | **All pass** |

## Critical Fixes Applied

### 1. Strict citation rejection (generation.py)
- **Before:** Invalid citations silently discarded; only checked if ≥1 valid citation existed
- **After:** Any invalid citation causes CitationError → abstention
- **Impact:** Prevents responses with mixed valid/invalid citations from being accepted

### 2. Supabase failure handling (chat.py)
- **Before:** Database errors caught by generic `except Exception` → returned 500/503
- **After:** Categorized safe failures (PostgrestAPIError, httpx errors) → return 200 + abstained; unknown failures → 500 (programmer bugs visible)
- **Impact:** Frozen contract now holds under dependency failures

### 3. AnchorStore domain-vector index mismatch (domains.py)
- **Before:** `self.domains` had 7 elements, `self.vectors` had 70 rows; `classify()` used argmax index into domains list → IndexError in production
- **After:** One averaged vector per domain; index mapping correct
- **Impact:** Domain classification now works with 7+ domains

## Evaluation Results

### Domain Classifier (keyword-only path)

| Metric | Value |
|---|---|
| Overall accuracy | 74.4% |
| Out-of-scope rejection | 100% |
| Strongest domains | pmfby (1.00 F1), pacs (0.92 F1) |
| Weakest domains | schemes (0.57 F1), grievance (0.57 F1) |

**Note:** This tests keyword path only. Embedding path (not evaluated) would improve recall for domains with weak keyword coverage.

### Corpus Quality

| Metric | Value |
|---|---|
| Files checked | 12 |
| Files passed | 12 |
| Placeholders found | 24 (source_quality: wikipedia_proxy markers) |
| Duplicate source_ids | 0 |

**Status:** Corpus contains Wikipedia proxy content with TODO markers. Must be replaced with verbatim government text before Phase 3 ingestion.

### Security

| Check | Status |
|---|---|
| .env not tracked | PASS |
| .gitignore includes .env | PASS |
| No API keys in source | PASS |
| No NEXT_PUBLIC secrets | PASS |
| No hardcoded credentials | PASS |

## Component Status

| Component | Status | Confidence | Measured |
|---|---|---|---|
| API contract | Tested (13 contract tests) | High | Yes |
| Citation verification | Strict (any invalid = abstain) | High | Yes |
| Evidence gate | Boundary-tested (18 tests) | High | Yes |
| Domain routing | 74.4% keyword-only (43 cases) | Medium | Partial |
| LLM fallback | Failure-injected (18 tests) | High | Yes |
| Session handling | Design reviewed | Medium-high | No |
| Ingestion pipeline | Idempotent, chunked | Medium | No |
| Corpus quality | Placeholder content | Low | Yes |
| Security | All checks pass | High | Yes |
| Reproducibility | Not yet demonstrated | Low | No |

## Remaining Risks

### P0 (Phase 2A gate — must complete before new features)
1. **Corpus placeholders** — Wikipedia proxy content must be replaced with verbatim official government text before any accuracy evaluation
2. **Hybrid domain accuracy not measured** — 74.4% is keyword-only; hybrid (keyword + embedding) accuracy unknown
3. **Domain evaluation set too small** — 43 cases insufficient; need 30-50/domain + adversarial

### P1 (before final demo)
4. **No performance baseline** — Latency not measured
5. **No concurrency testing** — Race conditions untested

### P2 (acceptable for hackathon)
6. **Domain keyword gaps** — 25.6% keyword misclassification (may be acceptable if hybrid accuracy is high)
7. **Whitespace-only questions** — Not rejected by Pydantic validation
8. **Provider malformed responses** — JSONDecodeError/KeyError not caught by fallback chain

## Exit Condition

### Code/Integrity Gate (PASSED)
- [x] All existing tests pass (31/31)
- [x] All new invariant tests pass (49/49)
- [x] Citation integrity: strict invalid rejection verified
- [x] Provider failures: 18 failure injection cases pass
- [x] Security scan: 5/5 checks pass
- [x] Corpus placeholder detection: automated

### Corpus/Retrieval Quality Gate (PENDING)
- [ ] Official corpus replacement (no placeholders)
- [ ] Hybrid domain accuracy measured (not just keyword-only)
- [ ] Evaluation set expanded to 30-50/domain
- [ ] Retrieval Recall@5 measured
- [ ] Jurisdiction contamination = 0
- [ ] Unsafe-answer rate ≈ 0
- [ ] Performance baseline recorded
- [ ] Concurrency tested

**Status: FOUNDATION-HARDENED — CODE/INTEGRITY GATE PASSED; CORPUS AND RETRIEVAL QUALITY GATE PENDING.**

The software behaves safely under many expected failures. Accuracy over the real government corpus has not yet been demonstrated. The next milestone is official corpus replacement + retrieval/domain evaluation before adding new user-facing functionality.
