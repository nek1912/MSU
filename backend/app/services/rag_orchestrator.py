"""RAG Orchestrator — unified dual-pipeline RAG with evidence merging.

Runs static RAG (Supabase pgvector) and web RAG (Tavily/Firecrawl) in
parallel, merges evidence chunks, builds a grounded prompt, generates an
answer via LLM with provider fallback, and returns a typed RAGResponse.

Architecture:
  1. ThreadPoolExecutor runs both pipelines concurrently
  2. Evidence chunks are merged (static first, then web)
  3. Context and prompt are built from merged evidence
  4. LLM generates answer (Groq primary, Gemini fallback)
  5. Citations are auto-appended if the LLM omitted them
  6. Confidence is computed from evidence bands + source count
  7. Speech text/segments are prepared
  8. RAGResponse is returned
"""

from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.citation_verifier import verify_citations
from app.config import Settings, get_settings
from app.contracts import (
    AbstentionReason,
    ConfidenceBand,
    EvidenceChunk,
    RAGResponse,
    RAGResult,
)
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

_SYSTEM_PROMPT = (
    "You are a helpful government information assistant. "
    "Synthesize an accurate answer from ALL provided evidence. "
    "Evidence is marked with [chunk:ID] citations — use the EXACT citation "
    "marker shown in the evidence. Treat all evidence as EQUAL inputs. "
    "After EVERY factual sentence, add the citation: [chunk:ID]. "
    "Use ONLY half-width square brackets []. "
    "If evidence is insufficient, say so clearly. "
    "Do NOT mention source types or priorities in your answer — just cite the evidence. "
    "CRITICAL: The question is written in the user's language. "
    "You MUST respond in the SAME language as the question. "
    "If the question is in Hindi, respond in Hindi. "
    "If the question is in Gujarati, respond in Gujarati. "
    "If the question is in English, respond in English. "
    "Never switch languages mid-response."
)


