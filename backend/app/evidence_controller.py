"""Evidence Controller — query classification, evidence bundling, prompt curation."""

from __future__ import annotations

import datetime
import logging
import re

from app.contracts import QueryRequirements

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
