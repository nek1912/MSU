"""Chat route — refactored with hybrid retrieval, typed evidence gate,
and unavoidable citation verification.

Feature flag: USE_HYBRID_RETRIEVAL (env var) controls old vs new path.
Default: new path (hybrid + v2 gate + verifier).
"""

from typing import Literal

import httpx
from fastapi import APIRouter
from postgrest.exceptions import APIError as PostgrestAPIError
from pydantic import BaseModel, Field

from app.config import get_settings
from app.contracts import RetrievalCandidate
from app.citation_verifier import verify_citations as verify_citations_v2
from app.db import get_supabase
from app.domains import get_anchor_store
from app.evidence_gate import evidence_gate_v2
from app.generation import SYSTEM_PROMPT, CitationError, build_user_prompt, verify_citations
from app.hybrid_retrieval import retrieve_hybrid
from app.language import normalize_language
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.embeddings import get_embedding_provider
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.retrieval import RetrievedChunk, retrieve
from app.session_store import get_state, touch_session

router = APIRouter()

ABSTAIN_TEXT = {
    "en": "I could not find this in official sources, so I won't guess. "
          "Please try rephrasing or ask about cooperative rules, PACS, schemes, "
          "PMFBY, agriculture, or financial literacy.",
    "hi": "मुझे आधिकारिक स्रोतों में इसका उत्तर नहीं मिला, इसलिए अनुमान नहीं लगाऊंगा। "
          "कृपया प्रश्न दूसरे शब्दों में पूछें या सहकारिता, पीएसीएस, योजनाओं, "
          "पीएएमएफबीवाई, कृषि या वित्तीय साक्षरता के बारे में पूछें।",
}

# Exceptions that represent expected dependency failures (not programmer bugs)
# → should return 200 + abstained per frozen contract
_SAFE_FAILURES = (
    CitationError,
    AllProvidersFailedError,
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.HTTPStatusError,
    PostgrestAPIError,
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi"]
    state: str | None = None


def _to_candidate(chunk: RetrievedChunk, expected_state: str | None) -> RetrievalCandidate:
    """Convert a RetrievedChunk to a RetrievalCandidate for evidence_gate_v2."""
    is_central = chunk.jurisdiction == "central"
    state_match = is_central or chunk.state == expected_state
    return RetrievalCandidate(
        chunk_id=chunk.chunk_id,
        document_id="",
        source_id="",
        dense_score=chunk.similarity,
        filter_decisions={
            "domain": True,
            "active": True,
            "is_central": is_central,
            "state_match": state_match,
        },
    )


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    settings = get_settings()
    lang = normalize_language(req.language, req.question)
    try:
        provider = get_embedding_provider()          # cached singleton (P0-1)
        embedding = provider.embed_texts([req.question])[0]
        domain, _score = get_anchor_store().classify(req.question, embedding)
        # Session is authoritative for jurisdiction (P1-7): explicit request
        # state updates it; a null state continues the session's prior state.
        resolved_state = req.state if req.state is not None else get_state(req.session_id)
        touch_session(req.session_id, resolved_state, lang)
        if domain == "out_of_scope":
            return _abstain(lang, "out_of_scope")

        # --- Hybrid retrieval (Stage 5) ---
        chunks = retrieve_hybrid(
            get_supabase(), embedding, req.question, domain, resolved_state,
        )

        # --- Evidence gate v2 (Stage 7) ---
        candidates = [_to_candidate(c, resolved_state) for c in chunks]
        abstained, reason, band = evidence_gate_v2(
            candidates, expected_domain=domain, expected_state=resolved_state,
        )
        if abstained:
            return _abstain(lang, reason.value if reason else None)

        prompt = build_user_prompt(req.question, chunks)
        answer = grounded_answer(GroqLLMProvider(settings),
                                 GeminiLLMProvider(settings), SYSTEM_PROMPT, prompt)

        # --- Citation verification v2 (Stage 8) ---
        chunk_ids = [c.chunk_id for c in chunks]
        verification = verify_citations_v2(answer, chunk_ids)
        if not verification.is_valid:
            return _abstain(lang, verification.reason.value if verification.reason else "citation_failure")

        citations = _citations_from(answer, chunks)
        _band_to_confidence = {"high": 0.9, "medium": 0.7, "low": 0.4}
        return {"answer": answer, "language": lang, "domain": domain,
                "confidence": _band_to_confidence.get(band.value, 0.4),
                "citations": citations, "abstained": False,
                "follow_up_question": None}
    except _SAFE_FAILURES:
        # Known dependency failures → contract-valid abstention
        return _abstain(lang, "dependency_failure")
    except Exception:
        # Unknown failures (programmer bugs) → let FastAPI return 500
        raise


def _abstain(lang: str, _reason: str | None) -> dict:
    return {"answer": ABSTAIN_TEXT[lang], "language": lang, "domain": "unknown",
            "confidence": 0.0, "citations": [], "abstained": True,
            "follow_up_question": None}


def _citations_from(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    valid, _invalid = verify_citations(answer, [c.chunk_id for c in chunks])
    by_id = {c.chunk_id: c for c in chunks}
    return [{"title": by_id[i].title, "page": by_id[i].page,
             "url": by_id[i].source_url} for i in valid]
