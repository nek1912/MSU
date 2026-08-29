"""PHASE 12: Intelligence layer — query understanding.

Analyzes the user's query to extract structured metadata:
- language, intent, domain, jurisdiction, entities, temporal_constraints
- retrieval_query (optimized for embedding/retrieval)

This is query UNDERSTANDING, not an alternative knowledge source.
It must NOT:
- Invent factual evidence
- Override retrieved evidence
- Bypass metadata filters
- Bypass the evidence gate
- Answer when retrieval fails

All patterns are loaded from data/intelligence_patterns.json — no hardcoded
scheme names, intent keywords, or jurisdiction lists in this file.
"""
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def _load_patterns() -> dict:
    """Load intelligence patterns from JSON config (cached)."""
    path = DATA_DIR / "intelligence_patterns.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    # Compile regex patterns
    return {
        "scheme": [(re.compile(p, re.IGNORECASE), tag) for p, tag in raw["scheme_patterns"]],
        "intent": [(re.compile(p, re.IGNORECASE), tag) for p, tag in raw["intent_patterns"]],
        "intent_priority": raw["intent_priority"],
        "temporal": [(re.compile(p, re.IGNORECASE), tag) for p, tag in raw["temporal_patterns"]],
        "jurisdiction": [(re.compile(p, re.IGNORECASE), tag) for p, tag in raw["jurisdiction_patterns"]],
    }


@dataclass
class QueryAnalysis:
    """Structured analysis of a user query.
    
    This is query UNDERSTANDING — not an alternative knowledge source.
    The retrieval_query is used for embedding, not for answering.
    """
    language: str = "en"
    intent: str = "question"
    domain: str | None = None  # will be overridden by AnchorStore
    jurisdiction: str | None = None
    entities: list[str] = field(default_factory=list)
    temporal_constraints: list[str] = field(default_factory=list)
    retrieval_query: str = ""  # optimized for embedding
    original_query: str = ""  # preserved for reference


def analyze_query(query: str, language: str = "en") -> QueryAnalysis:
    """Analyze a user query to extract structured metadata.
    
    PHASE 12: This is query understanding, not knowledge retrieval.
    The domain field is informational only — AnchorStore is authoritative.
    The retrieval_query optimizes the query for embedding similarity.
    """
    patterns = _load_patterns()
    original = query
    entities: list[str] = []
    temporal: list[str] = []
    jurisdiction: str | None = None
    intent = "question"

    # Extract entities (from config-driven patterns)
    for pattern, entity_type in patterns["scheme"]:
        if pattern.search(query) and entity_type not in entities:
            entities.append(entity_type)

    # Extract intent (from config-driven patterns + priority list)
    intents_found: list[str] = []
    for pattern, intent_type in patterns["intent"]:
        if pattern.search(query) and intent_type not in intents_found:
            intents_found.append(intent_type)
    if intents_found:
        for p in patterns["intent_priority"]:
            if p in intents_found:
                intent = p
                break

    # Extract temporal constraints (from config-driven patterns)
    for pattern, constraint_type in patterns["temporal"]:
        matches = pattern.findall(query)
        if matches:
            for m in matches:
                val = m if isinstance(m, str) else m[0]
                temporal.append(f"{constraint_type}:{val}")

    # Extract jurisdiction (from config-driven patterns)
    for pattern, state in patterns["jurisdiction"]:
        if pattern.search(query):
            jurisdiction = state
            break

    # Build retrieval query (strip temporal noise, keep semantic core)
    retrieval = _build_retrieval_query(query, entities, temporal)

    return QueryAnalysis(
        language=language,
        intent=intent,
        jurisdiction=jurisdiction,
        entities=entities,
        temporal_constraints=temporal,
        retrieval_query=retrieval,
        original_query=original,
    )


def _build_retrieval_query(query: str, entities: list[str],
                           temporal: list[str]) -> str:
    """Build an optimized retrieval query.
    
    Strategy:
    1. Keep the original query
    2. If temporal constraints exist, note them but don't let them dominate
    3. If entities exist, ensure they're in the query
    
    The goal is to maximize embedding similarity with relevant English chunks.
    """
    # For now, use the original query as the retrieval query.
    # The Gemini multilingual embedding already handles cross-lingual semantics.
    # Temporal and entity extraction are used for metadata filtering, not query rewriting.
    return query
