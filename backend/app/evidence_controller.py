"""Evidence Controller — query classification, evidence bundling, prompt curation."""

from __future__ import annotations

import datetime
import logging
import re

from app.contracts import (
    EvidenceBundle,
    DynamicEvidence,
    EvidenceChunk,
    QueryRequirements,
    RAGResult,
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
            current_year = datetime.datetime.now().year
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
        if temporal not in ("general", "historical"):
            # Explicit year → needs dynamic
            return True
        return False


# ---------------------------------------------------------------------------
# Source Priority Prompt
# ---------------------------------------------------------------------------

_SOURCE_PRIORITY_PROMPT = """You are a government information assistant. You must answer based on
the evidence provided, following these SOURCE PRIORITY RULES:

1. STATIC EVIDENCE (official documents, guidelines, policies) may establish:
   - Policy definitions and legal framework
   - Eligibility rules and general procedures
   - Historical or general scheme structure
   - How processes work (notification, application, etc.)

2. DYNAMIC EVIDENCE (web sources, current data) must establish:
   - Current values, amounts, figures
   - Current notifications and active schemes
   - District/state-specific information
   - Current portal/service availability
   - Current insurer assignments
   - Current premium/coverage figures

3. RULES FOR COMBINED EVIDENCE:
   - Never use static evidence to state a current/local fact unless
     dynamic evidence explicitly confirms it
   - If dynamic evidence is absent or insufficient for a current/local
     claim, say so clearly — do NOT infer from static evidence
   - Static evidence can explain the rule/framework surrounding an
     unanswered dynamic claim

4. EVIDENCE SEPARATION:
   - Evidence marked [STATIC] comes from official documents (may be outdated)
   - Evidence marked [DYNAMIC] comes from web sources (current but may vary)
   - Treat them as having different epistemic roles

5. CITATIONS:
   - After EVERY factual sentence, add the citation: [chunk:ID]
   - Use the EXACT citation marker shown in the evidence
   - Use ONLY half-width square brackets []

6. LANGUAGE:
   - Respond in the SAME language as the question
   - Do NOT switch languages mid-response"""


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
            static_parts.append(
                f"[STATIC] [chunk:{short_id}] ({chunk.title} — {chunk.section} — p.{chunk.page})\n{chunk.content}"
            )
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
            f"Synthesize an answer following the SOURCE PRIORITY RULES.\n"
            f"If dynamic evidence is absent for a current/local claim, state that clearly.\n"
            f"Do NOT infer current values from static guidelines."
        )

        return system_prompt, user_prompt
