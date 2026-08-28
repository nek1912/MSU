# Phase 2A Pre-Implementation Audit Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Conduct a data-flow audit of the current codebase and produce `docs/phase2a_preimplementation_audit.md` identifying all gaps between current code and MVP manifest requirements.

**Architecture:** Follow the data path from MVP manifest → PDF discovery → extraction → chunking → embedding → storage → retrieval → generation → citations. For each stage, read actual code, answer brainstorming questions, compare against MVP requirements, and identify gaps with severity and evidence.

**Tech Stack:** Python, YAML, SQL, FastAPI, Supabase, Gemini API

## Global Constraints

- Do not modify any code during this audit — research only
- Every finding must cite actual file/function/test evidence
- Severity levels: P0 (blocks MVP), P1 (degrades quality), P2 (nice-to-have)
- Output file: `docs/phase2a_preimplementation_audit.md`
- Do not treat preliminary findings as established facts — verify each one

---

### Task 1: Audit Manifest & Filesystem Consistency

**Files:**
- Read: `corpus/manifests/mvp_sources.yaml`
- Read: `corpus/manifests/hold_sources.yaml`
- Verify: All MVP manifest files exist on disk

**Interfaces:**
- Consumes: MVP manifest definitions
- Produces: Manifest-filesystem consistency report

- [ ] **Step 1: Read MVP manifest**

Read `corpus/manifests/mvp_sources.yaml` and extract all source entries with their file paths.

- [ ] **Step 2: Verify file existence**

For each source in MVP manifest, verify the file exists at the specified path. Check:
- `corpus/seeds/Model Byelaws 05.01.2023.pdf`
- `corpus/seeds/Revised Scheme guidelines (Computerization of PACS project).pdf`
- `corpus/seeds/Corrigendum and letter Jun 12, 2023.pdf`
- `corpus/seeds/operational_guidelines_pmfby.pdf`
- `corpus/seeds/NSFI_2025_30.pdf`

- [ ] **Step 3: Verify no hold files are ingestible**

Check that hold_sources.yaml files are not referenced by any ingestion code.

- [ ] **Step 4: Document findings**

Record manifest-filesystem consistency in audit report section 1.

---

### Task 2: Audit Ingestion Pipeline

**Files:**
- Read: `ingestion/ingestion/ingest.py`
- Read: `ingestion/ingestion/loader.py`
- Read: `ingestion/ingestion/chunker.py`

**Interfaces:**
- Consumes: Current ingestion code
- Produces: Ingestion pipeline gap analysis

- [ ] **Step 1: Analyze ingest.py**

Read `ingestion/ingestion/ingest.py` and answer:
- How does it discover files? (line 41: `SEEDS_DIR.glob("*.md")`)
- Can it accidentally ingest hold/non-MVP files?
- Can it read the MVP manifest directly?
- Is ingestion deterministic?
- Is ingestion idempotent?
- What happens if same document ingested twice?
- What happens if document replaced?
- Can stale chunks remain?
- Is source_id preserved?
- Is document_id deterministic?
- Is chunk_id deterministic?

- [ ] **Step 2: Analyze loader.py**

Read `ingestion/ingestion/loader.py` and answer:
- How does it parse chunk files?
- What format does it expect?

- [ ] **Step 3: Analyze chunker.py**

Read `ingestion/ingestion/chunker.py` and answer:
- What chunking algorithm is used?
- Is it heading-aware?
- Does it preserve page boundaries?
- Does it preserve section metadata?
- What token/chunk limits are implemented?
- Can chunks be empty?
- Is overlap deterministic?

- [ ] **Step 4: Document findings**

Record ingestion pipeline gaps in audit report section 2.

---

### Task 3: Audit Metadata Model

**Files:**
- Read: `corpus/manifests/mvp_sources.yaml` (metadata fields)
- Read: `backend/migrations/0001_init.sql` (documents table schema)
- Read: `corpus/seeds/*.md` (frontmatter fields)

**Interfaces:**
- Consumes: MVP manifest, DB schema, seed file metadata
- Produces: Metadata model gap analysis

- [ ] **Step 1: Extract MVP manifest metadata fields**

List all metadata fields in mvp_sources.yaml:
- source_id, filename, path, actual_title, issuing_organization
- document_date, effective_date, document_type, jurisdiction, state
- official_source_url, digital_scanned, status, primary_supplementary
- target_domain, target_seed, collection_status, mvp_required
- modifies, base_incorporates, legal_note, verification_note

- [ ] **Step 2: Extract DB schema fields**

List all fields in documents table:
- id, source_id, title, organization, jurisdiction, state
- domain, document_type, source_url, effective_date, verified_date
- document_hash, created_at

- [ ] **Step 3: Compare metadata models**

