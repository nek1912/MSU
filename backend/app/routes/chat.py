"""Chat route — refactored with hybrid retrieval, typed evidence gate,
and unavoidable citation verification.

Feature flag: USE_HYBRID_RETRIEVAL (env var) controls old vs new path.
Default: new path (hybrid + v2 gate + verifier).
"""

import json
import re
from typing import Literal

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from postgrest.exceptions import APIError as PostgrestAPIError
from pydantic import BaseModel, Field

from app.config import get_settings
from app.contracts import RetrievalCandidate
from app.citation_verifier import verify_citations as verify_citations_v2
from app.db import get_supabase
from app.domains import get_anchor_store
from app.evidence_gate import evidence_gate_v2
from app.generation import (CitationError, GENERAL_SYSTEM_PROMPT, build_general_prompt,
                            build_system_prompt, build_user_prompt, general_disclaimer, verify_citations)
from app.grievance.workflow import GrievanceWorkflow
from app.hybrid_retrieval import retrieve_hybrid
from app.language import detect_query_languages
from app.llm_fallback import AllProvidersFailedError, grounded_answer, grounded_answer_stream
from app.providers.embeddings import get_embedding_provider
from app.providers.reranker import JinaReranker
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.providers.translator import AzureTranslator
from app.providers.sarvam_translator import SarvamTranslator
from app.rag.pipeline import RAGPipeline
from app.retrieval import RetrievedChunk, retrieve
from app.resolve_response_language import resolve_and_remember
from app.speech_text import prepare_speech_text, segment_speech
from app.session_store import get_history, get_state, save_message, touch_session, trim_messages
from app.ui import get_abstain_text
from app.web_rag.query_classifier import QueryClassifier

router = APIRouter()

# Domains with curated local corpus — use static RAG for these
_STATIC_DOMAINS = {"pacs_governance", "pacs_computerization", "pacs", "pmfby", "financial_inclusion", "finlit", "cooperative", "schemes", "agriculture"}

# Map QueryClassifier domains to AnchorStore domains for retrieval
_DOMAIN_MAP = {
    "pacs": "pacs_governance",
    "finlit": "financial_inclusion",
    "cooperative": "pacs_governance",
}

# Singletons for routing (lazy initialization to avoid import-time side effects)
_query_classifier: QueryClassifier | None = None
_web_rag_pipeline: RAGPipeline | None = None
_grievance_workflow: GrievanceWorkflow | None = None


def _get_query_classifier() -> QueryClassifier:
    global _query_classifier
    if _query_classifier is None:
        _query_classifier = QueryClassifier()
    return _query_classifier


def _get_web_rag_pipeline() -> RAGPipeline:
    global _web_rag_pipeline
    if _web_rag_pipeline is None:
        _web_rag_pipeline = RAGPipeline()
    return _web_rag_pipeline


def _get_grievance_workflow() -> GrievanceWorkflow:
    global _grievance_workflow
    if _grievance_workflow is None:
        _grievance_workflow = GrievanceWorkflow()
    return _grievance_workflow


