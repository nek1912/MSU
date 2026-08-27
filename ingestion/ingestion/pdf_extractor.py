from pathlib import Path

from docling.document_converter import DocumentConverter


def validate_extraction(content: str, filename: str, min_length: int = 50) -> str:
    """Validate extracted content is usable.

    Args:
        content: Extracted markdown content
        filename: Original filename for error messages
        min_length: Minimum acceptable content length

    Returns:
        Validated content

    Raises:
        ValueError: If content is empty, too short, or whitespace-only
    """
    if not content or not content.strip():
        raise ValueError(f"Extraction from {filename} produced empty content")

    if len(content.strip()) < min_length:
        raise ValueError(f"Extraction from {filename} too short ({len(content.strip())} chars < {min_length})")

    return content


def extract_pdf_to_markdown(pdf_path: Path) -> str:
    """Extract text from PDF using Docling and return as markdown.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text as markdown string

    Raises:
        FileNotFoundError: If pdf_path does not exist
        ValueError: If extraction fails
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        return result.document.export_to_markdown()
    except Exception as e:  # noqa: BLE001 — Docling raises varied internal errors
        raise ValueError(f"Failed to extract PDF {pdf_path}: {e}")
