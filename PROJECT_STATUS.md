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

`2026-08-29 (4th session / integration stabilization): merged app stabilized on branch integration/stabilization — voice route refactored to service layer, evidence-gate domain fail-closed, frontend build fixed, full test suites green (backend 350 / frontend 22 / RAG eval PASS), Phase 10 multilingual query-translation wired`

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
| Citation verification | M2 | working | Set-membership based, routed through verifier |
| Abstention logic | M2 | working | Defense-in-depth: domain + jurisdiction + thresholds |
| Confidence calibration | M2 | working | Retrieval-signal-based scoring (not heuristic) |
| Contracts (Stage 1) | M1 | working | 12 Pydantic models in contracts.py |
| Migration (Stage 2) | M1 | working | 0005_rag_contracts.sql applied to Supabase |
| Jina task-type differentiation | M1 | working | Query vs passage embeddings for better retrieval |
| Azure voice provider | M2 | stubbed | Disabled until AZURE_SPEECH_KEY provided |
| Sarvam voice provider | M2 | stubbed | Disabled until SARVAM_API_KEY provided |
| Voice service (fallback) | M2 | working | Azure → Sarvam → text-only fallback chain |
| Voice routes | M2 | working | Refactored to service layer (routes/voice.py → services/voice_service.py); JSON bodies; 503 on VoiceUnavailableError. `tests/test_voice_routes.py` authoritative. |
| Multilingual query translation | M2 | working | Phase 10: non-English query → Azure Translator → English for embedding/classify/lexical retrieval; original lang kept for answer. Graceful fallback to original text. `tests/test_translator.py`. |
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
- **LLM citation adherence (blocks live answers, NOT a code regression):** Groq
  (Llama-3.3-70b, working primary) frequently returns `INSUFFICIENT_EVIDENCE` or
  omits the required `[chunk:id]` markers, so `verify_citations_v2` rejects and
  `/chat` returns a controlled abstention (no fabricated answer — correct
  fail-closed). Gemini fallback returns **404** (model `gemini-2.5-flash` name
  issue) and is non-functional. Live answers require the LLM to actually cite
  retrieved chunks; this is a model/prompt-tuning task, not a backend bug.
- **`sessions` table 400 in this env:** `touch_session` POST returns 400 (table
  likely not migrated), aborting `/chat` via `_SAFE_FAILURES` (`dependency_failure`)
  before retrieval. Production must have the `sessions` table; tests mock it.
- **Corpus still small (5 docs)**: expansion with more official documents is the
  real lever for Recall@5, not prompt/UI tuning.

## Resolved this session

- **Live corpus restored (the actual blocker):** the live Supabase DB still held
  the OLD 12-doc / 12-chunk `pdfplumber-v1` FAQ corpus while the code targeted the
  new architecture. Re-ran `seed_parser.py` → `ingest_seed.py`: now **5 documents,
  2,188 embedded chunks, 768d Jina v3, `parser_profile=mineru-content_list_v2`**,
  verified live. Schema was already `vector(768)` + HNSW (match_chunks works).
- **Frontend static fallback removed** (`frontend/src/app/api/chat/route.ts`):
  backend failure now returns 502/503, never a hardcoded ungrounded answer.
- **Out-of-scope fixed** (`backend/app/routes/chat.py`): `out_of_scope` now returns
  a controlled rejection (no factual LLM answer); was previously an ungrounded
  general-knowledge answer.
- **Citation metadata exposed** (`chat.py` `_citations_from`): `/chat` citations now
  carry stable `chunk_id`, `document_id`, `source_file`, `page_start/end`,
  `section`, `subsection`, `clause` (resolved via a chunks lookup), not just
  `{title, page, url}`.
- **Gold re-anchored** to current row UUIDs via `populate_gold_chunk_ids.py`
  (re-ingestion regenerates UUIDs, so the old gold pointed at dead rows → Recall 0).
- Retrieval eval re-run: PASS, essentially at baseline (see Retrieval Validation
  Baseline).

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

## Integration stabilization (4th session — branch `integration/stabilization`)

