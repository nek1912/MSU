"""Conftest for integration tests — does NOT override environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load real .env from backend directory
_backend_dir = Path(__file__).resolve().parent.parent / "backend"
_env_path = _backend_dir / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

# Clear any cached settings so real values are used
from app.config import get_settings
get_settings.cache_clear()

# Also clear the Supabase client cache
from app.db import get_supabase
get_supabase.cache_clear()
