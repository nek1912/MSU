# Task 3: Audit Metadata Model

**Files:**
- Read: `corpus/manifests/mvp_sources.yaml` (metadata fields)
- Read: `backend/migrations/0001_init.sql` (documents table schema)
- Read: `corpus/seeds/*.md` (frontmatter fields)

**Interfaces:**
- Consumes: MVP manifest, DB schema, seed file metadata
- Produces: Metadata model gap analysis

## Steps

1. List all metadata fields in mvp_sources.yaml
2. List all fields in documents table from 0001_init.sql
3. Compare metadata models and identify missing fields
4. Determine if missing metadata is required by Gate 2 invariants
5. Record metadata model gaps in audit report section 4

## Report Format

Write findings to `docs/superpowers/plans/task-3-report.md` with:
- MVP manifest metadata fields
- DB schema fields
- Gap analysis
- Gate 2 requirement check
- Evidence citations
