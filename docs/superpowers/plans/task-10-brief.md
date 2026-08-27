# Task 10: Audit Security & Resource Risks

**Files:**
- Read: `ingestion/ingestion/ingest.py` (path handling)
- Read: `backend/app/providers/embeddings.py` (API key handling)
- Read: `backend/app/config.py` (environment variables)

**Interfaces:**
- Consumes: Security-relevant code
- Produces: Security and resource risk analysis

## Steps

1. Check .env handling — verify .env is never committed, API keys never enter corpus metadata
2. Check path traversal — verify raw document paths do not leak into user responses
3. Check arbitrary file ingestion — verify only manifest-approved files are ingestible
4. Analyze memory risks for 8GB RAM / i3 CPU machine
5. Record security and resource risks in audit report sections 10-11

## Report Format

Write findings to `docs/superpowers/plans/task-10-report.md` with:
- .env handling analysis
- Path traversal analysis
- Arbitrary file ingestion analysis
- Memory risk analysis
- Evidence citations
