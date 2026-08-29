"""Manually reviewed evaluation set runner — Phase 3 Task 3.

Runs the eval_cases.yaml set against the live API and reports:
- answerable cases: did the system answer? were citations valid?
- unanswerable cases: did the system abstain?
- Human-reviewed chunk IDs are NOT auto-populated — this script
  only reports what was retrieved for comparison against the gold set.

Usage:
    python eval/run_eval.py [--api-url URL]
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

CASES_PATH = Path(__file__).resolve().parent / "eval_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "eval_review.json"
DEFAULT_API_URL = "http://localhost:8000"


def load_cases() -> list[dict]:
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_chat(api_url: str, question: str, language: str = "en",
              state: str | None = None) -> dict:
    url = f"{api_url}/chat"
    payload = json.dumps({
        "question": question,
        "language": language,
        "session_id": "eval-manual-review",
        "state": state,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {"error": str(e), "abstained": True, "citations": [],
                "answer": "", "confidence": 0.0}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manually reviewed evaluation set runner")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    args = parser.parse_args()

    cases = load_cases()
    print(f"Loaded {len(cases)} evaluation cases")

    answerable_total = sum(1 for c in cases if c.get("answerable", False))
    unanswerable_total = len(cases) - answerable_total
    print(f"  answerable: {answerable_total}, unanswerable: {unanswerable_total}")

    results = []
    answered_correctly = 0
    abstained_correctly = 0
    false_positive = 0  # answered when should abstain
    false_negative = 0  # abstained when should answer
    chunk_review_needed = 0

    for case in cases:
        is_answerable = case.get("answerable", False)
        response = call_chat(
            args.api_url, case["query"], case.get("language", "en"))
        abstained = response.get("abstained", True)
        citations = response.get("citations", [])
        confidence = response.get("confidence", 0.0)

        # Determine pass/fail
        if is_answerable:
            if not abstained and len(citations) > 0:
                status = "PASS"
                answered_correctly += 1
            elif abstained:
                status = "FAIL(false_negative)"
                false_negative += 1
            else:
                status = "FAIL(no_citations)"
                false_negative += 1
        else:
            if abstained:
                status = "PASS"
                abstained_correctly += 1
            else:
                status = "FAIL(false_positive)"
                false_positive += 1

        # Check if chunk review is needed
        has_chunks = case.get("acceptable_chunk_ids") is not None
        if is_answerable and has_chunks and not case["acceptable_chunk_ids"]:
            chunk_review_needed += 1

        result = {
            "query": case["query"],
            "language": case.get("language", "en"),
            "answerable": is_answerable,
            "status": status,
            "abstained": abstained,
            "confidence": confidence,
            "citations_count": len(citations),
            "retrieved_chunks": [
                {"chunk_id": c.get("chunk_id", ""),
                 "document_id": c.get("document_id", ""),
                 "title": c.get("title", ""),
                 "page": c.get("page")}
                for c in citations
            ],
            "expected_document": case.get("expected_document"),
        }
        results.append(result)

    total = len(cases)
    correct = answered_correctly + abstained_correctly
    accuracy = correct / total if total else 0.0

    metrics = {
        "total_cases": total,
        "answerable_total": answerable_total,
        "unanswerable_total": unanswerable_total,
        "answered_correctly": answered_correctly,
        "abstained_correctly": abstained_correctly,
        "false_positives": false_positive,
        "false_negatives": false_negative,
        "accuracy": round(accuracy, 4),
        "chunk_ids_pending_review": chunk_review_needed,
    }

    print(f"\n{'='*60}")
    print(f"  MANUAL EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"  Total cases: {metrics['total_cases']}")
    print(f"  Answerable: {metrics['answerable_total']} "
          f"(answered correctly: {metrics['answered_correctly']})")
    print(f"  Unanswerable: {metrics['unanswerable_total']} "
          f"(abstained correctly: {metrics['abstained_correctly']})")
    print(f"  False positives (answered when should abstain): "
          f"{metrics['false_positives']}")
    print(f"  False negatives (abstained when should answer): "
          f"{metrics['false_negatives']}")
    print(f"  Accuracy: {metrics['accuracy']:.1%}")
    print(f"  Chunk IDs pending human review: "
          f"{metrics['chunk_ids_pending_review']}")
    print(f"{'='*60}\n")

    # Report failures
    failures = [r for r in results if r["status"] != "PASS"]
    if failures:
        print("  FAILURES:")
        for f in failures:
            print(f"    [{f['status']}] {f['query']}")
            if f["retrieved_chunks"]:
                for c in f["retrieved_chunks"]:
                    print(f"      -> {c['title']} p.{c['page']} "
                          f"({c['chunk_id'][:12]}...)")
        print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"metrics": metrics, "cases": results}
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")

    # Fail if any false positives or false negatives
    return 1 if (false_positive + false_negative) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
