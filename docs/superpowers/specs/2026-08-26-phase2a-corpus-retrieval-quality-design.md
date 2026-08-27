# Phase 2A: Corpus & Retrieval Quality Gate — Design

**Date:** 2026-08-26
**Status:** Approved
**Supersedes:** None (extends the Phase 0-1 foundation hardened in `eval/reports/foundation_report.md`)
**Gate:** Gate 2 — Corpus/Retrieval Quality

## 1. Scope

Replace all placeholder corpus content with verified official government text, measure retrieval quality empirically, and pass 6 hard invariants before any new user-facing features (Phase 3 grievance workflow, Phase 6 voice).

**Entry condition:** Phase 0-1 code/integrity gate passed (80 tests passing, foundation hardened).

**Exit condition:** All 6 hard invariants pass. Results recorded in `eval/reports/gate2_report.md`.

**Primary blocker:** Official document provision by the team. Everything downstream depends on this.

## 2. Hard Invariants

These 6 invariants define the Gate 2 pass condition. A single failure on any hard invariant blocks progression to Phase 3.

### Invariant 1 — No placeholder/invalid corpus records

**Gate:** 0 failures

`corpus_check.py` validates every seed file for:
- No `wikipedia_proxy` / `TODO` markers
- No empty/near-empty content
- No invalid URLs
- No duplicate `source_id`
- Source URL domain matches declared official_domain against approved registry
- No non-official domains where official source is required
- Required provenance metadata present: `source_id`, `url`, `organization`, `domain`, `jurisdiction`, `state`, `effective_date`, `verified_date`, `official_domain`, `source_type`
- Document-location metadata (page/section) required only when applicable (PDFs yes, HTML pages no)

### Invariant 2 — Verified official provenance

**Gate:** 100% machine validation + corpus source review

Every source must pass:
1. **Official-domain verification:** URL domain matches an approved official-domain registry
2. **Source metadata verification:** All required provenance fields present and consistent
3. **Manual/semantic verification:** Corpus entry reviewed to confirm the source is genuinely official and authoritative (not automatable — human/agent validation step)

Automated gate enforces (1) and (2). Step (3) is part of the corpus-review procedure during document acquisition.

### Invariant 3 — Wrong-state/jurisdiction contamination

**Gate:** 0 wrong-state contamination; 100% jurisdiction validity

Two measurements:
- `wrong_state_contamination = 0`: State-specific queries must not retrieve chunks from wrong states
- `jurisdiction_validity = 100%`: Central chunks allowed only when explicitly applicable to the query/domain

Central sources are legitimately retrievable for central-level questions. The invariant targets wrong-state retrieval, not central-source retrieval.

### Invariant 4 — Retrieval quality

**Gate:** Recall@5 ≥ pre-frozen target T

Metrics measured:
- `Recall@1`, `Recall@3`, `Recall@5`, `MRR`

Target T is frozen **before** running the final evaluation. No arbitrary targets chosen after seeing results.

If the team does not yet know what target is defensible for the corpus size, explicitly mark as `TARGET_PENDING — must be frozen before final Gate 2 evaluation`.

### Invariant 5 — Unsupported-query safety

**Gate:** 0% unsafe-answer rate on hard test set

Definitions:
```
unsafe_answer_rate = unsupported queries that produced an answer / total unsupported queries
```

Hard invariant: `unsafe_answer_rate = 0%` on the deliberately constructed test set.

Separately measured (diagnostic): `abstention_rate` on unsupported queries (target: 100%).

### Invariant 6 — Citation provenance integrity

**Gate:** 100% valid retrieved-chunk/source/domain/jurisdiction mapping

Every citation in a generated answer must:
1. Correspond to an actually retrieved chunk (not fabricated)
2. Belong to the permitted jurisdiction/domain for the query
3. Point to the actual source document

Distinct from citation entailment (does the chunk actually support the factual claim?), which is measured as a diagnostic metric only.

## 3. Diagnostic Metrics

Measured but not gated. Reported in `gate2_report.md` for visibility.

| Metric | Description |
|---|---|
| Hybrid domain accuracy | Keyword + embedding path accuracy |
| Recall@1, @3, @5, MRR | Retrieval ranking quality |
| Abstention rate | % of unsupported queries that correctly abstain |
| Citation provenance accuracy | % of citations pointing to valid retrieved chunks |
| Citation entailment accuracy | % of citations where the chunk actually supports the claim (manual evaluation subset) |
| p50 retrieval latency | Median retrieval time |
| p95 retrieval latency | 95th percentile retrieval time |

