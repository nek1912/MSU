from pathlib import Path

from ingestion.pdf_extractor import extract_pdf_to_markdown

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
    from ingestion.manifest import load_mvp_manifest, validate_manifest_files
    sources = load_mvp_manifest(manifest_path)
    base_dir = manifest_path.parent.parent
    _valid, missing = validate_manifest_files(sources, base_dir)
    assert len(missing) == 0, f"MVP files missing: {[s.get('path') for s in missing]}"