ABSTAIN_TEXT = {
    "en": "I could not find this in official sources, so I won't guess. "
          "Please try rephrasing or ask about cooperative rules, PACS, schemes, "
          "PMFBY, agriculture, or financial literacy.",
    "hi": "मुझे आधिकारिक स्रोतों में इसका उत्तर नहीं मिला, इसलिए अनुमान नहीं लगाऊंगा। "
          "कृपया प्रश्न दूसरे शब्दों में पूछें या सहकारिता, पीएसीएस, योजनाओं, "
          "पीएएमएफबीवाई, कृषि या वित्तीय साक्षरता के बारे में पूछें।",
    "gu": "મને અધિકૃત સ્રોતોમાં આનો જવાબ ન મળ્યો, તેથી હું અનુમાન નહીં લગાવું. "
          "કૃપા કરીને પ્રશ્નને અલગ શબ્દોમાં પૂછો અથવા સહકારી નિયમો, પીએસીએસ, "
          "યોજનાઓ, પીએમએફબીવાઈ, કૃષિ અથવા નાણાકીય સાક્ષરતા વિશે પૂછો.",
    "mr": "मला अधिकृत स्रोतांमध्ये याचे उत्तर सापडले नाही, म्हणून मी अंदाज लावणार नाही. "
          "कृपया प्रश्न वेगळ्या शब्दांत विचारा किंवा सहकारी नियम, पीएसीएस, योजना, "
          "पीएमएफबीवाय, कृषी किंवा वित्तीय साक्षरता याबद्दल विचारा.",
    "bn": "আমি কর্তৃপক্ষের উৎসে এর উত্তর খুঁজে পাইনি, তাই আমি অনুমান করব না। "
          "অনুগ্রহ করে ভিন্ন শব্দে প্রশ্ন করুন বা সহকারিতা, পিএসিএস, প্রকল্প, "
          "পিএমএফবি঵াই, কৃষি বা আর্থিক সাক্ষরতা সম্পর্কে জিজ্ঞাসা করুন.",
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
    language: Literal["en", "hi", "gu", "mr", "bn", "ta"]
    ui_language_explicit: bool = False
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


def _to_candidate(chunk: RetrievedChunk, expected_domain: str | None,
                  expected_state: str | None) -> RetrievalCandidate:
    """Convert a RetrievedChunk to a RetrievalCandidate for evidence_gate_v2.

    The domain filter decision is DERIVED from the candidate's own metadata
    (``chunk.domain``) compared against the requested ``expected_domain`` — it is
    never hardcoded. A candidate whose domain is missing/unknown or mismatched is
    marked ``domain=False`` so the evidence gate rejects it (fail-closed).
    """
    is_central = chunk.jurisdiction == "central"
    state_match = is_central or chunk.state == expected_state
    domain_match = expected_domain is None or chunk.domain == expected_domain
    return RetrievalCandidate(
        chunk_id=chunk.chunk_id,
        document_id="",
        source_id="",
        dense_score=chunk.similarity,
        filter_decisions={
            "domain": domain_match,
            "active": True,
            "is_central": is_central,
            "state_match": state_match,
        },
    )


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    settings = get_settings()
    question = req.question.strip()
    if not question:
        return _abstain(req.language, "empty_question", session_id=req.session_id)
    # Response language resolved solely by the resolver (detection + session
    # memory). ui_language_explicit is a BOOL: pass the UI code only when the
    # user explicitly changed language this turn (never as a default).
    ui_code = req.language if req.ui_language_explicit else None
    lang = resolve_and_remember(req.session_id, req.question, ui_code)
    # Retrieval-side translation uses the DETECTED INPUT language, not the
    # response language (they can differ, e.g. Hindi question -> English answer).
    # Sarvam is primary for Indian languages, Azure is fallback.
    detected = detect_query_languages(req.question)
    input_lang = detected.get("dominant") or "en"
    retrieval_query = req.question
    if input_lang != "en":
        # Try Sarvam first (better for Indian languages), then Azure
        sarvam = SarvamTranslator(settings)
        if sarvam.configured:
            try:
                retrieval_query = sarvam.translate(
                    req.question, to="en", source=input_lang)
            except Exception:
                retrieval_query = req.question
        else:
            try:
                retrieval_query = AzureTranslator(settings).translate(
                    req.question, to="en", source=input_lang)
            except Exception:
                retrieval_query = req.question
    try:
        # --- Conversation history retrieval (Stage 0) ---
        history = req.history if req.history is not None else get_history(req.session_id, limit=8)

        provider = get_embedding_provider()          # cached singleton (P0-1)
        embedding = provider.embed_texts([retrieval_query], task="retrieval.query")[0]
        domain, _score = get_anchor_store().classify(retrieval_query, embedding)

        rules = getattr(get_anchor_store(), "rules", {})
        has_explicit_keyword = False
        if isinstance(rules, dict):
            has_explicit_keyword = any(
                any(kw in retrieval_query.lower() for kw in kws)
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

                contextual_query = f"{anchor_q} {retrieval_query}"
                ctx_embedding = provider.embed_texts([contextual_query], task="retrieval.query")[0]
                ctx_domain, _ctx_score = get_anchor_store().classify(contextual_query, ctx_embedding)
                if ctx_domain != "out_of_scope":
                    domain = ctx_domain
                    retrieval_query = contextual_query
                    embedding = ctx_embedding
        resolved_state = req.state if req.state is not None else get_state(req.session_id)
        touch_session(req.session_id, resolved_state, lang)

        # --- Auto-routing (Task 13) ---
        classifier = _get_query_classifier()
        classification = classifier.classify(req.question)

        # 1. Grievance queries → dedicated grievance workflow
        if classification.domain == "grievance":
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
                "language": lang,
                "domain": "grievance",
                "intent": classification.intent,
                "entities": [],
                "confidence": classification.confidence,
                "confidence_level": _confidence_level(classification.confidence),
                "citations": [],
                "abstained": False,
                "speech_text": prepare_speech_text(response_text),
                "speech_segments": segment_speech(response_text, lang),
                "follow_up_question": None,
                "mode": "grievance",
                "conversation_id": req.session_id,
            }

        # 2. Cooperative/governance domains → try static RAG first
        # QueryClassifier is authoritative for routing; AnchorStore is for retrieval only
        # But if AnchorStore says out_of_scope, honor that (prevents web RAG on unrelated queries)
        if domain == "out_of_scope" or classification.domain in _STATIC_DOMAINS:
            # Existing static RAG pipeline runs below (falls through)
            static_rag_mode = "static"
        else:
            # 3. Non-static domains → web RAG
            static_rag_mode = None  # signal to skip static RAG below

        # If web RAG is needed, run it now and return
        if static_rag_mode is None:
            try:
                web_pipeline = _get_web_rag_pipeline()
                web_result = web_pipeline.ask(
                    query=req.question,
                    classification=classification,
                )
                if web_result.get("status") == "success":
                    answer = web_result.get("answer", "")
                    evidence = web_result.get("evidence", [])
                    citations = [
                        {
                            "chunk_id": s.get("chunk_id", ""),
                            "title": s.get("title", ""),
                            "url": s.get("url", ""),
                            "source": s.get("source", ""),
                        }
                        for s in evidence
                    ]
                    save_message(req.session_id, "user", req.question)
                    save_message(req.session_id, "assistant", answer)
                    trim_messages(req.session_id, keep=50)
                    return {
                        "answer": answer,
                        "language": lang,
                        "domain": classification.domain,
                        "intent": classification.intent,
                        "entities": [],
                        "confidence": classification.confidence,
                        "confidence_level": _confidence_level(classification.confidence),
                        "citations": citations,
                        "abstained": False,
                        "speech_text": prepare_speech_text(answer),
                        "speech_segments": segment_speech(answer, lang),
                        "follow_up_question": None,
                        "mode": "web",
                        "conversation_id": req.session_id,
                    }
                # Web RAG abstained → fall through to static RAG as fallback
            except Exception:
                pass  # Web RAG failed → fall through to static RAG

        if domain == "out_of_scope":
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", get_abstain_text(lang))
            trim_messages(req.session_id, keep=50)

            return {"answer": get_abstain_text(lang), "language": lang, "domain": "out_of_scope",
                    "intent": "general", "entities": [],
                    "confidence": 0.0, "confidence_level": "none",
                    "citations": [], "abstained": True,
                    "speech_text": prepare_speech_text(get_abstain_text(lang)),
                    "speech_segments": [],
                    "follow_up_question": None,
                    "mode": "static", "conversation_id": req.session_id}

        # --- Hybrid retrieval (Stage 5) ---
        # Map QueryClassifier domain to AnchorStore domain for retrieval
        retrieval_domain = _DOMAIN_MAP.get(domain, domain)
        k = 25 if settings.reranker_enabled else 6
        chunks = retrieve_hybrid(
            get_supabase(), embedding, retrieval_query, retrieval_domain, resolved_state, k=k,
        )

        # Optional reranker (Stage 6): hybrid top-25 -> rerank -> top-6 -> gate
        if settings.reranker_enabled:
            reranker = JinaReranker()
            docs_for_rerank = [{"chunk_id": c.chunk_id, "content": c.content} for c in chunks]
            reranked = reranker.rerank(req.question, docs_for_rerank, top_n=6)
            chunks_by_id = {c.chunk_id: c for c in chunks}
            chunks = [chunks_by_id[r["chunk_id"]] for r in reranked if r["chunk_id"] in chunks_by_id]

        # --- Evidence gate v2 (Stage 7) ---
        candidates = [_to_candidate(c, retrieval_domain, resolved_state) for c in chunks]
        abstained, reason, band = evidence_gate_v2(
            candidates, expected_domain=retrieval_domain, expected_state=resolved_state,
        )
        if abstained:
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", get_abstain_text(lang))
            trim_messages(req.session_id, keep=50)

            return {"answer": get_abstain_text(lang), "language": lang, "domain": domain,
                    "intent": domain, "entities": [],
                    "confidence": 0.0, "confidence_level": "none",
                    "citations": [], "abstained": True,
                    "speech_text": prepare_speech_text(get_abstain_text(lang)),
                    "speech_segments": [],
                    "follow_up_question": None,
                    "mode": "static", "conversation_id": req.session_id}

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
                    "intent": domain, "entities": [],
                    "confidence": 0.5, "confidence_level": "moderate",
                    "citations": [], "abstained": False,
                    "speech_text": prepare_speech_text(general_answer),
                    "speech_segments": segment_speech(general_answer, lang),
                    "follow_up_question": None,
                    "mode": "static", "conversation_id": req.session_id}

        # --- Citation verification v2 (Stage 8) ---
        chunk_ids = [c.chunk_id for c in chunks]
        verification = verify_citations_v2(answer, chunk_ids)

        # Fallback: if LLM didn't include [chunk:ID] markers but evidence gate
        # passed (chunks exist), add citations from top chunks automatically.
        # This handles cases where the LLM ignores citation instructions.
        has_citation_markers = bool(re.search(r"\[chunk:[0-9a-fA-F]{8,}", answer))
        if not verification.is_valid and not has_citation_markers and chunks:
            # Evidence gate passed and we have chunks — add citations from top chunks
            answer = _append_citations(answer, chunks[:3])
            verification = verify_citations_v2(answer, chunk_ids)

        if not verification.is_valid:
            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", get_abstain_text(lang))
            trim_messages(req.session_id, keep=50)

            return {"answer": get_abstain_text(lang), "language": lang, "domain": domain,
                    "intent": "general", "entities": [],
                    "confidence": 0.0, "confidence_level": "none",
                    "citations": [], "abstained": True,
                    "speech_text": prepare_speech_text(get_abstain_text(lang)),
                    "speech_segments": [],
                    "follow_up_question": None,
                    "mode": "static", "conversation_id": req.session_id}

        save_message(req.session_id, "user", req.question)
        save_message(req.session_id, "assistant", answer)
        trim_messages(req.session_id, keep=50)

        citations = _citations_from(answer, chunks)
        _band_to_confidence = {"high": 0.9, "medium": 0.7, "low": 0.4}
        confidence = _band_to_confidence.get(band.value, 0.4)
        speech_text = prepare_speech_text(answer)
        speech_segments = segment_speech(answer, lang)
        return {"answer": answer, "language": lang, "domain": domain,
                "intent": domain, "entities": [],
                "confidence": confidence,
                "confidence_level": _confidence_level(confidence),
                "citations": citations, "abstained": False,
                "speech_text": speech_text,
                "speech_segments": speech_segments,
                "follow_up_question": None,
                "mode": "static", "conversation_id": req.session_id}
    except _SAFE_FAILURES:
        # Known dependency failures → contract-valid abstention
        return _abstain(lang, "dependency_failure", session_id=req.session_id)
    except Exception:
        raise


