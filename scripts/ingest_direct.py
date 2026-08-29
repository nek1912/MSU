import sys
sys.path.insert(0, ".")

from supabase import create_client
from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from ingestion.chunker import chunk_markdown
from ingestion.loader import parse_chunk_file
from pathlib import Path

s = get_settings()
sb = create_client(s.supabase_url, s.supabase_service_key)
provider = get_embedding_provider()

paths = sorted(Path("A:/MSU/corpus/seeds").glob("*.md"))
for path in paths:
    rec = parse_chunk_file(path)
    # Delete old doc
    sb.table("documents").delete().eq("source_id", rec["source_id"]).execute()
    # Insert doc
    doc = sb.table("documents").insert({
        "source_id": rec["source_id"], "title": rec["title"],
        "organization": rec.get("organization", ""), "domain": rec["domain"],
        "jurisdiction": rec.get("jurisdiction", "central"),
        "state": rec.get("state"),
        "document_type": "seed", "source_url": rec.get("url", ""),
    }).execute().data[0]
    
    pieces = chunk_markdown(rec["content"])
    vectors = provider.embed_texts(pieces)
    
    chunk_count = 0
    for i, (piece, vector) in enumerate(zip(pieces, vectors)):
        stable_id = f"{rec['source_id']}_{hash(piece) & 0xFFFFFFFF:08x}"
        try:
            sb.table("chunks").insert({
                "document_id": doc["id"],
                "chunk_id": stable_id,
                "page": rec.get("page", 0),
                "page_start": rec.get("page", 0),
                "page_end": rec.get("page", 0),
                "section": rec.get("section", ""),
                "content": piece,
                "embedding": vector,
                "ordinal": i,
            }).execute()
            chunk_count += 1
        except Exception as e:
            print(f"  CHUNK FAIL: {e}")
    
    print(f"  {rec['title']}: {chunk_count} chunks")

chunks = sb.table("chunks").select("id").execute().data
print(f"\nTotal chunks: {len(chunks)}")
