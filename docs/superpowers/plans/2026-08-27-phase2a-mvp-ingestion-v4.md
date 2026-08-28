# Phase 2A MVP Ingestion Implementation Plan (v4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the ingestion → storage → retrieval path work correctly with the five real MVP PDFs.

**Architecture:** Add Docling-based PDF extraction to the existing ingestion pipeline, driven by the MVP manifest. Extract → validate → chunk → embed → atomic DB replacement via PostgreSQL RPC transaction. Preserve existing seed-file ingestion for backward compatibility.

**Tech Stack:** Python, Docling, Supabase, Gemini API, Pydantic, YAML

## Global Constraints

- Do not rewrite the RAG architecture
- Do not add new providers (retry/backoff only, no fallback provider)
- Do not ingest hold sources
- Do not add OCR during this task
- External Gemini embedding calls cannot participate in Supabase transactions
- Safe sequence: extract → validate → chunk → embed successfully → atomic DB replacement via RPC
- Every finding must cite actual file/function/test evidence
- Severity levels: P0 (blocks MVP), P1 (degrades quality), P2 (nice-to-have)

## Failure Semantics (Explicit)

```
Manifest validation failure:
    FAIL entire run before processing anything.

Missing MVP file (per manifest):
    FAIL before extraction/embedding starts.

Individual PDF processing failure:
    isolate file, preserve existing DB state, continue other files.

RPC transaction failure:
    transaction rolls back, existing document preserved.
```

## Dry-Run Modes

```
--dry-run:
    manifest validation
    extraction
    validation
    chunking
    report
    NO embeddings, NO DB writes

--preflight:
    manifest validation
    extraction
    validation
    chunking
    embedding
    report
    NO DB writes

dry_run and preflight are mutually exclusive.
```

---

### Task 1: Add Document Date and Source Type to DB Schema

**Files:**
- Create: `backend/migrations/0003_add_document_date_source_type.sql`
- Modify: `backend/migrations/0001_init.sql` (for new deployments only)
- Modify: `ingestion/ingestion/ingest.py`
- Create: `backend/tests/test_schema_smoke.py`

**Interfaces:**
- Consumes: Existing documents table schema
- Produces: Extended documents table with `document_date` and `source_type` columns

- [ ] **Step 1: Create migration file**

Create `backend/migrations/0003_add_document_date_source_type.sql`:

```sql
-- Add document_date (publication date, distinct from effective_date)
-- Existing rows get NULL (unknown), new rows must provide explicit value
ALTER TABLE documents ADD COLUMN document_date date;

-- Add source_type to distinguish PDF, HTML, seed sources
-- Existing rows get 'seed' (backward compatible with current seed ingestion)
ALTER TABLE documents ADD COLUMN source_type text not null default 'seed';

-- Add index for source_type filtering
CREATE INDEX IF NOT EXISTS documents_source_type_idx ON documents(source_type);
```

- [ ] **Step 2: Update documents table in init.sql**

Add `document_date` and `source_type` columns to the CREATE TABLE statement in `0001_init.sql` for new deployments:

```sql
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  source_id text unique not null,
  title text not null,
  organization text not null,
  jurisdiction text not null check (jurisdiction in ('central','state')),
  state text,
  domain text not null,
  document_type text not null,
  source_url text not null,
  effective_date date,
  document_date date,
  verified_date date not null default current_date,
  document_hash text,
  source_type text not null default 'seed',
  created_at timestamptz not null default now()
);
```

- [ ] **Step 3: Update ingestion code to populate new fields**

Modify `ingestion/ingestion/ingest.py` to populate `document_date` and `source_type`:

```python
doc = supabase.table("documents").insert({
    "source_id": rec["source_id"], "title": rec["title"],
    "organization": rec["organization"], "domain": rec["domain"],
    "jurisdiction": rec["jurisdiction"], "state": rec.get("state"),
    "document_type": "seed", "source_url": rec["url"],
    "effective_date": rec.get("effective_date"),
    "document_date": rec.get("document_date"),
    "verified_date": rec["verified_date"],
    "source_type": "seed",  # Explicit value, not derived
}).execute().data[0]
```

- [ ] **Step 4: Write schema smoke test**

Create `backend/tests/test_schema_smoke.py`:

```python
def test_documents_has_document_date_column():
    """Verify document_date column exists in documents table."""
    from app.db import get_supabase
    supabase = get_supabase()
    result = supabase.table("documents").select("document_date").limit(1).execute()
    assert result.data is not None

def test_documents_has_source_type_column():
    """Verify source_type column exists in documents table."""
    from app.db import get_supabase
    supabase = get_supabase()
    result = supabase.table("documents").select("source_type").limit(1).execute()
    assert result.data is not None
```

- [ ] **Step 5: Run tests**

Run: `cd backend && python -m pytest tests/test_schema_smoke.py -v`
Expected: PASS (after migration is applied)

- [ ] **Step 6: Commit**

```bash
git add backend/migrations/0003_add_document_date_source_type.sql backend/migrations/0001_init.sql ingestion/ingestion/ingest.py backend/tests/test_schema_smoke.py
git commit -m "feat: add document_date and source_type columns to documents table"
```

---

### Task 2: Add State Value Normalization

**Files:**
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_state_normalization.py`

**Interfaces:**
- Consumes: Raw state values from YAML frontmatter or manifest
- Produces: Normalized (lowercase, trimmed) state values for DB insertion

- [ ] **Step 1: Write failing test**

Create `ingestion/tests/test_state_normalization.py`:

```python
from ingestion.ingestion.ingest import normalize_state

def test_normalize_state_lowercase():
    assert normalize_state("Gujarat") == "gujarat"

def test_normalize_state_trim():
    assert normalize_state("  Gujarat  ") == "gujarat"

def test_normalize_state_none():
    assert normalize_state(None) is None

def test_normalize_state_empty():
    assert normalize_state("") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_state_normalization.py -v`
Expected: FAIL with "import cannot be resolved" or "function not defined"

- [ ] **Step 3: Write minimal implementation**

Add to `ingestion/ingestion/ingest.py`:

```python
def normalize_state(state: str | None) -> str | None:
    """Normalize state value to lowercase trimmed string or None."""
    if not state or not isinstance(state, str):
        return None
    normalized = state.strip().lower()
    return normalized if normalized else None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_state_normalization.py -v`
Expected: PASS

- [ ] **Step 5: Update ingestion code to use normalization**

Modify `ingestion/ingestion/ingest.py` to use `normalize_state()`:

```python
doc = supabase.table("documents").insert({
    "source_id": rec["source_id"], "title": rec["title"],
    "organization": rec["organization"], "domain": rec["domain"],
    "jurisdiction": rec["jurisdiction"], "state": normalize_state(rec.get("state")),
    # ... rest of fields
}).execute().data[0]
```

- [ ] **Step 6: Run all ingestion tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add ingestion/ingestion/ingest.py ingestion/tests/test_state_normalization.py
git commit -m "feat: normalize state values to lowercase trimmed strings"
```

