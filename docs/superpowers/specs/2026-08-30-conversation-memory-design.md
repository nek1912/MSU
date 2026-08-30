# Design Spec: Conversation Memory

**Date:** 2026-08-30
**Status:** Approved
**Approach:** A — Simple Prepend (frontend sends history, backend prepends to prompt)

## Problem

The chatbot is fully stateless. Each `/chat` request sends only the current question. The LLM has no memory of prior turns, so follow-up questions like "What about the eligibility for that?" fail because:
1. Retrieval can't resolve "that" without context
2. The LLM prompt has no conversation history

## Solution

Add multi-turn conversation memory by:
1. Storing messages in a Supabase `messages` table
2. Frontend sends last 5 turns with each request
3. Backend prepends history to the user prompt

## Data Model

### Supabase `messages` table

```sql
CREATE TABLE messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(session_id),
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_messages_session ON messages(session_id, created_at DESC);
```

- Stores all messages per session, ordered by time
- TTL: delete messages older than 24h (matching sessions TTL)
- Max ~50 messages per session (auto-trim)

## Backend Changes

### 1. `ChatRequest` model (`routes/chat.py`)

Add `history` field:

```python
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi", "gu"]
    state: str | None = None
    history: list[dict] | None = None  # [{role: "user"|"assistant", content: str}]
```

### 2. `session_store.py` — message persistence

Add three functions:

```python
def save_message(session_id: str, role: str, content: str) -> None:
    """Insert a message into the messages table."""
    sb.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
    }).execute()

def get_history(session_id: str, limit: int = 5) -> list[dict]:
    """Retrieve the last N messages for a session, oldest first."""
    resp = (
        sb.table("messages")
        .select("role", "content")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = resp.data or []
    rows.reverse()  # chronological order
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def trim_messages(session_id: str, keep: int = 50) -> None:
    """Delete messages beyond the most recent `keep` for a session."""
    resp = (
        sb.table("messages")
        .select("id")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .range(keep, 10000)
        .execute()
    )
    ids = [r["id"] for r in (resp.data or [])]
    if ids:
        sb.table("messages").delete().in_("id", ids).execute()
```

### 3. `generation.py` — prepend history to prompt

Update `build_user_prompt`:

```python
def build_user_prompt(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> str:
    hist_text = ""
    if history:
        turns = "\n".join(
            f"{'User' if h['role'] == 'user' else 'Assistant'}: {h['content']}"
            for h in history
        )
        hist_text = f"Previous conversation:\n{turns}\n\n"

    ctx = "\n\n".join(
        f"[chunk:{c.chunk_id[:8]}] ({c.title} — §{c.section} — p.{c.page})\n{c.content}"
        for c in chunks
    )
    return f"{hist_text}Question: {question}\n\nContext:\n{ctx}"
```

### 4. `routes/chat.py` — wire it together

In the `/chat` handler:

```python
# Before retrieval/generation:
history = get_history(req.session_id, limit=5)

# Pass history to build_user_prompt:
user_prompt = build_user_prompt(req.question, chunks, history=history)

# After generating response:
save_message(req.session_id, "user", req.question)
save_message(req.session_id, "assistant", answer)
trim_messages(req.session_id, keep=50)
```

## Frontend Changes

### 1. `lib/api.ts` — accept history param

```typescript
export async function sendChat(params: {
  question: string;
  session_id: string;
  language: string;
  state: string | null;
  history?: Array<{ role: "user" | "assistant"; content: string }>;
}): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  // ... existing error handling
}
```

### 2. `components/ChatWindow.tsx` — pass last 5 turns

In the send handler, before calling `sendChat`:

```typescript
const history = msgs
  .filter((m): m is Msg & { text: string } => !!m.text)
  .slice(-5)
  .map(m => ({ role: m.role, content: m.text }));

const resp = await sendChat({
  question,
  session_id: sessionId,
  language: lang,
  state: null,
  history,
});
```

## Prompt Format

With history, the user prompt becomes:

```
Previous conversation:
User: What is PMFBY?
Assistant: PMFBY is the Pradhan Mantri Fasal Bima Yojana, a crop insurance scheme...
User: What are the eligibility criteria?
Assistant: ...

Question: What documents do I need?

Context:
[chunk:abc12345] (PMFBY Guidelines — §Eligibility — p.3)
To be eligible for PMFBY, a farmer must...
```

## Token Budget

- Each turn ≈ 100-200 tokens
- 5 turns ≈ 500-1000 tokens
- Well within Groq/Llama 70B context window (8K-32K)
- Retrieval chunks ≈ 500-1000 tokens
- System prompt ≈ 200 tokens
- **Total: ~1700-2200 tokens** (well under limits)

## Testing

1. **Unit test `get_history`**: Mock Supabase, verify chronological ordering and limit
2. **Unit test `build_user_prompt` with history**: Verify history is prepended correctly
3. **Unit test `save_message`**: Verify correct insert
4. **Integration test**: Send 3 messages, verify 3rd request has history in prompt
5. **Manual test**: Ask "What is PMFBY?" → "What are the eligibility criteria?" → verify LLM responds contextually

## Migration

Run SQL to create the `messages` table in Supabase. No existing data affected.

## Out of Scope

- Server-side history retrieval on page refresh (frontend localStorage handles UI)
- Streaming with history (future enhancement)
- History across different sessions
- Summarization of long histories
