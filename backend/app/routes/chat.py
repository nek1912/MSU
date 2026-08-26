from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.domains import get_anchor_store
from app.db import get_supabase
from app.generation import (SYSTEM_PROMPT, CitationError, build_user_prompt,
                            verify_citations)
from app.language import normalize_language
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.embeddings import get_embedding_provider
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.retrieval import RetrievedChunk, evidence_gate, retrieve
from app.session_store import get_state, touch_session

router = APIRouter()

ABSTAIN_TEXT = {
    "en": "I could not find this in official sources, so I won't guess. "
          "Please try rephrasing or ask about cooperative rules, PACS, schemes, "
          "PMFBY, agriculture, or financial literacy.",
    "hi": "मुझे आधिकारिक स्रोतों में इसका उत्तर नहीं मिला, इसलिए अनुमान नहीं लगाऊंगा। "
          "कृपया प्रश्न दूसरे शब्दों में पूछें या सहकारिता, पीएसीएस, योजनाओं, "
          "पीएमएफबीवाई, कृषि या वित्तीय साक्षरता के बारे में पूछें।",
}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi"]
    state: str | None = None


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
        chunks = retrieve(get_supabase(), embedding, domain, resolved_state)
        gate = evidence_gate(chunks, expected_domain=domain,
                             expected_state=resolved_state)
        if gate.abstained:
            return _abstain(lang, gate.reason)
        prompt = build_user_prompt(req.question, chunks)
        answer = grounded_answer(GroqLLMProvider(settings),
                                 GeminiLLMProvider(settings), SYSTEM_PROMPT, prompt)
        citations = _citations_from(answer, chunks)
        return {"answer": answer, "language": lang, "domain": domain,
                "confidence": gate.confidence, "citations": citations,
                "abstained": False, "follow_up_question": None}
    except (CitationError, AllProvidersFailedError):
        return _abstain(lang, "provider_or_citation_failure")
    except Exception:
        return _abstain(lang, "unexpected_error")


def _abstain(lang: str, _reason: str | None) -> dict:
    return {"answer": ABSTAIN_TEXT[lang], "language": lang, "domain": "unknown",
            "confidence": 0.0, "citations": [], "abstained": True,
            "follow_up_question": None}


def _citations_from(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    ids = verify_citations(answer, [c.chunk_id for c in chunks])
    by_id = {c.chunk_id: c for c in chunks}
    return [{"title": by_id[i].title, "page": by_id[i].page,
             "url": by_id[i].source_url} for i in ids]