Identify missing fields:
- Manifest has: filename, path, actual_title, issuing_organization, document_date, official_source_url, digital_scanned, status, primary_supplementary, target_domain, target_seed, collection_status, mvp_required, modifies, base_incorporates, legal_note, verification_note
- DB has: id, source_id, title, organization, jurisdiction, state, domain, document_type, source_url, effective_date, verified_date, document_hash, created_at

- [ ] **Step 4: Check if missing metadata required by Gate 2**

Determine if any missing metadata fields are required by Gate 2 invariants (from Phase 2A spec).

- [ ] **Step 5: Document findings**

Record metadata model gaps in audit report section 4.

---

### Task 4: Audit Embedding Behavior

**Files:**
- Read: `backend/app/providers/embeddings.py`
- Read: `backend/app/config.py` (EMBED_DIMS, REQUEST_TIMEOUT_S)

**Interfaces:**
- Consumes: Embedding provider code
- Produces: Embedding behavior analysis

- [ ] **Step 1: Analyze GeminiEmbeddingProvider**

Read `backend/app/providers/embeddings.py` and answer:
- How is Gemini embedding called?
- Does it process one string at a time or batches?
- Does it enforce expected vector dimension?
- What happens on malformed provider output?
- What happens on rate limiting?
- What happens on timeout?
- What happens if embedding generation partially succeeds?
- Can failed embeddings create incomplete ingestion?

- [ ] **Step 2: Document findings**

Record embedding behavior in audit report section 5.

---

### Task 5: Audit Supabase Ingestion

**Files:**
- Read: `backend/migrations/0001_init.sql`
- Read: `backend/app/db.py`
- Read: `ingestion/ingestion/ingest.py` (Supabase operations)

**Interfaces:**
- Consumes: DB schema, Supabase client, ingestion code
- Produces: Supabase ingestion analysis

- [ ] **Step 1: Analyze match_chunks RPC**

Read the `match_chunks` function in `0001_init.sql` and answer:
- How are documents/chunks inserted?
- How are old chunks removed during replacement?
- Are transactions used where appropriate?
- Can duplicate chunks occur?
- How is metadata stored?
- Does retrieval RPC filter by domain, jurisdiction, state?
- Can central sources coexist correctly with Gujarat sources?
- Can wrong-state chunks be returned?

- [ ] **Step 2: Document findings**

Record Supabase ingestion behavior in audit report section 6.

---

### Task 6: Audit Retrieval Behavior

**Files:**
- Read: `backend/app/retrieval.py`
- Read: `backend/app/routes/chat.py`
- Read: `backend/app/config.py` (thresholds)

**Interfaces:**
- Consumes: Retrieval code, chat route, config
- Produces: Retrieval behavior analysis

- [ ] **Step 1: Analyze retrieval.py**

Read `backend/app/retrieval.py` and answer:
- What exact retrieval function does /chat use?
- Does it use same retrieval as Gate 2 evaluation?
- Is reranking implemented or planned?
- What is current top-K?
- How are empty retrieval results handled?
- How is retrieval failure distinguished from "no evidence"?
- Does evidence gating happen before generation?
- Can weak retrieval still reach LLM?

- [ ] **Step 2: Analyze chat route**

Read `backend/app/routes/chat.py` and answer:
- How does the chat route use retrieval?
- What happens on retrieval failure?

- [ ] **Step 3: Document findings**

Record retrieval behavior in audit report section 7.

---

### Task 7: Audit Citation Behavior

**Files:**
- Read: `backend/app/generation.py`
- Read: `backend/app/routes/chat.py` (citation handling)

**Interfaces:**
- Consumes: Generation code, chat route
- Produces: Citation behavior analysis

- [ ] **Step 1: Analyze generation.py**

Read `backend/app/generation.py` and answer:
- Does generation only receive retrieved evidence?
- Does it know source metadata?
- Can it cite a chunk not actually retrieved?
- Does citation verification verify actual retrieved set?
- Does it verify source/domain/jurisdiction?
- Does zero citation cause failure for answerable answers?
- Does unsupported evidence cause abstention?

- [ ] **Step 2: Document findings**

Record citation behavior in audit report section 8.

---

### Task 8: Audit Gold Cases Consistency

**Files:**
- Read: `eval/gold_cases.yaml`
- Read: `corpus/manifests/mvp_sources.yaml`
- Read: `sources.yaml`

**Interfaces:**
- Consumes: Gold cases, MVP manifest, sources.yaml
- Produces: Gold cases consistency analysis

- [ ] **Step 1: Extract gold case source_ids**

List all source_ids referenced in gold_cases.yaml:
- model_pacs_bylaws, ministry_cooperation, ministry_pacs, etc.

- [ ] **Step 2: Extract MVP manifest source_ids**

List all source_ids in mvp_sources.yaml:
- pacs_model_bylaws_2023, pacs_computerization_guidelines, etc.