---

### Task 3: Add Manifest-Driven File Discovery with Fail-Loud

**Files:**
- Create: `ingestion/ingestion/manifest.py`
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_manifest.py`

**Interfaces:**
- Consumes: `corpus/manifests/mvp_sources.yaml`
- Produces: Validated file paths for ingestion (fails if any MVP file missing)

**Manifest Required Fields:**

```
Required and non-null:
    source_id, path, actual_title, issuing_organization,
    target_domain, jurisdiction, document_type, official_source_url,
    verified_date

Required key, nullable value:
    state, effective_date, document_date

Conditional:
    jurisdiction == "state" → state must be non-null/non-empty
    jurisdiction == "central" → state may be null
```

- [ ] **Step 1: Write failing test**

Create `ingestion/tests/test_manifest.py`:

```python
from pathlib import Path
from ingestion.ingestion.manifest import load_mvp_manifest, validate_manifest_files, validate_manifest_fields

MANIFEST_PATH = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"

def test_load_mvp_manifest_returns_list():
    sources = load_mvp_manifest(MANIFEST_PATH)
    assert isinstance(sources, list)
    assert len(sources) > 0

def test_load_mvp_manifest_has_required_fields():
    sources = load_mvp_manifest(MANIFEST_PATH)
    for source in sources:
        assert "source_id" in source
        assert "path" in source

def test_validate_manifest_files_all_exist():
    """All MVP manifest files must exist for production ingestion."""
    sources = load_mvp_manifest(MANIFEST_PATH)
    base_dir = MANIFEST_PATH.parent.parent
    valid, missing = validate_manifest_files(sources, base_dir)
    # For production ingestion, ALL files must exist
    assert len(missing) == 0, f"Missing MVP files: {[s.get('path') for s in missing]}"
    assert len(valid) == len(sources)

def test_validate_manifest_files_catches_missing():
    sources = [{"source_id": "test", "path": "nonexistent/file.pdf"}]
    valid, missing = validate_manifest_files(sources, Path("/tmp"))
    assert len(valid) == 0
    assert len(missing) == 1

def test_validate_manifest_fields_valid():
    """Verify manifest has all required fields for DB insertion."""
    sources = load_mvp_manifest(MANIFEST_PATH)
    for source in sources:
        errors = validate_manifest_fields(source)
        assert len(errors) == 0, f"Source {source.get('source_id')} missing fields: {errors}"

def test_validate_manifest_fields_catches_missing():
    source = {"source_id": "test"}  # Missing most required fields
    errors = validate_manifest_fields(source)
    assert len(errors) > 0
    assert "actual_title" in errors

def test_validate_manifest_fields_allows_nullable():
    """Verify nullable fields are allowed."""
    source = {
        "source_id": "test", "path": "test.pdf", "actual_title": "Test",
        "issuing_organization": "Org", "target_domain": "pacs",
        "jurisdiction": "central", "document_type": "pdf",
        "official_source_url": "https://test.com", "verified_date": "2026-08-27",
        "effective_date": None, "document_date": None, "state": None,
    }
    errors = validate_manifest_fields(source)
    assert len(errors) == 0

def test_validate_manifest_fields_requires_state_for_state_jurisdiction():
    """Verify state is required when jurisdiction is 'state'."""
    source = {
        "source_id": "test", "path": "test.pdf", "actual_title": "Test",
        "issuing_organization": "Org", "target_domain": "pacs",
        "jurisdiction": "state", "document_type": "pdf",
        "official_source_url": "https://test.com", "verified_date": "2026-08-27",
        "effective_date": None, "document_date": None, "state": None,
    }
    errors = validate_manifest_fields(source)
    assert "state" in errors

def test_hold_files_not_discovered():
    """Hold sources must never be discovered by ingestion."""
    from ingestion.ingestion.manifest import load_hold_manifest
    hold_path = MANIFEST_PATH.parent / "hold_sources.yaml"
    if hold_path.exists():
        hold_sources = load_hold_manifest(hold_path)
        mvp_sources = load_mvp_manifest(MANIFEST_PATH)
        mvp_ids = {s["source_id"] for s in mvp_sources}
        hold_ids = {s["source_id"] for s in hold_sources}
        # No overlap between MVP and hold sources
        assert len(mvp_ids & hold_ids) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_manifest.py -v`
Expected: FAIL with "import cannot be resolved"

- [ ] **Step 3: Write minimal implementation**

Create `ingestion/ingestion/manifest.py`:

```python
from pathlib import Path
import yaml


# Required fields that must be non-null
MANIFEST_REQUIRED_NON_NULL = [
    "source_id", "path", "actual_title", "issuing_organization",
    "target_domain", "jurisdiction", "document_type", "official_source_url",
    "verified_date",
]

# Required fields that may be null
MANIFEST_REQUIRED_KEYS = [
    "state", "effective_date", "document_date",
]


def load_mvp_manifest(manifest_path: Path) -> list[dict]:
    """Load MVP sources from YAML manifest file."""
    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("sources", [])


def load_hold_manifest(manifest_path: Path) -> list[dict]:
    """Load hold sources from YAML manifest file."""
    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("sources", [])


def validate_manifest_files(sources: list[dict], base_dir: Path) -> tuple[list[dict], list[dict]]:
    """Validate that manifest files exist on disk.
    
    Returns:
        (valid_sources, missing_sources) tuple
    """
    valid = []
    missing = []
    for source in sources:
        file_path = base_dir / source.get("path", "")
        if file_path.exists():
            valid.append(source)
        else:
            missing.append(source)
    return valid, missing


