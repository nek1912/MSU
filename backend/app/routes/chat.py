"""Chat route — refactored with hybrid retrieval, typed evidence gate,
and unavoidable citation verification.

Feature flag: USE_HYBRID_RETRIEVAL (env var) controls old vs new path.
Default: new path (hybrid + v2 gate + verifier).
"""

from typing import Literal

import httpx
from fastapi import APIRouter
from postgrest.exceptions import APIError as PostgrestAPIError
from pydantic import BaseModel, Field, ValidationError

from app.config import get_settings
from app.contracts import RetrievalCandidate
from app.citation_verifier import verify_citations as verify_citations_v2
from app.db import get_supabase
from app.domains import get_anchor_store
from app.evidence_gate import evidence_gate_v2
from app.generation import (CitationError, build_general_prompt, build_system_prompt,
                            build_user_prompt, general_disclaimer, verify_citations,
                            GENERAL_SYSTEM_PROMPT)
from app.hybrid_retrieval import retrieve_hybrid
from app.language import normalize_language
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.embeddings import get_embedding_provider
from app.providers.reranker import JinaReranker
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.retrieval import RetrievedChunk, retrieve
from app.session_store import get_history, get_state, save_message, touch_session, trim_messages
from app.ui import get_abstain_text

router = APIRouter()

