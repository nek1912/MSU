import pytest

from app.language import normalize_language


def test_selection_wins_on_plain_english():
    assert normalize_language("en", "What is PMFBY eligibility?") == "en"


def test_devanagari_overrides_en_selection():
    assert normalize_language("en", "पीएमएफबीवाई में कैसे आवेदन करें") == "hi"


def test_latin_script_hindi_stays_hi():
    # Latin-script Hindi must NOT flip just because of script
    assert normalize_language("hi", "meri fasal ka insurance kaise milega") == "hi"


def test_invalid_selection_rejected():
    with pytest.raises(ValueError):
        normalize_language("fr", "bonjour")