def validate_manifest_fields(source: dict) -> list[str]:
    """Validate that manifest source has all required fields for DB insertion.
    
    Returns:
        List of missing/invalid field names (empty if valid)
    """
    errors = []
    
    # Check required non-null fields
    for field in MANIFEST_REQUIRED_NON_NULL:
        if field not in source or source[field] is None:
            errors.append(field)
    
    # Check required keys (may be null)
    for field in MANIFEST_REQUIRED_KEYS:
        if field not in source:
            errors.append(field)
    
    # Conditional validation: state required when jurisdiction is "state"
    if source.get("jurisdiction") == "state":
        if not source.get("state"):
            errors.append("state")
    
    return errors
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_manifest.py -v`
Expected: PASS

- [ ] **Step 5: Add manifest-driven ingestion function with fail-loud**

Add to `ingestion/ingestion/ingest.py`:

```python
from ingestion.ingestion.manifest import load_mvp_manifest, validate_manifest_files, validate_manifest_fields


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
            # Extract PDF to markdown
            markdown_content = extract_pdf_to_markdown(file_path)
            markdown_content = validate_extraction(markdown_content, file_path.name)
            
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
            
            # Atomic replacement via RPC transaction
            doc_id = atomic_replace_document(
                supabase,
                source_id=source["source_id"],
                doc_data={
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
                },
                chunks_data=[
                    {"content": piece, "embedding": vector, "page": 0, "section": ""}
                    # page=0 means "page provenance unavailable in Phase 2A", not actual page 0
                    for piece, vector in zip(pieces, vectors)
                ]
            )
            
            succeeded.append(source["source_id"])
            print(f"Successfully ingested: {source['source_id']}")
            
        except Exception as e:
            failed.append({"source_id": source["source_id"], "error": str(e)})
            print(f"ERROR processing {source['source_id']}: {e}")
            continue
    
    print(f"\nSummary: {len(succeeded)} succeeded, {len(failed)} failed")
    if failed:
        print(f"Failed sources: {[f['source_id'] for f in failed]}")
    
    return {"succeeded": succeeded, "failed": failed}
```

- [ ] **Step 6: Write test for dry-run and preflight modes**

Add to `ingestion/tests/test_manifest.py`:

```python
def test_dry_run_does_not_write_to_db():
    from ingestion.ingestion.ingest import manifest_to_supabase
    from unittest.mock import MagicMock
    
    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()
    
    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase, dry_run=True)
    assert len(result["succeeded"]) > 0
    # Verify no DB writes occurred
    mock_supabase.table.return_value.insert.return_value.execute.assert_not_called()

def test_preflight_does_not_write_to_db():
    from ingestion.ingestion.ingest import manifest_to_supabase
    from unittest.mock import MagicMock
    
    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()
    
    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase, preflight=True)
    assert len(result["succeeded"]) > 0
    # Verify no DB writes occurred
    mock_supabase.table.return_value.insert.return_value.execute.assert_not_called()
    # Verify embeddings were called
    mock_embed.assert_called()

def test_dry_run_preflight_mutually_exclusive():
    from ingestion.ingestion.ingest import manifest_to_supabase
    from unittest.mock import MagicMock
    from pytest import raises
    
    mock_embed = MagicMock()
    mock_supabase = MagicMock()
    
    with raises(ValueError, match="mutually exclusive"):
        manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase, dry_run=True, preflight=True)
```

- [ ] **Step 7: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add ingestion/ingestion/manifest.py ingestion/ingestion/ingest.py ingestion/tests/test_manifest.py
git commit -m "feat: add manifest-driven file discovery with fail-loud, dry-run, and preflight modes"
```

---

### Task 4: Add Docling PDF Extraction

**Files:**
- Create: `ingestion/ingestion/pdf_extractor.py`
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_pdf_extractor.py`

**Interfaces:**
- Consumes: PDF file paths from MVP manifest
- Produces: Markdown text (page/section metadata deferred to P2)

**Note:** Docling API must be verified against installed version before implementation.

- [ ] **Step 1: Check Docling availability and API**

Run: `pip list | grep docling`
Run: `python -c "from docling.document_converter import DocumentConverter; print('Docling available')"`
If not installed: `pip install docling`

- [ ] **Step 2: Write failing test**

Create `ingestion/tests/test_pdf_extractor.py`:

```python
from pathlib import Path
from ingestion.ingestion.pdf_extractor import extract_pdf_to_markdown

SAMPLE_PDF = Path(__file__).parent.parent.parent / "corpus" / "seeds" / "operational_guidelines_pmfby.pdf"

def test_extract_pdf_returns_string():
    if not SAMPLE_PDF.exists():
        import pytest
        pytest.skip("Sample PDF not available")
    result = extract_pdf_to_markdown(SAMPLE_PDF)
    assert isinstance(result, str)
    assert len(result) > 0

def test_extract_pdf_nonexistent_raises():
    from pytest import raises
    with raises(FileNotFoundError):
        extract_pdf_to_markdown(Path("/nonexistent/file.pdf"))

def test_mvp_files_exist():
    """Verify all MVP PDF files exist before running extraction tests."""
    manifest_path = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"
    from ingestion.ingestion.manifest import load_mvp_manifest, validate_manifest_files
    sources = load_mvp_manifest(manifest_path)
    base_dir = manifest_path.parent.parent
    valid, missing = validate_manifest_files(sources, base_dir)
    assert len(missing) == 0, f"MVP files missing: {[s.get('path') for s in missing]}"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_pdf_extractor.py -v`
Expected: FAIL with "import cannot be resolved"

- [ ] **Step 4: Write minimal implementation**

Create `ingestion/ingestion/pdf_extractor.py`:

```python
from pathlib import Path
from docling.document_converter import DocumentConverter


