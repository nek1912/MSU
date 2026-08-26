from pathlib import Path

from ingestion.chunker import chunk_markdown
from ingestion.loader import parse_chunk_file

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"


def seeds_to_supabase(paths: list[Path], embed_texts, supabase) -> int:
    total = 0
    for path in paths:
        rec = parse_chunk_file(path)
        supabase.table("documents").delete().eq("source_id", rec["source_id"]).execute()
        doc = supabase.table("documents").insert({
            "source_id": rec["source_id"], "title": rec["title"],
            "organization": rec["organization"], "domain": rec["domain"],
            "jurisdiction": rec["jurisdiction"], "state": rec.get("state"),
            "document_type": "seed", "source_url": rec["url"],
            "effective_date": rec.get("effective_date"),
            "verified_date": rec["verified_date"],
        }).execute().data[0]
        # Same pipeline as the real corpus (P1-6): parse -> chunk -> embed -> insert.
        pieces = chunk_markdown(rec["content"])
        vectors = embed_texts(pieces)
        for piece, vector in zip(pieces, vectors):
            supabase.table("chunks").insert({
                "document_id": doc["id"], "page": rec.get("page", 0),
                "section": rec.get("section", ""), "content": piece,
                "embedding": vector})
        total += 1
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
