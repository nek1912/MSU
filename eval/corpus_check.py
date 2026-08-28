"""Database integrity check script — verifies corpus structure after ingestion.

Usage:
    python -m eval.corpus_check

Checks:
- No orphan chunks
- No duplicate source_ids
- No null embeddings
- Correct embedding dimension (768)
- Valid domain values
- Valid jurisdiction values
- Manifest↔DB consistency
- Metadata completeness
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_supabase_client():
    """Get Supabase client from environment."""
    from dotenv import load_dotenv
    from supabase import create_client
    
    # Load from backend/.env
    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)
    
    import os
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        raise ValueError(f"Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in {env_path}")
    
    return create_client(url, key)


def load_manifest() -> list[dict]:
    """Load MVP manifest."""
    manifest_path = PROJECT_ROOT / "corpus" / "manifests" / "mvp_sources.yaml"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("sources", [])


def check_orphan_chunks(supabase) -> list[dict]:
    """Find chunks with no valid document."""
    # Get all chunk document_ids
    chunks = supabase.table("chunks").select("id, document_id").execute().data
    doc_ids = set(c["document_id"] for c in chunks)
    
    # Get all document IDs
    docs = supabase.table("documents").select("id").execute().data
    valid_doc_ids = set(d["id"] for d in docs)
    
    # Find orphans
    orphans = []
    for chunk in chunks:
        if chunk["document_id"] not in valid_doc_ids:
            orphans.append({
                "chunk_id": chunk["id"],
                "document_id": chunk["document_id"],
            })
    
    return orphans


def check_duplicate_source_ids(supabase) -> list[str]:
    """Find duplicate source_ids in documents table."""
    docs = supabase.table("documents").select("source_id").execute().data
    seen = {}
    duplicates = []
    
    for doc in docs:
        sid = doc["source_id"]
        if sid in seen:
            duplicates.append(sid)
        seen[sid] = True
    
    return duplicates


def check_null_embeddings(supabase) -> list[str]:
    """Find chunks with null embeddings."""
    chunks = supabase.table("chunks").select("id, embedding").execute().data
    null_chunks = []
    
    for chunk in chunks:
        if chunk.get("embedding") is None:
            null_chunks.append(chunk["id"])
    
    return null_chunks


def check_embedding_dimension(supabase, expected_dim: int = 768) -> list[dict]:
    """Find chunks with wrong embedding dimension."""
    import json
    chunks = supabase.table("chunks").select("id, embedding").execute().data
    wrong_dim = []
    
    for chunk in chunks:
        embedding = chunk.get("embedding")
        if embedding is not None:
            # Handle both list and string (JSON) formats
            if isinstance(embedding, list):
                actual_dim = len(embedding)
            elif isinstance(embedding, str):
                try:
                    parsed = json.loads(embedding)
                    actual_dim = len(parsed) if isinstance(parsed, list) else 0
                except (json.JSONDecodeError, TypeError):
                    actual_dim = 0
            else:
                actual_dim = 0
            
            if actual_dim != expected_dim:
                wrong_dim.append({
                    "chunk_id": chunk["id"],
                    "expected": expected_dim,
                    "actual": actual_dim,
                })
    
    return wrong_dim


def check_domain_values(supabase, valid_domains: list[str]) -> list[dict]:
    """Find documents with invalid domain values."""
    docs = supabase.table("documents").select("id, source_id, domain").execute().data
    invalid = []
    
    for doc in docs:
        if doc["domain"] not in valid_domains:
            invalid.append({
                "document_id": doc["id"],
                "source_id": doc["source_id"],
                "domain": doc["domain"],
            })
    
    return invalid


def check_jurisdiction_values(supabase) -> list[dict]:
    """Find documents with invalid jurisdiction or missing state."""
    docs = supabase.table("documents").select(
        "id, source_id, jurisdiction, state"
    ).execute().data
    invalid = []
    
    for doc in docs:
        if doc["jurisdiction"] not in ("central", "state"):
            invalid.append({
                "document_id": doc["id"],
                "source_id": doc["source_id"],
                "issue": f"invalid jurisdiction: {doc['jurisdiction']}",
            })
        elif doc["jurisdiction"] == "state" and not doc.get("state"):
            invalid.append({
                "document_id": doc["id"],
                "source_id": doc["source_id"],
                "issue": "state jurisdiction but no state specified",
            })
    
    return invalid


def check_manifest_db_consistency(supabase, manifest_sources: list[dict]) -> dict:
    """Check consistency between manifest and database."""
    manifest_ids = {s["source_id"] for s in manifest_sources}
    
    # Get DB source_ids (only seed/pdf types)
    docs = supabase.table("documents").select("source_id, source_type").execute().data
    db_ids = {d["source_id"] for d in docs if d.get("source_type") in ("seed", "pdf")}
    
    return {
        "in_manifest_not_db": list(manifest_ids - db_ids),
        "in_db_not_manifest": list(db_ids - manifest_ids),
        "manifest_count": len(manifest_ids),
        "db_count": len(db_ids),
    }


def check_metadata_completeness(supabase) -> list[dict]:
    """Check that all documents have required metadata fields."""
    docs = supabase.table("documents").select(
        "id, source_id, title, organization, domain, jurisdiction, document_type, source_url"
    ).execute().data
    incomplete = []
    
    for doc in docs:
        missing = []
        for field in ["title", "organization", "domain", "jurisdiction", "document_type", "source_url"]:
            if not doc.get(field):
                missing.append(field)
        
        if missing:
            incomplete.append({
                "document_id": doc["id"],
                "source_id": doc["source_id"],
                "missing_fields": missing,
            })
    
    return incomplete


def check_chunks_per_document(supabase) -> dict:
    """Get chunks per document statistics."""
    docs = supabase.table("documents").select("id, source_id").execute().data
    stats = {}
    
    for doc in docs:
        chunks = supabase.table("chunks").select("id").eq("document_id", doc["id"]).execute().data
        stats[doc["source_id"]] = len(chunks)
    
    return stats


def generate_corpus_snapshot(supabase, doc_count: int, chunk_count: int) -> dict:
    """Generate a reproducible corpus snapshot."""
    docs = supabase.table("documents").select("source_id").order("source_id").execute().data
    source_ids = [d["source_id"] for d in docs]
    
    # Create hash from sorted source_ids + chunk counts
    hash_input = json.dumps({"source_ids": source_ids, "chunk_count": chunk_count}, sort_keys=True)
    corpus_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    return {
        "corpus_hash": corpus_hash,
        "document_count": doc_count,
        "chunk_count": chunk_count,
        "source_ids": source_ids,
        "embedding_model": "jina-embeddings-v3",  # Auto-detect in production
        "embedding_dimension": 768,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def run_integrity_check() -> dict:
    """Run full database integrity check."""
    print("Connecting to Supabase...")
    supabase = get_supabase_client()
    
    print("Loading manifest...")
    manifest_sources = load_manifest()
    
    # Get counts
    docs = supabase.table("documents").select("id").execute().data
    doc_count = len(docs)
    chunks = supabase.table("chunks").select("id").execute().data
    chunk_count = len(chunks)
    
    print(f"Documents: {doc_count}, Chunks: {chunk_count}")
    
    results = {
        "document_count": doc_count,
        "chunk_count": chunk_count,
        "checks": {},
        "blocking_failures": [],
        "warnings": [],
    }
    
    # Run all checks
    print("\nRunning checks...")
    
    # 1. Orphan chunks
    orphans = check_orphan_chunks(supabase)
    results["checks"]["orphan_chunks"] = {
        "count": len(orphans),
        "details": orphans[:10],  # First 10 for brevity
    }
    if orphans:
        results["blocking_failures"].append(f"Orphan chunks: {len(orphans)}")
    
    # 2. Duplicate source_ids
    duplicates = check_duplicate_source_ids(supabase)
    results["checks"]["duplicate_source_ids"] = {
        "count": len(duplicates),
        "details": duplicates,
    }
    if duplicates:
        results["blocking_failures"].append(f"Duplicate source_ids: {duplicates}")
    
    # 3. Null embeddings
    null_embeddings = check_null_embeddings(supabase)
    results["checks"]["null_embeddings"] = {
        "count": len(null_embeddings),
        "details": null_embeddings[:10],
    }
    if null_embeddings:
        results["blocking_failures"].append(f"Null embeddings: {len(null_embeddings)}")
    
    # 4. Wrong embedding dimension
    wrong_dim = check_embedding_dimension(supabase)
    results["checks"]["wrong_embedding_dimension"] = {
        "count": len(wrong_dim),
        "details": wrong_dim[:10],
    }
    if wrong_dim:
        results["blocking_failures"].append(f"Wrong embedding dimension: {len(wrong_dim)}")
    
    # 5. Invalid domain values
    valid_domains = ["cooperative", "pacs", "pacs_governance", "pacs_computerization",
                     "pmfby", "financial_inclusion", "schemes", "grievance", "out_of_scope"]
    invalid_domains = check_domain_values(supabase, valid_domains)
    results["checks"]["invalid_domains"] = {
        "count": len(invalid_domains),
        "details": invalid_domains[:10],
    }
    if invalid_domains:
        results["warnings"].append(f"Invalid domains: {len(invalid_domains)}")
    
    # 6. Invalid jurisdiction values
    invalid_jurisdiction = check_jurisdiction_values(supabase)
    results["checks"]["invalid_jurisdiction"] = {
        "count": len(invalid_jurisdiction),
        "details": invalid_jurisdiction[:10],
    }
    if invalid_jurisdiction:
        results["blocking_failures"].append(f"Invalid jurisdiction: {len(invalid_jurisdiction)}")
    
    # 7. Manifest↔DB consistency
    consistency = check_manifest_db_consistency(supabase, manifest_sources)
    results["checks"]["manifest_db_consistency"] = consistency
    if consistency["in_manifest_not_db"]:
        results["blocking_failures"].append(f"In manifest not in DB: {consistency['in_manifest_not_db']}")
    if consistency["in_db_not_manifest"]:
        results["warnings"].append(f"In DB not in manifest: {consistency['in_db_not_manifest']}")
    
    # 8. Metadata completeness
    incomplete = check_metadata_completeness(supabase)
    results["checks"]["metadata_completeness"] = {
        "count": len(incomplete),
        "details": incomplete[:10],
    }
    if incomplete:
        results["warnings"].append(f"Incomplete metadata: {len(incomplete)}")
    
    # 9. Chunks per document
    chunks_per_doc = check_chunks_per_document(supabase)
    results["checks"]["chunks_per_document"] = chunks_per_doc
    
    # Check for documents with 0 chunks
    empty_docs = [sid for sid, count in chunks_per_doc.items() if count == 0]
    if empty_docs:
        results["blocking_failures"].append(f"Documents with 0 chunks: {empty_docs}")
    
    # Check for documents with >1000 chunks (sanity check)
    oversized_docs = [sid for sid, count in chunks_per_doc.items() if count > 1000]
    if oversized_docs:
        results["warnings"].append(f"Documents with >1000 chunks: {oversized_docs}")
    
    # Generate corpus snapshot
    results["corpus_snapshot"] = generate_corpus_snapshot(supabase, doc_count, chunk_count)
    
    # Determine verdict
    results["blocking_failure_count"] = len(results["blocking_failures"])
    results["warning_count"] = len(results["warnings"])
    results["verdict"] = "PASS" if not results["blocking_failures"] else "FAIL"
    
    return results


def print_report(results: dict):
    """Print human-readable report."""
    print("\n" + "=" * 60)
    print("DATABASE INTEGRITY CHECK COMPLETE")
    print("=" * 60)
    print(f"  Documents: {results['document_count']}")
    print(f"  Chunks: {results['chunk_count']}")
    print()
    
    for check_name, check_result in results["checks"].items():
        if isinstance(check_result, dict) and "count" in check_result:
            status = "OK" if check_result["count"] == 0 else "FAIL"
            print(f"  {check_name}: {check_result['count']} [{status}]")
        elif isinstance(check_result, dict):
            print(f"  {check_name}: {check_result}")
    
    print()
    print(f"  Blocking failures: {results['blocking_failure_count']}")
    print(f"  Warnings: {results['warning_count']}")
    print(f"  Verdict: {results['verdict']}")
    
    if results["blocking_failures"]:
        print("\n  BLOCKING FAILURES:")
        for bf in results["blocking_failures"]:
            print(f"    - {bf}")
    
    if results["warnings"]:
        print("\n  WARNINGS:")
        for w in results["warnings"]:
            print(f"    - {w}")
    
    if "corpus_snapshot" in results:
        snapshot = results["corpus_snapshot"]
        print(f"\n  Corpus snapshot: {snapshot['corpus_hash']}")
        print(f"  Source IDs: {len(snapshot['source_ids'])}")
    
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run database integrity check")
    parser.add_argument("--output", type=Path, default=None, help="Path to save JSON report")
    args = parser.parse_args()
    
    results = run_integrity_check()
    print_report(results)
    
    # Save JSON report
    output_path = args.output or (PROJECT_ROOT / "eval" / "integrity_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {output_path}")
    
    # Exit with appropriate code
    if results["verdict"] == "FAIL":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
