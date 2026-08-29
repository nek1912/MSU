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
from app.generation import (CitationError, build_system_prompt,
                            build_user_prompt, verify_citations)
from app.hybrid_retrieval import retrieve_hybrid
from app.language import detect_query_languages
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.embeddings import get_embedding_provider
from app.providers.reranker import JinaReranker
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.providers.translator import AzureTranslator
from app.retrieval import RetrievedChunk, retrieve
from app.resolve_response_language import resolve_and_remember
from app.speech_text import prepare_speech_text, segment_speech
from app.session_store import get_state, touch_session
from app.ui import get_abstain_text

router = APIRouter()

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
    language: Literal["en", "hi", "gu", "mr", "bn"]
    ui_language_explicit: bool = False
    state: str | None = None
    as_of_date: str | None = None  # Optional date filter (YYYY-MM-DD)


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
    # Response language resolved solely by the resolver (detection + session
    # memory). ui_language_explicit is a BOOL: pass the UI code only when the
    # user explicitly changed language this turn (never as a default).
    ui_code = req.language if req.ui_language_explicit else None
    lang = resolve_and_remember(req.session_id, req.question, ui_code)
    # Retrieval-side translation uses the DETECTED INPUT language, not the
    # response language (they can differ, e.g. Hindi question -> English answer).
    detected = detect_query_languages(req.question)
    input_lang = detected.get("dominant") or "en"
    retrieval_query = req.question
    if input_lang != "en":
        try:
            retrieval_query = AzureTranslator(settings).translate(
                req.question, to="en", source=input_lang)
        except Exception:
            retrieval_query = req.question
    try:
        provider = get_embedding_provider()          # cached singleton (P0-1)
        embedding = provider.embed_texts([retrieval_query], task="retrieval.query")[0]
        domain, _score = get_anchor_store().classify(retrieval_query, embedding)
        resolved_state = req.state if req.state is not None else get_state(req.session_id)
        touch_session(req.session_id, resolved_state, lang)
        if domain == "out_of_scope":
            # Controlled out-of-scope response. Invariant #9: out-of-scope
            # queries must NOT receive an ungrounded factual LLM answer. Return
            # the standard controlled abstain rather than generating from
            # general knowledge.
            return _abstain(lang, "out_of_scope")

        # --- Hybrid retrieval (Stage 5) ---
        # When the reranker is enabled, pull a larger candidate pool (top 25)
        # so the reranker can re-order and the final top-5/6 reflects true
        # relevance rather than just dense/lexical score.
        k = 25 if settings.reranker_enabled else 6
        chunks = retrieve_hybrid(
            get_supabase(), embedding, retrieval_query, domain, resolved_state, k=k,
        )

        # Optional reranker (Stage 6): hybrid top-25 -> rerank -> top-6 -> gate
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
            return _abstain(lang, reason.value if reason else None)

        prompt = build_user_prompt(req.question, chunks)
        answer = grounded_answer(GroqLLMProvider(settings),
                                 GeminiLLMProvider(settings),
                                 build_system_prompt(lang), prompt)

        # --- Citation verification v2 (Stage 8) ---
        chunk_ids = [c.chunk_id for c in chunks]
        verification = verify_citations_v2(answer, chunk_ids)
        if not verification.is_valid:
            return _abstain(lang, verification.reason.value if verification.reason else "citation_failure")

        citations = _citations_from(answer, chunks)
        _band_to_confidence = {"high": 0.9, "medium": 0.7, "low": 0.4}
        confidence = _band_to_confidence.get(band.value, 0.4)
        # Speech-only copy: citation markers/URLs stripped AFTER verification.
        # TTS must consume this, never the raw `answer` (which carries [chunk:ID]).
        speech_text = prepare_speech_text(answer)
        speech_segments = segment_speech(answer, lang)
        return {"answer": answer, "language": lang, "domain": domain,
                "intent": domain, "entities": [],
                "confidence": confidence,
                "confidence_level": _confidence_level(confidence),
                "citations": citations, "abstained": False,
                "speech_text": speech_text,
                "speech_segments": speech_segments,
                "follow_up_question": None}
    except _SAFE_FAILURES:
        # Known dependency failures → contract-valid abstention
        return _abstain(lang, "dependency_failure")
    except Exception:
        raise


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


def _abstain(lang: str, _reason: str | None) -> dict:
    answer = get_abstain_text(lang)
    return {"answer": answer, "language": lang, "domain": "unknown",
            "intent": "unknown", "entities": [],
            "confidence": 0.0, "confidence_level": "none",
            "citations": [], "abstained": True,
            "speech_text": prepare_speech_text(answer),
            "speech_segments": [],
            "follow_up_question": None}