Goal of this branch: make the merged frontend + backend app demonstrably stable
(no known regressions) and prepare multilingual text RAG, WITHOUT touching
`main`. `origin/main` is already an ancestor of the branch HEAD, so the branch
is the fully-merged app. Working changes are isolated to this branch; a PR is
opened from it. No re-chunk / re-ingest / re-embed — corpus frozen at 2,188.

### What changed (backend)
- **Voice route → service layer (fixes `tests/test_voice_routes.py`, 9 failures):**
  `backend/app/routes/voice.py` now delegates STT/TTS to
  `app.services.voice_service.VoiceService` (exposed as module attr `voice_service`),
  uses JSON request bodies (`{audio: base64, language}`), returns
  `503 {"detail":"No voice providers available"}` on `VoiceUnavailableError`, and
  `body["audio"]` as hex. This is the intended architecture (routes never call a
  provider SDK directly).
- **Evidence-gate domain fail-closed (`tests/test_evidence_gate.py`):** 
  `evidence_gate.py:check_domain_match` now REJECTS when
  `filter_decisions.get("domain") is not True` (was `is not False`). A candidate
  with missing/unknown/mismatched domain is now rejected by default.
  `chat.py:_to_candidate` derives `domain` from `chunk.domain == expected_domain`;
  `hybrid_retrieval.py` fusion candidates derive it the same way. Invariant:
  wrong-domain chunks can no longer surface as answers.
- **Phase 10 multilingual query translation (`app/providers/translator.py`):**
  when the detected query language != English, the query is translated to English
  (Azure Translator) for embedding + classification + lexical retrieval only. The
  original language is preserved for answer generation (LLM answers in the user's
  language). `config.py` gained `azure_translator_*` settings. Translator fails
  **gracefully** to the original text if unconfigured or on any HTTP/parse error
  (retrieval degrades, never crashes). Verified: Hindi PMFBY query →
  "What is the PMFBY scheme..." → `domain=pmfby` → `retrieve_hybrid` receives the
  English query. New `tests/test_translator.py` (4 tests) covers fallback + success.

### What changed (frontend)
- `npm install gsap@^3.15.0` (was declared in package.json but not installed →
  build error).
- `frontend/src/app/grievance/status/page.tsx`: `tl.at` → `tl.timestamp`.
- `frontend/src/components/chat/MessageBubble.tsx`: import `EvidenceBand` +
  `evidenceBand`; `evidenceTone(resp.confidence)` → `evidenceBand(resp.confidence)`.
- `frontend/src/components/ChatWindow.tsx`: `translate()` now calls `/api/translate`
  (Azure Translator proxy). `tsc --noEmit` + `npm run build` both pass.

### Verification (all green)
- **Backend pytest:** `350 passed, 2 deselected` (was 346 + 4 new translator tests).
- **Frontend vitest:** `22 passed` (10 files). Frontend `tsc` + `build`: PASS.
- **RAG regression eval:** PASS, matches frozen baseline exactly
  (Recall@1 0.800, @5 0.925, @20 0.950, MRR 0.856, contamination 0).
- **Frontend/backend contract:** `ChatResponse` fields match; `/api/chat/route.ts`
  returns 502/503 on backend failure (no static fallback) — confirmed unchanged.

### Live `/chat` findings (not regressions — behaviors are correct/safe)
- **Groq (Llama-3.3-70b) is the working primary LLM.** Gemini returns a **404
  model-name error** and is non-functional as the fallback (`gemini-2.5-flash`).
  This is an API-config issue, not a code bug.
- **Citation verifier consistently triggers controlled abstention for in-domain
  queries:** Groq frequently returns the literal string `INSUFFICIENT_EVIDENCE`
  or omits the required `[chunk:id]` markers, so `verify_citations_v2` rejects
  and `/chat` returns `abstained=True` with NO fabricated answer. This is the
  **correct fail-closed safety behavior** — but it means live answers require the
  LLM to actually cite chunks. This is a **model/prompt adherence issue**, not a
  code regression. Tracked below as a Blocking issue.
- Out-of-scope ("capital of France") and wrong-domain queries correctly abstain.
- `sessions` table query returns **400** (likely not migrated) → `/chat` with a
  session that hits `touch_session` aborts via `_SAFE_FAILURES`
  (`dependency_failure`). In-test environments this is mocked; in production the
  `sessions` table must exist.
