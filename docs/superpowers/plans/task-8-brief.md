# Task 8: Audit Gold Cases Consistency

**Files:**
- Read: `eval/gold_cases.yaml`
- Read: `corpus/manifests/mvp_sources.yaml`
- Read: `sources.yaml`

**Interfaces:**
- Consumes: Gold cases, MVP manifest, sources.yaml
- Produces: Gold cases consistency analysis

## Steps

1. List all source_ids referenced in gold_cases.yaml
2. List all source_ids in mvp_sources.yaml
3. Compare source_ids and identify mismatches
4. Validate gold case structure for answerable/unanswerable cases
5. Record gold cases inconsistencies in audit report section 12

## Report Format

Write findings to `docs/superpowers/plans/task-8-report.md` with:
- Gold case source_ids
- MVP manifest source_ids
- Mismatch analysis
- Structure validation
- Evidence citations
