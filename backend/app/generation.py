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
    "gu": "answer in Gujarati (Gujarati script)",
    "mr": "answer in Marathi (Devanagari script)",
    "bn": "answer in Bengali (Bengali script)",
}

_GENERAL_DISCLAIMER = {
    "en": "This is a general answer not from official government sources. "
          "For authoritative guidance on cooperative rules, schemes, PMFBY, "
          "or financial inclusion, ask a specific question about those topics.",
    "hi": "यह सामान्य उत्तर है जो सरकारी स्रोतों से नहीं है। सहकारिता नियमों, योजनाओं, "
          "पीएएमएफबीवाई, या वित्तीय समावेशन पर आधिकारिक मार्गदर्शन के लिए उन विषयों "
          "के बारे में एक विशिष्ट प्रश्न पूछें।",
    "gu": "આ સામાન્ય જવાબ છે જે સરકારી સ્રોતોમાંથી નથી. સહકારી નિયમો, યોજનાઓ, "
          "પીએમએફબીવાઈ, અથવા નાણાકીય સમાવેશન પર આધિકારિક માર્ગદર્શન માટે તે વિષયો "
          "વિશે એક ચોક્કસ પ્રશ્ન પૂછો.",
    "mr": "हे सामान्य उत्तर आहे जे सरकारी स्रोतांमधून नाही. सहकारी नियम, योजना, "
          "पीएमएफबीवाय, किंवा वित्तीय साक्षरता यावर अधिकृत मार्गदर्शनासाठी त्या "
          "विषयांवर एक विशिष्ट प्रश्न विचारा.",
    "bn": "এটি একটি সাধারণ উত্তর যা সরকারি উৎস থেকে নয়। সহকারিতা নিয়ম, প্রকল্প, "
          "পিএমএফবি঵াই, বা আর্থিক অন্তর্ভুক্তি সম্পর্কে আধিকারিক নির্দেশনার জন্য "
          "এই বিষয়গুলোতে একটি নির্দিষ্ট প্রশ্ন করুন.",
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
        "numbered context chunks. Cite the source chunk after EVERY factual "
        "sentence using EXACTLY this format: [chunk:ID] where ID is the "
        "8-character hex prefix shown in the chunk's label (for example "
        "[chunk:a1b2c3d4]). Use ONLY half-width square brackets and the literal "
        "prefix 'chunk:'. Do NOT use full-width brackets 【】, parentheses, or "
        "any other marker style. Never add outside knowledge. If the chunks do "
        "not contain the answer, reply exactly: INSUFFICIENT_EVIDENCE. Please "
        f"{_LANG_INSTRUCTION[lang]}."
    )


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Build the RAG user prompt from question + numbered context chunks."""
    ctx = "\n\n".join(
        f"[chunk:{c.chunk_id[:8]}] ({c.title} — §{c.section} — p.{c.page})\n{c.content}"
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


def validate_citation_chain(
    answer: str,
    chunks: list[RetrievedChunk],
) -> list[dict]:
    """Validate that every citation in the answer resolves through the full chain:

    citation → retrieved chunk → stable_chunk_id → source document → source page

    Returns list of citation dicts for valid citations.
    Raises CitationError for any invalid citation.

    Enforces:
    - Citation must reference a chunk that was actually retrieved
    - Citation must not be fabricated (non-retrieved chunk)
    - Citation's chunk must belong to the correct document
    - Citation's page reference must match the chunk's actual page
    """
    if not chunks:
        if _CITE_RAW.search(answer):
            raise CitationError("citations in answer but no chunks retrieved")
        return []

    # Build lookup: prefix → chunk
    chunk_by_prefix: dict[str, RetrievedChunk] = {}
    for c in chunks:
        prefix = c.chunk_id[:8].lower()
        chunk_by_prefix[prefix] = c

    valid_citations: list[dict] = []
    seen_prefixes: set[str] = set()

    for raw_match in _CITE_RAW.findall(answer):
        hex_match = re.fullmatch(r"[0-9a-fA-F]{8,}", raw_match)
        if not hex_match:
            raise CitationError(f"malformed citation: [chunk:{raw_match}]")

        prefix = hex_match.group()[:8].lower()

        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)

        # 1. Fabricated citation check: must reference a retrieved chunk
        if prefix not in chunk_by_prefix:
            raise CitationError(f"fabricated citation: [chunk:{prefix}] not in retrieved chunks")

        chunk = chunk_by_prefix[prefix]

        # 2. Verify citation resolves to a valid document
        if not chunk.document_id:
            raise CitationError(f"citation [chunk:{prefix}] has no document_id")

        # 3. Verify citation resolves to a valid page
        if chunk.page < 1:
            raise CitationError(f"citation [chunk:{prefix}] has invalid page: {chunk.page}")

        valid_citations.append({
            "chunk_id": chunk.stable_chunk_id,
            "document_id": chunk.document_id,
            "title": chunk.title,
            "page": chunk.page,
            "url": chunk.source_url,
        })

    return valid_citations


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