def extract_pdf_to_markdown(pdf_path: Path) -> str:
    """Extract text from PDF using Docling and return as markdown.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as markdown string
        
    Raises:
        FileNotFoundError: If pdf_path does not exist
        ValueError: If extraction fails
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        return result.document.export_to_markdown()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF {pdf_path}: {e}")
```

**Note:** Page/section metadata is deferred to P2. The extraction returns markdown only.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_pdf_extractor.py -v`
Expected: PASS (if Docling is installed and sample PDF exists)

- [ ] **Step 6: Integrate PDF extraction into manifest ingestion**

Modify `ingestion/ingestion/ingest.py` to use PDF extraction:

```python
from ingestion.ingestion.pdf_extractor import extract_pdf_to_markdown


def manifest_to_supabase(manifest_path: Path, embed_texts, supabase, dry_run: bool = False, preflight: bool = False) -> dict:
    """Ingest PDF sources from MVP manifest."""
    if dry_run and preflight:
        raise ValueError("dry_run and preflight are mutually exclusive")
    
    sources = load_mvp_manifest(manifest_path)
    base_dir = manifest_path.parent.parent
    
    # FAIL entire run if any MVP file missing
    valid_sources, missing_sources = validate_manifest_files(sources, base_dir)
    if missing_sources:
        raise ValueError(f"Missing MVP files: {[s.get('path') for s in missing_sources]}")
    
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
            # Extract PDF to markdown
            markdown_content = extract_pdf_to_markdown(file_path)
            markdown_content = validate_extraction(markdown_content, file_path.name)
            
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
            
            # Atomic replacement via RPC transaction
            doc_id = atomic_replace_document(
                supabase,
                source_id=source["source_id"],
                doc_data={
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
                },
                chunks_data=[
                    {"content": piece, "embedding": vector, "page": 0, "section": ""}
                    # page=0 means "page provenance unavailable in Phase 2A", not actual page 0
                    for piece, vector in zip(pieces, vectors)
                ]
            )
            
            succeeded.append(source["source_id"])
            print(f"Successfully ingested: {source['source_id']}")
            
        except Exception as e:
            failed.append({"source_id": source["source_id"], "error": str(e)})
            print(f"ERROR processing {source['source_id']}: {e}")
            continue
    
    print(f"\nSummary: {len(succeeded)} succeeded, {len(failed)} failed")
    if failed:
        print(f"Failed sources: {[f['source_id'] for f in failed]}")
    
    return {"succeeded": succeeded, "failed": failed}
```

- [ ] **Step 7: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add ingestion/ingestion/pdf_extractor.py ingestion/ingestion/ingest.py ingestion/tests/test_pdf_extractor.py
git commit -m "feat: add Docling PDF extraction for MVP sources"
```

---

### Task 5: Add Per-File Error Isolation

**Files:**
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_error_isolation.py`

**Interfaces:**
- Consumes: File processing loop
- Produces: Graceful handling of individual file failures

- [ ] **Step 1: Write failing test**

Create `ingestion/tests/test_error_isolation.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch
from ingestion.ingestion.ingest import manifest_to_supabase

MANIFEST_PATH = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"

def test_per_file_error_isolation():
    """Verify that one bad file doesn't kill the entire run."""
    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()
    
    # Mock extract_pdf_to_markdown to fail on first call, succeed on second
    call_count = [0]
    def mock_extract(path):
        call_count[0] += 1
        if call_count[0] == 1:
            raise ValueError("Simulated extraction failure")
        return "# Test Content\n\nThis is test content."
    
    with patch("ingestion.ingestion.ingest.extract_pdf_to_markdown", mock_extract):
        # Should not raise, should continue processing
        result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)
        # At least one file should have been processed (the second one)
        assert len(result["succeeded"]) > 0
        assert len(result["failed"]) == 1
        # Verify embedding was called for successful file
        mock_embed.assert_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_error_isolation.py -v`
Expected: FAIL (current implementation may not handle errors gracefully)

- [ ] **Step 3: Verify manifest_to_supabase already has try/except**

The implementation in Task 4 already includes try/except around each file processing. Verify this works correctly.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_error_isolation.py -v`
Expected: PASS (if Task 4 implementation is correct)

- [ ] **Step 5: Add logging for failures**

Modify `ingestion/ingestion/ingest.py` to add structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# In manifest_to_supabase, replace print statements with logger:
logger.warning(f"WARNING: {len(missing_sources)} files missing:")
logger.error(f"ERROR processing {source['source_id']}: {e}")
logger.info(f"Successfully ingested: {source['source_id']}")
```

- [ ] **Step 6: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add ingestion/ingestion/ingest.py ingestion/tests/test_error_isolation.py
git commit -m "feat: add per-file error isolation with structured logging"
```

---

### Task 6: Add Extraction Validation (Fail-Loud)

**Files:**
- Modify: `ingestion/ingestion/pdf_extractor.py`
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_extraction_validation.py`

**Interfaces:**
- Consumes: Extracted markdown content
- Produces: Validated content or clear error messages

- [ ] **Step 1: Write failing test**

Create `ingestion/tests/test_extraction_validation.py`:

```python
from ingestion.ingestion.pdf_extractor import validate_extraction

def test_validate_extraction_empty_raises():
    from pytest import raises
    with raises(ValueError, match="empty"):
        validate_extraction("", "test.pdf")

def test_validate_extraction_too_short_raises():
    from pytest import raises
    with raises(ValueError, match="too short"):
        validate_extraction("Hi", "test.pdf")

def test_validate_extraction_valid():
    # Should not raise
    validate_extraction("# Title\n\n" + "x" * 100, "test.pdf")

def test_validate_extraction_whitespace_only_raises():
    from pytest import raises
    with raises(ValueError, match="empty"):
        validate_extraction("   \n  \n  ", "test.pdf")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_extraction_validation.py -v`
Expected: FAIL with "import cannot be resolved"

- [ ] **Step 3: Write minimal implementation**

Add to `ingestion/ingestion/pdf_extractor.py`:

```python
def validate_extraction(content: str, filename: str, min_length: int = 50) -> str:
    """Validate extracted content is usable.
    
    Args:
        content: Extracted markdown content
        filename: Original filename for error messages
        min_length: Minimum acceptable content length
        
    Returns:
        Validated content
        
    Raises:
        ValueError: If content is empty, too short, or whitespace-only
    """
    if not content or not content.strip():
        raise ValueError(f"Extraction from {filename} produced empty content")
    
    if len(content.strip()) < min_length:
        raise ValueError(f"Extraction from {filename} too short ({len(content.strip())} chars < {min_length})")
    
    return content
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_extraction_validation.py -v`
Expected: PASS

- [ ] **Step 5: Integrate validation into extraction flow**

Modify `ingestion/ingestion/ingest.py` to validate extraction:

```python
# In manifest_to_supabase, after extraction:
markdown_content = extract_pdf_to_markdown(file_path)
markdown_content = validate_extraction(markdown_content, file_path.name)
```

- [ ] **Step 6: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add ingestion/ingestion/pdf_extractor.py ingestion/ingestion/ingest.py ingestion/tests/test_extraction_validation.py
git commit -m "feat: add extraction validation with fail-loud behavior"
```

---

### Task 7: Add Gemini Retry/Backoff

**Files:**
- Modify: `backend/app/providers/embeddings.py`
- Create: `backend/tests/test_embedding_retry.py`

**Interfaces:**
- Consumes: Gemini API errors (429, 5xx)
- Produces: Retried embedding results with exponential backoff

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_embedding_retry.py`:

```python
from unittest.mock import patch, MagicMock
import httpx
from app.providers.embeddings import GeminiEmbeddingProvider
from app.config import Settings

