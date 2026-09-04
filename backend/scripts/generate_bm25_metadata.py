"""Generate BM25 metadata from database chunks.

Run this script to create backend/data/indexes/section_metadata.json
for the BM25 retriever.
"""
import json
from pathlib import Path

from app.db import get_supabase


def generate_metadata():
    supabase = get_supabase()
    
    # Fetch all chunks with document info
    result = supabase.table("chunks").select(
        "id, chunk_id, content, document_id, page, section, metadata"
    ).execute()
    
    chunks = result.data
    print(f"Fetched {len(chunks)} chunks from database")
    
    # Fetch documents for titles and URLs
    doc_result = supabase.table("documents").select(
        "id, title, source_url, domain, jurisdiction, state"
    ).execute()
    
    docs = {d["id"]: d for d in doc_result.data}
    print(f"Fetched {len(docs)} documents")
    
    metadata = []
    for chunk in chunks:
        doc = docs.get(chunk["document_id"], {})
        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "text": chunk["content"],
            "title": doc.get("title", ""),
            "source_url": doc.get("source_url", ""),
            "page": chunk.get("page"),
            "section_title": chunk.get("section", ""),
            "section_type": None,
            "language": None,
            "domain": doc.get("domain", ""),
            "jurisdiction": doc.get("jurisdiction", ""),
            "state": doc.get("state"),
        })
    
    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "indexes" / "section_metadata.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(metadata)} chunks to {output_path}")


if __name__ == "__main__":
    generate_metadata()
