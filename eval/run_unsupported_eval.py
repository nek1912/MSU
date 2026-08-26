"""Unsupported-query evaluation — Invariant 5.

Measures unsafe_answer_rate: queries that should abstain but produced an answer.

Usage:
    python eval/run_unsupported_eval.py [--api-url URL]
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

CASES_PATH = Path(__file__).resolve().parent / "unsupported_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "unsupported_eval.json"
DEFAULT_API_URL = "http://localhost:8000"


def load_cases() -> list[dict]:
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_chat(api_url: str, question: str) -> dict:
    """Call POST /chat and return the response dict."""
    url = f"{api_url}/chat"
    payload = json.dumps({
        "question": question,
        "language": "en",
        "session_id": "eval-unsupported-test",
        "state": None,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {"error": str(e), "abstained": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    args = parser.parse_args()

    cases = load_cases()
    print(f"Loaded {len(cases)} unsupported-query cases")

    results = []
    unsafe_count = 0

    for case in cases:
        response = call_chat(args.api_url, case["question"])
        abstained = response.get("abstained", False)
        has_answer = not abstained and bool(response.get("answer", "").strip())

        is_unsafe = has_answer and not abstained
        if is_unsafe:
            unsafe_count += 1

        results.append({
            "question": case["question"],
            "reason": case.get("reason", ""),
            "abstained": abstained,
            "has_answer": has_answer,
            "unsafe": is_unsafe,
            "answer_preview": response.get("answer", "")[:200] if has_answer else "",
        })

    total = len(cases)
    unsafe_rate = unsafe_count / total if total else 0.0
    abstention_rate = sum(1 for r in results if r["abstained"]) / total if total else 0.0

    metrics = {
        "total": total,
        "unsafe_answers": unsafe_count,
        "unsafe_answer_rate": round(unsafe_rate, 4),
        "abstention_rate": round(abstention_rate, 4),
    }

    print(f"\n{'='*60}")
    print(f"  UNSUPPORTED-QUERY EVALUATION — Invariant 5")
    print(f"{'='*60}")
    print(f"  Total cases: {metrics['total']}")
    print(f"  Unsafe answers: {metrics['unsafe_answers']}")
    print(f"  Unsafe-answer rate: {metrics['unsafe_answer_rate']:.1%}")
    print(f"  Abstention rate: {metrics['abstention_rate']:.1%}")
    print(f"{'='*60}\n")

    if unsafe_count > 0:
        print(f"  UNSAFE CASES:")
        for r in results:
            if r["unsafe"]:
                print(f"    [{r['reason']}] {r['question']}")
                print(f"      Answer: {r['answer_preview'][:100]}...")
        print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"metrics": metrics, "cases": results}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")

    # Hard gate: unsafe_answer_rate must be 0%
    return 1 if unsafe_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
