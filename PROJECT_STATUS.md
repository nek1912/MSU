# Project Status

**This is the one file every AI session and every team member reads first.**
Every other file in this repo (CLAUDE.md, PRD.md, architecture.md, design.md,
work-plan.md) describes what the system is *supposed* to be. This file
describes what it actually *is*, right now. When they disagree, this file wins
for "what do I do next" — the other files win for "what are the rules I must
not violate."

Update this at the end of every work session, before you stop. Not optional —
an out-of-date status file is worse than none, because the next session will
trust it. If you only have two minutes, update `Last updated` and the
`Blocking issues` section — that's the highest-value part.

---

## Last updated

`2026-09-01 (6th session), Task 14: Registered conversations, evidence, grievance routers in main.py`

## Current day / plan position

`Day N of 10` per work-plan.md. Note if you're ahead, on track, or behind —
and if behind, what got cut (check against work-plan.md's cut order and
PRD.md's Tier 1 / Tier 2 split).

## Selected state

`<state name>` — filled in Day 1. If this is still blank, nothing state-specific
in the corpus or jurisdiction filter can be trusted yet.

## Component status

Update the status column as things change. Use exactly these values so a
quick scan tells the story: `not started / stubbed / in progress / working /
broken`.

| Component | Owner | Status | Notes |
|---|---|---|---|
| Repo / CI / deploy pipeline | M4 | not started | |
| FastAPI skeleton + `/health` | M2 | working | |
| Next.js skeleton (chat + grievance screens) | M3 | working | |
| Document ingestion (MinerU content_list_v2.json) | M1 | working | NEW pipeline: backend/seed_parser.py parses content_list_v2.json (real page_idx + structure) -> corpus/seeds/chunks_jsonl/*.jsonl; old pdfplumber/Markdown pipeline + ingestion/ pkg DELETED |
| Embeddings (Jina v3 768d) | M1 | working | Frozen: jina-embeddings-v3, retrieval.passage (docs) / retrieval.query (queries), 768d, truncate:true, TPM-bucketed |
| Embeddings (Jina v3 768d) | M1 | working | Re-embedded 226 chunks, dimension mismatch fixed |
| Retrieval (Supabase pgvector, domain+state filter) | M1 | working | Dense-only, recall below targets |
| Hybrid retrieval (Stage 5) | M1 | working | Integrated into chat route: hybrid_retrieval.py with RRF fusion |
| Evidence gate v2 (Stage 7) | M2 | working | evidence_gate_v2 integrated with typed AbstentionReason |
| Reranker (Stage 6) | M2 | working | Wired into chat route, disabled by default (RERANKER_ENABLED=False) |
| Citation verifier (Stage 8) | M2 | working | citation_verifier.py, all responses routed through verification |
| `/chat` wired to retrieval | M2 | working | Session store, evidence gate v2, citations, abstention wired |
| Conversation memory / session history | M2 | working | `messages` table + last-5-turn history prepended to prompt; frontend sends history with each request |
| Web-grounded RAG pipeline (Task 9) | M2 | stubbed | `app/rag/` copied from sub-project, imports adapted; GeminiReranker + SourceVerifier are stubs; `ask()` calls `WebDiscoveryService().discover()` which needs integration verification |
| Citation verification | M2 | working | Set-membership based, routed through verifier |
| Abstention logic | M2 | working | Defense-in-depth: domain + jurisdiction + thresholds |
| Confidence calibration | M2 | working | Retrieval-signal-based scoring (not heuristic) |
| Contracts (Stage 1) | M1 | working | 12 Pydantic models in contracts.py |
| Migration (Stage 2) | M1 | working | 0005_rag_contracts.sql applied to Supabase |
| Jina task-type differentiation | M1 | working | Query vs passage embeddings for better retrieval |
| Azure voice provider | M2 | stubbed | Disabled until AZURE_SPEECH_KEY provided |
| Sarvam voice provider | M2 | stubbed | Disabled until SARVAM_API_KEY provided |
| Voice service (fallback) | M2 | working | Azure → Sarvam → text-only fallback chain |
| Voice routes | M2 | working | /voice/transcribe, /voice/speak (return 503 when disabled) |
| Grievance state machine | M2 | not started | |
| Grievance UI | M3 | not started | |
| Voice UI (Tier 2) | M3 | not started | |
| Evaluation set (~140 cases) | M1/M4 | working | 245 gold cases, 40 answerable |
| Skeleton exit-gate validator | M1 | working | |

## Provider account status

Fill these in as each is set up — this saves the next session from
rediscovering "wait, do we have a Groq key yet?"

| Provider | Account created | API key working | Known limits hit so far |
|---|---|---|---|
| Bhashini / ULCA | no | no | |
| Azure Cognitive Services | no | no | |
| Sarvam AI | no | no | |
| Groq | yes | yes | |
| Gemini API | yes | yes | |
| Supabase | yes | yes | |
| Jina | yes | yes | 429 rate limit during ingestion |
| Render | no | no | |
| Vercel | no | no | |

## Blocking issues

- **Gold set is retriever-anchored (weak supervision)**: `populate_gold_chunk_ids.py`
  now localizes the relevant chunk by embedding each query and ranking the chunks
  of the expected document — the SAME embed model the retriever uses. So the
  reported Recall is optimistic and measures "does the retriever surface its own
  best-matching chunk", not "does it surface the true answer span". Manual
  curation of gold answer spans is required before these numbers become a real
  pass/fail gate. (The raw dense numbers below are still a valid *regression*
  baseline vs the old 226-chunk corpus.)
- **Reranker degrades proxy recall**: with `RERANKER_ENABLED=true`, final top-6
  Recall@1 drops 0.85 -> 0.50 and Recall@5 0.975 -> 0.875 on the current gold
  (the reranker reorders the anchored-gold chunk out of the top set). KEEP THE
  RERANKER WIRED BUT OFF until validated against manually-curated gold. Wiring is
  done in `backend/app/routes/chat.py` (hybrid top-25 -> rerank -> top-6 -> gate);
  flip `RERANKER_ENABLED` in `backend/.env` to enable.
- **No answerable gold for 3 domains**: gold has 0 answerable cases for
  `financial_inclusion`(docs exist), `schemes`, `agriculture`, `grievance` beyond
  the 40 pacs/pmfby cases. Recall is therefore only measured on 2 of 7 domains.
- **Agriculture corpus missing**: `agriculture` queries route to `out_of_scope`
  (no agriculture docs ingested) — expected coverage gap, not a bug.
- **Vector index needs live confirmation**: `pg_indexes` is not exposed via the
  Supabase REST API, so the HNSW index could not be verified live this session.
  The migrations define `HNSW(embedding vector_cosine_ops)` and `match_chunks`
  uses `1 - (embedding <=> query)` (cosine) — consistent by construction. Run in
  the Supabase SQL editor to confirm:
  `SELECT indexname, indexdef FROM pg_indexes WHERE tablename='chunks';`
- **Voice providers disabled**: Azure and Sarvam providers exist but need API keys.
- **Corpus still small (5 docs)**: expansion with more official documents is the
  real lever for Recall@5, not prompt/UI tuning.

## Resolved this session

- Old RAG rows in Supabase wiped and re-ingested from MinerU `content_list_v2.json`.
- Old PDF->Markdown->fixed-char-chunk pipeline (`ingestion/` pkg, `run_ingestion*.py`,
  `retry_*.py`, `colabb.ipynb`) deleted. New pipeline: `backend/seed_parser.py`
  + `backend/ingest_seed.py`.
- Page numbers now come from `page_idx` (real pages, e.g. PMFBY premium = p.47),
  not the old `Pages: 1` bug.
- Tables are first-class (HTML extracted from `content_list_v2.json`), not image stubs.
- Lexical retrieval now honours domain + jurisdiction/state filter (no cross-domain leakage).
- Embedding model frozen to Jina Embeddings v3 768d (retrieval.passage / retrieval.query).
- **Anchor store caching bug fixed**: `get_anchor_store()` re-embedded ~70 anchors on
  every call (fresh bound method defeated `lru_cache`). Now a module-level singleton —
  this also cuts production `/chat` latency.
- **Gold mapping rebuilt**: `populate_gold_chunk_ids.py` translates old `source_id`
  slugs to the stored `source_id` values and localizes the relevant chunk per query
  (within the expected document) instead of grabbing the first 3 doc chunks.
- **Eval query-embedding bug fixed**: `eval/run_retrieval_eval.py` embedded queries
  with the default `retrieval.passage` while production uses `retrieval.query`. This
  made Recall look like 0.30; corrected to `retrieval.query` (now mirrors `/chat`).
- **Domain taxonomy normalized**: `pacs_computerization` was being swallowed by
  `pacs_governance` because `classify()` returns the first matching keyword and
  `pacs_governance` owned the bare keyword `pacs`. Reordered `keyword_rules.json`
  (computerization checked first) and gave it computerization-specific anchors
  (ICT/ERP/PMU/digital/data-readiness). `computerization of PACS project Gujarat`
  now routes to `pacs_computerization` with 0 contamination.
- **Reranker wired into `/chat`** (hybrid top-25 -> rerank -> top-6 -> evidence gate),
  but left OFF by default after eval showed it lowers proxy recall (see Blocking).
- **Frontend schemes.ts expanded**: Added 5 new cooperative scheme entries (nrcf,
  e-nam, soil-health, rganidhi, pmjdj) with English, Hindi, and Gujarati translations.
  Fixed corrupted nrcf entry that was incorrectly placed inside LocalizedScheme
  interface. Total schemes: 15 (was 10). Tests pass (22/22).
- **Conversation memory implemented**: `messages` table added, `session_store.py`
  now persists and fetches last-turn history, `build_user_prompt()` prepends prior
  turns, `/chat` persists user/assistant turns, and frontend `sendChat()` sends the
  last 5 turns with each request. Verified: 12 backend history tests pass; frontend
  TypeScript compile returns no errors.

## Corpus status

All 5 seed documents re-ingested from `corpus/seeds/json_files/*_content_list_v2.json`
via `backend/seed_parser.py` -> `backend/ingest_seed.py`. Old RAG rows in Supabase
were wiped and re-created. Embeddings: Jina Embeddings v3, 768d.

| Domain | Sources ingested | Chunk count (embedded) | Notes |
|---|---|---|---|
| pacs_governance | 1 | 337 | Model Byelaws 05.01.2023 |
| pacs_computerization | 2 | 214 | Revised Scheme guidelines (192) + Corrigendum (22) |
| pmfby | 1 | 1266 | operational_guidelines_pmfby |
| financial_inclusion | 1 | 371 | NSFI_2025_30 |
| schemes | 0 | 0 | |
| agriculture | 0 | 0 | |
| grievance | n/a | n/a | classification examples only |

**Total: 5 documents, 2188 embedded chunks (356 image/empty skipped), 768d Jina v3**

Canonical chunk manifest = `corpus/seeds/chunks_jsonl/*.jsonl` (page_start/page_end,
heading_path, clause, chunk_type, images, text). Markdown in `corpus/seeds/*.md`
is a human-readable derived artifact only.

### Retrieval Validation Baseline (2026-08-29) — frozen 2,188-chunk Jina-v3 corpus

Method: `eval/run_retrieval_eval.py` over 245 gold cases (40 answerable: 18
pacs_governance + 22 pmfby). Queries embedded with `retrieval.query` (mirrors
`/chat`). Gold = in-doc top-2 by query embedding (retriever-anchored, weak).

Raw dense (match_chunks top-20 pool) — this is the headline baseline:
- Recall@1: **0.850** (target 0.40)  PASS
- Recall@3: **0.950** (target 0.60)  PASS
- Recall@5: **0.975** (target 0.80)  PASS
- Recall@10: 0.975
- Recall@20: 1.000 (reranker candidate-pool ceiling)
- MRR: **0.904**
- Domain accuracy: 0.950 (diagnostic)
- Jurisdiction contamination: 0 (hard blocker)

vs the OLD 226-chunk baseline (2026-08-28): Recall@5 was 0.625. The new corpus
+ Jina v3 strategy is a large improvement — but see the weak-supervision caveat
above; treat as a regression baseline, not a target.

With reranker ON (final top-6): Recall@1 0.50, Recall@3 0.80, Recall@5 0.875,
MRR 0.67 — DEGRADES the dense baseline, hence reranker left OFF.

### Accuracy Metrics — page/citation/metadata (2026-08-29)

- Page accuracy: 0 structural problems across a 25-chunk sample; `source_file`
  correct; PMFBY premium -> page 47, sec "Variation in Premium Rate" (old
  `Pages: 1` bug confirmed gone).
- Metadata filters: PMFBY / PACS / computerization / Jan Dhan queries each return
  ONLY their own domain (contamination 0).
- Citation chain (chunk_id uuid -> document_id -> source_file -> page -> section)
  resolves; gap = chunk_id is a uuid, not the stable text id (would need an RPC
  change to expose `c.chunk_id` alongside `c.id`).

## Three flagship demos (from work-plan.md Day 9)

Track these independently — they're what actually gets shown to judges.

1. **Hindi PMFBY voice query**: not working
2. **Cooperative/PACS state-filtered question**: not working
3. **Hindi grievance create + status lookup**: not working

## Next immediate action

1. **Curate real gold answer spans** (manual) for the 40 answerable cases + add
   answerable cases for `financial_inclusion`, `schemes`, `grievance`. This is the
   only way to get a trustworthy Recall target — current numbers are retriever-anchored.
2. **Decide reranker**: tune or replace (e.g., rerank top-30, or a domain-aware
   reranker) and re-measure on curated gold before flipping `RERANKER_ENABLED=true`.
3. **Confirm HNSW index live** via the Supabase SQL editor (SQL in Blocking issues).
4. **Expose stable text chunk_id** from `match_chunks` (add `c.chunk_id` to the RPC
   returns) so citations survive re-ingestion; update `retrieval.py`/`hybrid_retrieval.py`
   and citation tests accordingly.
5. **Calibrate confidence**: replace the retrieval-signal heuristic with a calibrated
   model over held-out retrieval/evidence features (PROJECT_STATUS step 12).
6. **Multilingual text** (English+Hindi+Gujarati) only after English retrieval is
   stable: build eval cases per language, verify cross-lingual retrieval maps to the
   correct English clause. Voice (Azure STT/TTS) is last — never a separate retrieval path.
5. Security hardening pass.

**Re-ingestion is complete and verified** (domain classify -> hybrid retrieve -> evidence
gate returns grounded chunks with correct pages; off-topic routes to out_of_scope, no
hallucination). The pipeline to beat on retrieval quality is now `backend/seed_parser.py`
+ `backend/ingest_seed.py`.
