"""Tests for the entity catalogue module."""

from __future__ import annotations

import pytest

from app.entity_catalogue import (
    ALIASES,
    DOMAIN_ENTITIES,
    ENTITY_CATALOGUE,
    SLUG_TO_ENTITY,
    EntityEntry,
)


# ---------------------------------------------------------------------------
# Fixtures / constants
# ---------------------------------------------------------------------------

EXPECTED_ENTITY_IDS = [
    "pmfby",
    "pacs-membership",
    "kcc",
    "short-term-crop-credit",
    "godown-storage",
    "agro-input-supply",
    "pmfby-enrolment",
    "cooperative-subsidy",
    "cooperative-training",
    "digital-banking",
    "mscs-act-2002",
    "model-pacs-bye-laws",
    "board-election-rules",
    "cooperative-disputes",
    "state-coop-act",
]


# ---------------------------------------------------------------------------
# EntityEntry model validation
# ---------------------------------------------------------------------------


class TestEntityEntryModel:
    def test_valid_entry(self) -> None:
        entry = EntityEntry(
            entity_id="test",
            entity_type="scheme",
            domain_tag="test_domain",
            frontend_slugs=["test-slug"],
            canonical_name="Test Entity",
            aliases=["test alias"],
        )
        assert entry.entity_id == "test"
        assert entry.entity_type == "scheme"
        assert entry.frontend_slugs == ["test-slug"]

    def test_defaults(self) -> None:
        entry = EntityEntry(
            entity_id="x",
            entity_type="legal",
            domain_tag="y",
            canonical_name="X",
        )
        assert entry.frontend_slugs == []
        assert entry.aliases == []


# ---------------------------------------------------------------------------
# ENTITY_CATALOGUE completeness
# ---------------------------------------------------------------------------


class TestEntityCatalogue:
    def test_all_15_entities_present(self) -> None:
        assert len(ENTITY_CATALOGUE) == 15

    def test_expected_ids_present(self) -> None:
        for eid in EXPECTED_ENTITY_IDS:
            assert eid in ENTITY_CATALOGUE, f"Missing entity: {eid}"

    def test_no_unexpected_ids(self) -> None:
        assert set(ENTITY_CATALOGUE.keys()) == set(EXPECTED_ENTITY_IDS)

    def test_entity_types_valid(self) -> None:
        valid_types = {"scheme", "service", "legal"}
        for eid, entry in ENTITY_CATALOGUE.items():
            assert entry.entity_type in valid_types, (
                f"{eid} has invalid type: {entry.entity_type}"
            )

    def test_entity_ids_match_keys(self) -> None:
        for eid, entry in ENTITY_CATALOGUE.items():
            assert entry.entity_id == eid, (
                f"Key {eid} != entity_id {entry.entity_id}"
            )

    def test_all_entities_have_slugs(self) -> None:
        for eid, entry in ENTITY_CATALOGUE.items():
            assert len(entry.frontend_slugs) >= 1, (
                f"{eid} has no frontend slugs"
            )

    def test_all_entities_have_aliases(self) -> None:
        for eid, entry in ENTITY_CATALOGUE.items():
            assert len(entry.aliases) >= 1, (
                f"{eid} has no aliases"
            )


# ---------------------------------------------------------------------------
# SLUG_TO_ENTITY reverse lookup
# ---------------------------------------------------------------------------


class TestSlugToEntity:
    def test_all_slugs_mapped(self) -> None:
        for eid, entry in ENTITY_CATALOGUE.items():
            for slug in entry.frontend_slugs:
                assert slug in SLUG_TO_ENTITY, (
                    f"Slug '{slug}' not in SLUG_TO_ENTITY"
                )

    def test_slug_maps_to_correct_entity(self) -> None:
        assert SLUG_TO_ENTITY["pmfby"] == "pmfby"
        assert SLUG_TO_ENTITY["kisan-credit-card"] == "kcc"
        assert SLUG_TO_ENTITY["pacs-membership"] == "pacs-membership"
        assert SLUG_TO_ENTITY["mscs-act-2002"] == "mscs-act-2002"

    def test_duplicate_slugs_map_to_canonical(self) -> None:
        model_pacs_slugs = [
            "model-pacs-bye-laws",
            "pac-model-bye-laws-moc",
            "model-pacs-bylaws",
        ]
        for slug in model_pacs_slugs:
            assert SLUG_TO_ENTITY[slug] == "model-pacs-bye-laws", (
                f"Slug '{slug}' should map to model-pacs-bye-laws"
            )

    def test_total_slug_count(self) -> None:
        total = sum(len(e.frontend_slugs) for e in ENTITY_CATALOGUE.values())
        assert len(SLUG_TO_ENTITY) == total


