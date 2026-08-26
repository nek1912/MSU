import re

from app.providers.base import LLMProvider
from app.retrieval import RetrievedChunk

_CITE = re.compile(r"\[chunk:([0-9a-fA-F]{8,})\]")  # detect any 8+ hex prefix
_CITE_RAW = re.compile(r"\[chunk:(.*?)\]")  # detect ANY [chunk:...] for invalid detection


class CitationError(Exception): ...


SYSTEM_PROMPT = (
    "You answer ONLY from the numbered context chunks. Every factual sentence "
    "must end with a marker [chunk:ID] where ID is the first 8 hex characters "
    "of the chunk id you used. Never add outside knowledge. If the chunks do "
    "not contain the answer, reply exactly: INSUFFICIENT_EVIDENCE."
)


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    ctx = "\n\n".join(
        f"[chunk:{c.chunk_id[:8]}] ({c.title} \u2014 \u00a7{c.section} \u2014 p.{c.page})\n{c.content}"
        for c in chunks)
    return f"Question: {question}\n\nContext:\n{ctx}"


def verify_citations(answer: str, chunk_ids: list[str]) -> tuple[list[str], list[str]]:
    """Return (valid_ids, invalid_prefixes). Any invalid prefix means the
    response must be rejected per spec — we never silently discard bad
    citations."""
    valid: list[str] = []
    invalid: list[str] = []
    # First: find all [chunk:...] markers (any content inside brackets)
    for raw_match in _CITE_RAW.findall(answer):
        # Check if it's a valid 8+ hex prefix
        hex_match = re.fullmatch(r"[0-9a-fA-F]{8,}", raw_match)
        if not hex_match:
            # Not valid hex at all — definitely invalid
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


def generate_answer(llm: LLMProvider, question: str, chunks: list[RetrievedChunk]) -> str:
    answer = llm.generate(SYSTEM_PROMPT, build_user_prompt(question, chunks))
    if answer.strip() == "INSUFFICIENT_EVIDENCE":
        raise CitationError("model declined: insufficient evidence")
    valid, invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    if invalid:
        raise CitationError(f"invalid citations: {invalid}")
    if not valid:
        raise CitationError("answer carried no valid citations")
    return answer
