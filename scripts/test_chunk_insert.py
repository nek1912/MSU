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

path = Path("A:/MSU/corpus/seeds/pmfby_claims.md")
rec = parse_chunk_file(path)
docs = sb.table("documents").select("id").eq("source_id", rec["source_id"]).execute().data
if not docs:
    print("No doc found for", rec["source_id"])
    sys.exit(1)
doc_id = docs[0]["id"]
pieces = chunk_markdown(rec["content"])
print(f"Chunks to insert: {len(pieces)}")
vectors = provider.embed_texts(pieces)
for i, (piece, vector) in enumerate(zip(pieces, vectors)):
    stable_id = f"{rec['source_id']}_{hash(piece) & 0xFFFFFFFF:08x}"
    try:
        sb.table("chunks").insert({
            "document_id": doc_id,
            "chunk_id": stable_id,
            "page": rec.get("page", 0),
            "page_start": rec.get("page", 0),
            "page_end": rec.get("page", 0),
            "section": rec.get("section", ""),
            "content": piece,
            "embedding": vector,
            "ordinal": i,
        }).execute()
        print(f"  Chunk {i} OK")
    except Exception as e:
        print(f"  Chunk {i} FAILED: {e}")

# Verify
chunks = sb.table("chunks").select("id").execute().data
print(f"\nTotal chunks in DB: {len(chunks)}")
