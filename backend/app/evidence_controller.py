"""Evidence Controller — query classification, evidence bundling, prompt curation."""

from __future__ import annotations

import datetime
import logging
import re

from app.contracts import (
    DynamicEvidence,
    EvidenceAssessment,
    EvidenceBundle,
    EvidenceSufficiency,
    QueryRequirements,
    RAGResult,
    SourceRole,
    StaticEvidence,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Indicator word lists (English, Hindi, Gujarati)
# ---------------------------------------------------------------------------

_CURRENT_INDICATORS: dict[str, list[str]] = {
    "en": ["currently", "now", "today", "current", "active", "present"],
    "hi": ["हाल", "अभी", "वर्तमान", "चालू"],
    "gu": ["હાલ", "હાલમાં", "અત્યારે", "ચાલુ", "વર્તમાન"],
}

_HISTORICAL_INDICATORS: dict[str, list[str]] = {
    "en": ["previous", "earlier", "past", "old", "guidelines"],
    "hi": ["पिछला", "पुराना", "दिशानिर्देश"],
    "gu": ["અગાઉના", "જૂના", "માર્ગદર્શિકા"],
}

_DISTRICT_INDICATORS: dict[str, list[str]] = {
    "en": ["district", "city", "taluka", "tehsil"],
    "hi": ["जिला", "शहर", "तहसील"],
    "gu": ["જિલ્લો", "શહેર", "તાલુકો"],
}

_STATE_INDICATORS: dict[str, list[str]] = {
    "en": ["state", "gujarat", "maharashtra", "karnataka", "tamil nadu"],
    "hi": ["राज्य", "गुजरात", "महाराष्ट्र"],
    "gu": ["રાજ્ય", "ગુજરાત", "મહારાષ્ટ્ર"],
}

_YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")

# Gujarat districts (common)
_GUJARAT_DISTRICTS: list[str] = [
    "surat", "valsad", "navsari", "bardoli", "ahmedabad", "rajkot",
    "jamnagar", "bhuj", "gandhinagar", "vadodara", "anand", "nadiad",
    "mahesana", "patan", "banaskantha", "sabarkantha", "pritam nagar",
]


class QueryRequirementClassifier:
    """Determines what kind of evidence a query needs."""

    def classify(
        self,
        query: str,
        lang: str,
        session_state: dict | None = None,
    ) -> QueryRequirements:
        temporal = self._detect_temporal(query, lang)
        geographic = self._detect_geographic(query, lang, session_state)
        specificity = self._detect_specificity(query, lang, temporal, geographic)
        requires_dynamic = self._needs_dynamic(temporal, geographic, specificity)

        return QueryRequirements(
            temporal_scope=temporal,
            geographic_scope=geographic,
            required_specificity=specificity,
            requires_dynamic=requires_dynamic,
        )

    # -- temporal -----------------------------------------------------------

    def _detect_temporal(self, query: str, lang: str) -> str:
        q = query.lower()

        # Explicit year mention
        years = _YEAR_PATTERN.findall(q)
        if years:
            latest = max(int(y) for y in years)
            current_year = datetime.datetime.now(tz=datetime.UTC).year
            if latest >= current_year:
                return str(latest)
            return "historical"

        # Current-indicator words
        indicators = _CURRENT_INDICATORS.get(lang, []) + _CURRENT_INDICATORS["en"]
        if any(ind in q for ind in indicators):
            return "current"

        # Historical-indicator words
        indicators = _HISTORICAL_INDICATORS.get(lang, []) + _HISTORICAL_INDICATORS["en"]
        if any(ind in q for ind in indicators):
            return "historical"

        return "general"

    # -- geographic ---------------------------------------------------------

    def _detect_geographic(
        self, query: str, lang: str, session_state: dict | None,
    ) -> str:
        q = query.lower()

        # District-indicator words
        district_inds = _DISTRICT_INDICATORS.get(lang, []) + _DISTRICT_INDICATORS["en"]
        if any(ind in q for ind in district_inds):
            return "district"

        # Known Gujarat district names
        if any(d in q for d in _GUJARAT_DISTRICTS):
            return "district"

        # State-indicator words
        state_inds = _STATE_INDICATORS.get(lang, []) + _STATE_INDICATORS["en"]
        if any(ind in q for ind in state_inds):
            return "state"

        # Session-state fallback
        if session_state:
            if session_state.get("district"):
                return "district"
            if session_state.get("state"):
                return "state"

        return "none"

    # -- specificity --------------------------------------------------------

    def _detect_specificity(
        self, query: str, lang: str, temporal: str, geographic: str,
    ) -> str:
        if geographic == "district" and (
            temporal == "current" or _YEAR_PATTERN.search(temporal)
        ):
            return "crop+district+year"
        if geographic == "district":
            return "district"
        if geographic == "state":
            return "state"
        return "general"

    # -- dynamic-evidence decision ------------------------------------------

    def _needs_dynamic(
        self, temporal: str, geographic: str, specificity: str,
    ) -> bool:
        # Historical + no geographic specificity → static corpus is enough
        if temporal == "historical" and geographic == "none":
            return False
        # General + no geographic → static corpus is enough
        if temporal == "general" and geographic == "none":
            return False
        # District-level always needs dynamic (current local facts)
        if geographic == "district":
            return True
        # Current indicator or explicit future/current year → needs dynamic
        if temporal == "current":
            return True
        return temporal not in ("general", "historical")


# ---------------------------------------------------------------------------
# Source Priority Prompt
# ---------------------------------------------------------------------------

_SOURCE_PRIORITY_PROMPT = """You are a government information assistant helping citizens understand
cooperative governance, agriculture schemes, and financial inclusion in India.

CRITICAL LANGUAGE RULE - YOU MUST FOLLOW THIS:
The question is in a specific language. You MUST respond ENTIRELY in that SAME language.
If the question is in Gujarati, respond ENTIRELY in Gujarati.
If the question is in Hindi, respond ENTIRELY in Hindi.
If the question is in English, respond ENTIRELY in English.
DO NOT mix languages. DO NOT use English words when responding in Indian languages.
Translate ALL technical terms to the target language.

Answer based on the evidence provided, following these rules:

ANSWER STYLE:
- Use simple, clear language that ordinary citizens can understand
- Avoid technical jargon
- Be helpful and informative
- Answer what CAN be answered from the available evidence

FORMATTING RULES:
- Use proper markdown formatting for readability
- For lists of items, use markdown bullet points with hyphens (- item)
- For numbered steps, use markdown numbered lists (1. item)
- Use **bold** for important terms or document names
- Keep paragraphs short (2-3 sentences maximum)
- Use line breaks between sections for better readability

EVIDENCE RULES:
1. STATIC EVIDENCE (official documents) provides:
   - Policy rules, procedures, eligibility criteria
   - How schemes work (application process, documentation)
   - General framework and structure

2. DYNAMIC EVIDENCE (web sources) provides:
   - Current year notifications, active status
   - District/state-specific current information
   - Current premium rates, insurer assignments

3. WHEN DYNAMIC EVIDENCE IS MISSING:
   - Answer using static evidence what CAN be answered
   - At the END of your answer (not during), add ONE short note in the target language
   - Do NOT repeat this disclaimer multiple times
   - Do NOT refuse to answer what static evidence supports

CITATION RULES:
- After each factual sentence, add [chunk:ID] citation
- Use EXACT citation markers from the evidence
- Use ONLY half-width square brackets []

IMPORTANT:
- Be helpful, not restrictive
- Answer what you CAN from available evidence
- Only note limitations ONCE at the end if needed
- NEVER include chunk IDs like [chunk:xxx] in your visible response to users"""


def strip_citations(answer: str) -> tuple[str, list[str]]:
    """Extract [chunk:ID] markers from LLM output.

    Returns (clean_answer, extracted_ids).
    Backend guarantee: clean_answer contains no [chunk:xxx] patterns.

    Actual chunk-ID formats in this RAG system:
    - Static: 8-char hex prefix of UUID (e.g., 'a0eebc99')
    - Web: 'web_{hex12}_c{N}' prefix (e.g., 'web_a1b2c3d4e5f6_c102')

    Preserves surrounding Markdown structure (newlines, bullets, bold).
    Handles empty IDs [chunk:] and any characters inside the brackets.
    """
    pattern = r'\[chunk:([^\]]*)\]'
    ids = [i for i in re.findall(pattern, answer) if i]
    clean = re.sub(pattern, '', answer)
    # Remove only double-spaces left behind, NOT newlines or markdown structure
    clean = re.sub(r'  +', ' ', clean).strip()
    return clean, ids


# ---------------------------------------------------------------------------
# EvidenceController
# ---------------------------------------------------------------------------


class EvidenceController:
    """Wraps static + web evidence with metadata and requirements."""

    def build_bundle(
        self,
        static_result: RAGResult,
        web_result: RAGResult,
        query_requirements: QueryRequirements,
        query: str,
    ) -> EvidenceBundle:
        static = StaticEvidence(
            available=not static_result.abstained and len(static_result.chunks) > 0,
            chunks=static_result.chunks,
            summary=f"{len(static_result.chunks)} chunks from official documents",
        )

        web_available = not web_result.abstained and len(web_result.chunks) > 0
        web = DynamicEvidence(
            available=web_available,
            chunks=web_result.chunks,
            reason=None if web_available else (
                web_result.reason.value if web_result.reason else "No applicable web evidence found"
            ),
        )

        return EvidenceBundle(
            static=static,
            dynamic=web,
            query_requirements=query_requirements,
            query=query,
        )

    def build_curated_prompt(
        self,
        bundle: EvidenceBundle,
        english_query: str,
        history: list[dict] | None,
        lang: str,
    ) -> tuple[str, str]:
        system_prompt = _SOURCE_PRIORITY_PROMPT

        # Build history text
        hist_text = ""
        if history:
            turns = "\n".join(
                f"{'User' if h.get('role') == 'user' else 'Assistant'}: {h.get('content', '')}"
                for h in history if isinstance(h, dict)
            )
            if turns:
                hist_text = f"Previous conversation:\n{turns}\n\n"

        # Build static evidence section
        static_parts: list[str] = []
        for chunk in bundle.static.chunks:
            short_id = chunk.chunk_id[:8]
            meta_parts = [chunk.title]
            if chunk.section:
                meta_parts.append(chunk.section)
            if chunk.page is not None:
                meta_parts.append(f"p.{chunk.page}")
            meta_str = " — ".join(meta_parts)
            static_parts.append(f"[STATIC] [chunk:{short_id}] ({meta_str})\n{chunk.content}")
        static_section = "\n\n---\n\n".join(static_parts) if static_parts else "No static evidence available."

        # Build dynamic evidence section
        if bundle.dynamic.available:
            dynamic_parts: list[str] = []
            for chunk in bundle.dynamic.chunks:
                short_id = chunk.chunk_id[:8]
                dynamic_parts.append(
                    f"[DYNAMIC] [chunk:{short_id}] ({chunk.title} — web — {chunk.url})\n{chunk.content}"
                )
            dynamic_section = "\n\n---\n\n".join(dynamic_parts)
            dynamic_status = f"available — {len(bundle.dynamic.chunks)} chunks"
        else:
            dynamic_section = "No dynamic evidence available."
            dynamic_status = f"ABSENT — {bundle.dynamic.reason or 'No applicable web evidence found'}"

        user_prompt = (
            f"{hist_text}"
            f"Question: {english_query}\n\n"
            f"== STATIC EVIDENCE (official documents — may not reflect current status) ==\n"
            f"{static_section}\n\n"
            f"== DYNAMIC EVIDENCE (web sources — current information) ==\n"
            f"{dynamic_section}\n\n"
            f"== EVIDENCE AVAILABILITY ==\n"
            f"Static: {len(bundle.static.chunks)} chunks available\n"
            f"Dynamic: {dynamic_status}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. CRITICAL: Respond in the SAME language as the question. If question is in Gujarati, respond ENTIRELY in Gujarati.\n"
            f"2. Answer using static evidence what CAN be answered.\n"
            f"3. If dynamic evidence is missing for current/local details, "
            f"add ONE short note at the END of your answer (not during).\n"
            f"4. Do NOT repeat disclaimers. Do NOT refuse to answer what static evidence supports.\n"
            f"5. Use simple, clear language for ordinary citizens.\n"
            f"6. Do NOT include chunk IDs like [chunk:xxx] in your visible response."
        )

        return system_prompt, user_prompt

    def assess_evidence(
        self,
        static_result: RAGResult,
        web_result: RAGResult,
        query_requirements: QueryRequirements,
    ) -> EvidenceAssessment:
        """Assess evidence quality and determine source priority.

        Source-role rules override raw retrieval scores.
        """
        source_role = self._determine_source_role(query_requirements)
        static_quality = self._score_quality(static_result.chunks)
        web_quality = self._score_quality(web_result.chunks)
        sufficiency = self._check_sufficiency(static_result, web_result, source_role)
        assessment_text = self._generate_assessment_text(
            source_role, sufficiency, static_quality, web_quality,
        )
        return EvidenceAssessment(
            source_role=source_role,
            sufficiency=sufficiency,
            static_quality=static_quality,
            web_quality=web_quality,
            assessment_text=assessment_text,
        )

    # -- private helpers ----------------------------------------------------

    def _determine_source_role(self, qr: QueryRequirements) -> SourceRole:
        """Which source SHOULD have the answer based on query type."""
        if qr.requires_dynamic and qr.temporal_scope in ("current",):
            return SourceRole.WEB_PRIMARY
        if qr.temporal_scope == "general" and not qr.requires_dynamic:
            return SourceRole.STATIC_PRIMARY
        if qr.temporal_scope == "historical":
            return SourceRole.STATIC_PRIMARY
        if qr.temporal_scope not in ("general", "historical", "current"):
            # Explicit year (e.g. "2023") — prefer static with period-matching
            return SourceRole.STATIC_PRIMARY
        return SourceRole.BALANCED

    def _score_quality(self, chunks: list) -> str:
        """Score evidence quality based on retrieval scores."""
        if not chunks:
            return "low"
        high_scores = sum(1 for c in chunks if (c.dense_score or 0) >= 0.7)
        ratio = high_scores / len(chunks) if chunks else 0
        if ratio >= 0.5:
            return "high"
        if ratio >= 0.2:
            return "medium"
        return "low"

    def _check_sufficiency(
        self,
        static_result: RAGResult,
        web_result: RAGResult,
        source_role: SourceRole,
    ) -> EvidenceSufficiency:
        """Check if evidence is sufficient to answer the query.

        Considers: source-role match, retrieval quality, chunk count.
        Two irrelevant chunks are NOT sufficient. One highly authoritative
        chunk can be more useful than five generic ones.
        """
        static_count = len(static_result.chunks)
        web_count = len(web_result.chunks)
        total = static_count + web_count

        if total == 0:
            return EvidenceSufficiency.EMPTY

        static_high = sum(1 for c in static_result.chunks if (c.dense_score or 0) >= 0.5)
        web_high = sum(1 for c in web_result.chunks if (c.dense_score or 0) >= 0.5)

        if source_role == SourceRole.WEB_PRIMARY:
            if web_high >= 2:
                return EvidenceSufficiency.SUFFICIENT
            if web_high >= 1 or web_count >= 1:
                return EvidenceSufficiency.PARTIAL
            return EvidenceSufficiency.INSUFFICIENT

        if source_role == SourceRole.STATIC_PRIMARY:
            if static_high >= 2:
                return EvidenceSufficiency.SUFFICIENT
            if static_high >= 1 or static_count >= 1:
                return EvidenceSufficiency.PARTIAL
            return EvidenceSufficiency.INSUFFICIENT

        # BALANCED
        if (static_high + web_high) >= 3:
            return EvidenceSufficiency.SUFFICIENT
        if total >= 2:
            return EvidenceSufficiency.PARTIAL
        return EvidenceSufficiency.INSUFFICIENT

    def _generate_assessment_text(
        self,
        source_role: SourceRole,
        sufficiency: EvidenceSufficiency,
        static_quality: str,
        web_quality: str,
    ) -> str:
        """Generate human-readable assessment for the prompt."""
        role_text = {
            SourceRole.STATIC_PRIMARY: "Static evidence (official documents) is the primary source for this query.",
            SourceRole.WEB_PRIMARY: "Dynamic evidence (web sources) is the primary source for this query.",
            SourceRole.BALANCED: "Both static and dynamic evidence are relevant.",
        }
        sufficiency_text = {
            EvidenceSufficiency.SUFFICIENT: "Evidence is sufficient to answer.",
            EvidenceSufficiency.PARTIAL: "Evidence partially covers the query. Fill gaps carefully.",
            EvidenceSufficiency.INSUFFICIENT: "Limited evidence available. Answer only what is directly supported.",
            EvidenceSufficiency.EMPTY: "No relevant evidence found. Do not generate a general knowledge answer.",
        }
        return f"{role_text[source_role]} {sufficiency_text[sufficiency]}"
