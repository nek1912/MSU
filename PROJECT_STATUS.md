# Project Status

**This is the one file every AI session and every team member reads first.**
The actual code files are the ground truth. This file reflects what is
currently implemented and working. When in doubt, read the code.

Update this at the end of every work session. An out-of-date status file is
worse than none — the next session will trust it.

---

## Last updated

`2026-09-04` — Full codebase audit. All status entries verified against actual source files.

## Current state

System is **feature-complete**. Backend RAG pipeline, 9-stage grievance workflow,
voice I/O, multi-language support (6 languages), and Next.js frontend are all
implemented and wired together.

**Selected state:** `gujarat` (`selected_state: "gujarat"` in `backend/app/config.py`)

---

## Component status

`not started / stubbed / in progress / working / broken`

| Component | File(s) | Status | Notes |
|---|---|---|---|
| FastAPI app + `/health`, `/health/providers` | `app/main.py` | working | 5 routers registered |
| `/chat` (sync) | `app/routes/chat.py` | working | Language detect → domain classify → RAGOrchestrator or GrievanceWorkflow |
| `/chat/stream` (SSE) | `app/routes/chat.py` | working | Same pipeline, Server-Sent Events with `thinking/token/metadata/done` events |
| `/voice`, `/voice/transcribe`, `/voice/speak` | `app/routes/voice.py` | working | Full audio→STT→RAG→TTS pipeline |
| `/conversations` | `app/routes/conversations.py` | working | Session history retrieval |
| `/evidence` | `app/routes/evidence.py` | working | Evidence endpoint |
| `/grievance` (route) | `app/routes/grievance.py` | working | Grievance REST endpoint |
| Domain classifier (AnchorStore) | `app/domains.py` | working | Keyword rules + embedding cosine; floor 0.30 |
| Session store | `app/session_store.py` | working | Supabase-backed, keeps last 50 messages |
| Language detection | `app/language.py` | working | Detects dominant language and language mix |
| Translation (Sarvam primary, Azure fallback) | `app/providers/sarvam_translator.py`, `app/providers/translator.py` | working | Used in chat.py pre/post RAG |
| RAGOrchestrator | `app/services/rag_orchestrator.py` | working | Async dual-pipeline: static + web in parallel via `asyncio.gather` |
| StaticRAGService | `app/services/static_rag.py` | working | Supabase pgvector hybrid retrieval (dense + lexical RRF) → EvidenceChunks |
| WebRAGService | `app/services/web_rag.py` | working | 10-step web RAG: Tavily/Firecrawl → BM25 → Gemini pre-rank → RRF → Gemini final-rank → source verify → EvidenceChunks |
| EvidenceController + prompt builder | `app/evidence_controller.py` | working | Merges chunks, builds curated source-priority prompt |
| Evidence gate | `app/evidence_gate.py` | working | Threshold: `TOP1_THRESHOLD=0.25`, `SECONDARY_THRESHOLD=0.30`, `MIN_CHUNKS_ABOVE_SECONDARY=2` |
| Citation verifier | `app/citation_verifier.py` | working | Set-membership check — every `[chunk:id]` must map to a retrieved chunk |
| Confidence calculation | `app/services/rag_orchestrator.py` | working | Band-based; dual-source gets +0.10 boost |
| GrievanceWorkflow (9-stage state machine) | `app/grievance/workflow.py` | working | INTAKE → CLASSIFICATION → ENTITY_EXTRACTION → MISSING_FIELDS → FOLLOWUP → DRAFT_READY → SUBMISSION_GUIDE → STATUS_LOOKUP → COMPLETE |
| Grievance classifier | `app/grievance/classifier.py` | working | |
| Grievance draft builder | `app/grievance/draft_builder.py` | working | |
| Grievance entity extractor | `app/grievance/entity_extractor.py` | working | |
| Grievance field detector | `app/grievance/field_detector.py` | working | |
| Grievance semantic extractor | `app/grievance/semantic_extractor.py` | working | |
| Grievance submission guide | `app/grievance/submission_guide.py` | working | |
| Grievance status lookup | `app/grievance/status_lookup.py` | working | |
| Grievance state persistence | `app/grievance/workflow.py` | working | Supabase `grievance_states` table, upsert on `conversation_id` |
| VoiceService (STT/TTS fallback chain) | `app/services/voice_service.py` | working | STT: Sarvam→Azure; TTS: Sarvam only (Azure bad for Indic langs) |
| Sarvam STT/TTS providers | `app/providers/sarvam_voice.py` | working | Primary voice provider |
| Azure STT fallback | `app/providers/azure_voice.py` | working | Fallback STT only |
| Embeddings (Jina primary, Gemini fallback) | `app/providers/embeddings.py` | working | Jina v3 768d, task-typed (`retrieval.query` / `retrieval.passage`) |
| Jina reranker | `app/providers/reranker.py` | working | Wired in StaticRAGService but **disabled** (`RERANKER_ENABLED=false`) |
| Gemini LLM provider (fallback) | `app/providers/gemini_llm.py` | working | |
| Groq LLM provider (primary) | `app/providers/groq_llm.py` | working | Key rotation via `groq_keys` property |
| Sarvam chat provider | `app/providers/sarvam_chat.py` | working | |
| Web discovery (Tavily / Firecrawl) | `app/web_rag/service.py` | working | |
| Query classifier (web RAG) | `app/web_rag/query_classifier.py` | working | Domain, jurisdiction, state classification for web queries |
| Source verifier | `app/security/source_verifier.py` | working | Trust-score based filtering in web RAG |
| Next.js frontend (PWA) | `frontend/` | working | Next.js 16, React 19, Tailwind v4, GSAP |
| Frontend pages | `frontend/src/app/` | working | `/` (home), `/chat`, `/grievance`, `/schemes`, `/services`, `/library`, `/faq`, `/legal` |
| Frontend i18n (6 languages) | `frontend/src/lib/i18n/` | working | EN, HI, GU, MR, BN, TA |
| ChatWindow (streaming SSE) | `frontend/src/components/ChatWindow.tsx` | working | Handles `thinking/token/metadata/done` SSE events, voice recording, citation display |
| Document ingestion pipeline | `backend/seed_parser.py`, `backend/ingest_seed.py` | working | Parses MinerU `content_list_v2.json` → JSONL → embeds → Supabase |
| Database schema | `backend/schema.sql` | working | `documents`, `chunks` (vector 768d, HNSW), `sessions`, `grievance_states` |

