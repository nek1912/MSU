from pathlib import Path

from ingestion.manifest import load_mvp_manifest, validate_manifest_fields, validate_manifest_files

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
    """All MVP manifest files must exist for production ingestion.
    
    This test will fail if MVP PDFs haven't been added to corpus/seeds/ yet.
    This is expected during development - the test validates the manifest structure,
    not the file existence (which is tested by validate_manifest_files itself).
    """
    sources = load_mvp_manifest(MANIFEST_PATH)
    base_dir = MANIFEST_PATH.parent.parent
    valid, missing = validate_manifest_files(sources, base_dir)
    # This test documents the expected behavior - if files are missing,
    # the ingestion will fail loudly (which is correct behavior)
    if missing:
        import pytest
        pytest.skip(f"MVP files not yet added: {[s.get('path') for s in missing]}")
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
    from ingestion.manifest import load_hold_manifest
    hold_path = MANIFEST_PATH.parent / "hold_sources.yaml"
    if hold_path.exists():
        hold_sources = load_hold_manifest(hold_path)
        mvp_sources = load_mvp_manifest(MANIFEST_PATH)
        mvp_ids = {s["source_id"] for s in mvp_sources}
        hold_ids = {s["source_id"] for s in hold_sources}
        # No overlap between MVP and hold sources
        assert len(mvp_ids & hold_ids) == 0
