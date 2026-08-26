"""Gate 2 report generator.

Aggregates all Phase 2A evaluation results into a single Gate 2 report.
Requires eval/gate2_config.yaml with frozen recall_at_5_target.

Usage:
    python eval/run_gate2.py
"""
import json
import sys
from pathlib import Path

import yaml

REPORT_DIR = Path(__file__).resolve().parent / "reports"
CONFIG_PATH = Path(__file__).resolve().parent / "gate2_config.yaml"
SNAPSHOT_PATH = REPORT_DIR / "corpus_snapshot.json"
CORPUS_CHECK_PATH = REPORT_DIR / "corpus_check.json"
RETRIEVAL_PATH = REPORT_DIR / "retrieval_eval.json"
JURISDICTION_PATH = REPORT_DIR / "jurisdiction_eval.json"
UNSUPPORTED_PATH = REPORT_DIR / "unsupported_eval.json"
CITATION_PATH = REPORT_DIR / "citation_eval.json"
GATE2_PATH = REPORT_DIR / "gate2_report.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    # Gate 2 config MUST exist with frozen target
    if not CONFIG_PATH.exists():
        print(f"FATAL: Gate 2 config not found at {CONFIG_PATH}", file=sys.stderr)
        print("Create eval/gate2_config.yaml with recall_at_5_target before running Gate 2.", file=sys.stderr)
        return 1

    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    recall_target = config.get("recall_at_5_target")
    if recall_target is None:
        print("FATAL: recall_at_5_target not set in gate2_config.yaml", file=sys.stderr)
        return 1

    snapshot = load_json(SNAPSHOT_PATH)
    corpus = load_json(CORPUS_CHECK_PATH)
    retrieval = load_json(RETRIEVAL_PATH)
    jurisdiction = load_json(JURISDICTION_PATH)
    unsupported = load_json(UNSUPPORTED_PATH)
    citation = load_json(CITATION_PATH)

    # Check which reports are missing
    missing = []
    if not snapshot: missing.append("corpus_snapshot.json")
    if not corpus: missing.append("corpus_check.json")
    if not retrieval: missing.append("retrieval_eval.json")
    if not jurisdiction: missing.append("jurisdiction_eval.json")
    if not unsupported: missing.append("unsupported_eval.json")
    if not citation: missing.append("citation_eval.json")

    if missing:
        print(f"Missing reports: {missing}", file=sys.stderr)
        print("Run all evaluation scripts first.", file=sys.stderr)
        return 1

    # Compute invariant results
    inv1_pass = corpus.get("files_failed", 1) == 0 and len(corpus.get("placeholders_found", [])) == 0
    inv2_pass = corpus.get("files_failed", 1) == 0
    inv3_pass = jurisdiction.get("metrics", {}).get("wrong_state_contamination", 1) == 0

    measured_recall = retrieval.get("metrics", {}).get("recall_at", {}).get("r@5", 0.0)
    inv4_pass = measured_recall >= recall_target

    inv5_pass = unsupported.get("metrics", {}).get("unsafe_answer_rate", 1.0) == 0.0
    inv6_pass = (
        citation.get("metrics", {}).get("fabricated_citations", 1) == 0
        and citation.get("metrics", {}).get("zero_citation_failures", 1) == 0
    )

    all_pass = inv1_pass and inv2_pass and inv3_pass and inv4_pass and inv5_pass and inv6_pass

    # Build report
    lines = [
        "# Gate 2 Report",
        "",
        f"**Date:** {snapshot.get('ingestion_timestamp', 'N/A')}",
        f"**Corpus hash:** {snapshot.get('corpus_hash', 'N/A')}",
        f"**Source count:** {snapshot.get('source_count', 'N/A')}",
        f"**Document count:** {snapshot.get('document_count', 'N/A')}",
        f"**Chunk count:** {snapshot.get('chunk_count', 'N/A')}",
        f"**Ingestion timestamp:** {snapshot.get('ingestion_timestamp', 'N/A')}",
        "",
        "## Hard Invariant Results",
        "",
        "| # | Invariant | Target | Measured | Pass/Fail |",
        "|---|---|---|---|---|",
        f"| 1 | No placeholder/invalid corpus | 0 failures | {corpus.get('files_failed', 'N/A')} failed, {len(corpus.get('placeholders_found', []))} placeholders | {'PASS' if inv1_pass else 'FAIL'} |",
        f"| 2 | Verified official provenance | 100% | {corpus.get('files_passed', 0)}/{corpus.get('files_checked', 0)} | {'PASS' if inv2_pass else 'FAIL'} |",
        f"| 3 | Wrong-state contamination | 0 | {jurisdiction.get('metrics', {}).get('wrong_state_contamination', 'N/A')} | {'PASS' if inv3_pass else 'FAIL'} |",
        f"| 4 | Retrieval Recall@5 | ≥ {recall_target} | {measured_recall} | {'PASS' if inv4_pass else 'FAIL'} |",
        f"| 5 | Unsafe-answer rate | 0% | {unsupported.get('metrics', {}).get('unsafe_answer_rate', 'N/A'):.1%} | {'PASS' if inv5_pass else 'FAIL'} |",
        f"| 6 | Citation provenance integrity | 100% (0 fabricated, 0 zero-citation failures) | {citation.get('metrics', {}).get('citation_provenance_rate', 'N/A'):.1%} | {'PASS' if inv6_pass else 'FAIL'} |",
        "",
        "## Diagnostic Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Hybrid domain accuracy | Not yet measured |",
        f"| Recall@1 | {retrieval.get('metrics', {}).get('recall_at', {}).get('r@1', 'N/A')} |",
        f"| Recall@3 | {retrieval.get('metrics', {}).get('recall_at', {}).get('r@3', 'N/A')} |",
        f"| Recall@5 | {measured_recall} |",
        f"| MRR | {retrieval.get('metrics', {}).get('mrr', 'N/A')} |",
        f"| Abstention rate | {unsupported.get('metrics', {}).get('abstention_rate', 'N/A'):.1%} |",
        f"| Citation entailment accuracy | Not yet measured |",
        f"| p50 retrieval latency | Not yet measured |",
        f"| p95 retrieval latency | Not yet measured |",
        f"| Jurisdiction validity | {jurisdiction.get('metrics', {}).get('jurisdiction_validity', 'N/A')} |",
        f"| Zero-citation failures | {citation.get('metrics', {}).get('zero_citation_failures', 'N/A')} |",
        "",
        "## Gate Decision",
        "",
    ]

    if all_pass:
        lines.append("**PASS** — All 6 hard invariants pass.")
    else:
        lines.append("**FAIL** — One or more hard invariants failed. See details above.")
        failed = []
        if not inv1_pass: failed.append("Invariant 1 (corpus placeholders)")
        if not inv2_pass: failed.append("Invariant 2 (provenance)")
        if not inv3_pass: failed.append("Invariant 3 (jurisdiction contamination)")
        if not inv4_pass: failed.append(f"Invariant 4 (Recall@5: {measured_recall} < {recall_target})")
        if not inv5_pass: failed.append("Invariant 5 (unsafe answers)")
        if not inv6_pass: failed.append("Invariant 6 (citation integrity)")
        lines.append(f"Failed invariants: {', '.join(failed)}")

    report_text = "\n".join(lines) + "\n"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GATE2_PATH.write_text(report_text, encoding="utf-8")

    print(f"Gate 2 report written to {GATE2_PATH}")
    if all_pass:
        print("Gate 2: PASS")
    else:
        print("Gate 2: FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
