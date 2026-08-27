# Task 6: Audit Retrieval Behavior

**Files:**
- Read: `backend/app/retrieval.py`
- Read: `backend/app/routes/chat.py`
- Read: `backend/app/config.py` (thresholds)

**Interfaces:**
- Consumes: Retrieval code, chat route, config
- Produces: Retrieval behavior analysis

## Steps

1. Read `backend/app/retrieval.py` and answer:
   - What exact retrieval function does /chat use?
   - Does it use same retrieval as Gate 2 evaluation?
   - Is reranking implemented or planned?
   - What is current top-K?
   - How are empty retrieval results handled?
   - How is retrieval failure distinguished from "no evidence"?
   - Does evidence gating happen before generation?
   - Can weak retrieval still reach LLM?

2. Read `backend/app/routes/chat.py` and answer:
   - How does the chat route use retrieval?
   - What happens on retrieval failure?

3. Record retrieval behavior in audit report section 7.

## Report Format

Write findings to `docs/superpowers/plans/task-6-report.md` with:
- Retrieval function analysis
- Chat route integration analysis
- Evidence gating behavior
- Gaps identified with severity
- Evidence citations
