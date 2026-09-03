"""Tests for QueryRequirementClassifier — temporal/geographic query analysis."""

import pytest

from app.evidence_controller import QueryRequirementClassifier


classifier = QueryRequirementClassifier()


def test_general_query_no_year():
    qr = classifier.classify("What are PMFBY rules?", "en")
    assert qr.temporal_scope == "general"
    assert qr.requires_dynamic is False


def test_current_year_query():
    qr = classifier.classify("PMFBY premium 2026", "en")
    assert qr.temporal_scope == "2026"
    assert qr.requires_dynamic is True


def test_haalmaa_query():
    qr = classifier.classify("હાલમાં PMFBY notified crops", "gu")
    assert qr.temporal_scope == "current"
    assert qr.requires_dynamic is True


def test_historical_query():
    qr = classifier.classify("2023 PMFBY guidelines", "en")
    assert qr.temporal_scope == "historical"
    assert qr.requires_dynamic is False


def test_unspecified_with_district():
    qr = classifier.classify("Surat district crops", "en")
    assert qr.geographic_scope == "district"
    assert qr.requires_dynamic is True


def test_state_query():
    qr = classifier.classify("Gujarat PMFBY scheme", "en")
    assert qr.geographic_scope == "state"
    assert qr.requires_dynamic is False  # state-level doesn't always need dynamic


def test_no_geographic():
    qr = classifier.classify("What is PMFBY?", "en")
    assert qr.geographic_scope == "none"
    assert qr.requires_dynamic is False
