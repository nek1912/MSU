"""Gold-set semantic audit — verifies each gold chunk contains answer-bearing evidence.

Usage:
    python -m eval.gold_semantic_audit

This is a manual/semantic verification, not an embedding-similarity check.
"""
import json
import os
import sys
from pathlib import Path

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


def get_chunk_content(supabase, chunk_id: str) -> dict | None:
    """Get chunk content from database."""
    result = supabase.table("chunks").select("id, content, document_id, page, section").eq("id", chunk_id).execute()
    return result.data[0] if result.data else None


def get_document_info(supabase, doc_id: str) -> dict | None:
    """Get document info from database."""
    result = supabase.table("documents").select("id, source_id, title, domain").eq("id", doc_id).execute()
    return result.data[0] if result.data else None


def audit_semantic_relevance(cases: list[dict], supabase) -> dict:
    """Audit each gold chunk for semantic relevance."""
    results = {
        "total_cases": len(cases),
        "answerable_cases": 0,
        "total_gold_chunks": 0,
        "chunks_with_evidence": 0,
        "chunks_without_evidence": 0,
        "cases": [],
    }
    
    for case in cases:
        if not case.get("answerable", False):
            continue
        
        results["answerable_cases"] += 1
        question = case.get("question", "?")
        relevant_chunk_ids = case.get("relevant_chunk_ids", [])
        
        case_detail = {
            "question": question,
            "expected_domain": case.get("expected_domain"),
            "relevant_source_ids": case.get("relevant_source_ids", []),
            "relevant_chunk_ids": relevant_chunk_ids,
            "chunk_audit": [],
        }
        
        for chunk_id in relevant_chunk_ids:
            results["total_gold_chunks"] += 1
            chunk = get_chunk_content(supabase, chunk_id)
            
            if not chunk:
                case_detail["chunk_audit"].append({
                    "chunk_id": chunk_id,
                    "status": "MISSING",
                    "has_evidence": False,
                })
                results["chunks_without_evidence"] += 1
                continue
            
            # Get document info
            doc = get_document_info(supabase, chunk.get("document_id"))
            
            # Extract content preview
            content = chunk.get("content", "")
            content_preview = content[:500].replace("\n", " ")
            
            case_detail["chunk_audit"].append({
                "chunk_id": chunk_id,
                "status": "EXISTS",
                "source_id": doc.get("source_id") if doc else "?",
                "page": chunk.get("page"),
                "content_preview": content_preview,
                "content_length": len(content),
                # This field needs manual/semantic assessment
                "has_evidence": None,  # TODO: Manual verification needed (YES/PARTIAL/NO)
            })
        
        results["cases"].append(case_detail)
    
    return results


def generate_report(results: dict) -> str:
    """Generate markdown report."""
    lines = []
    lines.append("# Gold-Set Semantic Audit Report")
    lines.append("")
    lines.append("**Date:** 2026-08-28")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This audit verifies that each gold chunk actually contains answer-bearing evidence for its question.")
    lines.append("This is NOT an embedding-similarity check — it's a semantic relevance verification.")
    lines.append("")
    lines.append("**Important:** Don't require every individual gold chunk to independently answer the whole question.")
    lines.append("Some questions legitimately require multiple chunks. The criterion is whether the chunk provides")
    lines.append("meaningful evidence, and whether the **set of gold chunks collectively supports the answer**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total gold cases | {results['total_cases']} |")
    lines.append(f"| Answerable cases | {results['answerable_cases']} |")
    lines.append(f"| Total gold chunks | {results['total_gold_chunks']} |")
    lines.append(f"| Chunks needing verification | {results['total_gold_chunks']} |")
    lines.append("")
    lines.append("**Status:** PENDING MANUAL VERIFICATION")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Manual Verification Instructions")
    lines.append("")
    lines.append("For each case below, verify:")
    lines.append("")
    lines.append("1. Read the question.")
    lines.append("2. Read every assigned `relevant_chunk_id`.")
    lines.append("3. Inspect the actual chunk content.")
    lines.append("4. Mark each chunk:")
    lines.append("   - **YES** = directly contains answer-bearing evidence")
    lines.append("   - **PARTIAL** = supports an essential part but is insufficient alone")
    lines.append("   - **NO** = merely belongs to the correct document/domain")
    lines.append("5. For each case, ensure the remaining gold chunks collectively contain enough evidence to answer the question.")
    lines.append("6. Replace/remove incorrect gold chunks using semantic judgment, NOT embedding similarity.")
    lines.append("7. Record the reason for every change.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Cases
    for i, case in enumerate(results["cases"]):
        lines.append(f"## Case {i+1}: {case['question']}")
        lines.append("")
        lines.append(f"- **Domain:** {case['expected_domain']}")
        lines.append(f"- **Expected sources:** {case['relevant_source_ids']}")
        lines.append(f"- **Gold chunks:** {len(case['relevant_chunk_ids'])}")
        lines.append("")
        
        for j, chunk in enumerate(case["chunk_audit"]):
            lines.append(f"### Chunk {j+1}: `{chunk['chunk_id'][:12]}...`")
            lines.append("")
            lines.append(f"- **Status:** {chunk['status']}")
            lines.append(f"- **Source:** {chunk.get('source_id', '?')}")
            lines.append(f"- **Page:** {chunk.get('page', '?')}")
            lines.append(f"- **Content length:** {chunk.get('content_length', 0)} chars")
            lines.append("")
            
            if chunk.get("content_preview"):
                lines.append("**Content preview:**")
                lines.append("")
                lines.append(f"> {chunk['content_preview'][:300]}...")
                lines.append("")
            
            lines.append("**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit gold-set semantic relevance")
    parser.add_argument("--output", type=Path, default=None, help="Output path for report")
    args = parser.parse_args()
    
    print("Loading gold cases...")
    cases = load_gold_cases()
    
    print("Connecting to Supabase...")
    supabase = get_supabase_client()
    
    print("Auditing semantic relevance...")
    results = audit_semantic_relevance(cases, supabase)
    
    print(f"\nResults:")
    print(f"  Answerable cases: {results['answerable_cases']}")
    print(f"  Total gold chunks: {results['total_gold_chunks']}")
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    output_path = args.output or (PROJECT_ROOT / "eval" / "reports" / "gold_semantic_audit.md")
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
