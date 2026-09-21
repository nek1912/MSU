"""Entity Resolver — maps free-text queries to canonical entity IDs.

Synchronous resolution using alias + keyword matching only.
Embedding-based resolution will be added later (requires async).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.app.entity_catalogue import ALIASES, ENTITY_CATALOGUE


class EntityResolution(BaseModel):
    """Result of resolving a user query to a catalogue entity."""

    entity_id: str | None = Field(
        default=None,
        description="Canonical entity ID if resolved, else None",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the resolution",
    )
    method: str = Field(
        default="none",
        description="Resolution method used: alias | keyword | none",
    )
    domain_tag: str | None = Field(
        default=None,
        description="Domain tag of the matched entity",
    )


class EntityResolver:
    """Resolves user queries to entity IDs via alias and keyword matching."""

    def resolve(self, query: str) -> EntityResolution:
        """Resolve a query string to an entity.

        Priority:
        1. Exact alias match (confidence 1.0)
        2. Keyword match — entity canonical name or alias appears in query (0.85)
        3. No match (0.0)
        """
        normalised = query.lower().strip()

        # --- 1. Exact alias match ---
        entity_id = ALIASES.get(normalised)
        if entity_id is not None:
            entry = ENTITY_CATALOGUE[entity_id]
            return EntityResolution(
                entity_id=entity_id,
                confidence=1.0,
                method="alias",
                domain_tag=entry.domain_tag,
            )

        # --- 2. Keyword match ---
        best_match: EntityResolution | None = None
        for entry in ENTITY_CATALOGUE.values():
            keywords = [entry.canonical_name.lower(), *[a.lower() for a in entry.aliases]]
            for kw in keywords:
                if kw in normalised:
                    if best_match is None or best_match.confidence < 0.85:
                        best_match = EntityResolution(
                            entity_id=entry.entity_id,
                            confidence=0.85,
                            method="keyword",
                            domain_tag=entry.domain_tag,
                        )
                    break  # one keyword hit is enough for this entity

        if best_match is not None:
            return best_match

        # --- 3. No match ---
        return EntityResolution(
            entity_id=None,
            confidence=0.0,
            method="none",
            domain_tag=None,
        )
