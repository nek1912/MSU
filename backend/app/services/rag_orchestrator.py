"""RAG Orchestrator — async dual-pipeline RAG with evidence bundle.

Runs static RAG (Supabase pgvector) and web RAG (Tavily/Firecrawl) in
parallel via asyncio.gather, merges evidence chunks into an EvidenceBundle,
builds a curated source-priority prompt, generates an answer via LLM with
provider fallback, verifies citations, calculates confidence,
and returns a typed RAGResponse.

Architecture:
  1. asyncio.gather runs both pipelines concurrently (return_exceptions=True)
  2. EvidenceController builds an EvidenceBundle + curated prompt
  3. LLM generates answer (Groq primary, Gemini fallback)
  4. Citations are verified
  5. Confidence is calculated
  6. RAGResponse is returned
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from app.citation_verifier import verify_citations
from app.config import Settings, get_settings
from app.contracts import (
    AbstentionReason,
    ConfidenceBand,
    EvidenceBundle,
    EvidenceChunk,
    RAGResponse,
    RAGResult,
)
from app.evidence_controller import EvidenceController, QueryRequirementClassifier, strip_citations
from app.llm_fallback import AllProvidersFailedError, grounded_answer
from app.providers.gemini_llm import GeminiLLMProvider
from app.providers.groq_llm import GroqLLMProvider
from app.services.static_rag import StaticRAGService
from app.services.web_rag import WebRAGService
from app.speech_text import prepare_speech_text, segment_speech
from app.ui import get_abstain_text
from app.web_rag.query_classifier import QueryClassification

logger = logging.getLogger(__name__)

_BAND_TO_CONFIDENCE: dict[str, float] = {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.4,
}


class RAGOrchestrator:
    """Runs async dual-pipeline RAG with evidence bundling and claim verification.

    Usage:
        orchestrator = RAGOrchestrator(settings)
        response = await orchestrator.run(
            query="What is PMFBY?",
            english_query="What is PMFBY?",
            embedding=[0.1] * 768,
            domain="pmfby",
            state="gujarat",
            classification=classification,
            history=[],
            lang="en",
            session_id="sess-123",
        )
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._static_rag = StaticRAGService(self._settings)
        self._web_rag = WebRAGService()
        self._evidence_controller = EvidenceController()
        self._query_classifier = QueryRequirementClassifier()

    async def run(
        self,
        query: str,
        english_query: str,
        embedding: list[float],
        domain: str,
        state: str | None,
        classification: QueryClassification | None,
        history: list[dict] | None,
        lang: str,
        session_id: str,
        language_mix: dict[str, float] | None = None,
    ) -> RAGResponse:
        """Execute the full async dual-pipeline RAG flow.

        Args:
            query: Original user query (may be non-English).
            english_query: Translated English query for retrieval.
            embedding: Query embedding vector.
            domain: Detected domain from AnchorStore.
            state: Resolved state for jurisdiction filtering.
            classification: Query classification from QueryClassifier.
            history: Conversation history turns.
            lang: Response language code.
            session_id: Session identifier.

        Returns:
            RAGResponse with answer, citations, confidence, and speech data.
        """
        self._user_lang = lang
        logger.info(
            "RAGOrchestrator.run: domain=%s state=%s lang=%s session=%s",
            domain, state, lang, session_id,
        )

        # Step 1: Classify query requirements
        query_requirements = self._query_classifier.classify(query, lang)

        # Step 2: Run both pipelines in parallel via asyncio.gather
        static_result, web_result = await self._run_pipelines(
            english_query=english_query,
            embedding=embedding,
            domain=domain,
            state=state,
            classification=classification,
        )

        has_static = not static_result.abstained and len(static_result.chunks) > 0
        has_web = not web_result.abstained and len(web_result.chunks) > 0

        logger.info(
            "Pipeline results: static=%d chunks (abstained=%s), web=%d chunks (abstained=%s)",
            len(static_result.chunks), static_result.abstained,
            len(web_result.chunks), web_result.abstained,
        )

        # Step 3: If both pipelines abstained, return abstain response
        if not has_static and not has_web:
            return self._abstain_response(
                lang=lang,
                reason=static_result.reason or web_result.reason or AbstentionReason.NO_ELIGIBLE_SOURCE,
                domain=domain,
                session_id=session_id,
            )

        # Step 4: Build evidence bundle
        bundle = self._evidence_controller.build_bundle(
            static_result, web_result, query_requirements, query,
        )

        # Step 5: Assess evidence
        assessment = self._evidence_controller.assess_evidence(
            static_result, web_result, query_requirements,
        )

        # Step 6: Build curated prompt with source-priority rules
        system_prompt, user_prompt = self._evidence_controller.build_curated_prompt(
            bundle, english_query, history, lang,
            language_mix=language_mix,
            assessment=assessment,
        )

        # Step 7: Generate answer via LLM (Groq primary, Gemini fallback)
        mode = "groq"
        try:
            answer = grounded_answer(
                GroqLLMProvider(self._settings),
                GeminiLLMProvider(self._settings),
                system_prompt,
                user_prompt,
            )
            answer = answer.replace("\u3010", "[").replace("\u3011", "]")
        except AllProvidersFailedError:
            logger.exception("All LLM providers failed")
            return self._abstain_response(
                lang=lang,
                reason=AbstentionReason.PROVIDER_UNAVAILABLE,
                domain=domain,
                session_id=session_id,
            )

        # Step 8: Auto-append citations if missing
        all_chunks = self._merge_evidence(static_result.chunks, web_result.chunks)
        answer = self._auto_append_citations(answer, all_chunks)

        # Step 9: Verify citations against evidence
        all_chunk_ids = [chunk.chunk_id for chunk in all_chunks]
        citation_verification = verify_citations(answer, all_chunk_ids)
        if not citation_verification.is_valid:
            logger.warning(
                "Citation verification failed: reason=%s invalid_prefixes=%s",
                citation_verification.reason, citation_verification.invalid_prefixes,
            )
            return self._abstain_response(
                lang=lang,
                reason=citation_verification.reason or AbstentionReason.CITATION_FAILURE,
                domain=domain,
                session_id=session_id,
            )

        # Step 10: Strip internal citation markers from visible answer
        clean_answer, extracted_ids = strip_citations(answer)
        answer = clean_answer

        # Step 11: Calculate confidence
        confidence, confidence_band = self._calculate_confidence(
            static_result, web_result, has_static, has_web,
            [],  # No claim verifications
        )

        # Step 12: Build citations list
        citations = self._build_citations(all_chunks)

        # Step 13: Prepare speech text
        speech_text = prepare_speech_text(answer)
        speech_segments = segment_speech(answer, lang)

        # Step 14: Determine mode
        if has_static and has_web:
            mode = "dual_rag"
        elif has_static:
            mode = "static"
        else:
            mode = "web"

        logger.info(
            "RAGOrchestrator response: confidence=%.2f band=%s mode=%s citations=%d",
            confidence, confidence_band.value, mode, len(citations),
        )

        return RAGResponse(
            answer=answer,
            language=lang,
            domain=domain,
            confidence=confidence,
            confidence_level=confidence_band,
            citations=citations,
            abstained=False,
            speech_text=speech_text,
            speech_segments=speech_segments,
            follow_up_question=None,
            mode=mode,
            conversation_id=session_id,
        )

    async def _run_pipelines(
        self,
        english_query: str,
        embedding: list[float],
        domain: str,
        state: str | None,
        classification: QueryClassification | None,
    ) -> tuple[RAGResult, RAGResult]:
        """Run static and web RAG pipelines in parallel via asyncio.gather."""
        static_coro = asyncio.to_thread(
            self._static_rag.retrieve,
            embedding=embedding,
            query=english_query,
            domain=domain,
            state=state,
        )
        web_coro = asyncio.to_thread(
            self._web_rag.retrieve,
            query=english_query,
            domain=domain,
            state=state,
            classification=classification,
        )

        results = await asyncio.gather(static_coro, web_coro, return_exceptions=True)

        static_result: RAGResult
        web_result: RAGResult

        if isinstance(results[0], Exception):
            logger.exception("Static RAG pipeline failed: %s", results[0])
            static_result = RAGResult(
                chunks=[],
                abstained=True,
                reason=AbstentionReason.PROVIDER_UNAVAILABLE,
                domain=domain,
            )
        else:
            static_result = results[0]

        if isinstance(results[1], Exception):
            logger.exception("Web RAG pipeline failed: %s", results[1])
            web_result = RAGResult(
                chunks=[],
                abstained=True,
                reason=AbstentionReason.PROVIDER_UNAVAILABLE,
                domain=domain,
            )
        else:
            web_result = results[1]

        return static_result, web_result

    def _merge_evidence(
        self,
        static_chunks: list[EvidenceChunk],
        web_chunks: list[EvidenceChunk],
    ) -> list[EvidenceChunk]:
        """Merge evidence from both pipelines with equal priority.

        Static chunks come first (official documents), then web chunks.
        """
        merged = list(static_chunks) + list(web_chunks)
        logger.info(
            "Merged evidence: %d static + %d web = %d total",
            len(static_chunks), len(web_chunks), len(merged),
        )
        return merged

    def _auto_append_citations(
        self,
        answer: str,
        chunks: list[EvidenceChunk],
    ) -> str:
        """Auto-append citation markers if the LLM omitted them entirely."""
        has_citation = bool(re.search(r"\[chunk:", answer))
        if has_citation or not chunks:
            return answer

        seen: set[str] = set()
        citation_parts: list[str] = []
        for chunk in chunks[:3]:
            short_id = chunk.chunk_id[:8]
            if short_id not in seen:
                seen.add(short_id)
                citation_parts.append(f"[chunk:{short_id}]")

        if citation_parts:
            answer = answer.rstrip() + " " + " ".join(citation_parts)

        return answer

    def _build_citations(
        self,
        chunks: list[EvidenceChunk],
    ) -> list[dict]:
        """Build the citations list for the API response."""
        citations: list[dict] = []
        seen: set[str] = set()

        for chunk in chunks:
            short_id = chunk.chunk_id[:8]
            if short_id in seen:
                continue
            seen.add(short_id)

            citation: dict[str, Any] = {
                "chunk_id": short_id,
                "title": chunk.title,
                "source": chunk.source_type,
                "source_label": "Official Document" if chunk.source_type == "static" else "Web Source",
                "url": chunk.url,
            }
            if chunk.page is not None:
                citation["page"] = chunk.page
            if chunk.section:
                citation["section"] = chunk.section

            citations.append(citation)

        return citations

    def _calculate_confidence(
        self,
        static_result: RAGResult,
        web_result: RAGResult,
        has_static: bool,
        has_web: bool,
        claim_verifications: list | None = None,
    ) -> tuple[float, ConfidenceBand]:
        """Compute claim-level confidence score and band from evidence.

        After claim verification, confidence is adjusted based on:
        - Number of unsupported claims (lower confidence)
        - Number of filtered claims (lower confidence)
        - Source quality (static + web dual-source boost)
        """
        # Static confidence from evidence gate band
        static_band = static_result.band
        static_conf = _BAND_TO_CONFIDENCE.get(
            getattr(static_band, "value", ""), 0.4
        )

        # Web confidence from evidence gate band
        web_band = web_result.band
        web_conf = _BAND_TO_CONFIDENCE.get(
            getattr(web_band, "value", ""), 0.4
        )

        if has_static and has_web:
            # Dual-source: average with a small boost
            base = (static_conf + web_conf) / 2.0
            confidence = min(base + 0.10, 1.0)
        elif has_static:
            confidence = static_conf
        elif has_web:
            confidence = web_conf
        else:
            confidence = 0.0

        # Adjust confidence based on claim verification results
        if claim_verifications is not None and len(claim_verifications) > 0:
            unsupported = sum(1 for v in claim_verifications if not v.is_supported)
            total_verified = len(claim_verifications)
            if total_verified > 0:
                # Each unsupported claim reduces confidence by a factor
                unsupported_ratio = unsupported / total_verified
                penalty = unsupported_ratio * 0.3  # up to 30% penalty
                confidence = max(confidence - penalty, 0.0)

        # Map to band
        if confidence >= 0.7:
            band = ConfidenceBand.HIGH
        elif confidence >= 0.5:
            band = ConfidenceBand.MEDIUM
        else:
            band = ConfidenceBand.LOW

        return round(confidence, 2), band

    def _abstain_response(
        self,
        lang: str,
        reason: AbstentionReason,
        domain: str,
        session_id: str,
    ) -> RAGResponse:
        """Build a standardized abstention response."""
        answer = get_abstain_text(lang)
        return RAGResponse(
            answer=answer,
            language=lang,
            domain=domain,
            confidence=0.0,
            confidence_level=ConfidenceBand.LOW,
            citations=[],
            abstained=True,
            speech_text=prepare_speech_text(answer),
            speech_segments=[],
            follow_up_question=None,
            mode="dual_rag",
            conversation_id=session_id,
        )
