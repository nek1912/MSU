# Design

## Design principles

- Evidence-first: never answer without grounded, cited sources.
- Fail safe: abstain over guessing. Label prototype grievances clearly.
- Simplicity: a single orchestrated RAG agent with tools, not an autonomous
  multi-agent framework. See AGENT.md for why.
- Provider abstraction: swap LLM/voice providers without touching business logic.

## Agent design

Single orchestrator with tools: `retrieve_docs, create_grievance,
get_grievance_status, get_source`. Full tool contracts and guardrails are in
AGENT.md — this file covers the turn pipeline and retrieval mechanics.

Turn pipeline:
1. Detect language (IndicLID, or provider-native detection)
2. Classify domain (embedding similarity to domain anchors, or a small
   classifier — not a full LLM call if avoidable, for latency and cost)
3. Resolve jurisdiction (session state + domain)
4. Retrieve (pgvector, domain+state filter applied before vector search, top_k=6)
5. Evidence gate: max score >= THRESHOLD, else abstain
6. Generate grounded answer strictly from retrieved chunks
7. Verify citations: each maps to a retrieved chunk ID
8. Return structured response

## Domain taxonomy

`pacs_governance | pacs_computerization | pmfby | financial_inclusion | schemes | agriculture | grievance | out_of_scope`

## Retrieval design

- Chunk size ~500-800 tokens, ~80-token overlap.
- Metadata filter (domain, jurisdiction, state) applied *before* vector search —
  this is what prevents a Maharashtra question from surfacing a Gujarat by-law.
- Store page + section on every chunk for precise, checkable citations.
- Confidence = normalized top-k similarity + coverage heuristic (not an LLM
  self-reported confidence score — those aren't reliable).

## Grievance state machine

```
NEW → NEEDS_INFORMATION → CLASSIFIED → CREATED → IN_PROGRESS → RESOLVED
```

Extracted entities: `category, location, department, date, missing_fields`.
Reference format: `DEMO-<DOMAIN>-<5digits>`. `is_official_submission` is always
`false` — there is no real integration to a government grievance system.

## Response contract (chat)

```json
{
  "answer": "string",
  "language": "en|hi",
  "domain": "string",
  "confidence": 0.0,
  "citations": [{
    "chunk_id": "string (stable app id)",
    "document_id": "uuid",
    "source_file": "string",
    "title": "string",
    "page": 0,
    "page_start": 0,
    "page_end": 0,
    "section": "string",
    "subsection": "string",
    "clause": "string",
    "url": "string"
  }],
  "abstained": false,
  "follow_up_question": null
}
```

Out-of-scope queries return `domain: "out_of_scope"`, `abstained: true`, and a
controlled scope message (no factual LLM answer). Retrieval is hybrid
(dense + lexical RRF); the reranker is wired but disabled pending curated eval.

## Prompting rules

- Provide only retrieved chunks as context, each tagged with an ID and source.
- Require the model to cite chunk IDs; if citations don't validate against
  what was actually retrieved, drop the answer and return `abstained: true`.
- System prompt forbids using outside/parametric knowledge for factual claims.
- This is enforced in code (citation verification step), not trusted to hold
  from the prompt alone.

## Evaluation design

Build ~140 golden test cases: 20 each across cooperative, pacs, schemes, pmfby,
agriculture, finlit, grievance. Each case: `question, expected_domain,
expected_source, answerable (bool), required_fact`.

Metrics: groundedness, correctness, citation accuracy, latency, abstention
correctness, domain accuracy, jurisdiction accuracy.

Ragas (github.com/vibrantlabsai/ragas — this org was formerly explodinggradients,
same project) can be used optionally for scoring. Do not make it a core runtime
dependency — it's an eval-time tool, not something the live chat path depends on.

## UX design

- Show a "Searching official sources" state while retrieving.
- Flow: answer → source cards → confidence → optional "Create grievance" action.
- Never expose internal terms (vector database, embeddings, retrieval
  internals, model infrastructure) to end users.
- Mobile-first responsive layout.

## UX error states to support

`provider unavailable, provider timeout, empty input, unsupported language,
out-of-scope question, insufficient evidence, grievance missing information,
database unavailable`

## Security / privacy

- API keys server-side only, never in frontend code or Git.
- Minimal grievance PII; label clearly as prototype data.
- Use synthetic data for demos and testing, not real personal information.
- No unnecessary personal information sent to LLM providers.
- Structured logs without secrets or PII.