def test_retry_on_rate_limit():
    """Verify retry logic handles 429 errors."""
    settings = Settings(
        groq_api_key="test",
        gemini_api_key="test",
        supabase_url="http://test",
        supabase_service_key="test"
    )
    provider = GeminiEmbeddingProvider(settings)
    
    call_count = [0]
    def mock_post(self, url, **kwargs):
        call_count[0] += 1
        if call_count[0] < 3:
            # First two calls fail with 429
            response = MagicMock()
            response.status_code = 429
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "rate limited", request=MagicMock(), response=response
            )
            return response
        # Third call succeeds
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        response.json.return_value = {"embedding": {"values": [0.1] * 768}}
        return response
    
    with patch("httpx.Client.post", mock_post):
        result = provider.embed_texts(["test text"])
        assert len(result) == 1
        assert len(result[0]) == 768
        assert call_count[0] == 3  # 3 total attempts / 2 retries
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_embedding_retry.py -v`
Expected: FAIL (no retry logic currently)

- [ ] **Step 3: Write minimal implementation**

Modify `backend/app/providers/embeddings.py`:

```python
import time
from functools import lru_cache
import httpx
from app.config import EMBED_DIMS, REQUEST_TIMEOUT_S, Settings, get_settings


class GeminiEmbeddingProvider:
    def __init__(self, settings: Settings):
        self._key = settings.gemini_api_key
        self._endpoint = ("https://generativelanguage.googleapis.com/v1beta/models/"
                          f"{settings.embed_model}:embedContent")
        self._max_attempts = 3  # 3 total attempts / 2 retries
        self._base_delay = 1.0  # seconds

    def _embed_single(self, text: str, client: httpx.Client) -> list[float]:
        """Embed a single text with retry logic."""
        last_exception = None
        
        for attempt in range(self._max_attempts):
            try:
                r = client.post(f"{self._endpoint}?key={self._key}", json={
                    "content": {"parts": [{"text": text}]},
                    "output_dimensionality": EMBED_DIMS})
                r.raise_for_status()
                values = r.json()["embedding"]["values"]
                if len(values) != EMBED_DIMS:
                    raise ValueError(f"unexpected dims {len(values)}")
                return values
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                # Check if retryable
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code not in (429, 500, 502, 503, 504):
                    raise  # Non-retryable error
                if attempt < self._max_attempts - 1:
                    delay = self._base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
        
        raise last_exception

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        with httpx.Client(timeout=REQUEST_TIMEOUT_S) as client:
            for text in texts:
                values = self._embed_single(text, client)
                out.append(values)
        return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_embedding_retry.py -v`
Expected: PASS

- [ ] **Step 5: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/providers/embeddings.py backend/tests/test_embedding_retry.py
git commit -m "feat: add retry with exponential backoff for embedding provider"
```

---

### Task 8: Fix Citation Verification Bug

**Files:**
- Modify: `backend/app/routes/chat.py`
- Modify: `backend/app/generation.py`
- Create: `backend/tests/test_citation_fix.py`

**Interfaces:**
- Consumes: LLM answer text with `[chunk:ID]` markers
- Produces: Validated answer with only valid citations

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_citation_fix.py`:

```python
from app.routes.chat import _citations_from
from app.retrieval import RetrievedChunk
from app.generation import verify_citations

def test_citations_from_filters_invalid():
    chunks = [
        RetrievedChunk(chunk_id="abc12345", title="T", page=1, section="S",
                       content="C", similarity=0.9, source_url="https://x",
                       domain="pacs", jurisdiction="central", state=None),
    ]
    answer = "This is about PACS [chunk:abc12345] but also [chunk:deadbeef]"
    citations = _citations_from(answer, chunks)
    # Should only include valid citation
    assert len(citations) == 1
    assert citations[0]["title"] == "T"

def test_verify_citations_rejects_invalid():
    """Verify that invalid citations cause rejection."""
    chunks = [
        RetrievedChunk(chunk_id="abc12345", title="T", page=1, section="S",
                       content="C", similarity=0.9, source_url="https://x",
                       domain="pacs", jurisdiction="central", state=None),
    ]
    answer = "This is about PACS [chunk:deadbeef]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 0
    assert len(invalid) == 1

def test_verify_citations_accepts_valid():
    """Verify that valid citations are accepted."""
    chunks = [
        RetrievedChunk(chunk_id="abc12345", title="T", page=1, section="S",
                       content="C", similarity=0.9, source_url="https://x",
                       domain="pacs", jurisdiction="central", state=None),
    ]
    answer = "This is about PACS [chunk:abc12345]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 1
    assert len(invalid) == 0

def test_verify_citations_rejects_mixed():
    """Verify that mixed valid/invalid citations cause rejection."""
    chunks = [
        RetrievedChunk(chunk_id="abc12345", title="T", page=1, section="S",
                       content="C", similarity=0.9, source_url="https://x",
                       domain="pacs", jurisdiction="central", state=None),
    ]
    answer = "PACS [chunk:abc12345] and also [chunk:deadbeef]"
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    assert len(valid) == 1
    assert len(invalid) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_citation_fix.py -v`
Expected: FAIL (current implementation may have issues)

- [ ] **Step 3: Trace actual call path and fix**

The issue is that `chat.py` calls `grounded_answer()` which bypasses `verify_citations()`. The fix is to ensure citation verification happens before returning the answer.

Modify `backend/app/routes/chat.py` to validate citations before returning:

```python
# In chat() function, after getting answer:
answer = grounded_answer(GroqLLMProvider(settings),
                         GeminiLLMProvider(settings), SYSTEM_PROMPT, prompt)

# Validate citations before returning
valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
if invalid:
    # Invalid citations found - abstain
    return _abstain(lang, "invalid_citations")

citations = _citations_from(answer, chunks)
```

- [ ] **Step 4: Add route-level citation verification test**

Create `backend/tests/test_chat_citation_route.py`:

```python
from unittest.mock import MagicMock, patch
from app.routes.chat import chat, ChatRequest

def test_chat_abstains_on_invalid_citations():
    """Verify chat route abstains when LLM produces invalid citations."""
    # This test requires mocking the LLM to return invalid citations
    # and verifying the route returns abstained=True
    # Implementation depends on actual LLM mock behavior
    pass  # Placeholder for actual implementation
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_citation_fix.py -v`
Expected: PASS

- [ ] **Step 6: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/routes/chat.py backend/app/generation.py backend/tests/test_citation_fix.py backend/tests/test_chat_citation_route.py
git commit -m "fix: validate citations before returning answer in chat route"
```

---

### Task 9: Fix Eval Source-ID Bug

**Files:**
- Modify: `eval/run_retrieval_eval.py`
- Create: `eval/tests/test_eval_fix.py`

**Interfaces:**
- Consumes: Supabase RPC response
- Produces: Correctly extracted document_id with source_id lookup

- [ ] **Step 1: Write failing test**

Create `eval/tests/test_eval_fix.py`:

