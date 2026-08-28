# Gold Set Final Validation Report

**Date:** 2026-08-28  
**Status:** GOLD SET — VALIDATED

---

## Summary

| Metric | Value |
|--------|-------|
| Total cases | 245 |
| Answerable | 40 |
| Unanswerable | 205 |
| Cases corrected | 14 |
| Cases verified | 40 |

---

## Corrections Applied

### PMFBY Cases (9 corrections)
- Fixed 9 cases that used wrong gold chunk `f945e35d` (Coverage of Risks)
- Assigned topic-specific gold chunks for: premium rates, eligibility, enrollment, technology, coverage area, empanelment, indemnity, exclusion period

### PACS Cases (5 corrections)
- Fixed cases with wrong gold chunks
- Assigned topic-specific gold chunks for: surplus, dividend, bylaw amendment

---

## Validation Results

| Check | Status |
|-------|--------|
| All gold chunks exist in DB | ✅ |
| All gold chunks resolve to documents | ✅ |
| All gold chunks have correct source_id | ✅ |
| All gold chunks have correct domain | ✅ |
| No mechanically repeated chunks | ✅ |
| All cases have gold_rationale | ✅ |

---

## Retrieval Metrics After Gold Fix

| Metric | Before | After | Threshold | Gap |
|--------|--------|-------|-----------|-----|
| Recall@1 | 0.350 | 0.375 | 0.40 | -0.025 |
| Recall@3 | 0.500 | 0.525 | 0.60 | -0.075 |
| Recall@5 | 0.600 | 0.625 | 0.80 | -0.175 |
| MRR | 0.450 | 0.475 | 0.50 | -0.025 |

---

## Failure Analysis

| Type | Count | Percentage |
|------|-------|------------|
| SUCCESS | 29 | 72.5% |
| EMBEDDING_RANKING | 7 | 17.5% |
| PARTIAL_RETRIEVAL | 4 | 10% |

---

## Corpus Coverage

| Domain | Answerable Cases | Status |
|--------|------------------|--------|
| pacs_governance | 21 | ✅ Covered |
| pmfby | 19 | ✅ Covered |
| financial_inclusion | 0 | UNVALIDATED |
| schemes | 0 | UNVALIDATED |
| agriculture | 0 | UNVALIDATED |
| grievance | 0 | UNVALIDATED |

---

## Frozen State

| Item | Hash/Version |
|------|--------------|
| Corpus snapshot | 2fc08e7d9e959de4 |
| Gold set | 2026-08-28 validated |
| Embedding profile | jina-embeddings-v3 / 768d |
| Git commit | 861bae9 |

---

## Verdict

**GOLD SET — VALIDATED**

All 40 answerable cases have semantically correct gold chunks. The gold set is now trustworthy for evaluation.
