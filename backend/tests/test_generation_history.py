from app.generation import build_user_prompt
from app.retrieval import RetrievedChunk


def _make_chunk(content: str = "test") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="aaaabbbb-1111-2222-3333-444444444444",
        stable_chunk_id="doc:p1:c0",
        document_id="doc-id",
        title="Test Doc",
        page=1,
        page_start=1,
        page_end=1,
        section="Sec",
        subsection=None,
        clause=None,
        content=content,
        similarity=0.8,
        source_url="https://example.com",
        source_file="example.com",
        domain="test",
        jurisdiction="central",
        state=None,
    )


def test_build_user_prompt_no_history():
    prompt = build_user_prompt("What is PMFBY?", [_make_chunk()])
    assert "Previous conversation:" not in prompt
    assert "Question: What is PMFBY?" in prompt


def test_build_user_prompt_with_history():
    history = [
        {"role": "user", "content": "What is PMFBY?"},
        {"role": "assistant", "content": "PMFBY is a crop insurance scheme [chunk:aaaabbbb]."},
    ]
    prompt = build_user_prompt("What are the eligibility criteria?", [_make_chunk()], history=history)
    assert "Previous conversation:" in prompt
    assert "User: What is PMFBY?" in prompt
    assert "Assistant: PMFBY is a crop insurance scheme" in prompt
    assert "Question: What are the eligibility criteria?" in prompt


def test_build_user_prompt_empty_history():
    prompt = build_user_prompt("test", [_make_chunk()], history=[])
    assert "Previous conversation:" not in prompt
