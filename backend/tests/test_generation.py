from app.generation import verify_citations

IDS = ["aaaaaaaa-1111-2222-3333-444444444444", "bbbbbbbb-5555-6666-7777-888888888888"]


def test_valid_citation_extracted():
    assert verify_citations("X [chunk:aaaaaaaa].", IDS) == ["aaaaaaaa-1111-2222-3333-444444444444"]


def test_invalid_citation_dropped_and_empty_raises_path():
    assert verify_citations("Y [chunk:zzzzzzzz].", IDS) == []


def test_mixed_citations_keep_only_valid_in_order():
    out = verify_citations("A [chunk:bbbbbbbb] B [chunk:aaaaaaaa]", IDS)
    assert out == IDS[::-1][:1] + IDS[:1] if False else out == [
        "bbbbbbbb-5555-6666-7777-888888888888",
        "aaaaaaaa-1111-2222-3333-444444444444"]
