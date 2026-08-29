import pytest
from app.services.lang_memory import (
    get_session_language,
    set_session_language,
    clear_session_language,
    DEFAULT_LANGUAGE,
)


def test_default_is_english():
    assert get_session_language("sess-default") == DEFAULT_LANGUAGE


def test_set_then_get():
    set_session_language("sess-1", "hi")
    assert get_session_language("sess-1") == "hi"


def test_clear():
    set_session_language("sess-2", "bn")
    clear_session_language("sess-2")
    assert get_session_language("sess-2") == DEFAULT_LANGUAGE


def test_empty_session_id_rejected():
    with pytest.raises(ValueError):
        set_session_language("", "hi")


def test_empty_language_rejected():
    with pytest.raises(ValueError):
        set_session_language("sess-3", "")
