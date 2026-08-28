"""Retrieval evaluation script — measures Recall@k, MRR, domain accuracy, jurisdiction contamination.

Usage:
    python -m eval.run_retrieval_eval [--config eval/gate2_config.yaml]

Reads thresholds from eval/gate2_config.yaml (single source of truth).
Auto-detects embedding provider from backend code.
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_config(config_path: Path = None) -> dict:
    """Load gate2 config thresholds."""
    if config_path is None:
        config_path = PROJECT_ROOT / "eval" / "gate2_config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_gold_cases(cases_path: Path = None) -> list[dict]:
    """Load gold evaluation cases."""
    if cases_path is None:
        cases_path = PROJECT_ROOT / "eval" / "gold_cases.yaml"
    with open(cases_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_embedding_provider():
    """Auto-detect embedding provider from backend code."""
    from dotenv import load_dotenv
    
    # Load from backend/.env
    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)
    
    from app.providers.embeddings import get_embedding_provider as _get_provider
    
    # get_embedding_provider() is a singleton with @lru_cache, takes no args
    provider = _get_provider()
    
    return {
        "provider": provider.__class__.__name__,
        "model": getattr(provider, 'model', 'unknown'),
        "dimension": getattr(provider, 'dimension', 768),
        "embed_fn": provider.embed_texts,
    }


def classify_domain(query: str, embed_fn) -> tuple[str, float]:
    """Classify query domain using keyword rules + cosine anchors."""
    from app.domains import get_anchor_store
    
    # Get the anchor store (singleton, cached)
    anchor_store = get_anchor_store()
    
    # Get query embedding for domain classification (mirror chat.py: uses
    # retrieval.query for queries, matching production retrieval).
    query_embedding = embed_fn([query], task="retrieval.query")[0]
    
    domain, score = anchor_store.classify(query, query_embedding)
    return domain, score


def retrieve_chunks(query: str, embed_fn, domain: str, state: str = None, k: int = 20) -> list[dict]:
    """Retrieve top-k chunks via Supabase match_chunks RPC with full provenance."""
    from dotenv import load_dotenv
    from supabase import create_client
    
    # Load from backend/.env
    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)
    
    import os
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    supabase = create_client(url, key)
    
    # Get query embedding (mirror chat.py: retrieval.query for queries)
    query_embedding = embed_fn([query], task="retrieval.query")[0]
    
    # Call match_chunks RPC
    result = supabase.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_domain": domain if domain != "out_of_scope" else None,
            "match_state": state,
            "match_count": k,
        }
    ).execute()
    
    rows = result.data or []
    
    # Resolve provenance: document_id → source_id
    # (RPC returns domain directly, but source_id requires document lookup)
    doc_ids = list(set(r.get("document_id") for r in rows if r.get("document_id")))
    doc_map = {}
    if doc_ids:
        docs = supabase.table("documents").select("id, source_id").in_("id", doc_ids).execute()
        doc_map = {d["id"]: d.get("source_id", "?") for d in (docs.data or [])}
    
    # Enrich results with source_id
    enriched = []
    for r in rows:
        doc_id = r.get("document_id")
        enriched.append({
            **r,
            "source_id": doc_map.get(doc_id, "?"),
        })

    # Optional second-stage reranker (mirrors /chat when RERANKER_ENABLED).
    # If enabled, the eval reports recall on the FINAL reranked top-n, i.e. the
    # set the evidence gate and LLM actually see.
    if os.environ.get("RERANKER_ENABLED", "false").lower() == "true":
        from app.providers.reranker import JinaReranker
        rr = JinaReranker()
        reranked = rr.rerank(query, [{"chunk_id": r["chunk_id"], "content": r.get("content", "")} for r in enriched], top_n=6)
        id_to_row = {r["chunk_id"]: r for r in enriched}
        enriched = [id_to_row[r["chunk_id"]] for r in reranked if r["chunk_id"] in id_to_row]

    return enriched


def compute_recall_at_k(retrieved_chunk_ids: list[str], relevant_chunk_ids: list[str], k: int) -> bool:
    """Check if ≥1 relevant chunk appears in top-k retrieved chunks."""
    top_k = set(retrieved_chunk_ids[:k])
    return bool(top_k.intersection(set(relevant_chunk_ids)))


def compute_mrr(retrieved_chunk_ids: list[str], relevant_chunk_ids: list[str]) -> float:
    """Compute reciprocal rank of first relevant chunk."""
    relevant_set = set(relevant_chunk_ids)
    for i, chunk_id in enumerate(retrieved_chunk_ids):
        if chunk_id in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def check_jurisdiction_contamination(retrieved: list[dict], expected_state: str, expected_jurisdiction: str) -> bool:
    """Check if any retrieved chunk has wrong state jurisdiction."""
    for chunk in retrieved:
        chunk_state = chunk.get("state")
        chunk_jurisdiction = chunk.get("jurisdiction", "central")
        
        # Central sources are always allowed
        if chunk_jurisdiction == "central":
            continue
        
        # State sources must match expected state
        if expected_state and chunk_state != expected_state:
            return True  # Contamination found
    
    return False


def run_evaluation(config: dict) -> dict:
    """Run full retrieval evaluation."""
    print("Loading gold cases...")
    cases = load_gold_cases()
    answerable_cases = [c for c in cases if c.get("answerable", False)]
    
    print(f"Total cases: {len(cases)}, Answerable: {len(answerable_cases)}")
    
    print("Loading embedding provider...")
    provider_info = get_embedding_provider()
    embed_fn = provider_info["embed_fn"]
    print(f"Provider: {provider_info['provider']} ({provider_info['model']}, {provider_info['dimension']}d)")
    
    # Load thresholds from config
    retrieval_config = config.get("retrieval", {})
    jurisdiction_config = config.get("jurisdiction", {})
    domain_config = config.get("domain", {})
    
    # Initialize metrics
    results = {
        "total_cases": len(cases),
        "answerable_cases": len(answerable_cases),
        "provider": provider_info["provider"],
        "model": provider_info["model"],
        "dimension": provider_info["dimension"],
        "recall_at_1": 0,
        "recall_at_3": 0,
        "recall_at_5": 0,
        "recall_at_10": 0,
        "recall_at_20": 0,
        "mrr": 0.0,
        "domain_accuracy": 0.0,
        "jurisdiction_contamination": 0,
        "failed_cases": [],
        "contaminated_cases": [],
        "domain_mismatches": [],
    }
    
    recall_1_hits = 0
    recall_3_hits = 0
    recall_5_hits = 0
    recall_10_hits = 0
    recall_20_hits = 0
    mrr_sum = 0.0
    domain_correct = 0
    
    print("\nRunning evaluation...")
    start_time = time.time()
    
    for i, case in enumerate(answerable_cases):
        query = case["question"]
        expected_domain = case.get("expected_domain", "unknown")
        expected_state = case.get("expected_state")
        expected_jurisdiction = case.get("jurisdiction", "central")
        relevant_chunk_ids = case.get("relevant_chunk_ids", [])
        relevant_source_ids = case.get("relevant_source_ids", [])
        
        if not relevant_chunk_ids:
            print(f"  [{i+1}/{len(answerable_cases)}] SKIP (no relevant_chunk_ids): {query[:50]}...")
            continue
        
        try:
            # Classify domain
            predicted_domain, domain_score = classify_domain(query, embed_fn)
            
            # Check domain accuracy
            if predicted_domain == expected_domain:
                domain_correct += 1
            else:
                results["domain_mismatches"].append({
                    "case_id": case.get("id", i),
                    "query": query[:100],
                    "expected": expected_domain,
                    "predicted": predicted_domain,
                    "score": domain_score,
                })
            
            # Retrieve chunks
            retrieved = retrieve_chunks(query, embed_fn, predicted_domain, expected_state)
            retrieved_chunk_ids = [r.get("chunk_id", "") for r in retrieved]
            retrieved_source_ids = list(set(r.get("source_id", "") for r in retrieved))
            
            # Compute Recall@k
            if compute_recall_at_k(retrieved_chunk_ids, relevant_chunk_ids, 1):
                recall_1_hits += 1
            if compute_recall_at_k(retrieved_chunk_ids, relevant_chunk_ids, 3):
                recall_3_hits += 1
            if compute_recall_at_k(retrieved_chunk_ids, relevant_chunk_ids, 5):
                recall_5_hits += 1
            if compute_recall_at_k(retrieved_chunk_ids, relevant_chunk_ids, 10):
                recall_10_hits += 1
            if compute_recall_at_k(retrieved_chunk_ids, relevant_chunk_ids, 20):
                recall_20_hits += 1
            
            # Compute MRR
            mrr_sum += compute_mrr(retrieved_chunk_ids, relevant_chunk_ids)
            
            # Check jurisdiction contamination
            if check_jurisdiction_contamination(retrieved, expected_state, expected_jurisdiction):
                results["jurisdiction_contamination"] += 1
                results["contaminated_cases"].append({
                    "case_id": case.get("id", i),
                    "query": query[:100],
                    "expected_state": expected_state,
                    "retrieved_states": list(set(r.get("state") for r in retrieved if r.get("state"))),
                })
            
            print(f"  [{i+1}/{len(answerable_cases)}] OK: domain={predicted_domain}, retrieved={len(retrieved)}, relevant_chunks={len(relevant_chunk_ids)}")
            
        except Exception as e:
            print(f"  [{i+1}/{len(answerable_cases)}] ERROR: {e}")
            results["failed_cases"].append({
                "case_id": case.get("id", i),
                "query": query[:100],
                "error": str(e),
            })
    
    elapsed = time.time() - start_time
    
    # Compute final metrics
    n = len(answerable_cases)
    results["recall_at_1"] = recall_1_hits / n if n > 0 else 0
    results["recall_at_3"] = recall_3_hits / n if n > 0 else 0
    results["recall_at_5"] = recall_5_hits / n if n > 0 else 0
    results["recall_at_10"] = recall_10_hits / n if n > 0 else 0
    results["recall_at_20"] = recall_20_hits / n if n > 0 else 0
    results["mrr"] = mrr_sum / n if n > 0 else 0
    results["domain_accuracy"] = domain_correct / n if n > 0 else 0
    results["duration_seconds"] = round(elapsed, 2)
    
    # Check thresholds
    thresholds_met = True
    verdicts = {}
    
    for metric_name, config_key in [
        ("recall_at_1", "recall_at_1"),
        ("recall_at_3", "recall_at_3"),
        ("recall_at_5", "recall_at_5"),
        ("mrr", "mrr"),
    ]:
        metric_config = retrieval_config.get(config_key, {})
        minimum = metric_config.get("minimum", 0)
        is_blocker = metric_config.get("blocker", True)
        actual = results[metric_name]
        
        if actual < minimum:
            verdicts[metric_name] = "FAIL" if is_blocker else "WARN"
            if is_blocker:
                thresholds_met = False
        else:
            verdicts[metric_name] = "PASS"
    
    # Jurisdiction contamination
    contamination_max = jurisdiction_config.get("contamination", {}).get("maximum", 0)
    contamination_blocker = jurisdiction_config.get("contamination", {}).get("blocker", True)
    if results["jurisdiction_contamination"] > contamination_max:
        verdicts["jurisdiction_contamination"] = "FAIL"
        if contamination_blocker:
            thresholds_met = False
    else:
        verdicts["jurisdiction_contamination"] = "PASS"
    
    # Domain accuracy (diagnostic)
    domain_min = domain_config.get("accuracy", {}).get("minimum", 0.85)
    if results["domain_accuracy"] < domain_min:
        verdicts["domain_accuracy"] = "WARN"
    else:
        verdicts["domain_accuracy"] = "PASS"
    
    results["verdicts"] = verdicts
    results["thresholds_met"] = thresholds_met
    results["overall_verdict"] = "PASS" if thresholds_met else "FAIL"
    
    return results


def print_report(results: dict):
    """Print human-readable report."""
    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION COMPLETE")
    print("=" * 60)
    print(f"  Gold cases: {results['total_cases']}")
    print(f"  Answerable: {results['answerable_cases']}")
    print(f"  Provider: {results['provider']} ({results['model']}, {results['dimension']}d)")
    print()
    print(f"  Recall@1:  {results['recall_at_1']:.3f}")
    print(f"  Recall@3:  {results['recall_at_3']:.3f}")
    print(f"  Recall@5:  {results['recall_at_5']:.3f}")
    print(f"  Recall@10: {results['recall_at_10']:.3f}")
    print(f"  Recall@20: {results['recall_at_20']:.3f}  (reranker candidate-pool ceiling)")
    print(f"  MRR: {results['mrr']:.3f}")
    print()
    print(f"  Domain accuracy: {results['domain_accuracy']:.3f} (diagnostic)")
    print(f"  Jurisdiction contamination: {results['jurisdiction_contamination']}")
    print()
    print(f"  Duration: {results['duration_seconds']}s")
    print(f"  Verdict: {results['overall_verdict']}")
    print()
    
    if results["failed_cases"]:
        print(f"  Failed cases: {len(results['failed_cases'])}")
        for fc in results["failed_cases"][:5]:
            print(f"    - {fc['case_id']}: {fc['error'][:50]}")
    
    if results["contaminated_cases"]:
        print(f"  Contaminated cases: {len(results['contaminated_cases'])}")
        for cc in results["contaminated_cases"][:5]:
            print(f"    - {cc['case_id']}: expected={cc['expected_state']}, got={cc['retrieved_states']}")
    
    if results["domain_mismatches"]:
        print(f"  Domain mismatches: {len(results['domain_mismatches'])} (diagnostic)")
        for dm in results["domain_mismatches"][:5]:
            print(f"    - {dm['case_id']}: expected={dm['expected']}, predicted={dm['predicted']}")
    
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run retrieval evaluation")
    parser.add_argument("--config", type=Path, default=None, help="Path to gate2_config.yaml")
    parser.add_argument("--output", type=Path, default=None, help="Path to save JSON report")
    args = parser.parse_args()
    
    config = load_config(args.config)
    results = run_evaluation(config)
    
    print_report(results)
    
    # Save JSON report
    output_path = args.output or (PROJECT_ROOT / "eval" / "retrieval_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {output_path}")
    
    # Exit with appropriate code
    if results["overall_verdict"] == "FAIL":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
