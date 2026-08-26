# Provider Setup Runbook

Follow this exact order to create all provider accounts and populate `.env`.

## 1. Supabase (Postgres + pgvector)

1. Go to https://supabase.com/dashboard
2. Click **New Project**
3. Project name: `sahayak-dev`
4. Region: nearest to your team
5. Copy **Project URL** and **service_role key** into `.env`:
   ```
   SUPABASE_URL=https://<ref>.supabase.co
   SUPABASE_SERVICE_KEY=<service_role key>
   ```

## 2. Groq (LLM inference)

1. Go to https://console.groq.com
2. Navigate to **API Keys**
3. Create a new key
4. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

## 3. Gemini (Embeddings)

1. Go to https://aistudio.google.com
2. Click **Get API key**
3. Add to `.env`:
   ```
   GEMINI_API_KEY=...
   ```

## 4. Bhashini (Voice — Hindi STT/TTS)

1. Go to https://bhashini.gov.in
2. Register for a ULCA API key request
3. **Approval lead time is unverified** — submit NOW, record submission date in `PROJECT_STATUS.md` Blocking issues; do not block other work on it.

## 5. Render (Backend hosting)

1. Go to https://dashboard.render.com
2. Sign up (used by Task 4)

## Smoke Tests

After accounts exist, run from repo root with `.env` loaded:

```bash
python scripts/smoke_groq.py
python scripts/smoke_gemini_embeddings.py
```

Expected output:
- `groq ok: OK`
- `gemini-embedding-2 ok: 3 inputs -> 3 distinct 768-dim vectors`

If the aggregation assertion in the Gemini script fails: **STOP**. Revert embedding model to `gemini-embedding-001` per DECISIONS.md guard, re-log, adjust `config.py` (Task 3) to add manual L2 normalization.

For Supabase smoke (run after Task 3's migration):
```bash
python scripts/smoke_supabase.py
```

## Model ID Verification

- **Groq**: `llama-3.3-70b-versatile` — verify at https://console.groq.com/docs/models
- **Gemini LLM**: `gemini-2.5-flash` — verify at https://ai.google.dev/gemini-api/docs

If model IDs have changed, use the documented successor and update `config.py`.
