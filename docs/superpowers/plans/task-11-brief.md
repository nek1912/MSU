# Task 11: Audit Production vs Evaluation Consistency

**Files:**
- Read: `eval/run_retrieval_eval.py`
- Read: `backend/app/retrieval.py`
- Read: `backend/app/routes/chat.py`

**Interfaces:**
- Consumes: Production and evaluation retrieval code
- Produces: Consistency analysis

## Steps

1. Compare production retrieval and Gate 2 evaluation implementations
2. Check if they use same: chunk format, embeddings, metadata, filtering, Supabase RPC, top-K, scoring assumptions
3. Document discrepancies
4. Record production-vs-evaluation inconsistencies in audit report section 12

## Report Format

Write findings to `docs/superpowers/plans/task-11-report.md` with:
- Production retrieval analysis
- Evaluation retrieval analysis
- Comparison results
- Discrepancies found
- Evidence citations
