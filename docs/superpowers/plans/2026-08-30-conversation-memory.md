# Conversation Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add multi-turn conversation memory so the LLM remembers prior turns in a session.

**Architecture:** Frontend sends last 5 turns with each `/chat` request. Backend stores messages in Supabase `messages` table, retrieves history, and prepends it to the user prompt before generation.

**Tech Stack:** FastAPI, Supabase Postgres, Pydantic, Next.js, TypeScript

## Global Constraints

- Python 3.14, Pydantic v2, type hints everywhere
- Supabase Postgres + pgvector
- Frontend: Next.js 16, React 19, TypeScript
- No bare `except` — always catch specific exceptions
- API keys in backend env vars only, never in frontend

---

### Task 1: Create Supabase `messages` table

**Files:**
- Create: `backend/migrations/0004_messages_table.sql`

**Interfaces:**
- Produces: `messages` table with `id`, `session_id`, `role`, `content`, `created_at`

- [ ] **Step 1: Write the migration SQL**

```sql
-- backend/migrations/0004_messages_table.sql
CREATE TABLE IF NOT EXISTS messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID NOT NULL REFERENCES sessions(session_id),
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_session
  ON messages(session_id, created_at DESC);
```

- [ ] **Step 2: Run migration in Supabase SQL editor**

Go to Supabase Dashboard → SQL Editor → paste the SQL → Run.

Verify: `SELECT * FROM messages LIMIT 1;` returns empty set (table exists).

- [ ] **Step 3: Commit**

```bash
git add backend/migrations/0004_messages_table.sql
git commit -m "feat: add messages table migration for conversation memory"
```

---

### Task 2: Add message persistence functions to `session_store.py`

**Files:**
- Modify: `backend/app/session_store.py:1-33` (append new functions)

**Interfaces:**
- Consumes: `get_supabase()` from `app.db`
- Produces: `save_message(session_id, role, content)`, `get_history(session_id, limit)`, `trim_messages(session_id, keep)`

- [ ] **Step 1: Write tests for message functions**

```python
# backend/tests/test_session_store_messages.py
import uuid
from unittest.mock import MagicMock, patch


@patch("app.session_store.get_supabase")
def test_save_message_inserts(mock_sb):
    from app.session_store import save_message
    sb = MagicMock()
    mock_sb.return_value = sb
    save_message(str(uuid.uuid4()), "user", "Hello")
    sb.table.assert_called_with("messages")
    sb.table().insert.assert_called_once()
    call_args = sb.table().insert.call_args[0][0]
    assert call_args["role"] == "user"
    assert call_args["content"] == "Hello"


@patch("app.session_store.get_supabase")
def test_get_history_returns_chronological(mock_sb):
    from app.session_store import get_history
    sb = MagicMock()
    mock_sb.return_value = sb
    # Simulate Supabase returning newest-first
    sb.table().select().eq().order().limit().execute.return_value.data = [
        {"role": "assistant", "content": "B"},
        {"role": "user", "content": "A"},
    ]
    result = get_history(str(uuid.uuid4()), limit=5)
    assert result == [{"role": "user", "content": "A"}, {"role": "assistant", "content": "B"}]


@patch("app.session_store.get_supabase")
def test_get_history_returns_empty_on_error(mock_sb):
    from app.session_store import get_history
    sb = MagicMock()
    mock_sb.return_value = sb
    sb.table().select().eq().order().limit().execute.side_effect = Exception("table missing")
    result = get_history(str(uuid.uuid4()), limit=5)
    assert result == []


@patch("app.session_store.get_supabase")
def test_trim_messages_deletes_old(mock_sb):
    from app.session_store import trim_messages
    sb = MagicMock()
    mock_sb.return_value = sb
    sb.table().select().eq().order().range().execute.return_value.data = [
        {"id": "old-1"}, {"id": "old-2"}
    ]
    trim_messages(str(uuid.uuid4()), keep=50)
    sb.table().delete.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_session_store_messages.py -v`
Expected: FAIL (module not imported / function not found)

- [ ] **Step 3: Implement message functions**

Append to `backend/app/session_store.py`:

