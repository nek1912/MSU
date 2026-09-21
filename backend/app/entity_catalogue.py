"""Entity Catalogue — single source of truth for scheme/service/legal entities.

Maps canonical entity IDs to metadata, provides reverse lookups from frontend
slugs and common aliases, and groups entities by domain.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EntityEntry(BaseModel):
    """A canonical entity (scheme, service, or legal document)."""

    entity_id: str
    entity_type: str  # "scheme" | "service" | "legal"
    domain_tag: str
    frontend_slugs: list[str] = Field(default_factory=list)
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Catalogue — canonical entity definitions
# ---------------------------------------------------------------------------

ENTITY_CATALOGUE: dict[str, EntityEntry] = {
    "pmfby": EntityEntry(
        entity_id="pmfby",
        entity_type="scheme",
        domain_tag="pmfby",
        frontend_slugs=["pmfby"],
        canonical_name="Pradhan Mantri Fasal Bima Yojana",
        aliases=["PMFBY", "crop insurance", "fasal bima", "PMFBY scheme"],
    ),
    "pacs-membership": EntityEntry(
        entity_id="pacs-membership",
        entity_type="service",
        domain_tag="pacs_governance",
        frontend_slugs=["pacs-membership"],
        canonical_name="PACS Membership & Services",
        aliases=["PACS membership", "primary agricultural cooperative society", "PACS"],
    ),
    "kcc": EntityEntry(
        entity_id="kcc",
        entity_type="scheme",
        domain_tag="financial_inclusion",
        frontend_slugs=["kisan-credit-card"],
        canonical_name="Kisan Credit Card",
        aliases=["KCC", "Kisan Credit Card", "kisan card"],
    ),
    "short-term-crop-credit": EntityEntry(
        entity_id="short-term-crop-credit",
        entity_type="service",
        domain_tag="financial_inclusion",
        frontend_slugs=["short-term-crop-credit"],
        canonical_name="Short-term Crop Credit",
        aliases=["short term crop loan", "crop credit", "kcc loan"],
    ),
    "godown-storage": EntityEntry(
        entity_id="godown-storage",
        entity_type="service",
        domain_tag="pacs_governance",
        frontend_slugs=["godown-storage"],
        canonical_name="Godown & Storage",
        aliases=["godown", "warehouse", "storage facility", "PACS godown"],
    ),
    "agro-input-supply": EntityEntry(
        entity_id="agro-input-supply",
        entity_type="service",
        domain_tag="pacs_governance",
        frontend_slugs=["agro-input-supply"],
        canonical_name="Agro-input Supply",
        aliases=["agro input", "seeds", "fertilizers", "pesticides supply", "PACS input"],
    ),
    "pmfby-enrolment": EntityEntry(
        entity_id="pmfby-enrolment",
        entity_type="service",
        domain_tag="pmfby",
        frontend_slugs=["pmfby-enrolment"],
        canonical_name="PMFBY Enrolment Assistance",
        aliases=["PMFBY enrollment", "crop insurance enrollment", "PMFBY registration"],
    ),
    "cooperative-subsidy": EntityEntry(
        entity_id="cooperative-subsidy",
        entity_type="service",
        domain_tag="pacs_governance",
        frontend_slugs=["cooperative-subsidy"],
        canonical_name="Cooperative Subsidy",
        aliases=["subsidy", "cooperative subsidy", "PACS subsidy"],
    ),
    "cooperative-training": EntityEntry(
        entity_id="cooperative-training",
        entity_type="service",
        domain_tag="pacs_governance",
        frontend_slugs=["cooperative-training"],
        canonical_name="Cooperative Training Programs",
        aliases=["training", "cooperative training", "PACS training"],
    ),
    "digital-banking": EntityEntry(
        entity_id="digital-banking",
        entity_type="service",
        domain_tag="financial_inclusion",
        frontend_slugs=["digital-banking"],
        canonical_name="Digital Banking Services",
        aliases=["digital banking", "online banking", "internet banking", "PACS digital"],
    ),
    "mscs-act-2002": EntityEntry(
        entity_id="mscs-act-2002",
        entity_type="legal",
        domain_tag="pacs_governance",
        frontend_slugs=["mscs-act-2002"],
        canonical_name="Multi-State Cooperative Societies Act, 2002",
        aliases=["MSCS Act", "multi-state cooperative act", "MSCS 2002"],
    ),
    "model-pacs-bye-laws": EntityEntry(
        entity_id="model-pacs-bye-laws",
        entity_type="legal",
        domain_tag="pacs_governance",
        frontend_slugs=["model-pacs-bye-laws", "pac-model-bye-laws-moc", "model-pacs-bylaws"],
        canonical_name="Model Bye-laws of PACS",
        aliases=["PACS bye-laws", "model bye-laws", "PACS bylaws", "model PACS bye-laws"],
    ),
    "board-election-rules": EntityEntry(
        entity_id="board-election-rules",
        entity_type="legal",
        domain_tag="pacs_governance",
        frontend_slugs=["board-election-rules"],
        canonical_name="Election of Board of Directors — MSCS Rules, 2011",
        aliases=["board election rules", "MSCS election rules", "cooperative election"],
    ),
    "cooperative-disputes": EntityEntry(
        entity_id="cooperative-disputes",
        entity_type="legal",
        domain_tag="pacs_governance",
        frontend_slugs=["cooperative-disputes"],
        canonical_name="Cooperative Dispute Resolution",
        aliases=["dispute resolution", "cooperative disputes", "PACS disputes"],
    ),
    "state-coop-act": EntityEntry(
        entity_id="state-coop-act",
        entity_type="legal",
        domain_tag="pacs_governance",
        frontend_slugs=["state-coop-act"],
        canonical_name="State Cooperative Societies Act",
        aliases=["state cooperative act", "state act", "cooperative societies act"],
    ),
}


# ---------------------------------------------------------------------------
# Reverse lookup: frontend slug → entity_id
# ---------------------------------------------------------------------------

SLUG_TO_ENTITY: dict[str, str] = {}
for _eid, _entry in ENTITY_CATALOGUE.items():
    for _slug in _entry.frontend_slugs:
        SLUG_TO_ENTITY[_slug] = _eid


# ---------------------------------------------------------------------------
# Flat alias lookup: alias (lowercased) → entity_id
# ---------------------------------------------------------------------------

ALIASES: dict[str, str] = {}
for _eid, _entry in ENTITY_CATALOGUE.items():
    for _alias in _entry.aliases:
        ALIASES[_alias.lower()] = _eid


# ---------------------------------------------------------------------------
# Domain grouping: domain_tag → list[entity_id]
# ---------------------------------------------------------------------------

DOMAIN_ENTITIES: dict[str, list[str]] = {}
for _eid, _entry in ENTITY_CATALOGUE.items():
    DOMAIN_ENTITIES.setdefault(_entry.domain_tag, []).append(_eid)
