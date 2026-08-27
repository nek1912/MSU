from ingestion.ingest import normalize_state


def test_normalize_state_lowercase():
    assert normalize_state("Gujarat") == "gujarat"


def test_normalize_state_trim():
    assert normalize_state("  Gujarat  ") == "gujarat"


def test_normalize_state_none():
    assert normalize_state(None) is None


def test_normalize_state_empty():
    assert normalize_state("") is None
