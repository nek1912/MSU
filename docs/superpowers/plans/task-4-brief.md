# Task 4: Audit Embedding Behavior

**Files:**
- Read: `backend/app/providers/embeddings.py`
- Read: `backend/app/config.py` (EMBED_DIMS, REQUEST_TIMEOUT_S)

**Interfaces:**
- Consumes: Embedding provider code
- Produces: Embedding behavior analysis

## Steps

1. Read `backend/app/providers/embeddings.py` and answer:
   - How is Gemini embedding called?
   - Does it process one string at a time or batches?
   - Does it enforce expected vector dimension?
   - What happens on malformed provider output?
   - What happens on rate limiting?
   - What happens on timeout?
   - What happens if embedding generation partially succeeds?
   - Can failed embeddings create incomplete ingestion?

2. Record embedding behavior in audit report section 5.

## Report Format

Write findings to `docs/superpowers/plans/task-4-report.md` with:
- Embedding provider analysis
- Error handling behavior
- Gaps identified with severity
- Evidence citations
