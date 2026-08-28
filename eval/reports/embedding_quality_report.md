# Embedding Quality Report

**Date:** 2026-08-28  
**Status:** EMBEDDING HEALTHY

---

## Embedding Profile

| Property | Value |
|----------|-------|
| Provider | JinaEmbeddingProvider |
| Model | jina-embeddings-v3 |
| Dimension | 768 |
| Normalization | Unit-normalized (API default) |
| Query encoding | Same as documents |
| Document encoding | Same as queries |
| Similarity metric | Cosine (1 - cosine_distance) |

---

## Controlled Pair Test

| Pair Type | Cosine Similarity | Interpretation |
|-----------|-------------------|----------------|
| Identical text | 1.0000 | Perfect match |
| Paraphrase | 0.8794 | High similarity |
| Related content | 0.7232 | Good similarity |
| Unrelated content | 0.4141 | Low similarity |

**Separation:** Related (0.72) vs Unrelated (0.41) — clear margin of 0.31

---

## Real Case Test

| Query | Gold Chunk | Cosine |
|-------|------------|--------|
| "What are the byelaws for a cooperative society?" | Definitions section | 0.7060 |

---

## Consistency Verification

| Check | Result |
|-------|--------|
| All chunks dimension = 768 | ✅ 226/226 |
| All chunks norm ≈ 1.0 | ✅ 226/226 |
| Re-embedding cosine > 0.99 | ✅ 0.999985 |
| Python cosine = SQL cosine | ✅ 0.000000 difference |

---

## Conclusion

**Embedding health: HEALTHY**

The Jina jina-embeddings-v3 model produces:
- Unit-normalized vectors
- Meaningful similarity scores
- Clear separation between related and unrelated content
- Consistent results across re-embedding

The embedding foundation is sound. Retrieval quality issues are NOT caused by embedding model problems.
