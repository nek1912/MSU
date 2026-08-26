import re

from app.providers.base import LLMProvider
from app.retrieval import RetrievedChunk

_CITE = re.compile(r"\[chunk:([0-9a-f]{8})\]")


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


def verify_citations(answer: str, chunk_ids: list[str]) -> list[str]:
    valid: list[str] = []
    for prefix in _CITE.findall(answer):
        for cid in chunk_ids:
            if cid.startswith(prefix) and cid not in valid:
                valid.append(cid)
    return valid


def generate_answer(llm: LLMProvider, question: str, chunks: list[RetrievedChunk]) -> str:
    answer = llm.generate(SYSTEM_PROMPT, build_user_prompt(question, chunks))
    if answer.strip() == "INSUFFICIENT_EVIDENCE":
        raise CitationError("model declined: insufficient evidence")
    if not verify_citations(answer, [c.chunk_id for c in chunks]):
        raise CitationError("answer carried no valid citations")
    return answer