```python
def save_message(session_id: str, role: str, content: str) -> None:
    """Insert a message into the messages table."""
    try:
        get_supabase().table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
        }).execute()
    except Exception:
        pass  # Non-UUID session IDs or missing table — silently skip


def get_history(session_id: str, limit: int = 5) -> list[dict]:
    """Retrieve the last N messages for a session, oldest first."""
    try:
        resp = (
            get_supabase().table("messages")
            .select("role", "content")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        rows = resp.data or []
        rows.reverse()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception:
        return []


def trim_messages(session_id: str, keep: int = 50) -> None:
    """Delete messages beyond the most recent `keep` for a session."""
    try:
        resp = (
            get_supabase().table("messages")
            .select("id")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .range(keep, 10000)
            .execute()
        )
        ids = [r["id"] for r in (resp.data or [])]
        if ids:
            get_supabase().table("messages").delete().in_("id", ids).execute()
    except Exception:
        pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_session_store_messages.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/session_store.py backend/tests/test_session_store_messages.py
git commit -m "feat: add save_message, get_history, trim_messages to session_store"
```

---

### Task 3: Update `generation.py` to accept and prepend history

**Files:**
- Modify: `backend/app/generation.py:65-70` (`build_user_prompt` signature)
- Create: `backend/tests/test_generation_history.py`

**Interfaces:**
- Consumes: `history: list[dict] | None` (each dict has `role` and `content` keys)
- Produces: Updated `build_user_prompt(question, chunks, history=None)` → str

- [ ] **Step 1: Write failing test for history prepended to prompt**

```python
# backend/tests/test_generation_history.py
from app.generation import build_user_prompt
from app.retrieval import RetrievedChunk


def _make_chunk(content: str = "test") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="aaaabbbb-1111-2222-3333-444444444444",
        stable_chunk_id="doc:p1:c0",
        document_id="doc-id",
        title="Test Doc",
        page=1,
        page_start=1,
        page_end=1,
        section="Sec",
        subsection=None,
        clause=None,
        content=content,
        similarity=0.8,
        source_url="https://example.com",
        source_file="example.com",
        domain="test",
        jurisdiction="central",
        state=None,
    )


def test_build_user_prompt_no_history():
    prompt = build_user_prompt("What is PMFBY?", [_make_chunk()])
    assert "Previous conversation:" not in prompt
    assert "Question: What is PMFBY?" in prompt


def test_build_user_prompt_with_history():
    history = [
        {"role": "user", "content": "What is PMFBY?"},
        {"role": "assistant", "content": "PMFBY is a crop insurance scheme [chunk:aaaabbbb]."},
    ]
    prompt = build_user_prompt("What are the eligibility criteria?", [_make_chunk()], history=history)
    assert "Previous conversation:" in prompt
    assert "User: What is PMFBY?" in prompt
    assert "Assistant: PMFBY is a crop insurance scheme" in prompt
    assert "Question: What are the eligibility criteria?" in prompt


def test_build_user_prompt_empty_history():
    prompt = build_user_prompt("test", [_make_chunk()], history=[])
    assert "Previous conversation:" not in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_generation_history.py -v`
Expected: FAIL (`TypeError: build_user_prompt() got an unexpected keyword argument 'history'`)

- [ ] **Step 3: Update `build_user_prompt` to accept history**

In `backend/app/generation.py`, replace `build_user_prompt` (lines 65-70):

```python
def build_user_prompt(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> str:
    """Build the RAG user prompt from question + numbered context chunks.

    When history is provided, prepend it so the LLM has conversational context
    for resolving pronouns and follow-up references.
    """
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

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_generation_history.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/generation.py backend/tests/test_generation_history.py
git commit -m "feat: build_user_prompt accepts conversation history"
```

---

### Task 4: Wire history into `/chat` route

**Files:**
- Modify: `backend/app/routes/chat.py:62-68` (`ChatRequest` model)
- Modify: `backend/app/routes/chat.py:135-202` (`chat` handler)
- Create: `backend/tests/test_chat_history.py`

**Interfaces:**
- Consumes: `ChatRequest.history: list[dict] | None`, `get_history()`, `save_message()`, `trim_messages()`
- Produces: History is stored after each turn, prepended to prompt on next turn

