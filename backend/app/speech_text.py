"""Speech-safe text preparation.

The RAG ``answer`` intentionally carries ``[chunk:ID]`` citation markers: they
are required for citation verification (app.citation_verifier) and for the UI
to render source links. But those markers, URLs, and markdown syntax must NEVER
reach a text-to-speech engine — otherwise the assistant reads out chunk IDs and
URLs instead of the answer.

This module produces a speech-only representation of an answer that has ALREADY
passed citation verification. Verification still operates on the original
``answer`` (with markers); only the *speech copy* is cleaned. The same generic
transform is applied to every supported language — there is deliberately no
language-specific branching here.

Order matters: clean AFTER verification, never before.
"""

from __future__ import annotations

import re

# Canonical half-width markers produced by the LLM / normalised by the verifier.
_CITE = re.compile(r"\[chunk:[0-9a-fA-F]{8,}\]")
# Full-width 【ID】 / 【chunk:ID】 variants the LLM sometimes emits.
_FULLWIDTH_CITE = re.compile(r"【\s*(?:chunk:)?\s*[0-9a-fA-F]{8,}\s*】")
# Bare half-width hex bracket [ID] (missing the `chunk:` prefix).
_BARE_HEX_CITE = re.compile(r"\[\s*[0-9a-fA-F]{8,}\s*\]")
# Markdown links [text](url) — keep the visible text, drop the URL.
_MD_LINK = re.compile(r"\[([^\]]+)\]\((\s*https?://\S+)\)")
# Standalone URLs (never speakable, and the verifier flags fabricated ones).
_URL = re.compile(r"https?://\S+")
# Collapse runs of whitespace and tidy spacing before punctuation.
_WS = re.compile(r"[ \t]{2,}")
_BEFORE_PUNCT = re.compile(r"\s+([.,;:!?])")
_MANY_NL = re.compile(r"\n{3,}")


def prepare_speech_text(answer: str) -> str:
    """Return a TTS-safe copy of an already-verified answer.

    Removes citation markers (all recognised variants), markdown link syntax,
    and URLs. Legitimate content — percentages, dates, clause/section numbers,
    scheme names, amounts — is preserved verbatim. The input is expected to have
    already passed citation verification; this function only changes presentation.
    """
    if not answer:
        return ""

    text = _FULLWIDTH_CITE.sub("", answer)
    text = _BARE_HEX_CITE.sub("", text)
    text = _CITE.sub("", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _URL.sub("", text)

    text = _WS.sub(" ", text)
    text = _BEFORE_PUNCT.sub(r"\1", text)
    text = _MANY_NL.sub("\n\n", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def _char_script(ch: str, answer_language: str) -> str | None:
    """Map a character to a language bucket for segmentation.

    Gujarati/Bengali/Latin are script-unique. Devanagari is mapped to the
    *already resolved* answer language (NOT guessed) — this is answer-side only.
    Punctuation/spaces return None (attach to the current run).
    """
    cp = ord(ch)
    if 0x0A80 <= cp <= 0x0AFF:
        return "gu"
    if 0x0980 <= cp <= 0x09FF:
        return "bn"
    if 0x0900 <= cp <= 0x097F:
        return answer_language
    if ch.isascii() and (ch.isalpha() or ch.isdigit()):
        return "en"
    return None


def segment_speech(answer: str, answer_language: str) -> list[dict]:
    """Split a verified answer into language-tagged segments by script run.

    Generic — no per-language hardcoding. Devanagari runs take the resolved
    ``answer_language`` so Hindi/Marathi answers segment correctly. Marker
    envelopes are removed generically before segmenting (never spoken).
    """
    if not answer:
        return []
    answer = prepare_speech_text(answer)
    text = answer
    segments: list[dict] = []
    current_lang: str | None = None
    current_text: list[str] = []
    for ch in text:
        lang = _char_script(ch, answer_language)
        if lang is None:
            if current_lang is not None:
                current_text.append(ch)
            continue
        if lang != current_lang:
            if current_lang is not None:
                seg = "".join(current_text).strip()
                if seg:
                    segments.append({"language": current_lang, "text": seg})
            current_lang = lang
            current_text = [ch]
        else:
            current_text.append(ch)
    if current_lang is not None:
        seg = "".join(current_text).strip()
        if seg:
            segments.append({"language": current_lang, "text": seg})
    return segments
