from ingestion.pdf_extractor import validate_extraction


def test_validate_extraction_empty_raises():
    from pytest import raises
    with raises(ValueError, match="empty"):
        validate_extraction("", "test.pdf")


def test_validate_extraction_too_short_raises():
    from pytest import raises
    with raises(ValueError, match="too short"):
        validate_extraction("Hi", "test.pdf")


def test_validate_extraction_valid():
    # Should not raise
    validate_extraction("# Title\n\n" + "x" * 100, "test.pdf")


def test_validate_extraction_whitespace_only_raises():
    from pytest import raises
    with raises(ValueError, match="empty"):
        validate_extraction("   \n  \n  ", "test.pdf")