- A `UnicodeEncodeError` observed during local debug was a Windows console
  (cp1252) logging artifact, NOT a production bug (responses are UTF-8 JSON).

### Test-file reconciliation (Phase 9)
- `tests/test_voice_routes.py` (20 tests) is authoritative for the refactored
  service-layer voice route and passes.
- `tests/test_voice.py::TestVoiceRoutes` (4 tests) tested the **pre-refactor**
  multipart/`AzureSTTProvider` route and was BROKEN by the refactor. Treated as
  **obsolete** (provider-level behaviour is still covered by that file's
  `TestAzureSTT`/`TestAzureTTS` classes). Updated `TestVoiceRoutes` to the new
  JSON/voice-service interface (mirrors `test_voice_routes.py`); all 32 voice
  tests now pass. This is a documented smallest-test-correction, not a masking of
  a real failure.

## Citation verification fix (4th session — blocker #1)

**Root cause (traced, not guessed):** The citation verifier only recognised the
exact half-width marker `[chunk:ID]`. Groq (Llama-3.3-70b) frequently emits the
correct chunk-ID *prefix* but in the wrong *format* — full-width brackets
`【ID】` (e.g. `【fdc569dd】`) or a bare half-width hex bracket `[ID]` missing the
`chunk:` prefix. `extract_citations_from_answer` therefore found **zero**
markers → `valid_ids=[]` → verifier failed closed → `/chat` abstained for
in-domain queries. This is a model-output-format / parser gap, NOT a retrieval
or evidence-gate problem (retrieval, domain routing, and the gate were all
working — the chunks and correct prefixes were present).

**Fix (smallest generic, gate not weakened):** `backend/app/citation_verifier.py`
now normalises recognised citation-format variants to the canonical `[chunk:ID]`
before validation:
- `【chunk:ID】` / `【ID】` (full-width) → `[chunk:ID]`
- `[ID]` (half-width, missing `chunk:` prefix) → `[chunk:ID]`
Only the *format* changes; validity is still decided against the retrieved
evidence set, so a non-retrieved or fabricated ID remains rejected. The regex
bug that required the literal `chunk` prefix (`chunk:?`) was corrected to
`(?:chunk:)?` so the bare full-width form is also handled.

`backend/app/generation.py:build_system_prompt` was strengthened to specify the
exact `[chunk:ID]` format with a placeholder example and to forbid full-width
brackets / other marker styles (generic — no hardcoded document/query IDs).

**Behavior now matches the required contract:**
- valid retrieved citation (`【id】` / `[id]` matching evidence) → accepted
- missing required citation → rejected / abstained
- citation for a chunk NOT retrieved → rejected
- fabricated citation → rejected (LLM can never invent source IDs)

**Tests:** added `tests/test_citation_coverage.py` (full-width accept + reject)
and `tests/test_chat_route.py` (route-level full-width accept → grounded answer;
full-width non-retrieved → abstain). Full backend suite: **354 passed, 0 failed**
(incl. 4 new). Frontend unaffected.

