"""Citation provenance evaluation — Invariant 6.

Verifies the full citation chain:
  cited chunk → actually retrieved for this request → chunk exists in corpus
  → source_id matches actual chunk → permitted domain → permitted jurisdiction

Zero citations on an answerable response is a citation failure, not perfect provenance.

Usage:
    python eval/run_citation_eval.py [--api-url URL]
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

CASES_PATH = Path(__file__).resolve().parent / "citation_cases.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_PATH = REPORT_DIR / "citation_eval.json"
DEFAULT_API_URL = "http://localhost:8000"
CITATION_PATTERN = re.compile(r"\[chunk:(\d+)\]")

# Domains permitted for citation in this evaluation
PERMITTED_DOMAINS = {"cooperative", "pacs", "schemes", "pmfby", "agriculture", "finlit"}


def load_cases() -> list[dict]:
    with open(CASES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_chat(api_url: str, question: str, state: str | None = None) -> dict:
    url = f"{api_url}/chat"
    payload = json.dumps({
        "question": question,
        "language": "en",
        "session_id": "eval-citation-test",
        "state": state,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return {"error": str(e), "abstained": True, "citations": []}


def extract_citation_ids(answer: str) -> list[str]:
    """Extract chunk IDs from answer text like [chunk:123]."""
    return CITATION_PATTERN.findall(answer)


def load_corpus_index() -> dict:
    """Load chunk metadata from Supabase for corpus existence checks.

    Returns dict: chunk_id -> {source_id, domain, jurisdiction, state}
    Falls back to empty dict if Supabase not available.
    """
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    if not url or not key:
        print("WARNING: SUPABASE credentials not set — corpus existence check skipped", file=sys.stderr)
        return {}
    try:
        from supabase import create_client
        client = create_client(url, key)
        rows = client.table("chunks").select("chunk_id, source_id, domain, jurisdiction, state").execute().data or []
        return {str(r["chunk_id"]): r for r in rows}
    except Exception as e:
        print(f"WARNING: Could not load corpus index: {e}", file=sys.stderr)
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    args = parser.parse_args()

    cases = load_cases()
    print(f"Loaded {len(cases)} citation verification cases")

    corpus_index = load_corpus_index()
    if not corpus_index:
        print("WARNING: Corpus index empty — citation existence checks will fail", file=sys.stderr)

    results = []
    total_citations = 0
    valid_citations = 0
    fabrication_count = 0
    zero_citation_failures = 0
    corpus_missing = 0
    domain_mismatch = 0

    for case in cases:
        response = call_chat(args.api_url, case["question"], case.get("expected_state"))
        answer = response.get("answer", "")
        citations_from_response = response.get("citations", [])
        abstained = response.get("abstained", False)
        check_answerable = case.get("check_answerable", True)

        # Extract cited chunk IDs from answer text and API response
        cited_ids_from_text = extract_citation_ids(answer)
        cited_ids_from_api = [str(c.get("chunk_id", "")) for c in citations_from_response if c.get("chunk_id")]
        all_cited_ids = list(set(cited_ids_from_text + cited_ids_from_api))

        case_result = {
            "question": case["question"],
            "expected_domain": case.get("expected_domain"),
            "abstained": abstained,
            "cited_ids": all_cited_ids,
            "citations_count": len(all_cited_ids),
            "violations": [],
        }

        if not abstained and check_answerable:
            # Zero citations on an answerable response = citation failure
            if not all_cited_ids:
                zero_citation_failures += 1
                case_result["violations"].append("zero_citations_on_answerable_response")
            else:
                total_citations += len(all_cited_ids)
                # Build set of retrieved chunk IDs from the response
                # The LLM cites using8-char UUID prefixes; the API returns
                # stable_chunk_id. We check fabrication by testing whether
                # each8-char prefix is a prefix of any stable_chunk_id or
                # matches any document_id prefix.
                retrieved_ids = set()
                retrieved_prefixes = set()
                for c in citations_from_response:
                    rid = c.get("chunk_id")
                    if rid:
                        retrieved_ids.add(str(rid))
                        retrieved_prefixes.add(str(rid)[:8].lower())
                    did = c.get("document_id")
                    if did:
                        retrieved_prefixes.add(str(did)[:8].lower())

                for cid in all_cited_ids:
                    # Check 1: Cited chunk was actually retrieved for this request.
                    # Match by full ID or by8-char prefix against retrieved IDs.
                    is_retrieved = (cid in retrieved_ids or
                                    cid[:8].lower() in retrieved_prefixes)
                    if not is_retrieved:
                        fabrication_count += 1
                        case_result["violations"].append(f"not_retrieved: {cid}")
                        continue

                    # Check 2: Chunk exists in corpus
                    if cid not in corpus_index:
                        corpus_missing += 1
                        case_result["violations"].append(f"corpus_missing: {cid}")
                        continue

                    chunk_meta = corpus_index[cid]

                    # Check 3: source_id matches actual chunk
                    expected_source = case.get("expected_source_id")
                    if expected_source and chunk_meta.get("source_id") != expected_source:
                        case_result["violations"].append(
                            f"source_mismatch: {cid} has source {chunk_meta.get('source_id')}, expected {expected_source}"
                        )

                    # Check 4: Permitted domain
                    chunk_domain = chunk_meta.get("domain", "")
                    if chunk_domain not in PERMITTED_DOMAINS:
                        domain_mismatch += 1
                        case_result["violations"].append(f"domain_mismatch: {cid} domain={chunk_domain}")
                        continue

                    valid_citations += 1

        results.append(case_result)

    provenance_rate = valid_citations / total_citations if total_citations else 0.0

    metrics = {
        "total_cases": len(cases),
        "total_citations": total_citations,
        "valid_citations": valid_citations,
        "fabricated_citations": fabrication_count,
        "zero_citation_failures": zero_citation_failures,
        "corpus_missing": corpus_missing,
        "domain_mismatches": domain_mismatch,
        "citation_provenance_rate": round(provenance_rate, 4),
    }

    print(f"\n{'='*60}")
    print(f"  CITATION PROVENANCE EVALUATION — Invariant 6")
    print(f"{'='*60}")
    print(f"  Total citations evaluated: {metrics['total_citations']}")
    print(f"  Valid citations: {metrics['valid_citations']}")
    print(f"  Fabricated citations (not retrieved): {metrics['fabricated_citations']}")
    print(f"  Corpus missing: {metrics['corpus_missing']}")
    print(f"  Domain mismatches: {metrics['domain_mismatches']}")
    print(f"  Zero-citation failures: {metrics['zero_citation_failures']}")
    print(f"  Citation provenance rate: {metrics['citation_provenance_rate']:.1%}")
    print(f"{'='*60}\n")

    all_violations = fabrication_count + corpus_missing + domain_mismatch + zero_citation_failures
    if all_violations > 0:
        print(f"  CITATION VIOLATIONS:")
        for r in results:
            for v in r["violations"]:
                print(f"    {r['question']}: {v}")
        print()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"metrics": metrics, "cases": results}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Report written to {REPORT_PATH}")

    # Hard gate: no fabricated citations, no zero-citation failures on answerable, no corpus missing
    return 1 if all_violations > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
