# Task 1: Audit Manifest & Filesystem Consistency

**Files:**
- Read: `corpus/manifests/mvp_sources.yaml`
- Read: `corpus/manifests/hold_sources.yaml`
- Verify: All MVP manifest files exist on disk

**Interfaces:**
- Consumes: MVP manifest definitions
- Produces: Manifest-filesystem consistency report

## Steps

1. Read `corpus/manifests/mvp_sources.yaml` and extract all source entries with their file paths.
2. For each source in MVP manifest, verify the file exists at the specified path. Check:
   - `corpus/seeds/Model Byelaws 05.01.2023.pdf`
   - `corpus/seeds/Revised Scheme guidelines (Computerization of PACS project).pdf`
   - `corpus/seeds/Corrigendum and letter Jun 12, 2023.pdf`
   - `corpus/seeds/operational_guidelines_pmfby.pdf`
   - `corpus/seeds/NSFI_2025_30.pdf`
3. Check that hold_sources.yaml files are not referenced by any ingestion code.
4. Record manifest-filesystem consistency in audit report section 1.

## Report Format

Write findings to `docs/superpowers/plans/task-1-report.md` with:
- Files verified to exist
- Files missing
- Hold file ingestion risk assessment
- Evidence citations (file paths, line numbers)
