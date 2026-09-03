"""AI-powered translation layer using LLM for context-aware translation.

Instead of direct API translation, this uses the LLM itself to translate
evidence chunks and queries to English with better context preservation.
The LLM understands domain-specific terminology and can produce more
accurate translations for government/legal content.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

_TRANSLATION_SYSTEM_PROMPT = """You are a professional translator specializing in Indian government and legal documents.

Translate the following text to English. Rules:
1. Preserve all proper nouns, scheme names, section numbers, and legal terminology exactly.
2. Keep numerical values, dates, percentages, and monetary amounts unchanged.
3. Maintain the original structure (paragraphs, bullet points, etc.).
4. Do NOT add explanations or notes — output ONLY the translated text.
5. If the text is already in English, return it unchanged.
6. For Hindi/regional terms that have no direct English equivalent, use the transliterated form in parentheses after the English translation.
7. Preserve citation markers like [EVIDENCE N], [static:XXX], [web:NNN] exactly as-is.
"""


def _is_likely_english(text: str) -> bool:
    """Quick heuristic to check if text is predominantly English."""
    if not text:
        return True
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return ascii_chars / max(len(text), 1) > 0.85


def translate_to_english_llm(
    text: str,
    llm_provider: LLMProvider,
    max_chars: int = 8000,
) -> str:
    """Translate text to English using the LLM for context-aware translation.

    Falls back to returning original text if translation fails.
    """
    if not text or _is_likely_english(text):
        return text

    truncated = text[:max_chars] if len(text) > max_chars else text

    try:
        result = llm_provider.generate(
            system=_TRANSLATION_SYSTEM_PROMPT,
            user=f"Translate this to English:\n\n{truncated}",
        )
        if result and len(result.strip()) > 10:
            return result.strip()
        logger.warning("LLM translation returned empty/short result, using original")
        return text
    except Exception as e:
        logger.warning("LLM translation failed: %s, using original", e)
        return text


def translate_evidence_batch(
    evidence_texts: list[str],
    llm_provider: LLMProvider,
    batch_max_chars: int = 6000,
) -> list[str]:
    """Translate a batch of evidence chunks to English in a single LLM call.

    More efficient than translating each chunk separately.
    Returns list of translated texts in the same order.
    """
    if not evidence_texts:
        return []

    # Filter out already-English texts
    needs_translation = []
    english_indices = set()
    for i, text in enumerate(evidence_texts):
        if _is_likely_english(text):
            english_indices.add(i)
            needs_translation.append(None)
        else:
            needs_translation.append(text)

    # If all English, return as-is
    if not any(t is not None for t in needs_translation):
        return evidence_texts

    # Build combined prompt for batch translation
    numbered_parts = []
    part_idx = 0
    for i, text in enumerate(needs_translation):
        if text is not None:
            part_idx += 1
            numbered_parts.append(f"[CHUNK {part_idx}]\n{text}")

    combined = "\n\n".join(numbered_parts)
    if len(combined) > batch_max_chars:
        combined = combined[:batch_max_chars]

    try:
        result = llm_provider.generate(
            system=_TRANSLATION_SYSTEM_PROMPT,
            user=f"Translate each numbered chunk to English. Output format: one translated chunk per section, separated by blank lines, preserving the [CHUNK N] markers:\n\n{combined}",
        )

        # Parse the response back into individual chunks
        if result:
            translated_parts = _parse_numbered_chunks(result, part_idx)
            # Reassemble with english chunks
            output = []
            transl_idx = 0
            for i in range(len(evidence_texts)):
                if i in english_indices:
                    output.append(evidence_texts[i])
                else:
                    if transl_idx < len(translated_parts):
                        output.append(translated_parts[transl_idx])
                    else:
                        output.append(evidence_texts[i] if needs_translation[i] is None else needs_translation[i])
                    transl_idx += 1
            return output
    except Exception as e:
        logger.warning("Batch LLM translation failed: %s", e)

    return evidence_texts


def _parse_numbered_chunks(text: str, expected_count: int) -> list[str]:
    """Parse [CHUNK N] markers from translated output."""
    import re
    chunks = []
    parts = re.split(r"\[CHUNK \d+\]\s*", text)
    for part in parts:
        stripped = part.strip()
        if stripped:
            chunks.append(stripped)
    return chunks[:expected_count] if chunks else [text]
