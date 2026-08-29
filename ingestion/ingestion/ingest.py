from pathlib import Path

from ingestion.chunker import chunk_markdown
from ingestion.loader import parse_chunk_file

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"


def _serialize_date(val):
    """Convert date/datetime to ISO string for JSON serialization."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def seeds_to_supabase(paths: list[Path], embed_texts, supabase) -> int:
    total = 0
    for path in paths:
        rec = parse_chunk_file(path)
        supabase.table("documents").delete().eq("source_id", rec["source_id"]).execute()
        doc = supabase.table("documents").insert({
            "source_id": rec["source_id"], "title": rec["title"],
            "organization": rec.get("organization", ""), "domain": rec["domain"],
            "jurisdiction": rec.get("jurisdiction", "central"),
            "state": rec.get("state"),
            "document_type": "seed", "source_url": rec.get("url", ""),
            "effective_date": _serialize_date(rec.get("effective_date")),
            "verified_date": _serialize_date(rec.get("verified_date")),
        }).execute().data[0]
        # Same pipeline as the real corpus (P1-6): parse -> chunk -> embed -> insert.
        pieces = chunk_markdown(rec["content"])
        vectors = embed_texts(pieces)
        for i, (piece, vector) in enumerate(zip(pieces, vectors)):
            stable_id = f"{rec['source_id']}_{hash(piece) & 0xFFFFFFFF:08x}"
            supabase.table("chunks").insert({
                "document_id": doc["id"],
                "chunk_id": stable_id,
                "page": rec.get("page", 0),
                "page_start": rec.get("page", 0),
                "page_end": rec.get("page", 0),
                "section": rec.get("section", ""),
                "content": piece,
                "embedding": vector,
                "ordinal": i,
            })
        total += 1
        print(f"  ingested: {rec['title']}")
    return total


if __name__ == "__main__":
    from supabase import create_client

    from app.config import get_settings
    from app.providers.embeddings import get_embedding_provider

    s = get_settings()
    paths = sorted(SEEDS_DIR.glob("*.md"))
    count = seeds_to_supabase(paths, get_embedding_provider().embed_texts,
                              create_client(s.supabase_url, s.supabase_service_key))
    print(f"ingested {count} seed documents")
