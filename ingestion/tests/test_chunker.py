from ingestion.chunker import chunk_markdown


def test_short_body_single_chunk():
    assert chunk_markdown("one two three") == ["one two three"]


def test_heading_split_then_length_split():
    body = "# A\n" + ("word " * 500) + "\n# B\n" + ("term " * 500)
    chunks = chunk_markdown(body, target_tokens=300, min_tokens=100,
                            max_tokens=350, overlap_tokens=40)
    assert len(chunks) >= 3
    assert all(len(c.split()) <= 350 for c in chunks)