class RAGOrchestrator:
    """Runs dual-pipeline RAG, merges evidence, and generates grounded answers.

    Usage:
        orchestrator = RAGOrchestrator(settings)
        response = orchestrator.run(
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

    def run(
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
    ) -> RAGResponse:
        """Execute the full dual-pipeline RAG flow.

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
        self._user_lang = lang  # store for prompt building
        logger.info(
            "RAGOrchestrator.run: domain=%s state=%s lang=%s session=%s",
            domain, state, lang, session_id,
        )

        # Step 1: Run both pipelines in parallel
        static_result, web_result = self._run_pipelines(
            english_query=english_query,
            embedding=embedding,
            domain=domain,
            state=state,
            query=query,
            classification=classification,
        )

        static_chunks = static_result.chunks
        web_chunks = web_result.chunks
        has_static = not static_result.abstained and len(static_chunks) > 0
        has_web = not web_result.abstained and len(web_chunks) > 0

        logger.info(
            "Pipeline results: static=%d chunks (abstained=%s), web=%d chunks (abstained=%s)",
            len(static_chunks), static_result.abstained,
            len(web_chunks), web_result.abstained,
        )

        # Step 2: If both pipelines abstained, return abstain response
        if not has_static and not has_web:
            return self._abstain_response(
                lang=lang,
                reason=static_result.reason or web_result.reason or AbstentionReason.NO_ELIGIBLE_SOURCE,
                domain=domain,
                session_id=session_id,
            )

        # Step 3: Merge evidence chunks
        all_chunks = self._merge_evidence(static_chunks, web_chunks)

        # Step 4: Build context and prompt
        context = self._build_context(all_chunks, history, english_query)
        prompt = self._build_prompt(english_query, context, history, len(static_chunks), len(web_chunks))

        # Step 5: Generate answer via LLM
        try:
            answer = grounded_answer(
                GroqLLMProvider(self._settings),
                GeminiLLMProvider(self._settings),
                _SYSTEM_PROMPT,
                prompt,
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

        # Step 6: Auto-append citations if missing
        answer = self._auto_append_citations(answer, all_chunks)

        # Step 6b: Verify citations against evidence
        all_chunk_ids = [chunk.chunk_id for chunk in all_chunks]
        verification = verify_citations(answer, all_chunk_ids)
        if not verification.is_valid:
            logger.warning(
                "Citation verification failed: reason=%s invalid_prefixes=%s",
                verification.reason, verification.invalid_prefixes,
            )
            return self._abstain_response(
                lang=lang,
                reason=verification.reason or AbstentionReason.CITATION_FAILURE,
                domain=domain,
                session_id=session_id,
            )

        # Step 7: Calculate confidence
        confidence, confidence_band = self._calculate_confidence(
            static_result, web_result, has_static, has_web,
        )

        # Step 8: Build citations list
        citations = self._build_citations(all_chunks)

        # Step 9: Prepare speech text
        speech_text = prepare_speech_text(answer)
        speech_segments = segment_speech(answer, lang)

        # Step 10: Determine mode
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

    def _run_pipelines(
        self,
        english_query: str,
        embedding: list[float],
        domain: str,
        state: str | None,
        query: str,
        classification: QueryClassification | None,
    ) -> tuple[RAGResult, RAGResult]:
        """Run static and web RAG pipelines in parallel via ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="rag-orch") as executor:
            static_future = executor.submit(
                self._static_rag.retrieve,
                embedding=embedding,
                query=english_query,
                domain=domain,
                state=state,
            )
            web_future = executor.submit(
                self._web_rag.retrieve,
                query=english_query,
                domain=domain,
                state=state,
                classification=classification,
            )

            static_result = static_future.result()
            web_result = web_future.result()

        return static_result, web_result

    def _merge_evidence(
        self,
        static_chunks: list[EvidenceChunk],
        web_chunks: list[EvidenceChunk],
    ) -> list[EvidenceChunk]:
        """Merge evidence from both pipelines with equal priority.

        Static chunks come first (official documents), then web chunks.
        Deduplication by chunk_id is not needed since the two pipelines
        produce non-overlapping IDs.
        """
        merged = list(static_chunks) + list(web_chunks)
        logger.info(
            "Merged evidence: %d static + %d web = %d total",
            len(static_chunks), len(web_chunks), len(merged),
        )
        return merged

    def _build_context(
        self,
        chunks: list[EvidenceChunk],
        history: list[dict] | None,
        english_query: str,
    ) -> str:
        """Build the context string from merged evidence chunks."""
        if not chunks:
            return "No evidence available."

        parts: list[str] = []
        for chunk in chunks:
            short_id = chunk.chunk_id[:8]
            if chunk.source_type == "static":
                parts.append(
                    f"[chunk:{short_id}] ({chunk.title} \u2014 {chunk.section} \u2014 p.{chunk.page})\n{chunk.content}"
                )
            else:
                parts.append(
                    f"[chunk:{short_id}] ({chunk.title} \u2014 web \u2014 {chunk.url})\n{chunk.content}"
                )

        return "\n\n---\n\n".join(parts)

    def _build_prompt(
        self,
        english_query: str,
        context: str,
        history: list[dict] | None,
        static_count: int,
        web_count: int,
    ) -> str:
        """Build the user prompt for the LLM from context and history."""
        hist_text = ""
        if history:
            turns = "\n".join(
                f"{'User' if h.get('role') == 'user' else 'Assistant'}: {h.get('content', '')}"
                for h in history
                if isinstance(h, dict)
            )
            if turns:
                hist_text = f"Previous conversation:\n{turns}\n\n"

        source_hint: list[str] = []
        if static_count > 0:
            source_hint.append(f"{static_count} chunks from official documents")
        if web_count > 0:
            source_hint.append(f"{web_count} chunks from web sources")
        source_str = " and ".join(source_hint) if source_hint else "no evidence sources"

        lang_instruction = ""
        if hasattr(self, '_user_lang') and self._user_lang and self._user_lang != "en":
            lang_instruction = (
                f"\n\nIMPORTANT: The user's language is '{self._user_lang}'. "
                f"You MUST respond in this language. "
                f"Do NOT respond in English."
            )

        return (
            f"{hist_text}"
            f"Question: {english_query}\n\n"
            f"{context}\n\n"
            f"Available sources: {source_str}\n"
            f"Synthesize an answer using whichever evidence best answers the question. "
            f"Combine evidence from multiple sources when it strengthens the answer."
            f"{lang_instruction}"
        )

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
    ) -> tuple[float, ConfidenceBand]:
        """Compute confidence score and band from evidence.

        Dual-source evidence gets a boost; single-source uses its own band.
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
