"""Grounding-aware generation with multilingual prompt engineering.

Two answer modes:
- RAG (in-domain): answer ONLY from retrieved chunks, every sentence cited,
  respond in the user's language. Chain: generate -> verify -> reject if broken.
- General (out-of-scope): answer from the LLM's own knowledge, clearly NOT
  grounded in official sources, respond in the user's language. No citations
  required because there is no retrieved evidence.
"""

import re

from app.providers.base import LLMProvider
from app.retrieval import RetrievedChunk

_CITE = re.compile(r"\[chunk:([0-9a-fA-F]{8,})\]")
_CITE_RAW = re.compile(r"\[chunk:(.*?)\]")

_LANG_INSTRUCTION = {
    "en": "answer in English",
    "hi": "answer in Hindi (Devanagari script)",
}

_GENERAL_DISCLAIMER = {
    "en": "This is a general answer not from official government sources. "
          "For authoritative guidance on cooperative rules, schemes, PMFBY, "
          "or financial inclusion, ask a specific question about those topics.",
    "hi": "यह सामान्य उत्तर है जो सरकारी स्रोतों से नहीं है। सहकारिता नियमों, योजनाओं, "
          "पीएमएफबीवाई, या वित्तीय समावेशन पर आधिकारिक मार्गदर्शन के लिए उन विषयों "
          "के बारे में एक विशिष्ट प्रश्न पूछें।",
}

GENERAL_SYSTEM_PROMPT = (
    "You are a helpful, truthful assistant. Answer the user's question clearly "
    "and accurately from your general knowledge. If a question concerns specific "
    "Indian government rules, schemes, or legal details, be careful not to state "
    "precise amounts, deadlines, or clauses you are not certain about; when you "
    "are unsure of a concrete official detail, say so plainly instead of guessing."
)


class CitationError(Exception): ...


def build_system_prompt(language: str) -> str:
    """RAG system prompt instructing grounded, cited, language-matched output.

    Generic: no domain names are hardcoded. Chunks carry their own labels.
    """
    lang = language if language in _LANG_INSTRUCTION else "en"
    return (
        "You are a careful assistant that answers ONLY from the provided "
        "numbered context chunks. Every factual sentence must end with a marker "
        "[chunk:ID] where ID is the first 8 hex characters of the chunk id it "
        "came from. Never add outside knowledge. If the chunks do not contain "
        "the answer, reply exactly: INSUFFICIENT_EVIDENCE. Please "
        f"{_LANG_INSTRUCTION[lang]}."
    )


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Build the RAG user prompt from question + numbered context chunks."""
    ctx = "\n\n".join(
        f"[chunk:{c.chunk_id[:8]}] ({c.title} \u2014 \u00a7{c.section} \u2014 p.{c.page})\n{c.content}"
        for c in chunks)
    return f"Question: {question}\n\nContext:\n{ctx}"


def build_general_prompt(question: str, language: str) -> str:
    """User prompt for an out-of-scope question answered from general knowledge."""
    lang = language if language in _LANG_INSTRUCTION else "en"
    return (
        f"Question: {question}\n\n"
        "Answer the question helpfully and accurately from your general "
        f"knowledge. {_LANG_INSTRUCTION[lang].capitalize()}. Do not invent "
        "specific Indian government scheme amounts, deadlines, or legal clauses; "
        "if you are unsure of a concrete official detail, say so clearly rather "
        "than guessing."
    )


def general_disclaimer(language: str) -> str:
    """User-facing note that a general answer is not from official sources."""
    return _GENERAL_DISCLAIMER.get(language, _GENERAL_DISCLAIMER["en"])


def verify_citations(answer: str, chunk_ids: list[str]) -> tuple[list[str], list[str]]:
    """Return (valid_ids, invalid_prefixes). Any invalid prefix means the
    response must be rejected per spec:
    """
    valid: list[str] = []
    invalid: list[str] = []
    for raw_match in _CITE_RAW.findall(answer):
        hex_match = re.fullmatch(r"[0-9a-fA-F]{8,}", raw_match)
        if not hex_match:
            if raw_match not in invalid:
                invalid.append(raw_match)
            continue
        prefix = hex_match.group()[:8].lower()
        matched = any(cid.startswith(prefix) for cid in chunk_ids)
        if matched:
            for cid in chunk_ids:
                if cid.startswith(prefix) and cid not in valid:
                    valid.append(cid)
                    break
        else:
            if prefix not in invalid:
                invalid.append(prefix)
    return valid, invalid


def generate_answer(llm: LLMProvider, question: str, chunks: list[RetrievedChunk],
                    language: str = "en") -> str:
    """Generate a grounded, cited answer in the user's language topically."""
    system = build_system_prompt(language)
    user = build_user_prompt(question, chunks)
    answer = llm.generate(system, user)
    if answer.strip() == "INSUFFICIENT_EVIDENCE":
        raise CitationError("model declined: insufficient evidence")
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    if invalid:
        raise CitationError(f"invalid citations: {invalid}")
    if not valid:
        raise CitationError("answer carried no valid citations")
    return answer


def generate_general_answer(llm: LLMProvider, question: str, language: str = "en") -> str:
    """Generate an out-of-scope answer from the LLM's own knowledge."""
    return llm.generate(GENERAL_SYSTEM_PROMPT, build_general_prompt(question, language))
