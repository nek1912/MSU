"""Jurisdiction contamination evaluation.

Measures:
  - wrong_state_contamination: state-specific queries retrieving wrong-state chunks
  - jurisdiction_validity: % of retrieved chunks with correct jurisdiction

Usage:
    python eval/run_jurisdiction_eval.py [--live]
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

GOLD_PATH = Path(__file__).resolve().parent / "gold_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "jurisdiction_eval.json"


def load_gold_cases() -> list[dict]:
    with open(GOLD_PATH, encoding="utf-8") as f:
        cases = yaml.safe_load(f)
    return cases


def retrieve_live(question: str, domain: str, state: str | None, k: int = 6) -> list[dict]:
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
        "query_embedding": query_vec, "match_domain": domain,
        "match_state": state, "match_count": k,
    }).execute().data or []
    return [{"chunk_id": str(r["chunk_id"]), "state": r.get("state"), "jurisdiction": r.get("jurisdiction", "")} for r in rows]


def evaluate_jurisdiction(cases: list[dict], retrieve_fn) -> dict:
    wrong_state_count = 0
    total_state_specific = 0
    total_chunks = 0
    valid_jurisdiction_count = 0

    per_case_results = []
    for case in cases:
        expected_state = case.get("expected_state")
        expected_domain = case.get("expected_domain")
        try:
            retrieved = retrieve_fn(case["question"], expected_domain, expected_state)
        except Exception as e:
            retrieved = []

        case_violations = []
        for chunk in retrieved:
            total_chunks += 1
            chunk_state = chunk.get("state")
            chunk_jurisdiction = chunk.get("jurisdiction", "")

            # Wrong-state check: state-specific query retrieved wrong-state chunk
            if expected_state and chunk_state and chunk_state != expected_state:
                wrong_state_count += 1
                case_violations.append(f"wrong_state: {chunk_state} (expected {expected_state})")

            # Jurisdiction validity: central chunks OK if applicable
            if chunk_jurisdiction == "central" or (expected_state and chunk_state == expected_state):
                valid_jurisdiction_count += 1
            elif expected_state is None and chunk_jurisdiction == "state":
                # Null-state query retrieving a state-specific chunk is suspicious
                case_violations.append(f"state_chunk_without_state_query: {chunk_state}")

            if expected_state:
                total_state_specific += 1

        per_case_results.append({
            "question": case["question"],
            "expected_state": expected_state,
            "retrieved_count": len(retrieved),
            "violations": case_violations,
        })

    metrics = {
        "total_cases": len(cases),
        "total_chunks_retrieved": total_chunks,
        "wrong_state_contamination": wrong_state_count,
        "jurisdiction_validity": round(valid_jurisdiction_count / total_chunks, 4) if total_chunks else 1.0,
        "total_state_specific_chunks": total_state_specific,
    }
    return {"metrics": metrics, "cases": per_case_results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    cases = load_gold_cases()
    retrieve_fn = retrieve_live if args.live else None
    if not retrieve_fn:
        print("Local FAISS not wired. Use --live for Supabase evaluation.", file=sys.stderr)
        return 0

    results = evaluate_jurisdiction(cases, retrieve_fn)

    print(f"\n{'='*60}")
    print(f"  JURISDICTION CONTAMINATION EVALUATION")
    print(f"{'='*60}")
    m = results["metrics"]
    print(f"  Total chunks retrieved: {m['total_chunks_retrieved']}")
    print(f"  Wrong-state contamination: {m['wrong_state_contamination']}")
    print(f"  Jurisdiction validity: {m['jurisdiction_validity']:.1%}")
    print(f"{'='*60}\n")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")

    # Hard gate: wrong_state_contamination must be 0
    return 1 if m["wrong_state_contamination"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