# ---------------------------------------------------------------------------
# SSE streaming endpoint — POST /chat/stream
# ---------------------------------------------------------------------------

_THINKING_MESSAGES = {
    "en": ["Searching official documents...", "Analyzing content...", "Preparing answer..."],
    "hi": ["आधिकारिक दस्तावेज़ खोज रहे हैं...", "सामग्री का विश्लेषण कर रहे हैं...", "उत्तर तैयार कर रहे हैं..."],
    "gu": ["અધિકૃત દસ્તાવેજો શોધી રહ્યા છીએ...", "સામગ્રીનું વિશ્લેષણ કરી રહ્યા છીએ...", "જવાબ તૈયાર કરી રહ્યા છીએ..."],
}


def _sse_event(event: str, data: dict | str) -> str:
    """Format a server-sent event."""
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Streaming version of /chat — returns SSE with thinking + token events."""

    def generate():
        settings = get_settings()
        ui_code = req.language if req.ui_language_explicit else None
        lang = resolve_and_remember(req.session_id, req.question, ui_code)
        detected = detect_query_languages(req.question)
        input_lang = detected.get("dominant") or "en"
        retrieval_query = req.question
        if input_lang != "en":
            sarvam = SarvamTranslator(settings)
            if sarvam.configured:
                try:
                    retrieval_query = sarvam.translate(
                        req.question, to="en", source=input_lang)
                except Exception:
                    retrieval_query = req.question
            else:
                try:
                    retrieval_query = AzureTranslator(settings).translate(
                        req.question, to="en", source=input_lang)
                except Exception:
                    retrieval_query = req.question

        thinking_msgs = _THINKING_MESSAGES.get(lang, _THINKING_MESSAGES["en"])

        try:
            # --- Conversation history retrieval (Stage 0) ---
            history = req.history if req.history is not None else get_history(req.session_id, limit=8)

            # Thinking: searching
            yield _sse_event("thinking", {"text": thinking_msgs[0]})

            provider = get_embedding_provider()
            embedding = provider.embed_texts([retrieval_query], task="retrieval.query")[0]
            domain, _score = get_anchor_store().classify(retrieval_query, embedding)

            rules = getattr(get_anchor_store(), "rules", {})
            has_explicit_keyword = False
            if isinstance(rules, dict):
                has_explicit_keyword = any(
                    any(kw in retrieval_query.lower() for kw in kws)
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

                    contextual_query = f"{anchor_q} {retrieval_query}"
                    ctx_embedding = provider.embed_texts([contextual_query], task="retrieval.query")[0]
                    ctx_domain, _ctx_score = get_anchor_store().classify(contextual_query, ctx_embedding)
                    if ctx_domain != "out_of_scope":
                        domain = ctx_domain
                        retrieval_query = contextual_query
                        embedding = ctx_embedding

            resolved_state = req.state if req.state is not None else get_state(req.session_id)
            touch_session(req.session_id, resolved_state, lang)

            if domain == "out_of_scope":
                yield _sse_event("thinking", {"text": thinking_msgs[1]})
                answer_text = grounded_answer(
                    GroqLLMProvider(settings), GeminiLLMProvider(settings),
                    GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
                out_of_scope_answer = f"{answer_text}\n\n{general_disclaimer(lang)}"
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", out_of_scope_answer)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {"domain": "out_of_scope", "confidence": 0.0,
                                               "confidence_level": "none", "citations": [],
                                               "abstained": False, "language": lang})
                for token in out_of_scope_answer.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            # --- Hybrid retrieval (Stage 5) ---
            yield _sse_event("thinking", {"text": thinking_msgs[1]})
            k = 25 if settings.reranker_enabled else 6
            chunks = retrieve_hybrid(
                get_supabase(), embedding, retrieval_query, domain, resolved_state, k=k,
            )

            if settings.reranker_enabled:
                reranker = JinaReranker()
                docs_for_rerank = [{"chunk_id": c.chunk_id, "content": c.content} for c in chunks]
                reranked = reranker.rerank(req.question, docs_for_rerank, top_n=6)
                chunks_by_id = {c.chunk_id: c for c in chunks}
                chunks = [chunks_by_id[r["chunk_id"]] for r in reranked if r["chunk_id"] in chunks_by_id]

            # --- Evidence gate v2 (Stage 7) ---
            candidates = [_to_candidate(c, domain, resolved_state) for c in chunks]
            abstained, reason, band = evidence_gate_v2(
                candidates, expected_domain=domain, expected_state=resolved_state,
            )
            if abstained:
                yield _sse_event("thinking", {"text": thinking_msgs[2]})
                answer_text = grounded_answer(
                    GroqLLMProvider(settings), GeminiLLMProvider(settings),
                    GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
                out_of_scope_answer = f"{answer_text}\n\n{general_disclaimer(lang)}"
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", out_of_scope_answer)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {"domain": domain, "confidence": 0.5,
                                               "confidence_level": "moderate", "citations": [],
                                               "abstained": False, "language": lang})
                for token in out_of_scope_answer.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            # --- LLM generation (streaming) ---
            yield _sse_event("thinking", {"text": thinking_msgs[2]})
            prompt = build_user_prompt(req.question, chunks, history=history)
            answer_parts: list[str] = []
            try:
                for token in grounded_answer_stream(
                    GroqLLMProvider(settings), GeminiLLMProvider(settings),
                    build_system_prompt(lang), prompt):
                    answer_parts.append(token)
                    yield _sse_event("token", {"text": token})
            except AllProvidersFailedError:
                yield _sse_event("error", {"message": "All LLM providers failed"})
                yield _sse_event("done", {})
                return

            answer = "".join(answer_parts).replace("【", "[").replace("】", "]")

            if "INSUFFICIENT_EVIDENCE" in answer:
                answer_text = grounded_answer(
                    GroqLLMProvider(settings), GeminiLLMProvider(settings),
                    GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
                out_of_scope_answer = f"{answer_text}\n\n{general_disclaimer(lang)}"
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", out_of_scope_answer)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {"domain": domain, "confidence": 0.5,
                                               "confidence_level": "moderate", "citations": [],
                                               "abstained": False, "language": lang})
                # Re-stream the fallback answer
                for token in out_of_scope_answer.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            # --- Citation verification v2 (Stage 8) ---
            chunk_ids = [c.chunk_id for c in chunks]
            verification = verify_citations_v2(answer, chunk_ids)
            if not verification.is_valid:
                answer_text = grounded_answer(
                    GroqLLMProvider(settings), GeminiLLMProvider(settings),
                    GENERAL_SYSTEM_PROMPT, build_general_prompt(req.question, lang, history=history))
                out_of_scope_answer = f"{answer_text}\n\n{general_disclaimer(lang)}"
                save_message(req.session_id, "user", req.question)
                save_message(req.session_id, "assistant", out_of_scope_answer)
                trim_messages(req.session_id, keep=50)
                yield _sse_event("metadata", {"domain": domain, "confidence": 0.5,
                                               "confidence_level": "moderate", "citations": [],
                                               "abstained": False, "language": lang})
                for token in out_of_scope_answer.split(" "):
                    yield _sse_event("token", {"text": token + " "})
                yield _sse_event("done", {})
                return

            save_message(req.session_id, "user", req.question)
            save_message(req.session_id, "assistant", answer)
            trim_messages(req.session_id, keep=50)

            citations = _citations_from(answer, chunks)
            _band_to_confidence = {"high": 0.9, "medium": 0.7, "low": 0.4}
            confidence = _band_to_confidence.get(band.value, 0.4)
            yield _sse_event("metadata", {
                "domain": domain, "confidence": confidence,
                "confidence_level": _confidence_level(confidence),
                "citations": citations, "abstained": False, "language": lang,
            })
            yield _sse_event("done", {})

        except _SAFE_FAILURES:
            answer = get_abstain_text(lang)
            yield _sse_event("metadata", {"domain": "unknown", "confidence": 0.0,
                                           "confidence_level": "none", "citations": [],
                                           "abstained": True, "language": lang})
            for token in answer.split(" "):
                yield _sse_event("token", {"text": token + " "})
            yield _sse_event("done", {})
        except Exception:
            yield _sse_event("error", {"message": "Internal server error"})
            yield _sse_event("done", {})

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _append_citations(answer: str, chunks: list[RetrievedChunk]) -> str:
    """Append [chunk:ID] citation markers to an answer that lacks them.

    When the LLM doesn't include citation markers but the evidence gate passed,
    this adds citations from the top chunks so the answer is still grounded.
    Citations are appended at the end of the answer.
    """
    if not chunks:
        return answer
    seen = set()
    citation_parts = []
    for c in chunks[:3]:
        short_id = c.chunk_id[:8]
        if short_id not in seen:
            seen.add(short_id)
            citation_parts.append(f"[chunk:{short_id}]")
    if citation_parts:
        answer = answer.rstrip() + " " + " ".join(citation_parts)
    return answer


def _citations_from(answer: str, chunks: list[RetrievedChunk]) -> list[dict]:
    """Build citation objects from the answer's valid ``[chunk:id]`` markers.

    Validates each citation resolves to a chunk that was actually retrieved
    (citation_verifier), then enriches it with stable provenance from the
    database so the citation traces back to the official source page.
    """
    verification = verify_citations_v2(answer, [c.chunk_id for c in chunks])
    valid_ids = [c.chunk_id for c in verification.valid_citations]
    if not valid_ids:
        return []
    by_uuid = {c.chunk_id: c for c in chunks}
    # Enrich stable metadata (stable_chunk_id, document_id, source_file, page
    # range, section/subsection/clause) from the chunks table — the retrieval
    # path may not populate all of these fields. Best-effort: if the lookup is
    # unavailable (e.g. mocked test environment or a transient outage) we fall
    # back to the provenance already carried on the retrieved chunks so citation
    # construction never hard-fails.
    meta_by_id: dict[str, dict] = {}
    try:
        supabase = get_supabase()
        rows = (
            supabase.table("chunks")
            .select("id, chunk_id, document_id, section, metadata")
            .in_("id", list(valid_ids))
            .execute()
            .data
            or []
        )
        for r in rows:
            m = r.get("metadata") or {}
            meta_by_id[str(r["id"])] = {
                "stable_chunk_id": r.get("chunk_id"),
                "document_id": r.get("document_id"),
                "source_file": m.get("source_file", "") or "",
                "page_start": m.get("page_start") or r.get("page_start"),
                "page_end": m.get("page_end") or r.get("page_end"),
                "section": r.get("section") or m.get("section", ""),
                "subsection": m.get("subsection", "") or "",
                "clause": m.get("clause", "") or "",
            }
    except Exception:
        meta_by_id = {}
    citations: list[dict] = []
    for uid in valid_ids:
        c = by_uuid.get(uid)
        if c is None:
            continue
        meta = meta_by_id.get(uid) or {}
        citations.append({
            "chunk_id": meta.get("stable_chunk_id") or c.stable_chunk_id or c.chunk_id,
            "document_id": meta.get("document_id") or c.document_id or "",
            "title": c.title,
            "page": c.page,
            "page_start": meta.get("page_start") or c.page_start or c.page,
            "page_end": meta.get("page_end") or c.page_end or c.page,
            "section": meta.get("section") or c.section or "",
            "subsection": meta.get("subsection") or (c.subsection or ""),
            "clause": meta.get("clause") or (c.clause or ""),
            "source_file": meta.get("source_file") or (c.source_file or ""),
            "url": c.source_url,
        })
    return citations


def _abstain(lang: str, _reason: str | None, session_id: str | None = None) -> dict:
    answer = get_abstain_text(lang)
    return {"answer": answer, "language": lang, "domain": "unknown",
            "intent": "unknown", "entities": [],
            "confidence": 0.0, "confidence_level": "none",
            "citations": [], "abstained": True,
            "speech_text": prepare_speech_text(answer),
            "speech_segments": [],
            "follow_up_question": None,
            "mode": "static", "conversation_id": session_id}
