"""Tests for gold_cases.yaml validation — integrity check."""
import os
import yaml


def _load_yaml(relative_path):
    base = os.path.join(os.path.dirname(__file__), "..")
    with open(os.path.join(base, relative_path), encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_all_source_ids_exist():
    """Every source_id in gold_cases must exist in sources.yaml."""
    sources = _load_yaml("sources.yaml")
    source_ids = {s["id"] for s in sources.get("sources", [])}
    cases = _load_yaml("eval/gold_cases.yaml")

    missing = set()
    for case in cases:
        for sid in case.get("relevant_source_ids", []):
            if sid not in source_ids:
                missing.add(sid)
    assert not missing, f"Missing source_ids in sources.yaml: {missing}"


def test_answerable_has_nonempty_source_ids():
    """answerable=true requires non-empty relevant_source_ids."""
    cases = _load_yaml("eval/gold_cases.yaml")
    violations = [
        c["question"] for c in cases
        if c.get("answerable", False) and not c.get("relevant_source_ids")
    ]
    assert not violations, f"answerable=true with empty relevant_source_ids: {violations}"


def test_answerable_has_nonempty_chunk_ids():
    """answerable=true requires non-empty relevant_chunk_ids."""
    cases = _load_yaml("eval/gold_cases.yaml")
    violations = [
        c["question"] for c in cases
        if c.get("answerable", False) and not c.get("relevant_chunk_ids")
    ]
    # This test will initially fail — chunk_ids are empty until after ingestion.
    # It serves as a reminder to populate chunk_ids after ingestion.
    assert not violations, (
        f"answerable=true with empty relevant_chunk_ids: {violations}. "
        "Populate chunk_ids after ingestion."
    )


def test_unanswerable_has_empty_lists():
    """answerable=false requires empty relevant_source_ids and relevant_chunk_ids."""
    cases = _load_yaml("eval/gold_cases.yaml")
    violations = [
        c["question"] for c in cases
        if not c.get("answerable", False) and (
            c.get("relevant_source_ids") or c.get("relevant_chunk_ids")
        )
    ]
    assert not violations, f"answerable=false with non-empty lists: {violations}"


def test_all_cases_have_required_fields():
    """Every case must have question, expected_domain, answerable."""
    cases = _load_yaml("eval/gold_cases.yaml")
    for i, case in enumerate(cases):
        assert "question" in case, f"Case {i} missing 'question'"
        assert "expected_domain" in case, f"Case {i} missing 'expected_domain'"
        assert "answerable" in case, f"Case {i} missing 'answerable'"


def test_case_count_matches_expected():
    """Gold set should have 245 cases (30/domain x 7 + 5 adversarial x 7)."""
    cases = _load_yaml("eval/gold_cases.yaml")
    assert len(cases) == 245, f"Expected 245 cases, got {len(cases)}"
