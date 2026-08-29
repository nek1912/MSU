"""Retrieval evaluation script — measures Recall@k, MRR, domain accuracy, jurisdiction contamination.

Usage:
    python -m eval.run_retrieval_eval                 # three-mode experiment + curated diagnostic
    python -m eval.run_retrieval_eval --mode dense    # single-mode regression (legacy)
    python -m eval.run_retrieval_eval --no-curated    # skip curated diagnostic
    python -m eval.run_retrieval_eval --config eval/gate2_config.yaml

Task 4: evaluates three retrieval strategies on the SAME corpus + SAME queries:
    dense            -> Supabase match_chunks RPC (production default path)
    hybrid           -> dense + lexical + RRF fusion (app.hybrid_retrieval.retrieve_hybrid)
    hybrid_reranker  -> hybrid, then Jina reranker applied on the fused top-k

Numeric Recall@k/MRR are computed on eval/gold_cases.yaml (the retriever-anchored
regression set, 40 answerable). eval/curated_eval.yaml (acceptable_chunk_ids EMPTY)
is used for DIAGNOSTIC reporting only — authoritative recall is NOT computed from it.
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


def _make_supabase():
    from dotenv import load_dotenv
    from supabase import create_client

    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


def retrieve_chunks(query: str, embed_fn, domain: str, state: str = None, k: int = 20,
                    mode: str = "dense", supabase=None, reranker=None) -> list[dict]:
    """Retrieve top-k chunks. `mode` selects the retrieval strategy generically:

    - dense:           Supabase match_chunks RPC (production default path)
    - hybrid:         dense + lexical + RRF fusion (app.hybrid_retrieval.retrieve_hybrid)
    - hybrid_reranker: hybrid, then Jina reranker applied on the fused top-k

    No query/document/chunk-specific branching. The internal DB uuid is returned as
    ``chunk_id`` so it matches gold relevant_chunk_ids; ``stable_chunk_id`` carries the
    re-ingestion-safe application id.
    """
    if supabase is None:
        supabase = _make_supabase()

    # Query embeddings always use retrieval.query (mirrors production chat route).
    query_embedding = embed_fn([query], task="retrieval.query")[0]

    if mode in ("hybrid", "hybrid_reranker"):
        from app.hybrid_retrieval import retrieve_hybrid
        chunks = retrieve_hybrid(supabase, query_embedding, query, domain, state, k=k)
        docs = [{
            "chunk_id": c.chunk_id,
            "stable_chunk_id": c.stable_chunk_id,
            "document_id": c.document_id,
            "source_file": c.source_file,
            "page": c.page,
            "page_start": c.page_start,
            "page_end": c.page_end,
            "content": c.content,
            "domain": c.domain,
            "jurisdiction": c.jurisdiction,
            "state": c.state,
            "similarity": c.similarity,
        } for c in chunks]
        if mode == "hybrid_reranker":
            if reranker is None:
                from app.providers.reranker import JinaReranker
                reranker = JinaReranker()
            reranked = reranker.rerank(
                query,
                [{"chunk_id": d["chunk_id"], "content": d["content"]} for d in docs],
                top_n=6,
            )
            id_map = {d["chunk_id"]: d for d in docs}
            docs = [id_map[r["chunk_id"]] for r in reranked if r["chunk_id"] in id_map]
        return docs

    # dense (default / production path)
    result = supabase.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_domain": domain if domain != "out_of_scope" else None,
            "match_state": state,
            "match_count": k,
        },
    ).execute()

    rows = result.data or []

    # Resolve provenance: document_id -> source_id, and chunk id -> source_file
    # (match_chunks does not return source_file; enrich so all modes report the
    # same provenance fields for a fair diagnostic comparison).
    doc_ids = list(set(r.get("document_id") for r in rows if r.get("document_id")))
    doc_map = {}
    if doc_ids:
        docs = supabase.table("documents").select("id, source_id").in_("id", doc_ids).execute()
        doc_map = {d["id"]: d.get("source_id", "?") for d in (docs.data or [])}

    chunk_ids = [r.get("chunk_id") for r in rows if r.get("chunk_id")]
    meta_map = {}
    if chunk_ids:
        meta_rows = (supabase.table("chunks")
                     .select("id, chunk_id, metadata")
                     .in_("id", chunk_ids).execute().data or [])
        meta_map = {str(mr["id"]): mr for mr in meta_rows}

    enriched = []
    for r in rows:
        doc_id = r.get("document_id")
        rec = {**r, "source_id": doc_map.get(doc_id, "?")}
        mr = meta_map.get(str(r.get("chunk_id")))
        if mr:
            rec["stable_chunk_id"] = mr.get("chunk_id")
            rec["source_file"] = (mr.get("metadata") or {}).get("source_file", "")
        enriched.append(rec)

    return enriched


def compute_recall_at_k(retrieved_chunk_ids: list[str], relevant_chunk_ids: list[str], k: int) -> bool:
    """Check if >=1 relevant chunk appears in top-k retrieved chunks."""
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


def _evaluate_cases(cases: list[dict], embed_fn, modes: list[str], supabase,
                    reranker, k: int = 20) -> dict:
    """Run all `modes` over the answerable `cases`; return per-mode metrics."""
    acc = {m: {"r1": 0, "r3": 0, "r5": 0, "r10": 0, "r20": 0, "mrr": 0.0,
               "dom_ok": 0, "contam": 0, "n": 0, "fails": [], "dom_mismatch": [],
               "contam_cases": []}
          for m in modes}

    for case in cases:
        if not case.get("answerable", False):
            continue
        query = case["question"]
        expected_domain = case.get("expected_domain", "unknown")
        expected_state = case.get("expected_state")
        relevant_chunk_ids = case.get("relevant_chunk_ids", [])
        if not relevant_chunk_ids:
            continue

        # Classify once per case so every mode sees identical domain + queries.
        predicted_domain, domain_score = classify_domain(query, embed_fn)

        for m in modes:
            a = acc[m]
            try:
                retrieved = retrieve_chunks(query, embed_fn, predicted_domain, expected_state,
                                            k=k, mode=m, supabase=supabase, reranker=reranker)
                retrieved_ids = [r.get("chunk_id", "") for r in retrieved]
                a["n"] += 1
                if predicted_domain == expected_domain:
                    a["dom_ok"] += 1
                else:
                    a["dom_mismatch"].append({
                        "query": query[:100], "expected": expected_domain,
                        "predicted": predicted_domain, "score": domain_score,
                    })
                if compute_recall_at_k(retrieved_ids, relevant_chunk_ids, 1):
                    a["r1"] += 1
                if compute_recall_at_k(retrieved_ids, relevant_chunk_ids, 3):
                    a["r3"] += 1
                if compute_recall_at_k(retrieved_ids, relevant_chunk_ids, 5):
                    a["r5"] += 1
                if compute_recall_at_k(retrieved_ids, relevant_chunk_ids, 10):
                    a["r10"] += 1
                if compute_recall_at_k(retrieved_ids, relevant_chunk_ids, 20):
                    a["r20"] += 1
                a["mrr"] += compute_mrr(retrieved_ids, relevant_chunk_ids)
                if check_jurisdiction_contamination(retrieved, expected_state,
                                                    case.get("jurisdiction", "central")):
                    a["contam"] += 1
                    a["contam_cases"].append(query[:100])
            except Exception as e:
                a["fails"].append({"query": query[:100], "error": str(e)})

    out = {}
    for m in modes:
        a = acc[m]
        n = a["n"] or 1
        out[m] = {
            "recall_at_1": a["r1"] / n,
            "recall_at_3": a["r3"] / n,
            "recall_at_5": a["r5"] / n,
            "recall_at_10": a["r10"] / n,
            "recall_at_20": a["r20"] / n,
            "mrr": a["mrr"] / n,
            "domain_accuracy": a["dom_ok"] / n,
            "jurisdiction_contamination": a["contam"],
            "n": a["n"],
            "fails": a["fails"],
            "dom_mismatch": a["dom_mismatch"],
            "contam_cases": a["contam_cases"],
        }
    return out


def run_evaluation(config: dict, mode: str = "dense") -> dict:
    """Legacy single-mode regression evaluation (dense by default)."""
    print("Loading gold cases...")
    cases = load_gold_cases()
    answerable = [c for c in cases if c.get("answerable", False)]
    print(f"Total cases: {len(cases)}, Answerable: {len(answerable)}")

    print("Loading embedding provider...")
    provider_info = get_embedding_provider()
    embed_fn = provider_info["embed_fn"]
    print(f"Provider: {provider_info['provider']} ({provider_info['model']}, {provider_info['dimension']}d)")

    supabase = _make_supabase()
    reranker = None
    metrics = _evaluate_cases(answerable, embed_fn, [mode], supabase, reranker, k=20)[mode]

    results = {
        "total_cases": len(cases),
        "answerable_cases": len(answerable),
        "mode": mode,
        "provider": provider_info["provider"],
        "model": provider_info["model"],
        "dimension": provider_info["dimension"],
        "recall_at_1": metrics["recall_at_1"],
        "recall_at_3": metrics["recall_at_3"],
        "recall_at_5": metrics["recall_at_5"],
        "recall_at_10": metrics["recall_at_10"],
        "recall_at_20": metrics["recall_at_20"],
        "mrr": metrics["mrr"],
        "domain_accuracy": metrics["domain_accuracy"],
        "jurisdiction_contamination": metrics["jurisdiction_contamination"],
        "failed_cases": metrics["fails"],
        "contaminated_cases": [{"query": q} for q in metrics["contam_cases"]],
        "domain_mismatches": metrics["dom_mismatch"],
    }

    # Thresholds (only meaningful for the production 'dense' baseline).
    retrieval_config = config.get("retrieval", {})
    jurisdiction_config = config.get("jurisdiction", {})
    domain_config = config.get("domain", {})
    thresholds_met = True
    verdicts = {}
    for metric_name, config_key in [("recall_at_1", "recall_at_1"), ("recall_at_3", "recall_at_3"),
                                    ("recall_at_5", "recall_at_5"), ("mrr", "mrr")]:
        mc = retrieval_config.get(config_key, {})
        minimum = mc.get("minimum", 0)
        is_blocker = mc.get("blocker", True)
        actual = results[metric_name]
        if actual < minimum:
            verdicts[metric_name] = "FAIL" if is_blocker else "WARN"
            if is_blocker:
                thresholds_met = False
        else:
            verdicts[metric_name] = "PASS"
    cmax = jurisdiction_config.get("contamination", {}).get("maximum", 0)
    cblock = jurisdiction_config.get("contamination", {}).get("blocker", True)
    if results["jurisdiction_contamination"] > cmax:
        verdicts["jurisdiction_contamination"] = "FAIL"
        if cblock:
            thresholds_met = False
    else:
        verdicts["jurisdiction_contamination"] = "PASS"
    dmin = domain_config.get("accuracy", {}).get("minimum", 0.85)
    verdicts["domain_accuracy"] = "PASS" if results["domain_accuracy"] >= dmin else "WARN"
    results["verdicts"] = verdicts
    results["thresholds_met"] = thresholds_met
    results["overall_verdict"] = "PASS" if thresholds_met else "FAIL"
    return results


def run_experiment(modes: list[str] = None, k: int = 20) -> dict:
    """Run the three-mode retrieval experiment over the gold regression set."""
    if modes is None:
        modes = ["dense", "hybrid", "hybrid_reranker"]

    print("=" * 70)
    print("TASK 4 RETRIEVAL STRATEGY EXPERIMENT")
    print("=" * 70)
    print(f"Modes: {modes}")
    print("Corpus: 5 docs / 2,188 chunks / 768d Jina v3 (frozen).")
    print("Numeric Recall computed on eval/gold_cases.yaml (retriever-anchored, 40 answerable).")

    cases = load_gold_cases()
    answerable = [c for c in cases if c.get("answerable", False)]
    print(f"Gold cases: {len(cases)}, Answerable: {len(answerable)}")

    provider_info = get_embedding_provider()
    embed_fn = provider_info["embed_fn"]
    print(f"Provider: {provider_info['provider']} ({provider_info['model']}, {provider_info['dimension']}d)")

    supabase = _make_supabase()
    from app.providers.reranker import JinaReranker
    reranker = JinaReranker() if "hybrid_reranker" in modes else None

    t0 = time.time()
    metrics = _evaluate_cases(answerable, embed_fn, modes, supabase, reranker, k=k)
    elapsed = time.time() - t0

    # Print comparison table
    print("\n" + "-" * 70)
    print(f"{'Metric':<22}{'Dense':>12}{'Hybrid':>12}{'Hybrid+Reranker':>16}")
    print("-" * 70)
    for label, key in [("Recall@1", "recall_at_1"), ("Recall@3", "recall_at_3"),
                       ("Recall@5", "recall_at_5"), ("Recall@10", "recall_at_10"),
                       ("Recall@20", "recall_at_20"), ("MRR", "mrr"),
                       ("Domain accuracy", "domain_accuracy")]:
        row = ""
        for m in modes:
            v = metrics[m][key]
            row += f"{v:>12.3f}" if isinstance(v, float) else f"{v:>12}"
        print(f"{label:<22}{row}")
    print("-" * 70)
    print(f"{'Contamination':<22}" + "".join(f"{metrics[m]['jurisdiction_contamination']:>12}" for m in modes))
    print(f"{'Failed cases':<22}" + "".join(f"{len(metrics[m]['fails']):>12}" for m in modes))
    print(f"{'n (answerable)':<22}" + "".join(f"{metrics[m]['n']:>12}" for m in modes))
    print(f"Duration: {elapsed:.1f}s")

    # Domain mismatches (diagnostic, shared across modes)
    for m in modes:
        if metrics[m]["dom_mismatch"]:
            print(f"\nDomain mismatches [{m}] ({len(metrics[m]['dom_mismatch'])}):")
            for dm in metrics[m]["dom_mismatch"][:8]:
                print(f"  - exp={dm['expected']} pred={dm['predicted']} :: {dm['query']}")

    return {"modes": modes, "metrics": metrics, "duration_seconds": elapsed,
            "n_answerable": len(answerable)}


def run_curated_diagnostic(modes: list[str] = None, k: int = 20):
    """Diagnostic on eval/curated_eval.yaml (acceptable_chunk_ids EMPTY).

    Does NOT compute authoritative recall. Reports:
      - answerable: whether expected_document surfaces in retrieved top-20 (doc-presence)
      - unanswerable: whether retrieval would produce actionable in-domain evidence and
        whether the evidence gate would reject (out_of_scope, or empty retrieval).
    """
    if modes is None:
        modes = ["dense", "hybrid", "hybrid_reranker"]

    print("\n" + "=" * 70)
    print("CURATED SET DIAGNOSTIC (eval/curated_eval.yaml)")
    print("=" * 70)
    print("acceptable_chunk_ids are EMPTY -> diagnostic only; authoritative recall")
    print("CANNOT be calculated. No gold labels manufactured.")

    cases = yaml.safe_load(open(PROJECT_ROOT / "eval" / "curated_eval.yaml", encoding="utf-8"))
    embed_fn = get_embedding_provider()["embed_fn"]
    supabase = _make_supabase()
    from app.providers.reranker import JinaReranker
    reranker = JinaReranker() if "hybrid_reranker" in modes else None

    for m in modes:
        print(f"\n--- mode={m} ---")
        answerable = [c for c in cases if c.get("answerable", False)]
        unanswerable = [c for c in cases if not c.get("answerable", False)]
        print(f"ANSWERABLE (expected_document presence in top-20): {len(answerable)}")
        for c in answerable:
            q = c["query"]
            exp_doc = (c.get("expected_document") or "").lower()
            dom, _ = classify_domain(q, embed_fn)
            retrieved = retrieve_chunks(q, embed_fn, dom, None, k=k, mode=m,
                                        supabase=supabase, reranker=reranker)
            docs = [ (r.get("source_file") or "") for r in retrieved ]
            matched = any(exp_doc and exp_doc in (r.get("source_file") or "").lower() for r in retrieved[:20])
            print(f"  [{'HIT ' if matched else 'MISS'}] dom={dom:<16} exp={c.get('expected_document')}")
        print(f"UNANSWERABLE (gate diagnostic): {len(unanswerable)}")
        for c in unanswerable:
            q = c["query"]
            dom, _ = classify_domain(q, embed_fn)
            if dom == "out_of_scope":
                actionable = False
                gate_reject = True
            else:
                retrieved = retrieve_chunks(q, embed_fn, dom, None, k=k, mode=m,
                                            supabase=supabase, reranker=reranker)
                actionable = len(retrieved) > 0
                gate_reject = (len(retrieved) == 0)
            print(f"  dom={dom:<14} actionable_evidence={actionable} gate_reject={gate_reject} :: {q[:55]}")


def print_report(results: dict):
    """Print human-readable report (legacy single-mode)."""
    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION COMPLETE")
    print("=" * 60)
    print(f"  Mode: {results.get('mode', 'dense')}")
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
    print(f"  Verdict: {results['overall_verdict']}")
    print()

    if results["failed_cases"]:
        print(f"  Failed cases: {len(results['failed_cases'])}")
    if results["contaminated_cases"]:
        print(f"  Contaminated cases: {len(results['contaminated_cases'])}")
    if results["domain_mismatches"]:
        print(f"  Domain mismatches: {len(results['domain_mismatches'])} (diagnostic)")
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run retrieval evaluation")
    parser.add_argument("--config", type=Path, default=None, help="Path to gate2_config.yaml")
    parser.add_argument("--output", type=Path, default=None, help="Path to save JSON report")
    parser.add_argument("--mode", type=str, default=None,
                        choices=["dense", "hybrid", "hybrid_reranker"],
                        help="Single-mode regression (legacy). Omit to run all three modes.")
    parser.add_argument("--no-curated", action="store_true", help="Skip curated diagnostic")
    args = parser.parse_args()

    if args.mode:
        # Legacy single-mode regression path
        config = load_config(args.config)
        results = run_evaluation(config, mode=args.mode)
        print_report(results)
        output_path = args.output or (PROJECT_ROOT / "eval" / f"retrieval_report_{args.mode}.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nReport saved to: {output_path}")
        sys.exit(0 if results["overall_verdict"] == "PASS" else 1)

    # Default: three-mode experiment + curated diagnostic
    experiment = run_experiment(["dense", "hybrid", "hybrid_reranker"])
    if not args.no_curated:
        run_curated_diagnostic(["dense", "hybrid", "hybrid_reranker"])

    output_path = args.output or (PROJECT_ROOT / "eval" / "task4_experiment.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(experiment, f, indent=2, ensure_ascii=False)
    print(f"\nExperiment report saved to: {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