```python
def test_retrieve_live_extracts_document_id():
    """Verify retrieve_live extracts document_id correctly."""
    from eval.run_retrieval_eval import retrieve_live
    from unittest.mock import patch, MagicMock
    
    mock_response = MagicMock()
    mock_response.data = [
        {"chunk_id": "abc", "document_id": "doc123", "title": "Test"}
    ]
    
    mock_client = MagicMock()
    mock_client.rpc.return_value.execute.return_value = mock_response
    
    with patch("eval.run_retrieval_eval.create_client", return_value=mock_client):
        with patch("eval.run_retrieval_eval.get_embedding_provider") as mock_embed:
            mock_embed.return_value.embed_texts.return_value = [[0.1] * 768]
            result = retrieve_live("test question", "pacs", None)
            # Should return document_id, not source_id
            assert result[0]["document_id"] == "doc123"
            # source_id should be looked up separately or not returned
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd eval && python -m pytest tests/test_eval_fix.py -v`
Expected: FAIL (current implementation extracts wrong field)

- [ ] **Step 3: Fix the bug**

Modify `eval/run_retrieval_eval.py:62`:

```python
# Change from:
return [{"chunk_id": str(r["chunk_id"]), "source_id": r.get("source_id", "")} for r in rows]

# To:
return [{"chunk_id": str(r["chunk_id"]), "document_id": str(r.get("document_id", ""))} for r in rows]
```

- [ ] **Step 4: Update gold case comparison to use document_id**

The evaluator needs to compare gold `source_id` against the actual document's `source_id`. This requires a join or separate lookup. For now, return `document_id` and update the comparison logic.

- [ ] **Step 5: Add test for final gold-vs-live comparison**

Create `eval/tests/test_gold_comparison.py`:

```python
def test_gold_comparison_uses_source_id():
    """Verify gold case comparison uses source_id, not document_id."""
    # This test should verify the complete pipeline:
    # retrieval result → document_id → documents.id lookup → source_id → compare against gold
    # Implementation depends on actual evaluation harness
    pass  # Placeholder for actual implementation
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd eval && python -m pytest tests/test_eval_fix.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add eval/run_retrieval_eval.py eval/tests/test_eval_fix.py eval/tests/test_gold_comparison.py
git commit -m "fix: extract document_id correctly in eval retrieval"
```

---

### Task 10: Add Atomic DB Replacement via RPC Transaction

**Files:**
- Create: `backend/migrations/0004_atomic_replace_document.sql`
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_atomic_replacement.py`
- Create: `ingestion/tests/test_rpc_atomicity.py` (integration test)

**Interfaces:**
- Consumes: Document and chunk data
- Produces: Atomic replacement in Supabase via PostgreSQL RPC transaction

**Note:** The RPC uses `jsonb` (not `jsonb[]`) for chunk data, with `jsonb_array_elements()` in the SQL function.

- [ ] **Step 1: Create migration file**

Create `backend/migrations/0004_atomic_replace_document.sql`:

```sql
CREATE OR REPLACE FUNCTION atomic_replace_document(
  p_source_id text,
  p_doc_data jsonb,
  p_chunks_data jsonb  -- JSON array, not PostgreSQL array
)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_doc_id uuid;
  v_chunk jsonb;
BEGIN
  -- Delete old document (cascades to chunks)
  DELETE FROM documents WHERE source_id = p_source_id;
  
  -- Insert new document
  INSERT INTO documents (source_id, title, organization, jurisdiction, state, 
                         domain, document_type, source_url, effective_date, 
                         document_date, verified_date, source_type)
  VALUES (
    p_source_id,
    p_doc_data->>'title',
    p_doc_data->>'organization',
    p_doc_data->>'jurisdiction',
    p_doc_data->>'state',
    p_doc_data->>'domain',
    p_doc_data->>'document_type',
    p_doc_data->>'source_url',
    (p_doc_data->>'effective_date')::date,
    (p_doc_data->>'document_date')::date,
    (p_doc_data->>'verified_date')::date,
    p_doc_data->>'source_type'
  )
  RETURNING id INTO v_doc_id;
  
  -- Insert chunks from JSON array
  FOR v_chunk IN
    SELECT value
    FROM jsonb_array_elements(p_chunks_data)
  LOOP
    INSERT INTO chunks (document_id, page, section, content, embedding)
    VALUES (
      v_doc_id,
      (v_chunk->>'page')::int,
      v_chunk->>'section',
      v_chunk->>'content',
      (v_chunk->>'embedding')::vector(768)
    );
  END LOOP;
  
  RETURN v_doc_id;
END;
$$;
```

- [ ] **Step 2: Write failing test**

Create `ingestion/tests/test_atomic_replacement.py`:

```python
from unittest.mock import MagicMock, patch
from ingestion.ingestion.ingest import atomic_replace_document

def test_atomic_replace_uses_rpc():
    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.return_value = MagicMock(data="doc123")
    
    doc_id = atomic_replace_document(
        mock_supabase,
        source_id="test",
        doc_data={"title": "Test", "organization": "Org"},
        chunks_data=[{"content": "chunk1", "embedding": [0.1] * 768}]
    )
    
    # Verify RPC was called
    mock_supabase.rpc.assert_called_once()
    assert doc_id == "doc123"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_atomic_replacement.py -v`
Expected: FAIL with "atomic_replace_document not defined"

- [ ] **Step 4: Write minimal implementation**

Add to `ingestion/ingestion/ingest.py`:

```python
def atomic_replace_document(supabase, source_id: str, doc_data: dict, chunks_data: list[dict]) -> str:
    """Atomically replace a document and its chunks via RPC transaction.
    
    This uses a PostgreSQL function to ensure atomicity:
    - If any step fails, the entire transaction rolls back
    - Existing valid documents are protected by transaction rollback if replacement fails
    
    Args:
        supabase: Supabase client
        source_id: Document source ID
        doc_data: Document metadata dictionary
        chunks_data: List of chunk dictionaries with 'content' and 'embedding'
        
    Returns:
        Document ID of the new document
    """
    # Convert embeddings to strings for JSON serialization
    chunks_for_rpc = []
    for chunk in chunks_data:
        chunks_for_rpc.append({
            "content": chunk["content"],
            "embedding": str(chunk["embedding"]),  # Vector as string
            "page": chunk.get("page", 0),
            "section": chunk.get("section", ""),
        })
    
    result = supabase.rpc(
        "atomic_replace_document",
        {
            "p_source_id": source_id,
            "p_doc_data": doc_data,
            "p_chunks_data": chunks_for_rpc,  # JSON array
        }
    ).execute()
    
    return result.data
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_atomic_replacement.py -v`
Expected: PASS

- [ ] **Step 6: Add integration test for RPC atomicity**

Create `ingestion/tests/test_rpc_atomicity.py`:

```python
import pytest
from pathlib import Path

