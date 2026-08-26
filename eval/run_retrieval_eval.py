"""Retrieval evaluation — Recall@1, @3, @5, MRR.

Runs answerable gold cases through retrieval and measures whether
relevant chunks appear in top-k results.

Usage:
    python eval/run_retrieval_eval.py [--live]
    --live  Use Supabase match_chunks RPC instead of local FAISS
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

GOLD_PATH = Path(__file__).resolve().parent / "gold_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "retrieval_eval.json"


def load_gold_cases() -> list[dict]:
    """Load cases where answerable=true AND relevant_chunk_ids is non-empty."""
    with open(GOLD_PATH, encoding="utf-8") as f:
        cases = yaml.safe_load(f)
    return [
        c for c in cases
        if c.get("answerable", False)
        and c.get("relevant_source_ids")
        and c.get("relevant_chunk_ids")  # REQUIRED: Recall@5 is over chunks, not sources
    ]


def retrieve_local(question: str, domain: str, state: str | None, k: int = 6) -> list[dict]:
    """Retrieve using local FAISS index. Must be implemented before running."""
    raise NotImplementedError(
        "Local FAISS retrieval not wired. Use --live for Supabase, or implement local FAISS backend."
    )


def retrieve_live(question: str, domain: str, state: str | None, k: int = 6) -> list[dict]:
    """Retrieve using Supabase match_chunks RPC."""
    import os
    from supabase import create_client

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

    client = create_client(url, key)
    from app.providers.embeddings import get_embedding_provider
    provider = get_embedding_provider()
    query_vec = provider.embed_texts([question])[0]

    rows = client.rpc("match_chunks", {
        "query_embedding": query_vec,
        "match_domain": domain,
        "match_state": state,
        "match_count": k,
    }).execute().data or []
    return [{"chunk_id": str(r["chunk_id"]), "source_id": r.get("source_id", "")} for r in rows]


def compute_recall_metrics(results: list[dict], k_values: list[int] = [1, 3, 5]) -> dict:
    """Compute Recall@k and MRR.

    Denominator is the number of evaluated cases with non-empty relevant_chunk_ids
    (i.e., len(results) after filtering — not total gold cases, not total retrieved).
    """
    # All cases in results already have non-empty relevant_chunk_ids (filtered in load_gold_cases)
    total = len(results)
    if total == 0:
        return {"total": 0, "evaluated": 0, "recall_at": {f"r@{k}": 0.0 for k in k_values}, "mrr": 0.0}

    recall_counts = {k: 0 for k in k_values}
    reciprocal_ranks = []

    for r in results:
        retrieved_ids = [c["chunk_id"] for c in r["retrieved"]]
        relevant_ids = set(r["relevant_chunk_ids"])

        # Find first relevant chunk in retrieved list
        rr = 0.0
        for rank, cid in enumerate(retrieved_ids, 1):
            if cid in relevant_ids:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        # Recall@k: is at least one relevant chunk in top-k?
        for k in k_values:
            top_k = set(retrieved_ids[:k])
            if top_k & relevant_ids:
                recall_counts[k] += 1

    metrics = {
        "total": total,
        "evaluated": total,
        "recall_at": {f"r@{k}": round(recall_counts[k] / total, 4) for k in k_values},
        "mrr": round(sum(reciprocal_ranks) / total, 4) if total else 0.0,
    }
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Retrieval evaluation")
    parser.add_argument("--live", action="store_true", help="Use Supabase instead of local FAISS")
    args = parser.parse_args()

    cases = load_gold_cases()
    if not cases:
        print("No gold cases with non-empty relevant_chunk_ids. Populate chunk_ids after ingestion.", file=sys.stderr)
        return 1

    print(f"Loaded {len(cases)} answerable gold cases with relevant_chunk_ids")

    retrieve_fn = retrieve_live if args.live else retrieve_local

    results = []
    for case in cases:
        try:
            retrieved = retrieve_fn(
                question=case["question"],
                domain=case["expected_domain"],
                state=case.get("expected_state"),
            )
        except NotImplementedError as e:
            print(f"FATAL: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"ERROR retrieving for '{case['question']}': {e}", file=sys.stderr)
            retrieved = []

        results.append({
            "question": case["question"],
            "expected_domain": case["expected_domain"],
            "relevant_source_ids": case.get("relevant_source_ids", []),
            "relevant_chunk_ids": case.get("relevant_chunk_ids", []),
            "retrieved": retrieved,
        })

    metrics = compute_recall_metrics(results)

    print(f"\n{'='*60}")
    print(f"  RETRIEVAL EVALUATION")
    print(f"{'='*60}")
    print(f"  Evaluated cases: {metrics['evaluated']}")
    for k, v in metrics["recall_at"].items():
        print(f"  {k}: {v:.1%}")
    print(f"  MRR: {metrics['mrr']:.4f}")
    print(f"{'='*60}\n")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"metrics": metrics, "cases": results}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
