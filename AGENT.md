# AI Agent Implementation Plan

The MVP deliberately avoids a full autonomous multi-agent framework. The "AI
agent" is a **single orchestrated RAG agent with tools**. This is a design
choice, not a shortcut: multi-agent frameworks add failure modes (inter-agent
miscommunication, harder debugging, unpredictable tool-call sequences) that are
a bad trade for a system whose core promise is "never guess." A deterministic
router + one tool-using agent is easier to test, easier to debug live during a
demo, and easier for a judge to audit.

## Agent responsibilities

```text
Input (text, or transcribed voice in Tier 2)
      ↓
1. Language detection        → detect hi / en
      ↓
2. Domain classification     → cooperative | pacs | schemes | pmfby |
                                agriculture | finlit | grievance | out_of_scope
      ↓
3. Jurisdiction resolution   → central / selected state
      ↓
4. Tool selection            → retrieve_docs / create_grievance /
                                get_grievance_status / get_source
      ↓
5. Retrieval                 → top-k chunks from pgvector,
                                domain + jurisdiction filtered
      ↓
6. Evidence check             → enough high-score chunks? otherwise abstain
      ↓
7. Grounded generation        → answer strictly from retrieved chunks
      ↓
8. Citation verification      → every citation maps to a real retrieved chunk
      ↓
9. Confidence + abstention    → return structured response
```

## Agent tools (function-calling contract)

```json
[
  {
    "name": "retrieve_docs",
    "description": "Semantic + metadata-filtered retrieval from the official corpus.",
    "parameters": {
      "query": "string",
      "domain": "string",
      "state": "string|null",
      "top_k": "int"
    }
  },
  {
    "name": "create_grievance",
    "description": "Create a prototype grievance reference after required fields are collected.",
    "parameters": {
      "description": "string",
      "category": "string",
      "location": "string|null",
      "language": "string"
    }
  },
  {
    "name": "get_grievance_status",
    "parameters": { "reference": "string" }
  },
  {
    "name": "get_source",
    "parameters": { "source_id": "string" }
  }
]
```

## Agent guardrails — implement these in code, not only in the prompt

A system prompt is a request, not an enforcement mechanism. Every rule below
needs a code path that holds even if the LLM ignores the instruction.

1. If no chunk score exceeds the retrieval threshold, set `abstained: true` and
   do not call the LLM for a factual answer at all — don't generate then discard.
2. Every citation in the output must reference a chunk ID that was actually
   retrieved during the current request. Validate this against the actual
   retrieval result set, not against a general "does this source exist" check.
3. Never fabricate: eligibility, amounts, dates, deadlines, legal clauses,
   contact information. If the retrieved chunks don't contain the specific fact
   asked for, abstain rather than filling the gap with model knowledge.
4. Always return `is_official_submission: false` on grievance responses.
5. Out-of-scope questions receive a scope response, not a guessed answer.

## Reference generation loop (pseudocode)

```python
def handle_turn(user_input, session):
    lang = detect_language(user_input)
    domain = classify_domain(user_input)

    if domain == "out_of_scope":
        return scope_response(lang)

    if domain == "grievance":
        return grievance_agent(user_input, session, lang)

    state = resolve_jurisdiction(session, domain)
    chunks = retrieve_docs(user_input, domain, state, top_k=6)

    if max_score(chunks) < THRESHOLD or len(chunks) == 0:
        return abstain_response(lang, domain)

    answer = generate_grounded_answer(user_input, chunks, lang)
    citations = verify_citations(answer, chunks)

    if not citations:
        return abstain_response(lang, domain)

    return build_response(
        answer, lang, domain,
        confidence=score(chunks),
        citations=citations,
        abstained=False,
    )
```