- [ ] **Step 3: Compare source_ids**

Identify mismatches between gold cases and MVP manifest.

- [ ] **Step 4: Validate gold case structure**

For each answerable case, verify:
- source_id must exist
- relevant_chunk_ids must exist (after ingestion)
- chunks must genuinely support the question
- jurisdiction must match
- domain must match

For unanswerable cases:
- source_id list empty
- chunk_id list empty

- [ ] **Step 5: Document findings**

Record gold cases inconsistencies in audit report section 12.

---

### Task 9: Audit Failure Handling

**Files:**
- Read: `ingestion/ingestion/ingest.py` (error handling)
- Read: `backend/app/providers/embeddings.py` (error handling)
- Read: `backend/app/retrieval.py` (error handling)
- Read: `backend/app/routes/chat.py` (error handling)

**Interfaces:**
- Consumes: Error handling code across pipeline
- Produces: Failure handling analysis

- [ ] **Step 1: Analyze extraction failures**

How are PDF extraction failures reported? Can failed extraction silently enter vector database?

- [ ] **Step 2: Analyze embedding failures**

What happens on malformed provider output, rate limiting, timeout, partial success?

- [ ] **Step 3: Analyze retrieval failures**

How is retrieval failure distinguished from "no evidence"?

- [ ] **Step 4: Document findings**

Record failure handling in audit report section 9.

---

### Task 10: Audit Security & Resource Risks

**Files:**
- Read: `ingestion/ingestion/ingest.py` (path handling)
- Read: `backend/app/providers/embeddings.py` (API key handling)
- Read: `backend/app/config.py` (environment variables)

**Interfaces:**
- Consumes: Security-relevant code
- Produces: Security and resource risk analysis

- [ ] **Step 1: Check .env handling**

Verify .env is never committed, API keys never enter corpus metadata.

- [ ] **Step 2: Check path traversal**

Verify raw document paths do not leak into user responses, PDFs cannot cause path traversal.

- [ ] **Step 3: Check arbitrary file ingestion**

Verify only manifest-approved files are ingestible.

- [ ] **Step 4: Analyze memory risks**

Identify steps that could cause excessive memory use on 8GB RAM / i3 CPU machine:
- PDF parsing
- Large documents
- Docling
- FAISS construction
- Embedding batches
- Concurrent processing

- [ ] **Step 5: Document findings**

Record security and resource risks in audit report sections 10-11.

---

### Task 11: Audit Production vs Evaluation Consistency

**Files:**
- Read: `eval/run_retrieval_eval.py`
- Read: `backend/app/retrieval.py`
- Read: `backend/app/routes/chat.py`

**Interfaces:**
- Consumes: Production and evaluation retrieval code
- Produces: Consistency analysis

- [ ] **Step 1: Compare retrieval implementations**

Check if production retrieval and Gate 2 evaluation use same:
- Chunk format
- Embeddings
- Metadata
- Filtering
- Supabase RPC
- Top-K
- Scoring assumptions

- [ ] **Step 2: Document discrepancies**

If they differ, explain the discrepancy.

- [ ] **Step 3: Document findings**

Record production-vs-evaluation inconsistencies in audit report section 12.

---

### Task 12: Compile Final Audit Report

**Files:**
- Create: `docs/phase2a_preimplementation_audit.md`

**Interfaces:**
- Consumes: All findings from Tasks 1-11
- Produces: Complete audit report

- [ ] **Step 1: Gather all findings**

Collect findings from Tasks 1-11.

- [ ] **Step 2: Organize by sections**

Organize findings into the 18-section structure defined in the spec.

- [ ] **Step 3: Apply severity levels**

Assign P0/P1/P2 severity to each finding based on:
- P0: Blocks MVP — must be fixed before any ingestion
- P1: Degrades quality — should be fixed for Gate 2 pass
- P2: Nice-to-have — can be deferred if time-constrained

- [ ] **Step 4: Add evidence citations**

For each finding, cite:
- File path
- Function/class name
- Line numbers (where relevant)
- Test coverage (if applicable)

- [ ] **Step 5: Write recommended minimal changes**

For each gap, recommend minimal changes to fix it.

- [ ] **Step 6: List files to modify**

List all files that would need modification.

- [ ] **Step 7: List tests to add**

List all tests that should be added.

- [ ] **Step 8: Identify dependencies/blockers**

Identify any dependencies or blockers for implementation.

- [ ] **Step 9: Final review**

Review the complete audit report for:
- Completeness (all 18 sections filled)
- Accuracy (all findings verified with evidence)
- Clarity (another engineer can understand)
- Actionability (clear next steps)

- [ ] **Step 10: Save audit report**

Save to `docs/phase2a_preimplementation_audit.md`.
