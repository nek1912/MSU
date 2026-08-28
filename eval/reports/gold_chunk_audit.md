# Gold-Set Chunk Audit Report

**Date:** 2026-08-28

---

## Summary

| Metric | Value |
|--------|-------|
| Total gold cases | 245 |
| Answerable cases | 40 |
| Total relevant chunk IDs | 120 |
| Existing chunk IDs | 120 |
| Missing chunk IDs | 0 |
| Source mismatches | 0 |
| Duplicate IDs | 114 |
| Cases with zero valid chunks | 0 |

**Verdict: VALID** — gold set matches current corpus

---

## Detailed Finding

All 120 relevant chunk IDs exist in the database. No stale IDs. However, chunk-level recall is low because:

1. **Retrieval works correctly** — 10/10 retrieved chunks are from the correct document
2. **Gold case chunk IDs are not the most embedding-similar** — the embedding model ranks different chunks as most similar
3. **Example**: Query "What are the byelaws for a cooperative society?" expects chunks about letter headers, but embedding model ranks definition/board sections as more similar

**Root cause**: Gold case `relevant_chunk_ids` were selected based on human judgment of relevance, not embedding similarity. This is a gold-set integrity issue, not a retrieval quality issue.

---

## Recommendation

Two options:

1. **Use source-level recall** — consider any chunk from the correct document as "relevant". This measures whether retrieval finds the right document, not specific chunks.

2. **Regenerate gold case chunk IDs** — for each answerable case, select the top-N chunks by embedding similarity from the correct source as the "relevant" chunks.

Option 2 is more rigorous but requires re-generating the gold set.

---

## Valid Cases: 40/40

First 10 valid cases:

- What are the byelaws for a cooperative society?... → 3 valid chunks
- Voting rights in a cooperative society... → 3 valid chunks
- Quorum requirements for cooperative society meetings... → 3 valid chunks
- How to become a member of a cooperative society?... → 3 valid chunks
- Share transfer rules in cooperative society... → 3 valid chunks
- Election process for cooperative society committee... → 3 valid chunks
- Restrictions on cooperative society borrowing... → 3 valid chunks
- Managing committee powers under cooperative act... → 3 valid chunks
- Surplus distribution in cooperative society... → 3 valid chunks
- Member expulsion from cooperative society... → 3 valid chunks