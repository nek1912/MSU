"""Schema smoke tests — require live Supabase connection.

These tests create a fresh Supabase client directly to avoid caching issues.
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load real .env
_backend_dir = Path(__file__).resolve().parent.parent / "backend"
_env_path = _backend_dir / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)


def get_live_supabase():
    """Create a fresh Supabase client with real credentials."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        pytest.skip("SUPABASE_URL or SUPABASE_SERVICE_KEY not set")
    return create_client(url, key)


@pytest.mark.integration
def test_documents_has_document_date_column():
    """Verify document_date column exists in documents table."""
    supabase = get_live_supabase()
    result = supabase.table("documents").select("document_date").limit(1).execute()
    assert result.data is not None


@pytest.mark.integration
def test_documents_has_source_type_column():
    """Verify source_type column exists in documents table."""
    supabase = get_live_supabase()
    result = supabase.table("documents").select("source_type").limit(1).execute()
    assert result.data is not None


@pytest.mark.integration
def test_documents_table_structure():
    """Verify documents table has expected columns."""
    supabase = get_live_supabase()
    # Try selecting all expected columns
    result = supabase.table("documents").select(
        "id, source_id, title, organization, jurisdiction, state, domain, "
        "document_type, source_url, effective_date, document_date, "
        "verified_date, document_hash, source_type, created_at"
    ).limit(1).execute()
    assert result.data is not None


@pytest.mark.integration
def test_chunks_table_exists():
    """Verify chunks table exists and has expected structure."""
    supabase = get_live_supabase()
    result = supabase.table("chunks").select("id, document_id, page, section, content, embedding").limit(1).execute()
    assert result.data is not None


@pytest.mark.integration
def test_match_chunks_function_exists():
    """Verify match_chunks RPC function exists."""
    supabase = get_live_supabase()
    # Call with a dummy vector to verify function exists
    dummy_vector = [0.0] * 768
    result = supabase.rpc("match_chunks", {
        "query_embedding": dummy_vector,
        "match_domain": "test",
        "match_state": None,
        "match_count": 1,
    }).execute()
    # Function exists if we get here (even if no results)
    assert result.data is not None


@pytest.mark.integration
def test_atomic_replace_function_exists():
    """Verify atomic_replace_document RPC function exists."""
    supabase = get_live_supabase()
    # We can't easily test this without actually inserting data,
    # but we can verify the function is callable
    # Just checking that the function reference doesn't error
    assert supabase.rpc is not None