- [ ] **Step 1: Write failing test for history in ChatRequest**

```python
# backend/tests/test_chat_history.py
import uuid
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_request_accepts_history():
    """ChatRequest should accept an optional history field."""
    payload = {
        "question": "What are the eligibility criteria?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
        "history": [
            {"role": "user", "content": "What is PMFBY?"},
            {"role": "assistant", "content": "PMFBY is a crop insurance scheme."},
        ],
    }
    # Validate the model directly (not the full endpoint)
    from app.routes.chat import ChatRequest
    req = ChatRequest(**payload)
    assert len(req.history) == 2
    assert req.history[0]["role"] == "user"


def test_chat_request_history_optional():
    """history=None should be valid."""
    from app.routes.chat import ChatRequest
    req = ChatRequest(
        question="test", session_id=str(uuid.uuid4()),
        language="en", state=None
    )
    assert req.history is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_chat_history.py -v`
Expected: FAIL (`ValidationError: 1 validation error for ChatRequest — history: Field required` or similar)

- [ ] **Step 3: Add `history` field to `ChatRequest`**

In `backend/app/routes/chat.py`, update the model (line 62-68):

```python
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi", "gu"]
    state: str | None = None
    as_of_date: str | None = None
    history: list[dict] | None = None  # [{role: "user"|"assistant", content: str}]
```

- [ ] **Step 4: Run model tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_chat_history.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/app/routes/chat.py backend/tests/test_chat_history.py
git commit -m "feat: add history field to ChatRequest model"
```

---

### Task 5: Wire history into chat handler logic

**Files:**
- Modify: `backend/app/routes/chat.py:135-202` (chat handler)

**Interfaces:**
- Consumes: `get_history()`, `save_message()`, `trim_messages()` from Task 2
- Consumes: `build_user_prompt()` with history param from Task 3

- [ ] **Step 1: Write failing test for history retrieval and persistence**

```python
# Add to backend/tests/test_chat_history.py

@patch("app.routes.chat.trim_messages")
@patch("app.routes.chat.save_message")
@patch("app.routes.chat.get_history")
@patch("app.routes.chat.grounded_answer")
@patch("app.routes.chat.get_embedding_provider")
@patch("app.routes.chat.get_anchor_store")
@patch("app.routes.chat.retrieve_hybrid")
@patch("app.routes.chat.evidence_gate_v2")
@patch("app.routes.chat.verify_citations_v2")
def test_chat_sends_history_to_prompt(
    mock_verify, mock_gate, mock_retrieve, mock_anchor,
    mock_embed, mock_llm, mock_history, mock_save, mock_trim,
    respx_mock,
):
    """When history is provided, it should be passed to build_user_prompt."""
    import httpx
    respx_mock.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent").mock(
        return_value=httpx.Response(200, json={"embedding": {"values": [0.5] * 768}})
    )
    mock_embed.return_value.embed_texts.return_value = [[0.5] * 768]
    mock_anchor.return_value.classify.return_value = ("pmfby", 0.8)
    mock_retrieve.return_value = []
    mock_gate.return_value = (False, None, MagicMock(value="high"))
    mock_verify.return_value = MagicMock(is_valid=True)
    mock_llm.return_value = "Answer [chunk:aaaabbbb]."
    mock_history.return_value = [{"role": "user", "content": "What is PMFBY?"}]

    from app.routes.chat import ChatRequest
    payload = {
        "question": "What are the criteria?",
        "session_id": str(uuid.uuid4()),
        "language": "en",
        "state": None,
        "history": [{"role": "user", "content": "What is PMFBY?"}],
    }

    r = client.post("/chat", json=payload)
    # The key assertion: get_history was called (server-side retrieval)
    mock_history.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_chat_history.py::test_chat_sends_history_to_prompt -v`
Expected: FAIL (imports not wired yet)

- [ ] **Step 3: Add imports and wire history into chat handler**

In `backend/app/routes/chat.py`, add imports at top (after existing imports):

```python
from app.session_store import get_history, save_message, trim_messages
```

Update the `chat` handler. Before the existing line 180 (`prompt = build_user_prompt(...)`), add history retrieval:

```python
        # --- Conversation history (Stage 8b) ---
        history = get_history(req.session_id, limit=5)
