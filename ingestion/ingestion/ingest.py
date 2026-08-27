from pathlib import Path

from ingestion.chunker import chunk_markdown
from ingestion.loader import parse_chunk_file
from ingestion.manifest import load_mvp_manifest, validate_manifest_fields, validate_manifest_files

SEEDS_DIR = Path(__file__).parent.parent / "corpus" / "seeds"


def normalize_state(state: str | None) -> str | None:
    """Normalize state value to lowercase trimmed string or None."""
    if not state or not isinstance(state, str):
        return None
    normalized = state.strip().lower()
    return normalized if normalized else None


def seeds_to_supabase(paths: list[Path], embed_texts, supabase) -> int:
    total = 0
    for path in paths:
        rec = parse_chunk_file(path)
        supabase.table("documents").delete().eq("source_id", rec["source_id"]).execute()
        doc = supabase.table("documents").insert({
            "source_id": rec["source_id"], "title": rec["title"],
            "organization": rec["organization"], "domain": rec["domain"],
            "jurisdiction": rec["jurisdiction"], "state": normalize_state(rec.get("state")),
            "document_type": "seed", "source_url": rec["url"],
            "effective_date": rec.get("effective_date"),
            "document_date": rec.get("document_date"),
            "verified_date": rec["verified_date"],
            "source_type": "seed",  # Explicit value, not derived
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


def manifest_to_supabase(manifest_path: Path, embed_texts, supabase, dry_run: bool = False, preflight: bool = False) -> dict:
    """Ingest PDF sources from MVP manifest.
    
    This function:
    1. Loads manifest
    2. Validates file existence (fails if any MVP file missing)
    3. Validates manifest fields (fails if required fields missing)
    4. Extracts text from PDFs using Docling
    5. Chunks extracted text
    6. Generates embeddings (if not dry_run)
    7. Atomically replaces old data in Supabase via RPC transaction
    
    Failure semantics:
    - Manifest validation failure: FAIL entire run before processing
    - Missing MVP file: FAIL before extraction/embedding starts
    - Individual PDF processing failure: isolate file, preserve existing DB state, continue
    
    Args:
        manifest_path: Path to MVP manifest YAML
        embed_texts: Embedding function
        supabase: Supabase client
        dry_run: If True, report what would be done without embeddings or DB writes
        preflight: If True, run full pipeline including embeddings but no DB writes
        
    Returns:
        Dict with 'succeeded' list and 'failed' list
    """
    if dry_run and preflight:
        raise ValueError("dry_run and preflight are mutually exclusive")
    
    sources = load_mvp_manifest(manifest_path)
    base_dir = manifest_path.parent.parent
    
    # FAIL entire run if any MVP file missing
    valid_sources, missing_sources = validate_manifest_files(sources, base_dir)
    if missing_sources:
        raise ValueError(f"Missing MVP files (required for ingestion): {[s.get('path') for s in missing_sources]}")
    
    # FAIL entire run if manifest fields invalid
    for source in valid_sources:
        errors = validate_manifest_fields(source)
        if errors:
            raise ValueError(f"Manifest source {source.get('source_id')} missing required fields: {errors}")
    
    succeeded = []
    failed = []
    
    for source in valid_sources:
        file_path = base_dir / source["path"]
        try:
            # Extract PDF to markdown (placeholder - will be implemented in Task 4)
            # For now, use a simple file read as placeholder
            markdown_content = f"# {source.get('actual_title', source['source_id'])}\n\nPlaceholder content for {file_path.name}"
            
            # Chunk the extracted content
            pieces = chunk_markdown(markdown_content)
            
            if dry_run:
                print(f"DRY RUN: Would process {source['source_id']}: {len(pieces)} chunks")
                succeeded.append(source["source_id"])
                continue
            
            # Generate embeddings
            vectors = embed_texts(pieces)
            
            if preflight:
                print(f"PREFLIGHT: Would process {source['source_id']}: {len(pieces)} chunks, {len(vectors)} embeddings")
                succeeded.append(source["source_id"])
                continue
            
            # Atomic replacement via RPC transaction (placeholder - will be implemented in Task 10)
            # For now, use simple insert
            supabase.table("documents").delete().eq("source_id", source["source_id"]).execute()
            doc = supabase.table("documents").insert({
                "source_id": source["source_id"],
                "title": source.get("actual_title", source["source_id"]),
                "organization": source.get("issuing_organization", ""),
                "domain": source.get("target_domain", ""),
                "jurisdiction": source.get("jurisdiction", "central"),
                "state": normalize_state(source.get("state")),
                "document_type": source.get("document_type", "pdf"),
                "source_url": source.get("official_source_url", ""),
                "effective_date": source.get("effective_date"),
                "document_date": source.get("document_date"),
                "verified_date": source.get("verified_date", "2026-08-27"),
                "source_type": "pdf",
            }).execute().data[0]
            
            # Insert chunks
            for piece, vector in zip(pieces, vectors):
                supabase.table("chunks").insert({
                    "document_id": doc["id"],
                    "page": 0,  # page=0 means "page provenance unavailable in Phase 2A"
                    "section": "",
                    "content": piece,
                    "embedding": vector
                }).execute()
            
            succeeded.append(source["source_id"])
            print(f"Successfully ingested: {source['source_id']}")
            
        except (FileNotFoundError, ValueError, KeyError) as e:
            failed.append({"source_id": source["source_id"], "error": str(e)})
            print(f"ERROR processing {source['source_id']}: {e}")
            continue
    
    print(f"\nSummary: {len(succeeded)} succeeded, {len(failed)} failed")
    if failed:
        print(f"Failed sources: {[f['source_id'] for f in failed]}")
    
    return {"succeeded": succeeded, "failed": failed}


if __name__ == "__main__":
    from app.config import get_settings
    from app.providers.embeddings import get_embedding_provider
    from supabase import create_client

    s = get_settings()
    paths = sorted(SEEDS_DIR.glob("*.md"))
    count = seeds_to_supabase(paths, get_embedding_provider().embed_texts,
                              create_client(s.supabase_url, s.supabase_service_key))
    print(f"ingested {count} seed documents")
