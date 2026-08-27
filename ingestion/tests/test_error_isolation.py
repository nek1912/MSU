import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

MANIFEST_PATH = Path(__file__).parent.parent.parent / "corpus" / "manifests" / "mvp_sources.yaml"


def _make_source(source_id: str, path: str | None = None) -> dict:
    """Create a minimal valid manifest source dict."""
    if path is None:
        path = f"{source_id}.pdf"
    return {
        "source_id": source_id,
        "path": path,
        "actual_title": f"Title {source_id}",
        "issuing_organization": "Org",
        "target_domain": "pacs",
        "jurisdiction": "central",
        "document_type": "pdf",
        "official_source_url": "https://example.com",
        "verified_date": "2026-08-27",
        "effective_date": None,
        "document_date": None,
        "state": None,
    }


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_one_bad_file_others_succeed(mock_load, mock_validate, mock_chunk, mock_extract):
    """If one PDF raises, the rest still process and the failed one is tracked."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("good1"), _make_source("bad"), _make_source("good2")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])

    def extract_side_effect(path):
        # path is base_dir / source["path"], so match on source["path"]
        if "bad.pdf" in str(path):
            raise ValueError("corrupt PDF")
        return "# content"

    mock_extract.side_effect = extract_side_effect
    mock_chunk.return_value = ["chunk"]

    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()

    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    assert "good1" in result["succeeded"]
    assert "good2" in result["succeeded"]
    assert len(result["failed"]) == 1
    assert result["failed"][0]["source_id"] == "bad"
    assert "corrupt PDF" in result["failed"][0]["error"]


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_all_fail_gracefully(mock_load, mock_validate, mock_chunk, mock_extract):
    """If every file raises, we get all failures and no crash."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("a"), _make_source("b")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])
    mock_extract.side_effect = RuntimeError("disk error")

    mock_embed = MagicMock()
    mock_supabase = MagicMock()

    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    assert len(result["succeeded"]) == 0
    assert len(result["failed"]) == 2
    mock_embed.assert_not_called()
    mock_supabase.table.assert_not_called()


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_exception_types_isolated(mock_load, mock_validate, mock_chunk, mock_extract):
    """Different exception types from different files are all caught."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("file1"), _make_source("file2"), _make_source("file3")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])

    def extract_side_effect(path):
        p = str(path)
        if "file1.pdf" in p:
            raise FileNotFoundError("missing file")
        if "file2.pdf" in p:
            raise KeyError("bad key")
        if "file3.pdf" in p:
            raise PermissionError("access denied")
        return "# ok"

    mock_extract.side_effect = extract_side_effect
    mock_chunk.return_value = ["chunk"]

    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()

    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    assert len(result["succeeded"]) == 0
    assert len(result["failed"]) == 3
    errors = {f["source_id"]: f["error"] for f in result["failed"]}
    assert "missing file" in errors["file1"]
    assert "bad key" in errors["file2"]
    assert "access denied" in errors["file3"]


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_db_not_called_for_failed_files(mock_load, mock_validate, mock_chunk, mock_extract):
    """Files that fail during extraction must not reach the DB layer."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("fail_me"), _make_source("ok")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])

    def extract_side_effect(path):
        if "fail_me.pdf" in str(path):
            raise ValueError("bad pdf")
        return "# ok"

    mock_extract.side_effect = extract_side_effect
    mock_chunk.return_value = ["chunk"]

    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()

    result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    assert "fail_me" in [f["source_id"] for f in result["failed"]]
    assert "ok" in result["succeeded"]
    # Delete+insert only for "ok" — fail_me never touches DB
    doc_ops = [c for c in mock_supabase.table.call_args_list if c.args[0] == "documents"]
    assert len(doc_ops) == 2


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_structured_log_on_failure(mock_load, mock_validate, mock_chunk, mock_extract, caplog):
    """Failure must produce a structured log entry with source_id and error."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("crasher")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])
    mock_extract.side_effect = RuntimeError("boom")

    mock_embed = MagicMock()
    mock_supabase = MagicMock()

    with caplog.at_level(logging.ERROR, logger="ingestion.ingest"):
        result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    assert len(result["failed"]) == 1
    assert any(
        "crasher" in record.message and "RuntimeError" in record.message
        for record in caplog.records
    )


@patch("ingestion.ingest.extract_pdf_to_markdown")
@patch("ingestion.ingest.chunk_markdown")
@patch("ingestion.ingest.validate_manifest_files")
@patch("ingestion.ingest.load_mvp_manifest")
def test_summary_logged(mock_load, mock_validate, mock_chunk, mock_extract, caplog):
    """Summary line is logged with counts."""
    from ingestion.ingest import manifest_to_supabase

    sources = [_make_source("ok1"), _make_source("bad")]
    mock_load.return_value = sources
    mock_validate.return_value = (sources, [])

    def extract_side_effect(path):
        if "bad.pdf" in str(path):
            raise ValueError("fail")
        return "# ok"

    mock_extract.side_effect = extract_side_effect
    mock_chunk.return_value = ["chunk"]

    mock_embed = MagicMock(return_value=[[0.1] * 768])
    mock_supabase = MagicMock()

    with caplog.at_level(logging.INFO, logger="ingestion.ingest"):
        result = manifest_to_supabase(MANIFEST_PATH, mock_embed, mock_supabase)

    summary_records = [
        r for r in caplog.records if "succeeded" in r.message and "failed" in r.message
    ]
    assert len(summary_records) >= 1
    assert "1 succeeded" in summary_records[0].message
    assert "1 failed" in summary_records[0].message
