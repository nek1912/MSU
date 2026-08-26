"""Corpus snapshot utility — records corpus version for reproducible evaluations.

Usage:
    python eval/corpus_version.py
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SEEDS_DIR = Path(__file__).resolve().parent.parent / "corpus" / "seeds"
SOURCES_PATH = Path(__file__).resolve().parent.parent / "sources.yaml"
REPORT_DIR = Path(__file__).resolve().parent / "reports"
SNAPSHOT_PATH = REPORT_DIR / "corpus_snapshot.json"


def compute_corpus_hash() -> str:
    """SHA-256 of all seed files sorted by name."""
    sha = hashlib.sha256()
    md_files = sorted(SEEDS_DIR.glob("*.md"))
    for f in md_files:
        sha.update(f.name.encode())
        sha.update(f.read_bytes())
    return sha.hexdigest()


def count_sources() -> int:
    """Count entries in sources.yaml."""
    import yaml
    with open(SOURCES_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return len(data.get("sources", []))


def count_documents() -> int:
    """Count seed files (each file = one document)."""
    return len(list(SEEDS_DIR.glob("*.md")))


def count_chunks() -> int:
    """Count ingested chunks from Supabase. Returns 0 if not available."""
    import os
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))
    if not url or not key:
        return 0
    try:
        from supabase import create_client
        client = create_client(url, key)
        result = client.rpc("count_chunks").execute()
        return result.data if result.data else 0
    except Exception:
        # Fallback: count rows directly
        try:
            from supabase import create_client
            client = create_client(url, key)
            rows = client.table("chunks").select("id", count="exact").execute()
            return rows.count if hasattr(rows, "count") else 0
        except Exception:
            return 0


def main() -> int:
    if not SEEDS_DIR.is_dir():
        print(f"Seeds directory not found: {SEEDS_DIR}", file=sys.stderr)
        return 1

    corpus_hash = compute_corpus_hash()
    source_count = count_sources()
    document_count = count_documents()
    chunk_count = count_chunks()
    timestamp = datetime.now(timezone.utc).isoformat()

    snapshot = {
        "corpus_hash": corpus_hash,
        "source_count": source_count,
        "document_count": document_count,
        "chunk_count": chunk_count,
        "ingestion_timestamp": timestamp,
        "seeds_dir": str(SEEDS_DIR),
    }

    print(f"Corpus hash: {corpus_hash}")
    print(f"Sources: {source_count}")
    print(f"Documents: {document_count}")
    print(f"Chunks: {chunk_count}")
    print(f"Timestamp: {timestamp}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Snapshot written to {SNAPSHOT_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