# ---------------------------------------------------------------------------
# ALIASES lookup
# ---------------------------------------------------------------------------


class TestAliases:
    def test_common_abbreviations(self) -> None:
        assert ALIASES["pmfby"] == "pmfby"
        assert ALIASES["kcc"] == "kcc"
        assert ALIASES["pacs"] == "pacs-membership"
        assert ALIASES["crop insurance"] == "pmfby"

    def test_alias_keys_are_lowercased(self) -> None:
        # ALIASES stores keys lowercased; original aliases like "PMFBY" become "pmfby"
        assert ALIASES["pmfby"] == "pmfby"
        assert ALIASES["kcc"] == "kcc"
        assert ALIASES["pacs"] == "pacs-membership"
        # Verify uppercase originals are also stored as lowercase
        assert "PMFBY".lower() in ALIASES
        assert "KCC".lower() in ALIASES
        assert "PACS".lower() in ALIASES

    def test_specific_aliases(self) -> None:
        assert ALIASES["fasal bima"] == "pmfby"
        assert ALIASES["kisan credit card"] == "kcc"
        assert ALIASES["kisan card"] == "kcc"
        assert ALIASES["warehouse"] == "godown-storage"
        assert ALIASES["subsidy"] == "cooperative-subsidy"
        assert ALIASES["dispute resolution"] == "cooperative-disputes"

    def test_mscs_act_aliases(self) -> None:
        assert ALIASES["mscs act"] == "mscs-act-2002"
        assert ALIASES["multi-state cooperative act"] == "mscs-act-2002"
        assert ALIASES["mscs 2002"] == "mscs-act-2002"

    def test_bye_laws_aliases(self) -> None:
        assert ALIASES["pacs bye-laws"] == "model-pacs-bye-laws"
        assert ALIASES["model bye-laws"] == "model-pacs-bye-laws"
        assert ALIASES["pacs bylaws"] == "model-pacs-bye-laws"

    def test_all_aliases_present(self) -> None:
        for eid, entry in ENTITY_CATALOGUE.items():
            for alias in entry.aliases:
                key = alias.lower()
                assert key in ALIASES, (
                    f"Alias '{alias}' (key='{key}') not in ALIASES for {eid}"
                )
                assert ALIASES[key] == eid


# ---------------------------------------------------------------------------
# DOMAIN_ENTITIES grouping
# ---------------------------------------------------------------------------


class TestDomainEntities:
    def test_pmfby_domain(self) -> None:
        assert "pmfby" in DOMAIN_ENTITIES
        assert set(DOMAIN_ENTITIES["pmfby"]) == {"pmfby", "pmfby-enrolment"}

    def test_financial_inclusion_domain(self) -> None:
        assert "financial_inclusion" in DOMAIN_ENTITIES
        fi_entities = set(DOMAIN_ENTITIES["financial_inclusion"])
        assert fi_entities == {"kcc", "short-term-crop-credit", "digital-banking"}

    def test_pacs_governance_domain(self) -> None:
        assert "pacs_governance" in DOMAIN_ENTITIES
        pg_entities = set(DOMAIN_ENTITIES["pacs_governance"])
        expected = {
            "pacs-membership",
            "godown-storage",
            "agro-input-supply",
            "cooperative-subsidy",
            "cooperative-training",
            "mscs-act-2002",
            "model-pacs-bye-laws",
            "board-election-rules",
            "cooperative-disputes",
            "state-coop-act",
        }
        assert pg_entities == expected

    def test_all_entities_in_some_domain(self) -> None:
        all_domain_entities = set()
        for entities in DOMAIN_ENTITIES.values():
            all_domain_entities.update(entities)
        assert all_domain_entities == set(ENTITY_CATALOGUE.keys())

    def test_no_entity_in_multiple_domains(self) -> None:
        seen: dict[str, str] = {}
        for domain, entities in DOMAIN_ENTITIES.items():
            for eid in entities:
                assert eid not in seen, (
                    f"{eid} appears in both '{seen[eid]}' and '{domain}'"
                )
                seen[eid] = domain
