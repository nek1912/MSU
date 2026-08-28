"""Gold-set chunk audit — verifies relevant_chunk_ids exist and are valid.

Usage:
    python -m eval.gold_chunk_audit

Produces:
    eval/reports/gold_chunk_audit.md
"""
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_supabase_client():
    """Get Supabase client from environment."""
    from dotenv import load_dotenv
    from supabase import create_client
    
    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


def load_gold_cases() -> list[dict]:
    """Load gold evaluation cases."""
    cases_path = PROJECT_ROOT / "eval" / "gold_cases.yaml"
    with open(cases_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_all_chunks(supabase) -> dict:
    """Get all chunks indexed by ID."""
    chunks = supabase.table("chunks").select("id, document_id, content, page, section").execute().data
    return {c["id"]: c for c in chunks}


def get_all_documents(supabase) -> dict:
    """Get all documents indexed by ID."""
    docs = supabase.table("documents").select("id, source_id, title, domain").execute().data
    return {d["id"]: d for d in docs}


def audit_gold_cases(cases: list[dict], chunks: dict, documents: dict) -> dict:
    """Audit all answerable gold cases."""
    results = {
        "total_cases": len(cases),
        "answerable_cases": 0,
        "total_relevant_chunk_ids": 0,
        "existing_chunk_ids": 0,
        "missing_chunk_ids": 0,
        "source_mismatches": 0,
        "duplicate_ids": 0,
        "cases_with_zero_valid_chunks": 0,
        "cases_with_semantic_mismatch": 0,
        "details": [],
    }
    
    seen_chunk_ids = set()
    
    for case in cases:
        if not case.get("answerable", False):
            continue
        
        results["answerable_cases"] += 1
        question = case.get("question", "?")
        expected_source_ids = set(case.get("relevant_source_ids", []))
        relevant_chunk_ids = case.get("relevant_chunk_ids", [])
        
        case_detail = {
            "question": question[:80],
            "expected_source_ids": list(expected_source_ids),
            "relevant_chunk_ids": relevant_chunk_ids,
            "valid_chunk_ids": [],
            "missing_chunk_ids": [],
            "source_mismatches": [],
            "semantic_issues": [],
        }
        
        results["total_relevant_chunk_ids"] += len(relevant_chunk_ids)
        
        for chunk_id in relevant_chunk_ids:
            # Check if chunk exists
            if chunk_id not in chunks:
                case_detail["missing_chunk_ids"].append(chunk_id)
                results["missing_chunk_ids"] += 1
                continue
            
            results["existing_chunk_ids"] += 1
            
            # Check for duplicates
            if chunk_id in seen_chunk_ids:
                results["duplicate_ids"] += 1
            seen_chunk_ids.add(chunk_id)
            
            # Resolve chunk → document → source_id
            chunk = chunks[chunk_id]
            doc_id = chunk.get("document_id")
            
            if doc_id not in documents:
                case_detail["source_mismatches"].append({
                    "chunk_id": chunk_id,
                    "issue": "document not found"
                })
                results["source_mismatches"] += 1
                continue
            
            doc = documents[doc_id]
            actual_source_id = doc.get("source_id")
            
            # Check source_id match
            if actual_source_id not in expected_source_ids:
                case_detail["source_mismatches"].append({
                    "chunk_id": chunk_id,
                    "expected_sources": list(expected_source_ids),
                    "actual_source": actual_source_id
                })
                results["source_mismatches"] += 1
                continue
            
            case_detail["valid_chunk_ids"].append(chunk_id)
        
        # Check if case has zero valid chunks
        if not case_detail["valid_chunk_ids"]:
            results["cases_with_zero_valid_chunks"] += 1
        
        results["details"].append(case_detail)
    
    return results


def generate_report(results: dict) -> str:
    """Generate markdown report."""
    lines = []
    lines.append("# Gold-Set Chunk Audit Report")
    lines.append("")
    lines.append(f"**Date:** 2026-08-28")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total gold cases | {results['total_cases']} |")
    lines.append(f"| Answerable cases | {results['answerable_cases']} |")
    lines.append(f"| Total relevant chunk IDs | {results['total_relevant_chunk_ids']} |")
    lines.append(f"| Existing chunk IDs | {results['existing_chunk_ids']} |")
    lines.append(f"| Missing chunk IDs | {results['missing_chunk_ids']} |")
    lines.append(f"| Source mismatches | {results['source_mismatches']} |")
    lines.append(f"| Duplicate IDs | {results['duplicate_ids']} |")
    lines.append(f"| Cases with zero valid chunks | {results['cases_with_zero_valid_chunks']} |")
    lines.append("")
    
    # Verdict
    if results["missing_chunk_ids"] > 0:
        lines.append("**Verdict: STALE GOLD SET** — chunk IDs do not match current corpus")
    elif results["source_mismatches"] > 0:
        lines.append("**Verdict: SOURCE MISMATCHES** — chunks reference wrong documents")
    elif results["cases_with_zero_valid_chunks"] > 0:
        lines.append("**Verdict: INCOMPLETE** — some cases have no valid evidence chunks")
    else:
        lines.append("**Verdict: VALID** — gold set matches current corpus")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Details for cases with issues
    problem_cases = [d for d in results["details"] 
                     if d["missing_chunk_ids"] or d["source_mismatches"] or not d["valid_chunk_ids"]]
    
    if problem_cases:
        lines.append("## Problem Cases")
        lines.append("")
        for case in problem_cases[:20]:  # First 20
            lines.append(f"### {case['question']}")
            lines.append("")
            lines.append(f"- Expected sources: {case['expected_source_ids']}")
            lines.append(f"- Relevant chunk IDs: {len(case['relevant_chunk_ids'])}")
            lines.append(f"- Valid chunk IDs: {len(case['valid_chunk_ids'])}")
            lines.append(f"- Missing chunk IDs: {len(case['missing_chunk_ids'])}")
            lines.append(f"- Source mismatches: {len(case['source_mismatches'])}")
            if case["missing_chunk_ids"]:
                lines.append(f"- Missing IDs: {case['missing_chunk_ids'][:5]}")
            if case["source_mismatches"]:
                for mm in case["source_mismatches"][:3]:
                    lines.append(f"- Mismatch: {mm['chunk_id']} → {mm.get('actual_source', '?')}")
            lines.append("")
    
    # Valid cases summary
    valid_cases = [d for d in results["details"] if d["valid_chunk_ids"]]
    lines.append(f"## Valid Cases: {len(valid_cases)}/{results['answerable_cases']}")
    lines.append("")
    
    if valid_cases:
        lines.append("First 10 valid cases:")
        lines.append("")
        for case in valid_cases[:10]:
            lines.append(f"- {case['question'][:60]}... → {len(case['valid_chunk_ids'])} valid chunks")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit gold-set chunk IDs")
    parser.add_argument("--output", type=Path, default=None, help="Output path for report")
    args = parser.parse_args()
    
    print("Loading gold cases...")
    cases = load_gold_cases()
    
    print("Connecting to Supabase...")
    supabase = get_supabase_client()
    
    print("Loading chunks...")
    chunks = get_all_chunks(supabase)
    print(f"  {len(chunks)} chunks loaded")
    
    print("Loading documents...")
    documents = get_all_documents(supabase)
    print(f"  {len(documents)} documents loaded")
    
    print("Auditing gold cases...")
    results = audit_gold_cases(cases, chunks, documents)
    
    print(f"\nResults:")
    print(f"  Answerable cases: {results['answerable_cases']}")
    print(f"  Total relevant chunk IDs: {results['total_relevant_chunk_ids']}")
    print(f"  Existing: {results['existing_chunk_ids']}")
    print(f"  Missing: {results['missing_chunk_ids']}")
    print(f"  Source mismatches: {results['source_mismatches']}")
    print(f"  Cases with zero valid chunks: {results['cases_with_zero_valid_chunks']}")
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    output_path = args.output or (PROJECT_ROOT / "eval" / "reports" / "gold_chunk_audit.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")
    
    # Also save JSON
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"JSON saved to: {json_path}")


if __name__ == "__main__":
    main()
