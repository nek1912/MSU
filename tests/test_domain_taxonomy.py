"""Tests for canonical domain taxonomy — ensures all domain IDs are valid."""
import json
import os
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent

# Canonical domain IDs — single source of truth
CANONICAL_DOMAINS = {
    "pacs_governance",
    "pacs_computerization",
    "pmfby",
    "financial_inclusion",
    "schemes",
    "agriculture",
    "grievance",
    "out_of_scope",
}


def _load_json(relative_path):
    with open(PROJECT_ROOT / relative_path, encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(relative_path):
    with open(PROJECT_ROOT / relative_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_keyword_rules_use_canonical_domains():
    """Every domain in keyword_rules.json must be a canonical domain ID."""
    rules = _load_json("backend/data/keyword_rules.json")
    invalid = set(rules.keys()) - CANONICAL_DOMAINS
    assert not invalid, f"Non-canonical domains in keyword_rules.json: {invalid}"


def test_domain_anchors_use_canonical_domains():
    """Every domain in domain_anchors.json must be a canonical domain ID."""
    anchors = _load_json("backend/data/domain_anchors.json")
    invalid = set(anchors.keys()) - CANONICAL_DOMAINS
    assert not invalid, f"Non-canonical domains in domain_anchors.json: {invalid}"


def test_database_documents_use_canonical_domains():
    """Every document in the database must have a canonical domain ID."""
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / "backend" / ".env")
    
    import os
    from supabase import create_client
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase credentials not available")
    
    supabase = create_client(url, key)
    docs = supabase.table("documents").select("source_id, domain").execute().data
    
    invalid = []
    for doc in docs:
        if doc["domain"] not in CANONICAL_DOMAINS:
            invalid.append(f"{doc['source_id']}: {doc['domain']}")
    
    assert not invalid, f"Non-canonical domains in database: {invalid}"


def test_gold_cases_use_canonical_domains():
    """Every expected_domain in gold cases must be a canonical domain ID."""
    cases = _load_yaml("eval/gold_cases.yaml")
    
    invalid = []
    for case in cases:
        domain = case.get("expected_domain")
        if domain and domain not in CANONICAL_DOMAINS:
            invalid.append(f"{case.get('question', '?')[:50]}: {domain}")
    
    assert not invalid, f"Non-canonical domains in gold cases: {invalid}"


def test_keyword_rules_have_all_canonical_domains():
    """keyword_rules.json must have entries for all canonical domains (except out_of_scope)."""
    rules = _load_json("backend/data/keyword_rules.json")
    expected = CANONICAL_DOMAINS - {"out_of_scope"}
    missing = expected - set(rules.keys())
    assert not missing, f"Missing domains in keyword_rules.json: {missing}"


def test_domain_anchors_have_all_canonical_domains():
    """domain_anchors.json must have entries for all canonical domains (except out_of_scope)."""
    anchors = _load_json("backend/data/domain_anchors.json")
    expected = CANONICAL_DOMAINS - {"out_of_scope"}
    missing = expected - set(anchors.keys())
    assert not missing, f"Missing domains in domain_anchors.json: {missing}"


def test_keyword_rules_have_keywords():
    """Every domain in keyword_rules.json must have at least one keyword."""
    rules = _load_json("backend/data/keyword_rules.json")
    empty = [domain for domain, keywords in rules.items() if not keywords]
    assert not empty, f"Domains with empty keyword lists: {empty}"


def test_domain_anchors_have_phrases():
    """Every domain in domain_anchors.json must have at least one anchor phrase."""
    anchors = _load_json("backend/data/domain_anchors.json")
    empty = [domain for domain, phrases in anchors.items() if not phrases]
    assert not empty, f"Domains with empty anchor phrases: {empty}"
