"""Tests for EntityResolver."""

from app.entity_resolver import EntityResolver


def test_exact_alias_pmfby():
    resolver = EntityResolver()
    result = resolver.resolve("PMFBY")
    assert result.entity_id == "pmfby"
    assert result.confidence == 1.0
    assert result.method == "alias"
    assert result.domain_tag == "pmfby"


def test_exact_alias_kcc():
    resolver = EntityResolver()
    result = resolver.resolve("KCC")
    assert result.entity_id == "kcc"
    assert result.confidence == 1.0
    assert result.method == "alias"
    assert result.domain_tag == "financial_inclusion"


def test_keyword_match_crop_insurance():
    resolver = EntityResolver()
    result = resolver.resolve("What is the crop insurance scheme?")
    assert result.entity_id == "pmfby"
    assert result.confidence == 0.85
    assert result.method == "keyword"


def test_keyword_match_pacs_membership():
    resolver = EntityResolver()
    result = resolver.resolve("How to become member of PACS?")
    assert result.entity_id == "pacs-membership"
    assert result.confidence == 0.85
    assert result.method == "keyword"


def test_no_match():
    resolver = EntityResolver()
    result = resolver.resolve("What is the weather today?")
    assert result.entity_id is None
    assert result.confidence == 0.0
    assert result.method == "none"
    assert result.domain_tag is None


def test_case_insensitivity():
    resolver = EntityResolver()
    lower = resolver.resolve("pmfby")
    upper = resolver.resolve("PMFBY")
    mixed = resolver.resolve("PmFbY")
    assert lower.entity_id == upper.entity_id == mixed.entity_id == "pmfby"
    assert lower.confidence == upper.confidence == mixed.confidence == 1.0


def test_alias_beats_keyword():
    resolver = EntityResolver()
    # "PACS" is an alias → exact match with confidence 1.0
    result = resolver.resolve("PACS")
    assert result.entity_id == "pacs-membership"
    assert result.confidence == 1.0
    assert result.method == "alias"
