# Task 2: Audit Ingestion Pipeline

**Files:**
- Read: `ingestion/ingestion/ingest.py`
- Read: `ingestion/ingestion/loader.py`
- Read: `ingestion/ingestion/chunker.py`

**Interfaces:**
- Consumes: Current ingestion code
- Produces: Ingestion pipeline gap analysis

## Steps

1. Read `ingestion/ingestion/ingest.py` and answer:
   - How does it discover files? (line 41: `SEEDS_DIR.glob("*.md")`)
   - Can it accidentally ingest hold/non-MVP files?
   - Can it read the MVP manifest directly?
   - Is ingestion deterministic?
   - Is ingestion idempotent?
   - What happens if same document ingested twice?
   - What happens if document replaced?
   - Can stale chunks remain?
   - Is source_id preserved?
   - Is document_id deterministic?
   - Is chunk_id deterministic?

2. Read `ingestion/ingestion/loader.py` and answer:
   - How does it parse chunk files?
   - What format does it expect?

3. Read `ingestion/ingestion/chunker.py` and answer:
   - What chunking algorithm is used?
   - Is it heading-aware?
   - Does it preserve page boundaries?
   - Does it preserve section metadata?
   - What token/chunk limits are implemented?
   - Can chunks be empty?
   - Is overlap deterministic?

4. Record ingestion pipeline gaps in audit report section 2.

## Report Format

Write findings to `docs/superpowers/plans/task-2-report.md` with:
- Ingestion pipeline analysis (file discovery, idempotency, etc.)
- Loader behavior analysis
- Chunker behavior analysis
- Gaps identified with severity (P0/P1/P2)
- Evidence citations (file paths, line numbers)
