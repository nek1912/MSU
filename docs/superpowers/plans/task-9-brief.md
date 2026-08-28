# Task 9: Audit Failure Handling

**Files:**
- Read: `ingestion/ingestion/ingest.py` (error handling)
- Read: `backend/app/providers/embeddings.py` (error handling)
- Read: `backend/app/retrieval.py` (error handling)
- Read: `backend/app/routes/chat.py` (error handling)

**Interfaces:**
- Consumes: Error handling code across pipeline
- Produces: Failure handling analysis

## Steps

1. Analyze extraction failures — how are PDF extraction failures reported?
2. Analyze embedding failures — what happens on malformed output, rate limiting, timeout?
3. Analyze retrieval failures — how is failure distinguished from "no evidence"?
4. Record failure handling in audit report section 9.

## Report Format

Write findings to `docs/superpowers/plans/task-9-report.md` with:
- Extraction failure handling
- Embedding failure handling
- Retrieval failure handling
- Gaps identified with severity
- Evidence citations
