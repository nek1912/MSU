# Task 7: Audit Citation Behavior

**Files:**
- Read: `backend/app/generation.py`
- Read: `backend/app/routes/chat.py` (citation handling)

**Interfaces:**
- Consumes: Generation code, chat route
- Produces: Citation behavior analysis

## Steps

1. Read `backend/app/generation.py` and answer:
   - Does generation only receive retrieved evidence?
   - Does it know source metadata?
   - Can it cite a chunk not actually retrieved?
   - Does citation verification verify actual retrieved set?
   - Does it verify source/domain/jurisdiction?
   - Does zero citation cause failure for answerable answers?
   - Does unsupported evidence cause abstention?

2. Record citation behavior in audit report section 8.

## Report Format

Write findings to `docs/superpowers/plans/task-7-report.md` with:
- Generation behavior analysis
- Citation verification analysis
- Gaps identified with severity
- Evidence citations
