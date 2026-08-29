"""Apply schema to Supabase and ingest seed corpus."""
import sys
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx
from supabase import create_client

from app.config import get_settings
from app.providers.embeddings import get_embedding_provider
from ingestion.ingest import seeds_to_supabase

SCHEMA_SQL = Path(__file__).parent.parent / "backend" / "schema.sql"


def apply_schema(supabase_url: str, service_key: str) -> None:
    """Apply schema SQL via Supabase PostgREST proxy."""
    sql = SCHEMA_SQL.read_text(encoding="utf-8")
    
    # Split by semicolons and execute each statement
    # (Supabase SQL API doesn't support multi-statement)
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    
    applied = 0
    skipped = 0
    errors = 0
    
    for stmt in statements:
        # Skip comments-only statements
        lines = [l for l in stmt.split("\n") if not l.strip().startswith("--")]
        clean = "\n".join(lines).strip()
        if not clean:
            skipped += 1
            continue
        
        try:
            r = httpx.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"query": clean + ";"},
                timeout=30.0,
            )
            if r.status_code in (200, 204):
                applied += 1
            else:
                # Try via the /pg endpoint
                r2 = httpx.post(
                    f"{supabase_url}/pg/query",
                    headers=headers,
                    json={"query": clean + ";"},
                    timeout=30.0,
                )
                if r2.status_code in (200, 204):
                    applied += 1
                else:
                    print(f"  WARN: {r.status_code} for: {clean[:80]}...")
                    errors += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1
    
    print(f"Schema: {applied} applied, {skipped} skipped, {errors} errors")


def check_tables(supabase) -> bool:
    """Check if documents table exists."""
    try:
        supabase.table("documents").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def main():
    settings = get_settings()
    sb = create_client(settings.supabase_url, settings.supabase_service_key)
    
    print("=== Checking Supabase tables ===")
    tables_exist = check_tables(sb)
    
    if not tables_exist:
        print("Tables not found. Applying schema...")
        apply_schema(settings.supabase_url, settings.supabase_service_key)
        
        # Verify
        if not check_tables(sb):
            print("\nSchema application may have partial failures.")
            print("Please apply schema manually:")
            print(f"  1. Open {settings.supabase_url.replace('https://', 'https://supabase.com/dashboard/project/')}/sql/new")
            print(f"  2. Paste contents of: {SCHEMA_SQL}")
            print(f"  3. Click 'Run'")
            print(f"\nThen re-run this script.")
            sys.exit(1)
        print("Schema applied successfully!")
    else:
        print("Tables already exist.")
    
    print("\n=== Ingesting seed corpus ===")
    seed_paths = sorted(Path(__file__).parent.parent / "corpus" / "seeds" / "*.md")
    if not seed_paths:
        print("No seed files found!")
        sys.exit(1)
    
    print(f"Found {len(seed_paths)} seed documents")
    
    embed_fn = get_embedding_provider().embed_texts
    count = seeds_to_supabase(seed_paths, embed_fn, sb)
    print(f"Ingested {count} seed documents")
    
    print("\n=== Verifying ===")
    docs = sb.table("documents").select("id, title, domain").execute().data
    chunks = sb.table("chunks").select("id").execute().data
    print(f"Documents in DB: {len(docs)}")
    print(f"Chunks in DB: {len(chunks)}")
    for d in docs:
        print(f"  - [{d['domain']}] {d['title']}")
    
    print("\nMVP is ready! Start servers:")
    print("  Backend:  cd backend && uvicorn app.main:app --port 8000")
    print("  Frontend: cd frontend && npm run dev")


if __name__ == "__main__":
    main()