## 4. Source Replacement Workflow

### Step 1: sources.yaml Update

Add Gujarat state-specific entries. Required fields per source:
```yaml
- id: <source_id>
  url: <official_url>
  organization: <issuing_body>
  domain: <cooperative|pacs|schemes|pmfby|agriculture|finlit>
  jurisdiction: <central|state|central_and_state>
  state: <gujarat|null>
  effective_date: <YYYY-MM-DD|null>
  verified_date: <YYYY-MM-DD>
  official_domain: <approved_domain>
  source_type: <official_web_source|legislation|guidelines|faq|financial_literacy|model_bylaw>
```

### Step 2: Document Intake

Team provides official documents for each of the 12 seed domains:
- PDFs, text, or HTML from official .gov.in / ministry / RBI / PMFBY portals
- Each document tagged with the metadata from Step 1

### Step 3: Automated Validation

`corpus_check.py` (enhanced) validates all Invariant 1 criteria.

### Step 4: Manual/Semantic Verification

Corpus entry reviewed to confirm the source is genuinely official and authoritative (Invariant 2, step 3).

### Step 5: Docling Parsing + Chunking

- Parse each document with Docling → Markdown
- Split on heading boundaries, merge undersized sections
- Target ~600 tokens per chunk (hard range 400–800), 80-token overlap
- Store page number and section heading on every chunk (where applicable)

### Step 6: Embedding + Ingestion

- Generate 768-dim embeddings via `gemini-embedding-2` (one per string)
- Idempotent upsert to Supabase (delete old, insert new)
- Verify document/chunk counts match expected values

### Step 7: Idempotency Verification

Re-run ingestion. Assert document/chunk counts unchanged. No duplicates created.

## 5. Evaluation Design

### Phase A — Local FAISS Evaluation (before Supabase ingestion)

**5.1 Gold Cases Expansion**

Expand `eval/domain_cases.yaml` from 43 to 245 cases:
- 30 cases per domain (7 domains × 30 = 210)
- 5 adversarial cross-domain cases per domain (7 × 5 = 35)
- Each case tagged:
  ```yaml
  question: <string>
  expected_domain: <domain>
  expected_state: <gujarat|null>
  relevant_source_ids: [<id>, ...]
  relevant_chunk_ids: [<id>, ...]
  answerable: <true|false>
  ```

**Gold case validation:** Every `source_id` and `chunk_id` referenced must exist in the ingested corpus. Invalid references = invalid ground truth → fix before evaluation.

**5.2 Corpus Snapshot**

Record with every evaluation:
- `corpus_hash: <sha256 of all seed files>`
- `chunk_count`
- `document_count`
- `ingestion_timestamp`

Results are reproducible only against this snapshot.

**5.3 Hybrid Domain Accuracy**

- Run keyword-only path → record accuracy
- Run keyword + embedding anchor path → record accuracy
- Report both separately (do not conflate)

**5.4 Local Retrieval Recall**

- Ingest seed files into local FAISS index
- Run all answerable queries through retrieval
- Measure Recall@1, @3, @5, MRR
- Freeze gate target T before seeing results

**5.5 Jurisdiction Contamination Tests**

- Gujarat-specific queries → assert 0 wrong-state chunks retrieved
- Central-only queries → assert no state-specific chunks from wrong states
- `out_of_scope` rejection → assert abstention

**5.6 Unsupported-Query Tests**

- 30 deliberately unanswerable questions:
  - Topics outside corpus scope
  - Ambiguous queries requiring information not in any source
  - Questions about states/topics not covered
- Assert `unsafe_answer_rate = 0%`

### Phase B — Live Supabase Evaluation (after ingestion)

**5.7 Re-run all Phase A tests** against live Supabase using `match_chunks` RPC.

**5.8 Local-vs-Supabase Comparison**

FAISS and pgvector can legitimately produce ranking differences. Define acceptable retrieval agreement tolerance:
- Investigate discrepancies beyond tolerance
- Do not demand identical rankings
- Focus gate metrics on live Supabase results

**5.9 Latency Measurement**

Record p50 and p95 retrieval latency against live Supabase.

### Phase C — Citation Provenance Audit

**5.10 Manual Citation Verification Set**

- 50 generated answers (10 per domain, distributed across answerable/unanswerable)
- For each citation: verify chunk exists in retrieval, belongs to correct source, belongs to correct jurisdiction
- Measure citation_entailment_accuracy on a subset (does the chunk actually support the claim?)

## 6. Implementation Structure