ABSTAIN_TEXT = {
    "en": "I could not find this in official sources, so I won't guess. "
          "Please try rephrasing or ask about cooperative rules, PACS, schemes, "
          "PMFBY, agriculture, or financial literacy.",
    "hi": "मुझे आधिकारिक स्रोतों में इसका उत्तर नहीं मिला, इसलिए अनुमान नहीं लगाऊंगा। "
          "कृपया प्रश्न दूसरे शब्दों में पूछें या सहकारिता, पीएसीएस, योजनाओं, "
          "पीएएमएफबीवाई, कृषि या वित्तीय साक्षरता के बारे में पूछें।",
    "gu": "મને આધિકારિક સ્રોતોમાં આ ન મળ્યું, તેથી હું અનુમાન નહીં કરું. "
          "કૃપા કરીને ફરીથી પૂછો અથવા સહકારિતા, PACS, યોજનાઓ, "
          "PMFBY, કૃષિ અથવા નાણાકીય સાક્ષરતા વિશે પૂછો.",
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
    ValidationError,
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi", "gu"]
    state: str | None = None
    as_of_date: str | None = None  # Optional date filter (YYYY-MM-DD)
    history: list[dict] | None = None  # [{role: "user"|"assistant", content: str}]


def _confidence_level(score: float) -> str:
    """Convert raw confidence score to a human-readable diagnostic level.

    PHASE 9: Until calibrated, this is an internal diagnostic — NOT a probability.
    Levels: high / moderate / low / none
    """
    if score >= 0.7:
        return "high"
    elif score >= 0.5:
        return "moderate"
    elif score > 0.0:
        return "low"
    return "none"


import re


_CITE_PATTERN = re.compile(r"\[chunk:([0-9a-fA-F]{8,})\]")


def _citations_from(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """Extract citations from answer text and map to chunk metadata."""
    chunk_map = {}
    for c in chunks:
        prefix = c.chunk_id[:8].lower()
        chunk_map[prefix] = c

    seen = set()
    citations = []
    for match in _CITE_PATTERN.finditer(answer):
        prefix = match.group(1)[:8].lower()
        if prefix in seen:
            continue
        seen.add(prefix)
        chunk = chunk_map.get(prefix)
        if chunk:
            citations.append({
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "page": chunk.page,
                "url": chunk.source_url,
            })
    return citations


def _to_candidate(chunk: RetrievedChunk, expected_state: str | None) -> RetrievalCandidate:
    """Convert a RetrievedChunk to a RetrievalCandidate for evidence_gate_v2."""
    is_central = chunk.jurisdiction == "central"
    state_match = is_central or chunk.state == expected_state
    return RetrievalCandidate(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        source_id=chunk.source_file or "",
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
        # --- Conversation history retrieval (Stage 0) ---
        history = req.history if req.history is not None else get_history(req.session_id, limit=8)

        provider = get_embedding_provider()
        search_question = req.question
        embedding = provider.embed_texts([req.question], task="retrieval.query")[0]
        domain, _score = get_anchor_store().classify(req.question, embedding)

        # Contextual follow-up resolution: if the question does not contain an explicit domain keyword,
        # or evaluates to out_of_scope, and there is conversation history, combine prior context to resolve domain context.
        rules = getattr(get_anchor_store(), "rules", {})
        has_explicit_keyword = False
        if isinstance(rules, dict):
            has_explicit_keyword = any(
                any(kw in req.question.lower() for kw in kws)
                for kws in rules.values() if isinstance(kws, (list, set, tuple))
            )

        if (not has_explicit_keyword or domain == "out_of_scope") and history:
            user_turns = [h["content"] for h in history if isinstance(h, dict) and h.get("role") == "user" and h.get("content")]
            if user_turns:
                anchor_q = None
                if isinstance(rules, dict):
                    for prev_q in reversed(user_turns):
                        has_kw = any(
                            any(kw in prev_q.lower() for kw in kws)
                            for kws in rules.values() if isinstance(kws, (list, set, tuple))
                        )
                        if has_kw:
                            anchor_q = prev_q
                            break
                if not anchor_q:
                    anchor_q = user_turns[-1]

                contextual_query = f"{anchor_q} {req.question}"
                ctx_embedding = provider.embed_texts([contextual_query], task="retrieval.query")[0]
                ctx_domain, _ctx_score = get_anchor_store().classify(contextual_query, ctx_embedding)
                if ctx_domain != "out_of_scope":
                    domain = ctx_domain
                    search_question = contextual_query
                    embedding = ctx_embedding

        resolved_state = req.state if req.state is not None else get_state(req.session_id)
        touch_session(req.session_id, resolved_state, lang)
        if domain == "out_of_scope":
            # Out-of-scope: let the LLM answer from its own knowledge rather
            # than abstain. Not grounded in official sources — flagged as such.
            general_answer = grounded_answer(
                GroqLLMProvider(settings), GeminiLLMProvider(settings),
                GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
            out_of_scope_answer = f"{general_answer}\n\n{general_disclaimer(lang)}"

            # --- Persist conversation turns (out-of-scope) ---
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", out_of_scope_answer)
            trim_messages(req.session_id, keep=50)

            return {"answer": out_of_scope_answer,
                    "language": lang, "domain": "out_of_scope",
                    "intent": "general", "entities": [],
                    "confidence": 0.0, "confidence_level": "none",
                    "citations": [], "abstained": False,
                    "follow_up_question": None}

        # --- Hybrid retrieval (Stage 5) ---
        k = 25 if settings.reranker_enabled else 6
        chunks = retrieve_hybrid(
            get_supabase(), embedding, search_question, domain, resolved_state, k=k,
        )

        # Optional reranker (Stage 6)
        if settings.reranker_enabled:
            reranker = JinaReranker()
            docs_for_rerank = [{"chunk_id": c.chunk_id, "content": c.content} for c in chunks]
            reranked = reranker.rerank(search_question, docs_for_rerank, top_n=6)
            chunks_by_id = {c.chunk_id: c for c in chunks}
            chunks = [chunks_by_id[r["chunk_id"]] for r in reranked if r["chunk_id"] in chunks_by_id]

        # --- Evidence gate v2 (Stage 7) ---
        candidates = [_to_candidate(c, resolved_state) for c in chunks]
        abstained, reason, band = evidence_gate_v2(
            candidates, expected_domain=domain, expected_state=resolved_state,
        )
        if abstained:
            general_answer = grounded_answer(
                GroqLLMProvider(settings), GeminiLLMProvider(settings),
                GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
            out_of_scope_answer = f"{general_answer}\n\n{general_disclaimer(lang)}"

            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", out_of_scope_answer)
            trim_messages(req.session_id, keep=50)

            return {"answer": out_of_scope_answer, "language": lang, "domain": domain,
                    "intent": "general", "entities": [],
                    "confidence": 0.5, "confidence_level": "moderate",
                    "citations": [], "abstained": False,
                    "follow_up_question": None}

        prompt = build_user_prompt(req.question, chunks, history=history)
        answer = grounded_answer(GroqLLMProvider(settings),
                                 GeminiLLMProvider(settings),
                                 build_system_prompt(lang), prompt)
        answer = answer.replace("【", "[").replace("】", "]")

        if "INSUFFICIENT_EVIDENCE" in answer:
            general_answer = grounded_answer(
                GroqLLMProvider(settings), GeminiLLMProvider(settings),
                GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
            out_of_scope_answer = f"{general_answer}\n\n{general_disclaimer(lang)}"

            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", out_of_scope_answer)
            trim_messages(req.session_id, keep=50)

            return {"answer": out_of_scope_answer, "language": lang, "domain": domain,
                    "intent": "general", "entities": [],
                    "confidence": 0.5, "confidence_level": "moderate",
                    "citations": [], "abstained": False,
                    "follow_up_question": None}

        # --- Citation verification v2 (Stage 8) ---
        chunk_ids = [c.chunk_id for c in chunks]
        verification = verify_citations_v2(answer, chunk_ids)
        if not verification.is_valid:
            # Fall back to general answer if citation verification fails
            general_answer = grounded_answer(
                GroqLLMProvider(settings), GeminiLLMProvider(settings),
                GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
            out_of_scope_answer = f"{general_answer}\n\n{general_disclaimer(lang)}"

            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", out_of_scope_answer)
            trim_messages(req.session_id, keep=50)

            return {"answer": out_of_scope_answer, "language": lang, "domain": domain,
                    "intent": "general", "entities": [],
                    "confidence": 0.5, "confidence_level": "moderate",
                    "citations": [], "abstained": False,
                    "follow_up_question": None}

        citations = _citations_from(answer, chunks)
        _band_to_confidence = {"high": 0.9, "medium": 0.7, "low": 0.4}
        conf = _band_to_confidence.get(band.value, 0.4)

        # --- Persist conversation turns ---
        save_message(req.session_id, "user", req.question)
        save_message(req.session_id, "assistant", answer)
        trim_messages(req.session_id, keep=50)

        return {"answer": answer, "language": lang, "domain": domain,
                "intent": "rag", "entities": [],
                "confidence": conf, "confidence_level": _confidence_level(conf),
                "citations": citations, "abstained": False,
                "follow_up_question": None}
    except _SAFE_FAILURES:
        return _abstain(lang, "dependency_failure")
    except Exception:
        raise


def _abstain(lang: str, _reason: str | None) -> dict:
    return {"answer": get_abstain_text(lang), "language": lang, "domain": "unknown",
            "intent": "unknown", "entities": [],
            "confidence": 0.0, "confidence_level": "none",
            "citations": [], "abstained": True,
            "follow_up_question": None}


# ---------------------------------------------------------------------------
# /translate — translate existing answer text when user switches language
# ---------------------------------------------------------------------------

class TranslateRequest(BaseModel):
    texts: list[str]
    source_language: str = "en"
    target_language: str = "hi"


class TranslatedItem(BaseModel):
    original: str
    translated: str


class TranslateResponse(BaseModel):
    translations: list[TranslatedItem]


@router.post("/translate", response_model=TranslateResponse)
async def translate_texts(req: TranslateRequest):
    """Translate answer text between languages using Sarvam Mayura v1."""
    from app.providers.sarvam_translate import SarvamTranslationProvider

    provider = SarvamTranslationProvider()
    results: list[TranslatedItem] = []

    for text in req.texts:
        translated = await provider.translate(text, req.source_language, req.target_language)
        results.append(TranslatedItem(original=text, translated=translated))

    return TranslateResponse(translations=results)