@pytest.mark.integration
def test_rpc_atomicity_rollback():
    """Test that RPC transaction rolls back on failure."""
    from app.db import get_supabase
    from ingestion.ingestion.ingest import atomic_replace_document
    
    supabase = get_supabase()
    
    # Insert a test document first
    test_doc = supabase.table("documents").insert({
        "source_id": "test_rollback_doc",
        "title": "Test Rollback",
        "organization": "Test",
        "jurisdiction": "central",
        "domain": "test",
        "document_type": "test",
        "source_url": "https://test.com",
        "verified_date": "2026-08-27",
        "source_type": "test",
    }).execute().data[0]
    
    original_doc_id = test_doc["id"]
    
    # Insert a chunk
    supabase.table("chunks").insert({
        "document_id": original_doc_id,
        "page": 1,
        "section": "Test",
        "content": "Test content",
        "embedding": [0.1] * 768,
    }).execute()
    
    # Try to replace with invalid data (should fail after deletion)
    # Use invalid vector dimension to force failure
    try:
        atomic_replace_document(
            supabase,
            source_id="test_rollback_doc",
            doc_data={"title": "Test Rollback"},
            chunks_data=[{"content": "chunk1", "embedding": [0.1] * 100}]  # Wrong dimension
        )
    except Exception:
        pass
    
    # Verify original document still exists (transaction rolled back)
    result = supabase.table("documents").select("id").eq("source_id", "test_rollback_doc").execute()
    assert len(result.data) == 1
    assert result.data[0]["id"] == original_doc_id
    
    # Verify original chunks still exist
    chunks = supabase.table("chunks").select("*").eq("document_id", original_doc_id).execute()
    assert len(chunks.data) == 1
    
    # Cleanup
    supabase.table("chunks").delete().eq("document_id", original_doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_rollback_doc").execute()
```

- [ ] **Step 7: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/migrations/0004_atomic_replace_document.sql ingestion/ingestion/ingest.py ingestion/tests/test_atomic_replacement.py ingestion/tests/test_rpc_atomicity.py
git commit -m "feat: add atomic document replacement via PostgreSQL RPC transaction"
```

---

### Task 11: Add Corpus Safety Invariant

**Files:**
- Modify: `ingestion/ingestion/ingest.py`
- Create: `ingestion/tests/test_corpus_safety.py`

**Interfaces:**
- Consumes: Ingestion pipeline
- Produces: Guaranteed preservation of existing valid documents

- [ ] **Step 1: Write failing test**

Create `ingestion/tests/test_corpus_safety.py`:

```python
import pytest
from pathlib import Path

@pytest.mark.integration
def test_existing_document_not_deleted_on_failure():
    """Verify existing document is not deleted if new ingestion fails."""
    from app.db import get_supabase
    from ingestion.ingestion.ingest import atomic_replace_document
    
    supabase = get_supabase()
    
    # Insert a test document with chunks
    test_doc = supabase.table("documents").insert({
        "source_id": "test_safety_doc",
        "title": "Test Safety",
        "organization": "Test",
        "jurisdiction": "central",
        "domain": "test",
        "document_type": "test",
        "source_url": "https://test.com",
        "verified_date": "2026-08-27",
        "source_type": "test",
    }).execute().data[0]
    
    original_doc_id = test_doc["id"]
    
    # Insert a chunk
    supabase.table("chunks").insert({
        "document_id": original_doc_id,
        "page": 1,
        "section": "Test",
        "content": "Test content",
        "embedding": [0.1] * 768,
    }).execute()
    
    # Try to replace with invalid data (should fail after deletion)
    # Use invalid vector dimension to force failure
    try:
        atomic_replace_document(
            supabase,
            source_id="test_safety_doc",
            doc_data={"title": "Test Safety"},
            chunks_data=[{"content": "chunk1", "embedding": [0.1] * 100}]  # Wrong dimension
        )
    except Exception:
        pass
    
    # Verify original document still exists (transaction rolled back)
    result = supabase.table("documents").select("id").eq("source_id", "test_safety_doc").execute()
    assert len(result.data) == 1
    assert result.data[0]["id"] == original_doc_id
    
    # Verify original chunks still exist
    chunks = supabase.table("chunks").select("*").eq("document_id", original_doc_id).execute()
    assert len(chunks.data) == 1
    
    # Cleanup
    supabase.table("chunks").delete().eq("document_id", original_doc_id).execute()
    supabase.table("documents").delete().eq("source_id", "test_safety_doc").execute()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ingestion && python -m pytest tests/test_corpus_safety.py -v`
Expected: FAIL (test may need adjustment based on current implementation)

- [ ] **Step 3: Verify RPC function handles rollback**

The PostgreSQL RPC function uses a transaction, so if any step fails, the entire transaction rolls back. This means existing documents are not deleted until the new data is successfully inserted.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ingestion && python -m pytest tests/test_corpus_safety.py -v`
Expected: PASS

- [ ] **Step 5: Run all tests**

Run: `cd ingestion && python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ingestion/ingestion/ingest.py ingestion/tests/test_corpus_safety.py
git commit -m "feat: add corpus safety invariant via RPC transaction rollback"
```

---

### Task 12: Integration Test with Real MVP PDF

**Files:**
- Create: `ingestion/tests/test_mvp_integration.py`

**Interfaces:**
- Consumes: Real MVP PDF files
- Produces: Verified ingestion into Supabase

- [ ] **Step 1: Write integration test**

Create `ingestion/tests/test_mvp_integration.py`:

```python
import pytest
from pathlib import Path
from ingestion.ingestion.ingest import manifest_to_supabase

MANIFEST_PATH = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"

@pytest.mark.integration
def test_mvp_ingestion_with_real_pdfs():
    """Integration test: ingest real MVP PDFs into Supabase.
    
    This test requires:
    1. Real MVP PDF files in corpus/seeds/
    2. Supabase connection (SUPABASE_URL, SUPABASE_SERVICE_KEY env vars)
    3. Gemini API key (GEMINI_API_KEY env var)
    """
    from app.providers.embeddings import get_embedding_provider
    from app.db import get_supabase
    from ingestion.ingestion.manifest import load_mvp_manifest, load_hold_manifest
    
    embed_provider = get_embedding_provider()
    supabase = get_supabase()
    
    result = manifest_to_supabase(
        MANIFEST_PATH,
        embed_provider.embed_texts,
        supabase
    )
    
    # Verify expected number of sources
    sources = load_mvp_manifest(MANIFEST_PATH)
    expected_ids = {s["source_id"] for s in sources}
    assert len(expected_ids) == 5, f"Expected 5 MVP sources, got {len(expected_ids)}"
    
    # Should have ingested all MVP documents
    assert len(result["succeeded"]) == len(expected_ids), f"Expected {len(expected_ids)} succeeded, got {len(result['succeeded'])}"
    assert len(result["failed"]) == 0, f"Expected 0 failed, got {len(result['failed'])}"
    
    # Verify all expected MVP source IDs exist
    docs = supabase.table("documents").select("id, source_id").execute().data
    actual_ids = {d["source_id"] for d in docs}
    
    # Verify all expected MVP IDs are present
    mvp_ids_present = expected_ids & actual_ids
    assert mvp_ids_present == expected_ids, f"Missing MVP sources: {expected_ids - actual_ids}"
    
    # Verify no hold source IDs exist
    hold_path = MANIFEST_PATH.parent / "hold_sources.yaml"
    if hold_path.exists():
        hold_sources = load_hold_manifest(hold_path)
        hold_ids = {s["source_id"] for s in hold_sources}
        assert len(actual_ids & hold_ids) == 0, f"Hold sources found: {actual_ids & hold_ids}"
    
    # Verify every MVP document has chunks
    for doc in docs:
        if doc["source_id"] in expected_ids:
            chunks = supabase.table("chunks").select("*").eq("document_id", doc["id"]).execute().data
            assert len(chunks) > 0, f"Document {doc['source_id']} has no chunks"
            
            # Verify embedding dimension
            assert len(chunks[0]["embedding"]) == 768
            
            # Verify no empty chunks
            for chunk in chunks:
                assert chunk["content"].strip(), f"Empty chunk in {doc['source_id']}"
```

- [ ] **Step 2: Mark test as integration (skip in normal runs)**

The test is marked with `@pytest.mark.integration` and will be skipped unless `--run-integration` is passed.

- [ ] **Step 3: Run unit tests only (should pass)**

Run: `cd ingestion && python -m pytest tests/ -v -k "not integration"`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add ingestion/tests/test_mvp_integration.py
git commit -m "test: add integration test for MVP PDF ingestion"
```

---

### Task 13: Update Gold Case Source IDs

**Files:**
- Modify: `eval/gold_cases.yaml`

**Interfaces:**
- Consumes: MVP manifest source_ids
- Produces: Aligned gold case source_ids (only justified mappings)

**Note:** This task should be performed AFTER successful corpus ingestion (Task 12), not before.

- [ ] **Step 1: Verify corpus ingestion succeeded**

Run Task 12 integration test first to ensure MVP documents are in Supabase.

- [ ] **Step 2: Read current gold case source IDs**

Extract unique source_ids from `eval/gold_cases.yaml`:
- `gujarat_cooperative_act`
- `ministry_cooperation`
- `model_pacs_bylaws`
- `ministry_pacs`
- `ministry_pacs_schemes`
- `pmfby_guidelines`
- `pmfby_faq`
- `rbi_financial_literacy`
- `pmjdy_financial_literacy`

- [ ] **Step 3: Read MVP manifest source IDs**

Extract source_ids from `corpus/manifests/mvp_sources.yaml`:
- `pacs_model_bylaws_2023`
- `pacs_computerization_guidelines`
- `pacs_computerization_corrigendum_2023_06_12`
- `pmfby_operational_guidelines`
- `nsfi_2025_30`

- [ ] **Step 4: Create ID mapping (only justified)**

Map gold case IDs to MVP manifest IDs where conceptually equivalent:
- `model_pacs_bylaws` → `pacs_model_bylaws_2023`
- `pmfby_guidelines` → `pmfby_operational_guidelines`

Other gold case IDs have no MVP equivalent. These should be marked as unanswerable until their sources exist.

- [ ] **Step 5: Update gold_cases.yaml**

Replace source_ids in `eval/gold_cases.yaml`:
- `model_pacs_bylaws` → `pacs_model_bylaws_2023`
- `pmfby_guidelines` → `pmfby_operational_guidelines`

For cases referencing sources not in MVP:
- Mark as `answerable: false`
- Clear `relevant_source_ids`
- Clear `relevant_chunk_ids`

- [ ] **Step 6: Validate gold case structure**

Verify all answerable cases have non-empty `relevant_source_ids` that exist in MVP manifest.

- [ ] **Step 7: Commit**

```bash
git add eval/gold_cases.yaml
git commit -m "fix: align gold case source IDs with MVP manifest and defer unanswerable cases"
```

---

### Task 14: Final Verification

**Files:**
- None (verification only)

**Interfaces:**
- Consumes: All implemented changes
- Produces: Verified working ingestion pipeline

- [ ] **Step 1: Run all unit tests**

Run: `cd backend && python -m pytest tests/ -v && cd ../ingestion && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 2: Verify schema smoke test**

Run: `cd backend && python -m pytest tests/test_schema_smoke.py -v`
Expected: PASS

- [ ] **Step 3: Verify manifest loading**

Run: `cd ingestion && python -m pytest tests/test_manifest.py -v`
Expected: PASS

- [ ] **Step 4: Verify PDF extraction (if Docling installed)**

Run: `cd ingestion && python -m pytest tests/test_pdf_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Verify error isolation**

Run: `cd ingestion && python -m pytest tests/test_error_isolation.py -v`
Expected: PASS

- [ ] **Step 6: Verify retry logic**

Run: `cd backend && python -m pytest tests/test_embedding_retry.py -v`
Expected: PASS

- [ ] **Step 7: Verify citation fix**

Run: `cd backend && python -m pytest tests/test_citation_fix.py -v`
Expected: PASS

- [ ] **Step 8: Verify eval fix**

Run: `cd eval && python -m pytest tests/test_eval_fix.py -v`
Expected: PASS

- [ ] **Step 9: Verify atomic replacement**

Run: `cd ingestion && python -m pytest tests/test_atomic_replacement.py -v`
Expected: PASS

- [ ] **Step 10: Verify corpus safety**

Run: `cd ingestion && python -m pytest tests/test_corpus_safety.py -v`
Expected: PASS

- [ ] **Step 11: Run full test suite including foundation gate**

Run: `python -m pytest backend/tests/ ingestion/tests/ eval/tests/ -v`
Expected: All PASS

- [ ] **Step 12: Run existing foundation/security/corpus validators**

Run: `python -m pytest backend/tests/test_contract.py backend/tests/test_health.py backend/tests/test_domains.py -v`
Expected: All PASS

- [ ] **Step 13: Commit final state**

```bash
git add -A
git commit -m "feat: Phase 2A MVP ingestion pipeline complete"
```