### New/Modified Files

```
eval/
├── run_retrieval_eval.py      # NEW: Recall@1/3/5, MRR measurement
├── run_jurisdiction_eval.py   # NEW: contamination + validity tests
├── run_unsupported_eval.py    # NEW: unsafe-answer rate measurement
├── run_citation_eval.py       # NEW: citation provenance audit
├── gold_cases.yaml            # EXPANDED: ~200 cases with full metadata
├── unsupported_cases.yaml     # NEW: 30 unanswerable questions
├── citation_cases.yaml        # NEW: 50 citation verification cases
├── reports/
│   └── gate2_report.md        # NEW: final Gate 2 report
└── ...

corpus/
├── seeds/                     # REPLACED: 12 real official docs
│   ├── bylaws_governance.md
│   ├── bylaws_membership.md
│   ├── pacs_credit.md
│   ├── pacs_role.md
│   ├── pacs_schemes_computerization.md
│   ├── pmfby_eligibility.md
│   ├── pmfby_coverage.md
│   ├── pmfby_premium.md
│   ├── pmfby_claims.md
│   ├── rbi_finlit_awareness.md
│   ├── pmjdy_account.md
│   └── pmjdy_rupay.md
└── ...

sources.yaml                 # UPDATED: add Gujarat state sources, official_domain, source_type
ingestion/
├── ingest.py                 # EXISTING: verify idempotency
├── chunker.py                # EXISTING: verify heading-aware splitting
└── ...
```

## 7. Execution Order

```
 1. sources.yaml update (Gujarat entries + metadata fields)
 2. Team provides official documents for 12 seed files
 3. corpus_check.py enhanced validation
 4. Docling parsing + chunking
 5. Gemini API key for embedding (only provider dependency needed)
 6. Embedding + Supabase ingestion
 7. Idempotency verification
 8. gold_cases.yaml validation (every source_id/chunk_id must exist)
 9. Freeze gate target T (before seeing results)
10. Local FAISS evaluation (domain routing, retrieval, jurisdiction, abstention)
11. Live Supabase evaluation (same tests)
12. Local-vs-Supabase comparison (investigate discrepancies; define acceptable retrieval agreement tolerance)
13. Citation provenance audit
14. Record corpus hash/version + results in gate2_report.md
```

## 8. Dependencies & Risks

### Dependencies

| Dependency | Required by | Mitigation |
|---|---|---|
| Gemini API key | Embedding generation (step 5) | Only provider needed for Phase 2A core |
| Supabase project | Ingestion + live eval | Already provisioned per DECISIONS.md |
| Official documents | Steps 2-4 | **Primary blocker** — team must provide |
| Docling | Parsing | Already in `ingestion/` package |
| FAISS | Local eval | Install locally, no cloud dependency |

### Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Team can't provide all 12 docs | Incomplete corpus | Start with 3-4 domains, measure partial gate |
| Gemini embedding per-string guard fails | Must fall back to `gemini-embedding-001` | Phase 0 guard test catches this early |
| FAISS vs Supabase ranking divergence | Gate metrics differ locally vs live | Define acceptable agreement tolerance before evaluation |
| Gold cases reference non-existent chunks | Invalid ground truth | gold_cases.yaml validation step (step 8) |
| Recall@5 target too aggressive | Gate never passes | Freeze T before results; adjust if needed based on corpus size |

## 9. Reporting

Every Gate 2 report (`eval/reports/gate2_report.md`) must include:

```markdown
# Gate 2 Report

**Date:** YYYY-MM-DD
**Corpus hash:** <sha256>
**Chunk count:** <N>
**Document count:** <N>
**Ingestion timestamp:** <ISO>

## Hard Invariant Results

| # | Invariant | Target | Measured | Pass/Fail |
|---|---|---|---|---|
| 1 | No placeholder/invalid corpus | 0 failures | <N> | |
| 2 | Verified official provenance | 100% | <N>% | |
| 3 | Wrong-state contamination | 0 | <N> | |
| 4 | Retrieval Recall@5 | ≥ <T> | <X> | |
| 5 | Unsafe-answer rate | 0% | <X>% | |
| 6 | Citation provenance integrity | 100% | <X>% | |

## Diagnostic Metrics

| Metric | Value |
|---|---|
| Hybrid domain accuracy | |
| Recall@1 | |
| Recall@3 | |
| MRR | |
| Abstention rate | |
| Citation entailment accuracy | |
| p50 retrieval latency | |
| p95 retrieval latency | |

## Gate Decision

PASS / FAIL
```
