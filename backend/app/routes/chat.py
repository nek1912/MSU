"""Chat route — HTTP layer delegating to RAGOrchestrator.

Keeps: ChatRequest model, language detection, domain classification,
       context disambiguation, out-of-scope check, grievance workflow,
       translation helpers.

Delegates to RAGOrchestrator for: evidence merging, prompt building,
LLM generation, citation handling, confidence calculation.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.domains import get_anchor_store
from app.grievance.workflow import GrievanceWorkflow
from app.language import detect_query_languages
from app.providers.embeddings import get_embedding_provider
from app.providers.sarvam_translator import SarvamTranslator
from app.providers.translator import AzureTranslator
from app.resolve_response_language import resolve_and_remember
from app.services.rag_orchestrator import RAGOrchestrator
from app.session_store import get_history, get_state, save_message, touch_session, trim_messages
from app.speech_text import prepare_speech_text, segment_speech
from app.ui import get_abstain_text
from app.web_rag.query_classifier import QueryClassifier, QueryClassification

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Singleton lazy-init helpers ──────────────────────────────────────────────

_query_classifier: QueryClassifier | None = None
_grievance_workflow: GrievanceWorkflow | None = None
_rag_orchestrator: RAGOrchestrator | None = None


def _get_query_classifier() -> QueryClassifier:
    global _query_classifier
    if _query_classifier is None:
        _query_classifier = QueryClassifier()
    return _query_classifier


def _get_grievance_workflow() -> GrievanceWorkflow:
    global _grievance_workflow
    if _grievance_workflow is None:
        _grievance_workflow = GrievanceWorkflow()
    return _grievance_workflow


def _get_rag_orchestrator(settings: Settings) -> RAGOrchestrator:
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator(settings)
    return _rag_orchestrator


# ── Request model ────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str
    language: Literal["en", "hi", "gu", "mr", "bn", "ta"]
    ui_language_explicit: bool = False
    state: str | None = None
    as_of_date: str | None = None
    history: list[dict] | None = None


# ── Helpers ──────────────────────────────────────────────────────────────────


def _confidence_level(score: float) -> str:
    if score >= 0.7:
        return "high"
    elif score >= 0.5:
        return "moderate"
    elif score > 0.0:
        return "low"
    return "none"


def _translate_to_english(question: str, input_lang: str, settings: Settings) -> str:
    if input_lang == "en":
        return question
    sarvam = SarvamTranslator(settings)
    if sarvam.configured:
        try:
            return sarvam.translate(question, to="en", source=input_lang)
        except Exception:
            logger.warning("Sarvam translation failed, trying Azure")
    try:
        return AzureTranslator(settings).translate(question, to="en", source=input_lang)
    except Exception:
        logger.warning("Azure translation failed, using original")
        return question


def _translate_from_english(text: str, target_lang: str, settings: Settings) -> str:
    if target_lang == "en":
        return text
    sarvam = SarvamTranslator(settings)
    if sarvam.configured:
        try:
            return sarvam.translate(text, to=target_lang, source="en")
        except Exception:
            logger.warning("Sarvam back-translation failed")
    try:
        return AzureTranslator(settings).translate(text, to=target_lang, source="en")
    except Exception:
        logger.warning("Azure back-translation failed, returning English answer")
        return text


def _abstain(lang: str, session_id: str | None = None) -> dict:
    answer = get_abstain_text(lang)
    return {
        "answer": answer, "language": lang, "domain": "unknown",
        "intent": "unknown", "entities": [],
        "confidence": 0.0, "confidence_level": "none",
        "citations": [], "abstained": True,
        "speech_text": prepare_speech_text(answer),
        "speech_segments": [],
        "follow_up_question": None,
        "mode": "dual_rag", "conversation_id": session_id or "",
    }


def _rag_response_to_dict(resp, lang: str, session_id: str) -> dict:
    return {
        "answer": resp.answer,
        "language": lang,
        "domain": resp.domain,
        "intent": resp.domain,
        "entities": [],
        "confidence": resp.confidence,
        "confidence_level": _confidence_level(resp.confidence),
        "citations": resp.citations,
        "abstained": resp.abstained,
        "speech_text": resp.speech_text,
        "speech_segments": resp.speech_segments,
        "follow_up_question": resp.follow_up_question,
        "mode": resp.mode,
        "conversation_id": session_id,
    }


@dataclass
class _ChatContext:
    """Resolved context shared between /chat and /chat/stream."""
    settings: Settings
    lang: str
    input_lang: str
    english_query: str
    embedding: list[float]
    domain: str
    classification: QueryClassification
    history: list[dict] | None
    resolved_state: str | None
    language_mix: dict[str, float] | None = None


@lru_cache(maxsize=1000)
def _cached_embedding(query_hash: str, query: str):
    return get_embedding_provider().embed_texts([query], task="retrieval.query")[0]

@lru_cache(maxsize=500)
def _cached_classification(query_lower: str):
    return _get_query_classifier().classify(query_lower)

async def _resolve_context(req: ChatRequest) -> _ChatContext:
    """Detect language, translate, classify domain, disambiguate context."""
    settings = get_settings()
    ui_code = req.language if req.ui_language_explicit else None
    lang = resolve_and_remember(req.session_id, req.question, ui_code)
    detected = detect_query_languages(req.question)
    input_lang = detected.get("dominant") or "en"
    language_mix = detected.get("language_mix")

    async def get_embedding():
        return await asyncio.to_thread(_cached_embedding, req.question, req.question)

    async def get_translation():
        if input_lang != "en":
            return await asyncio.to_thread(_translate_to_english, req.question, input_lang, settings)
        return req.question

    # Run embedding and translation in parallel
    embedding, english_query = await asyncio.gather(
        get_embedding(), get_translation()
    )

    # Classify on the translated English query for robust keyword matching
    classification = await asyncio.to_thread(_cached_classification, english_query.lower())

    history = req.history if req.history is not None else get_history(req.session_id, limit=8)
    
    # We use english_query for domain classification fallback inside anchor store
    domain, _score = await asyncio.to_thread(get_anchor_store().classify, english_query, embedding)

    # AnchorStore context disambiguation
    rules = getattr(get_anchor_store(), "rules", {})
    has_explicit_keyword = False
    if isinstance(rules, dict):
        has_explicit_keyword = any(
            any(kw in english_query.lower() for kw in kws)
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

            contextual_query = f"{anchor_q} {english_query}"
            ctx_embedding = get_embedding_provider().embed_texts([contextual_query], task="retrieval.query")[0]
            ctx_domain, _ctx_score = get_anchor_store().classify(contextual_query, ctx_embedding)
            if ctx_domain != "out_of_scope":
                domain = ctx_domain
                english_query = contextual_query
                embedding = ctx_embedding

    resolved_state = req.state if req.state is not None else get_state(req.session_id)

    return _ChatContext(
        settings=settings,
        lang=lang,
        input_lang=input_lang,
        english_query=english_query,
        embedding=embedding,
        domain=domain,
        classification=classification,
        history=history,
        resolved_state=resolved_state,
        language_mix=language_mix,
    )


# ── Main chat endpoint ──────────────────────────────────────────────────────


@router.post("/chat")
async def chat(req: ChatRequest) -> dict:
    question = req.question.strip()
    if not question:
        return _abstain(req.language, session_id=req.session_id)

    try:
        ctx = await _resolve_context(req)

        # Grievance queries → dedicated workflow
        if ctx.classification.domain == "grievance":
            workflow = _get_grievance_workflow()
            result = workflow.process_message(
                user_message=req.question,
                conversation_id=req.session_id,
                user_id=req.session_id,
            )
            response_text = result.response
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", response_text)
            trim_messages(req.session_id, keep=50)
            return {
                "answer": response_text,
                "language": ctx.lang,
                "domain": "grievance",
                "intent": ctx.classification.intent,
                "entities": [],
                "confidence": ctx.classification.confidence,
                "confidence_level": _confidence_level(ctx.classification.confidence),
                "citations": [],
                "abstained": False,
                "speech_text": prepare_speech_text(response_text),
                "speech_segments": segment_speech(response_text, ctx.lang),
                "follow_up_question": None,
                "mode": "grievance",
                "conversation_id": req.session_id,
            }

        touch_session(req.session_id, ctx.resolved_state, ctx.lang)

        # Out-of-scope → abstain (no RAG needed)
        if ctx.domain == "out_of_scope":
            abstain_msg = "I am a cooperative governance assistant and can only answer questions related to cooperatives, agriculture schemes, financial inclusion, and legal provisions in India. Please ask a question within my scope."
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", abstain_msg)
            trim_messages(req.session_id, keep=50)
            return {
                "answer": abstain_msg, "language": ctx.lang, "domain": "out_of_scope",
                "intent": "general", "entities": [],
                "confidence": 0.0, "confidence_level": "none",
                "citations": [], "abstained": True,
                "speech_text": prepare_speech_text(abstain_msg),
                "speech_segments": segment_speech(abstain_msg, ctx.lang),
                "follow_up_question": None,
                "mode": "dual_rag", "conversation_id": req.session_id,
            }

        # ── Core RAG via orchestrator ────────────────────────────────────
        orchestrator = _get_rag_orchestrator(ctx.settings)
        rag_response = await orchestrator.run(
            query=req.question,
            english_query=ctx.english_query,
            embedding=ctx.embedding,
            domain=ctx.domain,
            state=ctx.resolved_state,
            classification=ctx.classification,
            history=ctx.history,
            lang=ctx.lang,
            session_id=req.session_id,
            language_mix=ctx.language_mix,
        )

        # The LLM is instructed to respond in the user's language directly.
        # This translation call is a secondary safety net for any edge case
        # where the LLM does not fully comply with the language instruction.
        if ctx.lang != "en":
            rag_response.answer = _translate_from_english(rag_response.answer, ctx.lang, ctx.settings)
            rag_response.speech_text = prepare_speech_text(rag_response.answer)
            rag_response.speech_segments = segment_speech(rag_response.answer, ctx.lang)

        # ── Session persistence ──────────────────────────────────────────
        save_message(req.session_id, "user", req.question)
        save_message(req.session_id, "assistant", rag_response.answer)
        trim_messages(req.session_id, keep=50)

        return _rag_response_to_dict(rag_response, ctx.lang, req.session_id)

    except Exception:
        logger.exception("Chat route failed")
        return _abstain(req.language, session_id=req.session_id)


# ── SSE streaming endpoint ──────────────────────────────────────────────────

_THINKING_MESSAGES = {
    "en": ["Searching official documents & web...", "Analyzing evidence from both sources...", "Preparing answer..."],
    "hi": ["आधिकारिक दस्तावेज़ और वेब खोज रहे हैं...", "दोनों स्रोतों से साक्ष्य का विश्लेषण...", "उत्तर तैयार कर रहे हैं..."],
    "gu": ["અધિકૃત દસ્તાવેજો અને વેબ શોધી રહ્યા છીએ...", "બંને સ્રોતોમાંથી પુરાવાનું વિશ્લેષણ...", "જવાબ તૈયાર કરી રહ્યા છીએ..."],
    "mr": ["अधिकृत दस्तावेज आणि वेब शोधत आहोत...", "दोन्ही स्रोतांमधून पुराव्याचे विश्लेषण...", "उत्तर तयार करत आहोत..."],
    "bn": ["সরকারি নথিপত্র এবং ওয়েব খুঁজছি...", "উভয় উৎস থেকে প্রমাণ বিশ্লেষণ...", "উত্তর প্রস্তুত করছি..."],
    "ta": ["அதிகாரப்பூர்வ ஆவணங்கள் மற்றும் வலைத்தளத்தை தேடுகிறோம்...", "இரண்டு மூலங்களிலிருந்தும் சான்றுகளை பகுப்பாய்வு செய்கிறோம்...", "பதிலை தயாரிக்கிறோம்..."],
}


def _sse_event(event: str, data: dict | str) -> str:
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming version — delegates to orchestrator, emits SSE events."""

    async def generate():
        try:
            # Fire first thinking event IMMEDIATELY so user sees feedback
            initial_lang = req.language or "en"
            initial_msgs = _THINKING_MESSAGES.get(initial_lang, _THINKING_MESSAGES["en"])
            yield _sse_event("thinking", {"text": initial_msgs[0]})

            ctx = await _resolve_context(req)
            thinking_msgs = _THINKING_MESSAGES.get(ctx.lang, _THINKING_MESSAGES["en"])

            # Grievance → dedicated workflow
            if ctx.classification.domain == "grievance":
                yield _sse_event("thinking", {"text": thinking_msgs[0]})
                workflow = _get_grievance_workflow()
                result = workflow.process_message(
                    user_message=req.question,
                    conversation_id=req.session_id,
                    user_id=req.session_id,
                )
                answer_text = result.response
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", answer_text)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {
                    "domain": "grievance", "confidence": ctx.classification.confidence,
                    "confidence_level": _confidence_level(ctx.classification.confidence),
                    "citations": [], "abstained": False, "language": ctx.lang,
                })
                for token in answer_text.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            touch_session(req.session_id, ctx.resolved_state, ctx.lang)

            # Out-of-scope → abstain
            if ctx.domain == "out_of_scope":
                yield _sse_event("thinking", {"text": thinking_msgs[1]})
                abstain_msg = "I am a cooperative governance assistant and can only answer questions related to cooperatives, agriculture schemes, financial inclusion, and legal provisions in India. Please ask a question within my scope."
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", abstain_msg)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {
                    "domain": "out_of_scope", "confidence": 0.0,
                    "confidence_level": "none", "citations": [],
                    "abstained": True, "language": ctx.lang,
                })
                for token in abstain_msg.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            # ── Core RAG via orchestrator ────────────────────────────────
            yield _sse_event("thinking", {"text": thinking_msgs[1]})

            orchestrator = _get_rag_orchestrator(ctx.settings)
            rag_response = await orchestrator.run(
                query=req.question,
                english_query=ctx.english_query,
                embedding=ctx.embedding,
                domain=ctx.domain,
                state=ctx.resolved_state,
                classification=ctx.classification,
                history=ctx.history,
                lang=ctx.lang,
                session_id=req.session_id,
                language_mix=ctx.language_mix,
            )

            # Sarvam generates directly in user's language; only translate for Groq fallback
            if rag_response.mode == "groq_fallback" and ctx.lang != "en":
                rag_response.answer = _translate_from_english(rag_response.answer, ctx.lang, ctx.settings)
                rag_response.speech_text = prepare_speech_text(rag_response.answer)
                rag_response.speech_segments = segment_speech(rag_response.answer, ctx.lang)

            # Emit thinking + tokens
            yield _sse_event("thinking", {"text": thinking_msgs[2]})
            for token in rag_response.answer.split(" "):
                yield _sse_event("token", {"text": token + " "})

            # Session persistence
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", rag_response.answer)
            trim_messages(req.session_id, keep=50)

            yield _sse_event("metadata", {
                "domain": rag_response.domain,
                "confidence": rag_response.confidence,
                "confidence_level": _confidence_level(rag_response.confidence),
                "citations": rag_response.citations,
                "abstained": rag_response.abstained,
                "language": ctx.lang,
                "mode": rag_response.mode,
            })
            yield _sse_event("done", {})

        except Exception:
            logger.exception("Streaming chat route failed")
            answer = get_abstain_text(req.language)
            yield _sse_event("metadata", {
                "domain": "unknown", "confidence": 0.0,
                "confidence_level": "none", "citations": [],
                "abstained": True, "language": req.language,
            })
            for token in answer.split(" "):
                yield _sse_event("token", {"text": token + " "})
            yield _sse_event("done", {})

    return StreamingResponse(generate(), media_type="text/event-stream")