---

## Provider status

| Provider | Status | Role |
|---|---|---|
| Groq | configured | Primary LLM (key rotation supported) |
| Gemini | configured | Fallback LLM + Gemini reranker in WebRAGService + grievance model |
| Jina | configured | Primary embeddings (jina-embeddings-v3, 768d) |
| Supabase | configured | Postgres + pgvector (HNSW cosine), sessions, grievance_states |
| Sarvam AI | configured | Primary STT, TTS, translation (key rotation supported) |
| Tavily | configured | Primary web search |
| Firecrawl | configured | Web crawl / scrape fallback |
| Azure Cognitive Services | configured | Fallback STT only (TTS deliberately excluded — bad Indic output) |
| Bhashini / ULCA | stubbed | `bhashini_stub.py` present, not wired |
| Render | configured | Backend hosting (`render.yaml`) |

---

## Known issues / caveats

- **Reranker disabled**: `RERANKER_ENABLED=false` in config. When enabled, Recall@1 drops 0.85→0.50. Keep off.
- **Agriculture corpus missing**: `agriculture` domain routes to `out_of_scope` — no docs ingested, not a bug.
- **Gold eval set is retriever-anchored**: Recall metrics are optimistic (measures if retriever surfaces its own best-matching chunk, not true answer span). Manual curation needed for production eval.
- **Supabase free-tier pausing**: May pause after inactivity. Reactivate before demos.

---

## Corpus

All ingested from `corpus/seeds/json_files/*_content_list_v2.json`
via `backend/seed_parser.py` → `backend/ingest_seed.py`. Embeddings: Jina v3 768d.

| Domain | Chunks embedded | Source |
|---|---|---|
| pacs_governance | 337 | Model Byelaws 05.01.2023 |
| pacs_computerization | 214 | Revised Scheme guidelines (192) + Corrigendum (22) |
| pmfby | 1266 | operational_guidelines_pmfby |
| financial_inclusion | 371 | NSFI_2025_30 |
| schemes | 0 | not ingested |
| agriculture | 0 | not ingested |

**Total: 5 documents, 2188 embedded chunks, 768d Jina v3**

---

## Flagship demos

1. **Hindi PMFBY voice query** — Audio → Sarvam STT → RAGOrchestrator → Sarvam TTS audio response
2. **Cooperative/PACS state-filtered question** — `state="gujarat"` filtered in `static_rag.py` pgvector queries
3. **Grievance intake + status lookup** — Multi-turn intake → entity extraction → prototype reference (`DEMO-PACS-xxxxx`) → status lookup guidance
