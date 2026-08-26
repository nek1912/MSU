"""Domain classifier evaluation — keyword short-circuit path only.

Tests the keyword-based classification in AnchorStore.classify() without
requiring a live embedding provider.  Loads keyword_rules.json and checks
whether any domain keyword appears in the lowered question text.

Usage:
    python eval/run_domain_eval.py
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BACKEND_DATA = Path(__file__).resolve().parent.parent / "backend" / "data"
CASES_PATH = Path(__file__).resolve().parent / "domain_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "domain_eval.json"


# ---------------------------------------------------------------------------
# Minimal YAML-ish parser (avoids PyYAML dependency)
# ---------------------------------------------------------------------------
def _parse_yaml_cases(text: str) -> list[dict]:
    """Parse the simple YAML list-of-maps format used by domain_cases.yaml."""
    cases: list[dict] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("- "):
            if current is not None:
                cases.append(current)
            current = {}
            rest = line[2:]
            if ": " in rest:
                k, v = rest.split(": ", 1)
                current[k.strip()] = v.strip().strip('"').strip("'")
        elif current is not None and ": " in line:
            k, v = line.split(": ", 1)
            current[k.strip()] = v.strip().strip('"').strip("'")
    if current is not None:
        cases.append(current)
    return cases


# ---------------------------------------------------------------------------
# Keyword classifier (mirrors AnchorStore.classify keyword short-circuit)
# ---------------------------------------------------------------------------
def load_keyword_rules() -> dict[str, list[str]]:
    path = BACKEND_DATA / "keyword_rules.json"
    return json.loads(path.read_text(encoding="utf-8"))


def classify_by_keywords(question: str, rules: dict[str, list[str]]) -> str:
    """Return first matching domain or 'out_of_scope'."""
    lowered = question.lower()
    for domain, keywords in rules.items():
        if any(kw in lowered for kw in keywords):
            return domain
    return "out_of_scope"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
ALL_DOMAINS = ["cooperative", "pacs", "schemes", "pmfby", "agriculture",
               "finlit", "grievance", "out_of_scope"]


def compute_metrics(results: list[dict]) -> dict:
    correct = sum(1 for r in results if r["predicted"] == r["expected"])
    total = len(results)
    accuracy = correct / total if total else 0.0

    # Per-domain
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)
    for r in results:
        exp, pred = r["expected"], r["predicted"]
        if exp == pred:
            tp[exp] += 1
        else:
            fn[exp] += 1
            fp[pred] += 1

    per_domain = {}
    for d in ALL_DOMAINS:
        precision = tp[d] / (tp[d] + fp[d]) if (tp[d] + fp[d]) else 0.0
        recall = tp[d] / (tp[d] + fn[d]) if (tp[d] + fn[d]) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_domain[d] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": tp[d] + fn[d],
        }

    # Confusion pairs
    confusion = defaultdict(int)
    for r in results:
        if r["predicted"] != r["expected"]:
            confusion[f"{r['expected']} -> {r['predicted']}"] += 1
    confusion_pairs = dict(sorted(confusion.items(), key=lambda x: -x[1]))

    # Out-of-scope rejection rate
    oos_cases = [r for r in results if r["expected"] == "out_of_scope"]
    oos_rejected = sum(1 for r in oos_cases if r["predicted"] == "out_of_scope")
    oos_rate = oos_rejected / len(oos_cases) if oos_cases else 0.0

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "per_domain": per_domain,
        "confusion_pairs": confusion_pairs,
        "out_of_scope_rejection_rate": round(oos_rate, 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    cases_text = CASES_PATH.read_text(encoding="utf-8")
    cases = _parse_yaml_cases(cases_text)
    rules = load_keyword_rules()

    results = []
    for case in cases:
        question = case["question"]
        expected = case["expected"]
        predicted = classify_by_keywords(question, rules)
        results.append({
            "question": question,
            "expected": expected,
            "predicted": predicted,
            "correct": predicted == expected,
            "note": case.get("note", ""),
        })

    metrics = compute_metrics(results)

    # Human-readable summary
    print(f"\n{'='*60}")
    print(f"  DOMAIN CLASSIFIER EVALUATION — keyword short-circuit")
    print(f"{'='*60}")
    print(f"\n  Total cases:  {metrics['total']}")
    print(f"  Correct:      {metrics['correct']}")
    print(f"  Accuracy:     {metrics['accuracy']:.1%}")
    print(f"\n  Per-domain precision / recall / f1:")
    for d in ALL_DOMAINS:
        m = metrics["per_domain"][d]
        print(f"    {d:20s}  P={m['precision']:.2f}  R={m['recall']:.2f}  F1={m['f1']:.2f}  (n={m['support']})")
    print(f"\n  Out-of-scope rejection rate: {metrics['out_of_scope_rejection_rate']:.1%}")
    if metrics["confusion_pairs"]:
        print(f"\n  Confusion pairs:")
        for pair, count in metrics["confusion_pairs"].items():
            print(f"    {pair}: {count}")
    else:
        print(f"\n  No confusion pairs — perfect classification.")
    print(f"\n{'='*60}\n")

    # Write JSON report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"metrics": metrics, "cases": results}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Report written to {REPORT_PATH}")

    # Exit code: 1 if any failures
    failures = [r for r in results if not r["correct"]]
    if failures:
        print(f"\n  FAILURES ({len(failures)}):")
        for f in failures:
            print(f"    [{f['expected']}->{f['predicted']}] {f['question']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