```

Update the prompt building call (line 180):

```python
        prompt = build_user_prompt(req.question, chunks, history=history)
```

After the response is built (before the `return` on line 194), add message persistence:

```python
        # --- Persist conversation turns ---
        save_message(req.session_id, "user", req.question)
        save_message(req.session_id, "assistant", answer)
        trim_messages(req.session_id, keep=50)
```

Also add message persistence for the out-of-scope path (after line 156 return, before line 157):

```python
        save_message(req.session_id, "user", req.question)
        save_message(req.session_id, "assistant", f"{general_answer}\n\n{general_disclaimer(lang)}")
        trim_messages(req.session_id, keep=50)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_chat_history.py -v`
Expected: PASS (4 tests including the new one)

- [ ] **Step 5: Run all existing chat tests to check for regressions**

Run: `cd backend && python -m pytest tests/test_chat_route.py -v`
Expected: PASS (existing tests should still work — history=None is backward compatible)

- [ ] **Step 6: Commit**

```bash
git add backend/app/routes/chat.py backend/tests/test_chat_history.py
git commit -m "feat: wire conversation history into /chat handler"
```

---

### Task 6: Update frontend `sendChat` to accept history

**Files:**
- Modify: `frontend/src/lib/api.ts:16-29`

**Interfaces:**
- Consumes: `history` array from ChatWindow
- Produces: Backend receives `history` in request body

- [ ] **Step 1: Update `sendChat` type signature**

In `frontend/src/lib/api.ts`, update the `sendChat` function:

```typescript
export async function sendChat(payload: {
  question: string;
  session_id: string;
  language: Locale;
  state: string | null;
  history?: Array<{ role: "user" | "assistant"; content: string }>;
}): Promise<ChatResponse> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit 2>&1 | Select-String "api.ts"`
Expected: No errors in api.ts

- [ ] **Step 3: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat: sendChat accepts optional history parameter"
```

---

### Task 7: Pass conversation history from ChatWindow to sendChat

**Files:**
- Modify: `frontend/src/components/ChatWindow.tsx:250`

**Interfaces:**
- Consumes: `msgs` state (already exists)
- Produces: `history` array sent with each request

- [ ] **Step 1: Update the sendChat call to include history**

In `frontend/src/components/ChatWindow.tsx`, find the `sendChat` call (line 250). Replace:

```typescript
      const resp = await sendChat({ question, session_id: sessionId, language: lang, state: null });
```

With:

```typescript
      const history = msgs
        .filter((m): m is Msg & { text: string } => !!m.text)
        .slice(-5)
        .map(m => ({ role: m.role, content: m.text }));

      const resp = await sendChat({ question, session_id: sessionId, language: lang, state: null, history });
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit 2>&1 | Select-String "ChatWindow.tsx"`
Expected: Only pre-existing errors (IconBot, updatedAt), no new errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatWindow.tsx
git commit -m "feat: pass last 5 conversation turns to backend"
```

---

### Task 8: End-to-end verification

**Files:** None (verification only)

- [ ] **Step 1: Start backend server**

```bash
cd backend && python -m uvicorn app.main:app --reload
```

- [ ] **Step 2: Start frontend dev server**

```bash
cd frontend && npm run dev
```

- [ ] **Step 3: Manual test — multi-turn conversation**

1. Open `http://localhost:3000/chat`
2. Ask: "What is PMFBY?"
3. Wait for response
4. Ask: "What are the eligibility criteria?" (follow-up without restating "PMFBY")
5. Verify the LLM responds with PMFBY eligibility (not a generic answer)

- [ ] **Step 4: Verify messages appear in Supabase**

Go to Supabase Dashboard → Table Editor → `messages` table. Verify 2 user messages and 2 assistant messages exist.

- [ ] **Step 5: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 6: Run all frontend tests**

Run: `cd frontend && npx vitest run`
Expected: ALL PASS (22/22)

- [ ] **Step 7: Final commit (if any fixes needed)**

```bash
git add -A
git commit -m "feat: conversation memory — end-to-end verified"
```
