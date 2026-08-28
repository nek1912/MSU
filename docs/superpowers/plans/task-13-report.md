# Task 13: Update Gold Case Source IDs

## Status: DONE

## Summary

Updated `eval/gold_cases.yaml` source IDs to align with the MVP manifest (`corpus/manifests/mvp_sources.yaml`). Applied two justified mappings and marked all cases referencing unmapped sources as `answerable: false`.

## ID Mappings Applied

| Old ID | New ID | Justification |
|--------|--------|---------------|
| `model_pacs_bylaws` | `pacs_model_bylaws_2023` | Same document: PACS Model Bye-laws 2023 |
| `pmfby_guidelines` | `pmfby_operational_guidelines` | Same document: PMFBY Operational Guidelines |

## Unmapped Sources (not in MVP)

These source IDs were referenced in gold cases but have no MVP equivalent:

- `gujarat_cooperative_act` — Gujarat cooperative law (NOT COVERED in MVP)
- `ministry_cooperation` — Ministry of Cooperation docs (NOT in MVP corpus)
- `ministry_pacs` — Ministry PACS docs (NOT in MVP corpus)
- `ministry_pacs_schemes` — Ministry PACS schemes (NOT in MVP corpus)
- `pmfby_faq` — PMFBY FAQ (NOT in MVP corpus)
- `rbi_financial_literacy` — RBI financial literacy (NOT in MVP corpus)
- `pmjdy_financial_literacy` — PMJDY financial literacy (NOT in MVP corpus, explicitly "NOT COVERED")

## Changes Applied

For every case referencing **any** unmapped source:
1. Set `answerable: false`
2. Cleared `relevant_source_ids: []`
3. Cleared `relevant_chunk_ids: []`

For cases referencing **only** mapped sources:
1. Updated source IDs to new names
2. Kept `answerable: true` and existing lists

## Results

| Metric | Value |
|--------|-------|
| Total cases | 245 |
| Answerable (true) | 40 |
| Unanswerable (false) | 205 |
| Remaining unique source IDs | `pacs_model_bylaws_2023`, `pmfby_operational_guideline` |

## Domain Breakdown (answerable / total)

| Domain | Answerable | Total |
|--------|-----------|-------|
| cooperative | 14 | 35 |
| pacs | 4 | 33 |
| schemes | 0 | 33 |
| pmfby | 22 | 35 |
| agriculture | 0 | 30 |
| finlit | 0 | 34 |
| grievance | 0 | 30 |
| out_of_scope | 0 | 15 |

## Validation

- [x] Total case count preserved (245)
- [x] All `answerable: false` cases have empty `relevant_source_ids` and `relevant_chunk_ids`
- [x] All `answerable: true` cases have non-empty `relevant_source_ids`
- [x] All remaining source IDs are valid MVP IDs
- [x] No structure violations

## Concerns

- **Low answerable count**: Only 40/245 cases (16%) are answerable from the MVP corpus. This is expected — most gold cases reference cooperative law, ministry docs, financial literacy, and grievance sources not yet in the MVP corpus. These cases will become answerable as the corpus expands.
- **Finlit cases**: All 34 finlit cases are unanswerable. The MVP has `nsfi_2025_30` (RBI National Strategy for Financial Inclusion), but gold cases reference `rbi_financial_literacy` and `pmjdy_financial_literacy` which are different documents. A mapping was not justified without verifying document equivalence.
