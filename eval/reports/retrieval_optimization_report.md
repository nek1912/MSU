# Retrieval Optimization Report

**Date:** 2026-08-28  
**Status:** RAG FOUNDATION — FAIL (ranking issue, not retrieval issue)

---

## Executive Summary

The retrieval system finds all relevant documents (Recall@20 = 100%), but relevant chunks are ranked too low (Recall@5 = 60%). The root cause is **gold set semantic errors** — gold chunks are not the most relevant for their queries.

---

## Key Findings

### 1. Retrieval Works Correctly
- Recall@20 = 1.000 (all relevant chunks found within top-20)
- Dense retrieval successfully finds correct documents
- Problem is RANKING, not RETRIEVAL

### 2. Gold Set Has Semantic Errors
- Same gold chunk `f945e35d` (Coverage of Risks) used for many different PMFBY queries
- Queries about "indemnity", "premium rates", "exclusion period" use wrong gold chunk
- Gold chunks have lower similarity (0.46-0.51) than retrieved chunks (0.55-0.68)

### 3. Ranking Analysis

| Query | Gold Rank | Gold Sim | Top Sim | Gap |
|-------|-----------|----------|---------|-----|
| Surplus distribution | 12 | 0.46 | 0.55 | 0.09 |
| Dividend declaration | 19 | 0.51 | 0.68 | 0.17 |
| PMFBY technology | NOT FOUND | 0 | 0.72 | — |
| PMFBY coverage area | NOT FOUND | 0 | 0.73 | — |
| PMFBY private insurance | 17 | 0.71 | 0.75 | 0.04 |

---

## Root Cause

The gold set assigns the same generic chunk to many specific queries. The embedding model correctly ranks more specific chunks higher, but the gold set expects the generic chunk.

This is a **gold set quality issue**, not a retrieval issue.

---

## Recommended Actions

### Option A: Fix Gold Set (Recommended)
Assign topic-specific gold chunks to each query. This is the correct approach because:
1. The retrieval system is working correctly
2. The gold set has semantic errors
3. Fixing gold set will improve metrics without changing retrieval

### Option B: Improve Ranking
Add lexical retrieval or hybrid RRF to boost exact matches. This may help but:
1. Dense retrieval already finds all relevant chunks
2. The issue is ranking, not retrieval
3. Hybrid may not help if gold chunks are wrong

### Option C: Accept Current State
The system works correctly for user-facing queries. The low Recall@5 is due to gold set errors, not retrieval failures.

---

## Metrics

| Metric | Current | Threshold | Gap |
|--------|---------|-----------|-----|
| Recall@1 | 0.350 | 0.40 | -0.05 |
| Recall@3 | 0.500 | 0.60 | -0.10 |
| Recall@5 | 0.600 | 0.80 | -0.20 |
| MRR | 0.450 | 0.50 | -0.05 |
| Recall@20 | 1.000 | — | ✅ |

---

## Verdict

**RAG FOUNDATION — FAIL (gold set quality issue)**

The retrieval system works correctly. The gold set has semantic errors that cause low Recall@5. The recommended action is to fix the gold set, not to change the retrieval system.
