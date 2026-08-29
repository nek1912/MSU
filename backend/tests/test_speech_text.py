"""Tests for speech-safe answer preparation (app.speech_text).

These verify the core architectural requirement: TTS receives ONLY a
citation/URL/markdown-free copy of the answer, while the original `answer`
(with [chunk:ID]) and the structured `citations` remain untouched for the UI
and for citation verification.
"""

import pytest

from app.speech_text import prepare_speech_text


def test_removes_canonical_citation_marker():
    out = prepare_speech_text("Farmers are eligible [chunk:aaaaaaaa]. Apply online.")
    assert "[chunk:" not in out
    assert "Farmers are eligible" in out
    assert "Apply online." in out


def test_removes_fullwidth_citation_marker():
    out = prepare_speech_text("Coverage extends to notified crops 【aaaaaaaa】.")
    assert "【" not in out and "aaaaaaaa" not in out
    assert "Coverage extends to notified crops" in out


def test_removes_bare_hex_bracket_marker():
    out = prepare_speech_text("Premium is 2 percent [aaaaaaaa] of sum insured.")
    assert "[aaaaaaaa]" not in out
    assert "2 percent" in out


def test_removes_urls():
    out = prepare_speech_text("See https://pmfby.gov.in/faq for details.")
    assert "https://" not in out
    assert "See" in out and "details." in out


def test_strips_markdown_link_keeps_text():
    out = prepare_speech_text("Read the [guidelines](https://example.com/x) carefully.")
    assert "https://" not in out
    assert "guidelines" in out
    assert "carefully." in out


def test_preserves_legitimate_content():
    out = prepare_speech_text(
        "Claim within 72 hours. Subsidy is 25% [chunk:bbbbbbbb] per clause 4.2, "
        "w.e.f. 2024-01-01. Yields dropped 30%."
    )
    assert "[chunk:" not in out
    for token in ["72 hours", "25%", "clause 4.2", "2024-01-01", "30%", "Subsidy", "Yields"]:
        assert token in out


def test_works_for_hindi_answer_with_markers():
    out = prepare_speech_text("पीएमएफबीवाई में किसान पात्र हैं [chunk:cccccccc].")
    assert "[chunk:" not in out
    assert "पीएमएफबीवाई" in out


def test_works_for_marathi_and_bengali_answers():
    mr = prepare_speech_text("पीएमएफबीवाय अंतर्गत शेतकरी पात्र [chunk:dddddddd].")
    bn = prepare_speech_text("পিএমএফবি঵াই এর অন্তর্ভুক্ত কৃষক [chunk:eeeeeeee].")
    assert "[chunk:" not in mr and "पीएमएफबीवाय" in mr
    assert "[chunk:" not in bn and "পিএমএফবি঵াই" in bn


def test_tidies_space_before_punctuation():
    out = prepare_speech_text("Eligible farmers [chunk:aaaaaaaa] .")
    assert " ." not in out
    assert "Eligible farmers." in out


def test_empty_input():
    assert prepare_speech_text("") == ""
    assert prepare_speech_text(None) == ""  # type: ignore[arg-type]


def test_no_language_specific_branching():
    samples = {
        "en": "Loan at 7% [chunk:11111111] interest.",
        "hi": "ऋण 7% [chunk:22222222] ब्याज।",
        "gu": "લોન 7% [chunk:33333333] વ્યાજ.",
        "mr": "कर्ज 7% [chunk:44444444] व्याज.",
        "bn": "ঋণ 7% [chunk:55555555] সুদ.",
    }
    for text in samples.values():
        out = prepare_speech_text(text)
        assert "[chunk:" not in out
        assert "7%" in out


def test_segment_speech_single_latin():
    from app.speech_text import segment_speech
    segs = segment_speech("PMFBY provides crop insurance.", "en")
    assert segs == [{"language": "en", "text": "PMFBY provides crop insurance."}]


def test_segment_speech_mixed_hindi_english():
    from app.speech_text import segment_speech
    ans = "प्रधानमंत्री फसल बीमा योजना PMFBY के तहत"
    segs = segment_speech(ans, "hi")
    langs = [s["language"] for s in segs]
    assert langs == ["hi", "en", "hi"]
    assert segs[1]["text"] == "PMFBY"


def test_segment_speech_devanagari_uses_answer_language():
    from app.speech_text import segment_speech
    ans = "हे उत्तर मराठीत आहे"
    segs = segment_speech(ans, "mr")
    assert all(s["language"] == "mr" for s in segs)


def test_segment_speech_strips_markers_before_segmenting():
    from app.speech_text import segment_speech
    ans = "Eligible farmers [chunk:abc123] are covered."
    segs = segment_speech(ans, "en")
    assert "[chunk:" not in segs[0]["text"]


def test_segment_speech_preserves_unicode():
    from app.speech_text import segment_speech
    ans = "ગુજરાતી PMFBY માટે"
    segs = segment_speech(ans, "gu")
    joined = "".join(s["text"] for s in segs)
    assert "ગુજરાતી" in joined and "PMFBY" in joined
