# Task 5: Audit Supabase Ingestion

**Files:**
- Read: `backend/migrations/0001_init.sql`
- Read: `backend/app/db.py`
- Read: `ingestion/ingestion/ingest.py` (Supabase operations)

**Interfaces:**
- Consumes: DB schema, Supabase client, ingestion code
- Produces: Supabase ingestion analysis

## Steps

1. Read the `match_chunks` function in `0001_init.sql` and answer:
   - How are documents/chunks inserted?
   - How are old chunks removed during replacement?
   - Are transactions used where appropriate?
   - Can duplicate chunks occur?
   - How is metadata stored?
   - Does retrieval RPC filter by domain, jurisdiction, state?
   - Can central sources coexist correctly with Gujarat sources?
   - Can wrong-state chunks be returned?

2. Record Supabase ingestion behavior in audit report section 6.

## Report Format

Write findings to `docs/superpowers/plans/task-5-report.md` with:
- DB schema analysis
- match_chunks RPC analysis
- Ingestion behavior analysis
- Gaps identified with severity
- Evidence citations