**Actual `/chat` results (real Groq + real Supabase, session_store stubbed only
for the test — sessions-400 is the separate blocker #2):**
- **PMFBY (in-domain):** `abstained=false`, `confidence_level=high`, **4 valid
  citations** (real stable chunk IDs, titles, pages). FIX PROVEN end-to-end.
- **PACS (in-domain):** `abstained=true` — but at the **evidence gate**, not
  citations: `n_cands=0`, reason `NO_ELIGIBLE_SOURCE`. Retrieval returned zero
  eligible chunks for `pacs_computerization` + state `gujarat`. This is a
  **retrieval / state-filter issue, separate from the citation blocker** (likely
  the computerization corpus is filtered out by the `gujarat` state/jurisdiction
  filter). Tracked as a follow-up, not part of this fix.
- **Off-topic:** `abstained=true`, controlled rejection (no factual answer). ✓
- **Insufficient evidence:** `abstained=true`, safe abstention. ✓

**Corpus / database:** untouched — no re-chunk, re-ingest, re-embed, or schema
change. Jina v3 768d, retrieval.passage/query, reranker-off all unchanged.

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

Raw dense (match_chunks top-20 pool) — headline baseline (frozen 2026-08-29 2nd session):
- Recall@1: **0.850** (target 0.40)  PASS
- Recall@3: **0.950** (target 0.60)  PASS
- Recall@5: **0.975** (target 0.80)  PASS
- Recall@10: 0.975
- Recall@20: 1.000 (reranker candidate-pool ceiling)
- MRR: **0.904**
- Domain accuracy: 0.950 (diagnostic)
- Jurisdiction contamination: 0 (hard blocker)

Re-run after live corpus restoration (3rd session, same 40 answerable gold cases,
gold re-anchored to current row UUIDs via populate_gold_chunk_ids.py):
- Recall@1: 0.800   Recall@3: 0.900   Recall@5: 0.925   Recall@20: 0.950
- MRR: 0.856   Domain accuracy: 0.925   Contamination: 0   Verdict: PASS
- Small dip vs frozen baseline is from 3 domain-CLASSIFICATION mismatches
  (pacs_governance → pacs_computerization / out_of_scope), not retrieval.

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

## Next immediate action (current phase — Retrieval Validation & RAG Hardening)

The corpus is **frozen at 2,188 chunks**. Do NOT re-chunk / re-extract / regenerate.
Follow the 13-phase spec (Tasks 1–13). **Immediate task = Tasks 1–3 only**:

1. **Task 1 — Verify live vector index**: `vector(768)` + HNSW + `vector_cosine_ops`
   + retrieval uses cosine. (No `execute_sql` RPC from this env — verify via
   `match_chunks` behavior + migration `0001_init.sql`; apply DDL in Supabase SQL
   editor if it ever diverges.)
2. **Task 2 — Stable chunk identity through retrieval**: expose both internal DB
   `id` and stable application `chunk_id` (+ `document_id`, `source_file`,
   `page_start/end`, `section`, `subsection`, `clause`, `text`, `score`). Implemented
   in the Python retrieval layer (`hybrid_retrieval._enrich_chunks`); `match_chunks`
   RPC can later be enhanced to return these directly.
3. **Task 3 — Curated evaluation set**: create `eval/curated_eval.yaml` (human-reviewed
   `query / expected_document / expected_pages / expected_sections / expected_clauses /
   acceptable_chunk_ids`), separate from the retriever-anchored regression gold. Do
   NOT auto-populate `acceptable_chunk_ids` from the retriever.

Only after Tasks 1–3 pass: dense vs hybrid vs hybrid+reranker comparison (Tasks 4–5),
metadata-filter validation (6), evidence-gate tests (7), citation-resolution tests (8),
confidence calibration (9), then multilingual text (10–11), intelligence layer (12),
voice last (13). Reranker stays `RERANKER_ENABLED=false` until curated eval justifies it.

**Re-ingestion is complete and verified** (5 docs / 2,188 chunks / 768d Jina v3 /
`mineru-content_list_v2`). Domain classify → hybrid retrieve → evidence gate returns
grounded chunks with correct pages; off-topic returns a controlled `out_of_scope`
response (no factual LLM answer); frontend has no static fallback.

## Roadmap - Retrieval Validation & RAG Hardening (13 phases)

Corpus frozen at 2,188 chunks; no re-chunk/re-extract/regenerate. Reranker stays
OFF. No multilingual/voice until English text retrieval passes the gates.

1. Verify live vector index - 768d + HNSW + cosine; retrieval metric matches.
2. Stable chunk identity through retrieval - internal id + stable chunk_id + metadata.
3. Curated evaluation set - human-reviewed eval/curated_eval.yaml (separate from regression gold).
4. Compare strategies - dense vs hybrid vs hybrid+reranker on the curated set.
5. Reranker decision - enable ONLY if curated eval shows real improvement.
6. Metadata filtering - domain/jurisdiction/state/effective-date; 0 contamination, no per-query hacks.
7. Evidence gate - retrieve -> (rerank) -> gate -> LLM; insufficient evidence = no factual answer.
8. Citation correctness - citation resolves to retrieved chunk -> stable id -> doc -> page; reject invalid/fabricated.
9. Confidence - collect eval features; expose as diagnostic, not a stated probability, until calibrated.
10. Multilingual text - start after English gates pass; query in original lang, retrieve over English corpus.
11. Multilingual eval (en/hi/gujarati) - curated cases; source stays English.
12. Intelligence layer - query understanding only; must not invent/bypass evidence or gate.
13. Voice - Azure STT -> text RAG -> TTS; one RAG core, voice is I/O only.

## Phase 1 (Retrieval Validation & RAG Hardening) - Tasks 1-3 DONE

- Task 1 (verify live vector index): PASS. ector(768) confirmed via live
  match_chunks (cosine distance); HNSW + ector_cosine_ops defined in
  ackend/migrations/0001_init.sql. No migration change needed. NOTE: this
  environment has no SQL exec path (no execute_sql RPC / no DATABASE_URL /
  CLI not linked) - a human should run the catalog SQL in the Supabase SQL
  editor to confirm visually.
- Task 2 (stable chunk identity through retrieval): DONE in Python layer.
  RetrievedChunk now carries stable_chunk_id + document_id, source_file,
  page_start/page_end, subsection, clause. hybrid_retrieval._enrich_chunks
  populates them from the chunks row (metadata jsonb) keyed by the internal
  uuid (which still anchors [chunk:id] markers + citation verification).
  Verified live: retrieve_hybrid returns resolved stable ids + pages.
  chat.py._citations_from now emits the stable chunk_id + full provenance.
- Task 3 (curated eval set): DRAFTED eval/curated_eval.yaml (10 answerable
  across pmfby/pacs_governance/pacs_computerization/financial_inclusion + 4
  unanswerable off-domain cases). cceptable_chunk_ids intentionally EMPTY -
  needs HUMAN review before use as authoritative Recall target. Do NOT
  auto-populate from the retriever. Regression gold remains eval/gold_cases.yaml.

Pending (Tasks 4-13) not started this session, per scope.

## Phase 1 - Task 4 (Retrieval Strategy Evaluation) DONE

Three modes run on the SAME corpus + SAME 40 answerable gold cases
(retriever-anchored eval/gold_cases.yaml):

| Metric        | Dense | Hybrid | Hybrid+Reranker |
|---------------|-------|--------|-----------------|
| Recall@1      | 0.800 | 0.750  | 0.500           |
| Recall@3      | 0.900 | 0.850  | 0.750           |
| Recall@5      | 0.925 | 0.875  | 0.825           |
| Recall@10     | 0.950 | 0.900  | 0.900           |
| Recall@20     | 0.950 | 0.900  | 0.900           |
| MRR           | 0.856 | 0.806  | 0.645           |
| Domain acc    | 0.925 | 0.925  | 0.925           |
| Contamination | 0     | 0      | 0               |

Curated set (eval/curated_eval.yaml): diagnostic only - acceptable_chunk_ids
EMPTY, so authoritative recall NOT computed (no labels manufactured). Doc-presence
diagnostic: expected source surfaces in top-20 for 8/10 answerable; the 2 misses
are inancial_inclusion -> out_of_scope misclassification (domain-anchor gap,
not retrieval). All 4 unanswerable cases: retrieval returns no in-domain evidence,
gate would reject (correct).

RERANKER DECISION: KEEP DISABLED. Reranker measurably degrades top-ranked recall
(R@1 0.80->0.50, MRR 0.856->0.645) by reordering a relevant dense-top chunk below
rank 5 on several cases; it helps on ~1 case. Hybrid (RRF) is marginally below
dense, but the gap is inflated by an eval artifact: the dense eval path passes
match_domain=None for out_of_scope-classified queries (retrieving broadly), while
hybrid correctly passes the predicted domain and returns empty (matching
production, which abstains on out_of_scope). 3 domain-mismatch cases are shared
across all modes (classifier errors, e.g. pacs_governance->pacs_computerization/
out_of_scope) - a domain-anchor gap, not a retrieval-strategy issue.

Production default remains DENSE (match_chunks). No system change made to chase
the score. Artifacts: eval/task4_experiment.json, eval/task4_disagreements.txt.
