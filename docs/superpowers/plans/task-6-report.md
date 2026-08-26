# Task 6: Create unsupported-query evaluation script + 30 cases

**Status:** DONE

## Files Created

1. `eval/unsupported_cases.yaml` — 30 deliberately unanswerable questions
2. `eval/run_unsupported_eval.py` — evaluation script for Invariant 5

## Test Cases

- 28 out-of-scope questions (completely outside corpus scope)
- 2 ambiguous questions (agriculture/finlit domain but unanswerable from corpus)

## Script Features

- Calls `POST /chat` for each question via `--api-url` (default: `http://localhost:8000`)
- Measures `unsafe_answer_rate`: queries that produced an answer but should have abstained
- Measures `abstention_rate` as diagnostic metric
- Hard gate: returns exit code 1 if any unsafe answers detected
- Writes JSON report to `eval/reports/unsupported_eval.json`

## Verification

- `python eval/run_unsupported_eval.py --help` — shows usage ✓
- `python -c "import yaml; print(len(yaml.safe_load(open('eval/unsupported_cases.yaml'))), 'cases')"` — prints "30 cases" ✓

## Commit

`feat: add unsupported-query evaluation script and 30 test cases (Invariant 5)`
