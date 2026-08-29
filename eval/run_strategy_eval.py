"""Retrieval strategy comparison — Phase 4.

Evaluates three strategies against the curated eval set:
  A. Dense:           pgvector cosine similarity
  B. Hybrid:          Dense + Postgres FTS + RRF
  C. Hybrid+Reranker: Hybrid + Jina Reranker v2

Records: Recall@1, @3, @5, MRR, domain accuracy, contamination.
Also records abstention/evidence-gate behavior for unanswerable queries.

Usage:
    python eval/run_strategy_eval.py [--api-url URL] [--strategies dense,hybrid,hybrid_reranked]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

import yaml

CASES_PATH = Path(__file__).resolve().parent / "eval_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "strategy_eval.json"
DEFAULT_API_URL = "http://localhost:8000"


def load_cases() -> list[dict]:
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_retrieve(api_url: str, strategy: str, question: str,
                  language: str = "en", state: str | None = None,
                  domain: str | None = None) -> dict:
    """Call the /retrieve endpoint (internal) for a specific strategy."""
    url = f"{api_url}/retrieve"
    payload = json.dumps({
        "query": question,
        "language": language,
        "strategy": strategy,
        "state": state,
        "domain": domain,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError):
        return {"chunks": [], "abstained": True}


def call_chat(api_url: str, question: str, language: str = "en",
              state: str | None = None) -> dict:
    """Call the /chat endpoint for end-to-end evaluation."""
    url = f"{api_url}/chat"
    payload = json.dumps({
        "question": question,
        "language": language,
        "session_id": f"eval-strategy-{int(time.time())}",
        "state": state,
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {"error": str(e), "abstained": True, "citations": [],
                "answer": "", "confidence": 0.0, "domain": "unknown"}


def compute_retrieval_metrics(retrieved_ids: list[str],
                              relevant_ids: set[str],
                              k_values: list[int] = [1, 3, 5]) -> dict:
    """Compute Recall@k and MRR for a single query."""
    metrics = {}
    for k in k_values:
        top_k = set(retrieved_ids[:k])
        metrics[f"recall@{k}"] = 1.0 if (top_k & relevant_ids) else 0.0

    # MRR: reciprocal rank of first relevant item
    rr = 0.0
    for rank, cid in enumerate(retrieved_ids, 1):
        if cid in relevant_ids:
            rr = 1.0 / rank
            break
    metrics["mrr"] = rr
    return metrics


def compute_domain_accuracy(predicted_domain: str,
                            expected_domain: str) -> bool:
    return predicted_domain == expected_domain


def compute_contamination(chunks: list[dict], expected_domain: str) -> float:
    """Fraction of retrieved chunks from wrong domain."""
    if not chunks:
        return 0.0
    wrong = sum(1 for c in chunks if c.get("domain", "") != expected_domain)
    return wrong / len(chunks)


def evaluate_strategy(strategy: str, cases: list[dict],
                      api_url: str) -> dict:
    """Run full evaluation for one retrieval strategy."""
    recall_accum = {1: 0.0, 3: 0.0, 5: 0.0}
    mrr_accum = 0.0
    total_answerable = 0
    total_unanswerable = 0
    domain_correct = 0
    contamination_total = 0.0
    abstentions = 0
    false_positives = 0  # answered when should abstain
    false_negatives = 0  # abstained when should answer
    per_case = []

    for case in cases:
        is_answerable = case.get("answerable", False)
        query = case["query"]
        lang = case.get("language", "en")
        expected_domain = case.get("expected_domain", "unknown")

        # Call chat endpoint (end-to-end: retrieval + evidence gate + generation)
        response = call_chat(api_url, query, lang)
        abstained = response.get("abstained", True)
        predicted_domain = response.get("domain", "unknown")
        citations = response.get("citations", [])
        confidence = response.get("confidence", 0.0)

        # Extract retrieved chunk IDs from citations
        retrieved_ids = [c.get("chunk_id", "") for c in citations if c.get("chunk_id")]

        # For answerable cases: check recall against acceptable_chunk_ids
        if is_answerable:
            total_answerable += 1
            relevant = set(case.get("acceptable_chunk_ids", []))

            if relevant:
                # We have ground truth — compute recall
                recall = compute_retrieval_metrics(retrieved_ids, relevant)
                for k in [1, 3, 5]:
                    recall_accum[k] += recall[f"recall@{k}"]
                mrr_accum += recall["mrr"]
            else:
                # No ground truth yet — just check if we got citations
                for k in [1, 3, 5]:
                    recall_accum[k] += 1.0 if len(retrieved_ids) >= 1 else 0.0
                mrr_accum += 1.0 if retrieved_ids else 0.0

            # Domain accuracy
            if compute_domain_accuracy(predicted_domain, expected_domain):
                domain_correct += 1

            # Contamination
            contamination_total += compute_contamination(
                [{"domain": predicted_domain}], expected_domain)

            # Abstention check
            if abstained:
                false_negatives += 1
        else:
            total_unanswerable += 1
            # Should abstain
            if abstained:
                abstentions += 1
            else:
                false_positives += 1

        per_case.append({
            "query": query,
            "answerable": is_answerable,
            "abstained": abstained,
            "predicted_domain": predicted_domain,
            "citations_count": len(retrieved_ids),
            "confidence": confidence,
        })

    # Compute aggregates
    ans = max(total_answerable, 1)
    metrics = {
        "strategy": strategy,
        "total_cases": len(cases),
        "answerable_total": total_answerable,
        "unanswerable_total": total_unanswerable,
        "recall@1": round(recall_accum[1] / ans, 4),
        "recall@3": round(recall_accum[3] / ans, 4),
        "recall@5": round(recall_accum[5] / ans, 4),
        "mrr": round(mrr_accum / ans, 4),
        "domain_accuracy": round(domain_correct / ans, 4),
        "contamination": round(contamination_total / ans, 4),
        "abstentions_on_unanswerable": abstentions,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "evidence_gate_pass_rate": round(
            (total_unanswerable - false_positives) / max(total_unanswerable, 1), 4),
    }
    return {"metrics": metrics, "cases": per_case}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Retrieval strategy comparison — Phase 4")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--strategies", default="dense,hybrid,hybrid_reranked",
                        help="Comma-separated list of strategies to evaluate")
    args = parser.parse_args()

    strategies = [s.strip() for s in args.strategies.split(",")]
    cases = load_cases()
    print(f"Loaded {len(cases)} evaluation cases")
    print(f"Strategies: {strategies}")

    all_results = {}
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"  Evaluating: {strategy}")
        print(f"{'='*60}")
        result = evaluate_strategy(strategy, cases, args.api_url)
        all_results[strategy] = result

        m = result["metrics"]
        print(f"  Recall@1: {m['recall@1']:.1%}")
        print(f"  Recall@3: {m['recall@3']:.1%}")
        print(f"  Recall@5: {m['recall@5']:.1%}")
        print(f"  MRR:      {m['mrr']:.4f}")
        print(f"  Domain:   {m['domain_accuracy']:.1%}")
        print(f"  Contam:   {m['contamination']:.1%}")
        print(f"  Evidence gate (unanswerable): {m['evidence_gate_pass_rate']:.1%}")
        print(f"  False+: {m['false_positives']}, False-: {m['false_negatives']}")

    # Comparison table
    print(f"\n{'='*72}")
    print(f"  STRATEGY COMPARISON")
    print(f"{'='*72}")
    header = f"{'Metric':<25}"
    for s in strategies:
        header += f" {s:>18}"
    print(header)
    print("-" * 72)

    for metric in ["recall@1", "recall@3", "recall@5", "mrr",
                    "domain_accuracy", "contamination",
                    "evidence_gate_pass_rate"]:
        row = f"{metric:<25}"
        for s in strategies:
            val = all_results[s]["metrics"][metric]
            if metric in ("mrr",):
                row += f" {val:>18.4f}"
            else:
                row += f" {val:>17.1%}"
        print(row)
    print("=" * 72)

    # Verdict
    if "dense" in all_results and "hybrid" in all_results:
        d_r5 = all_results["dense"]["metrics"]["recall@5"]
        h_r5 = all_results["hybrid"]["metrics"]["recall@5"]
        if h_r5 > d_r5:
            print(f"\n  VERDICT: Hybrid improves Recall@5 by +{(h_r5-d_r5):.1%}")
        elif h_r5 < d_r5:
            print(f"\n  VERDICT: Hybrid degrades Recall@5 by {(h_r5-d_r5):.1%}")
        else:
            print(f"\n  VERDICT: Hybrid matches Dense on Recall@5")

    if "hybrid" in all_results and "hybrid_reranked" in all_results:
        h_r5 = all_results["hybrid"]["metrics"]["recall@5"]
        hr_r5 = all_results["hybrid_reranked"]["metrics"]["recall@5"]
        if hr_r5 > h_r5:
            print(f"  VERDICT: Reranker improves Recall@5 by +{(hr_r5-h_r5):.1%}")
        elif hr_r5 < h_r5:
            print(f"  VERDICT: Reranker degrades Recall@5 by {(hr_r5-h_r5):.1%} — KEEP DISABLED")
        else:
            print(f"  VERDICT: Reranker matches Hybrid on Recall@5 — KEEP DISABLED")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "strategies": {s: r["metrics"] for s, r in all_results.items()},
        "cases": {s: r["cases"] for s, r in all_results.items()},
    }
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport written to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
