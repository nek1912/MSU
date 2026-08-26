"""Tests for enhanced corpus_check.py (Invariant 1)."""
import os
import tempfile
import pytest
from pathlib import Path


def _write_seed(tmpdir, filename, frontmatter, body):
    """Helper: write a seed .md file with given frontmatter and body."""
    content = f"---\n{frontmatter}\n---\n{body}\n"
    path = os.path.join(tmpdir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


VALID_FRONTMATTER = (
    "source_id: test_source\n"
    "title: Test Document\n"
    "organization: Test Org\n"
    "domain: cooperative\n"
    "jurisdiction: central\n"
    "state: null\n"
    "source_type: official_web_source\n"
    "official_domain: gov.in\n"
    "url: https://example.gov.in/test\n"
    "effective_date: null\n"
    "verified_date: 2026-08-26"
)


class TestOfficialDomainValidation:
    def test_rejects_non_official_domain(self, tmp_path):
        from eval.corpus_check import check_file
        bad_fm = VALID_FRONTMATTER.replace("official_domain: gov.in", "official_domain: wikipedia.org")
        path = _write_seed(str(tmp_path), "bad.md", bad_fm, "Some content here.")
        errors, _ = check_file(path)
        domain_errors = [e for e in errors if "official_domain" in e.get("error", "")]
        assert len(domain_errors) > 0

    def test_accepts_valid_official_domain(self, tmp_path):
        from eval.corpus_check import check_file
        path = _write_seed(str(tmp_path), "good.md", VALID_FRONTMATTER, "Some content here.")
        errors, _ = check_file(path)
        domain_errors = [e for e in errors if "official_domain" in e.get("error", "")]
        assert len(domain_errors) == 0


class TestMetadataCompleteness:
    def test_rejects_missing_source_type(self, tmp_path):
        from eval.corpus_check import check_file
        bad_fm = VALID_FRONTMATTER.replace("source_type: official_web_source\n", "")
        path = _write_seed(str(tmp_path), "bad.md", bad_fm, "Some content here.")
        errors, _ = check_file(path)
        assert any("source_type" in e.get("error", "") for e in errors)

    def test_rejects_missing_official_domain(self, tmp_path):
        from eval.corpus_check import check_file
        bad_fm = VALID_FRONTMATTER.replace("official_domain: gov.in\n", "")
        path = _write_seed(str(tmp_path), "bad.md", bad_fm, "Some content here.")
        errors, _ = check_file(path)
        assert any("official_domain" in e.get("error", "") for e in errors)

    def test_rejects_empty_content(self, tmp_path):
        from eval.corpus_check import check_file
        path = _write_seed(str(tmp_path), "empty.md", VALID_FRONTMATTER, "")
        errors, _ = check_file(path)
        assert any("Empty content" in e.get("error", "") for e in errors)

    def test_rejects_duplicate_source_id(self, tmp_path):
        from eval.corpus_check import check_file
        _write_seed(str(tmp_path), "a.md", VALID_FRONTMATTER, "Content A.")
        bad_fm = VALID_FRONTMATTER.replace("source_id: test_source", "source_id: test_source")
        _write_seed(str(tmp_path), "b.md", bad_fm, "Content B.")
        errors, _ = check_file(os.path.join(str(tmp_path), "b.md"))
        assert any("Duplicate source_id" in e.get("error", "") for e in errors)

    def test_accepts_valid_seed(self, tmp_path):
        from eval.corpus_check import check_file
        path = _write_seed(str(tmp_path), "valid.md", VALID_FRONTMATTER, "Some real content.")
        errors, _ = check_file(path)
        assert len(errors) == 0


class TestApprovedOfficialDomains:
    def test_approved_domain_registry(self):
        from eval.corpus_check import APPROVED_OFFICIAL_DOMAINS
        assert "gov.in" in APPROVED_OFFICIAL_DOMAINS
        assert "cooperation.gov.in" in APPROVED_OFFICIAL_DOMAINS
        assert "pmfby.gov.in" in APPROVED_OFFICIAL_DOMAINS
        assert "rbi.org.in" in APPROVED_OFFICIAL_DOMAINS