"""Integration tests for entity-aware catalogue and retrieval layer."""
from app.entity_resolver import EntityResolver
from app.entity_catalogue import ENTITY_CATALOGUE, SLUG_TO_ENTITY, DOMAIN_ENTITIES


class TestEntityResolverIntegration:
    """End-to-end tests for entity resolution against the full catalogue."""

    def setup_method(self):
        self.resolver = EntityResolver()

    def test_pmfby_query_resolves(self):
        """Query about PMFBY resolves to pmfby entity."""
        result = self.resolver.resolve("What is PMFBY?")
        assert result.entity_id == "pmfby"
        assert result.domain_tag == "pmfby"
        assert result.confidence >= 0.7

    def test_kcc_query_resolves(self):
        """Query about KCC resolves to kcc entity."""
        result = self.resolver.resolve("KCC eligibility criteria")
        assert result.entity_id == "kcc"
        assert result.domain_tag == "financial_inclusion"

    def test_pacs_membership_query_resolves(self):
        """Query about PACS membership resolves."""
        result = self.resolver.resolve("How to become member of PACS?")
        assert result.entity_id == "pacs-membership"
        assert result.domain_tag == "pacs_governance"

    def test_pacs_byelaws_query_resolves(self):
        """Query about PACS bye-laws resolves to model-pacs-bye-laws."""
        result = self.resolver.resolve("PACS bye-laws")
        assert result.entity_id == "model-pacs-bye-laws"
        assert result.domain_tag == "pacs_governance"

    def test_crop_insurance_resolves_pmfby(self):
        """Query about crop insurance resolves to pmfby."""
        result = self.resolver.resolve("crop insurance scheme")
        assert result.entity_id == "pmfby"

    def test_cooperative_dispute_resolves(self):
        """Query about cooperative disputes resolves."""
        result = self.resolver.resolve("cooperative dispute resolution")
        assert result.entity_id == "cooperative-disputes"

    def test_unrelated_query_returns_none(self):
        """Unrelated query returns no entity match."""
        result = self.resolver.resolve("What is the weather today?")
        assert result.entity_id is None
        assert result.confidence == 0.0

    def test_all_entity_catalogue_entries_have_valid_domain(self):
        """All entities in the catalogue have valid domain tags."""
        valid_domains = {"pmfby", "pacs_governance", "financial_inclusion"}
        for entity_id, entry in ENTITY_CATALOGUE.items():
            assert entry.domain_tag in valid_domains, f"{entity_id} has invalid domain {entry.domain_tag}"

    def test_slug_reverse_lookup_completeness(self):
        """All frontend slugs in catalogue are in SLUG_TO_ENTITY."""
        for entity_id, entry in ENTITY_CATALOGUE.items():
            for slug in entry.frontend_slugs:
                assert slug in SLUG_TO_ENTITY, f"Slug {slug} not in SLUG_TO_ENTITY"
                assert SLUG_TO_ENTITY[slug] == entity_id

    def test_domain_entities_grouping(self):
        """DOMAIN_ENTITIES groups entities correctly by domain."""
        for domain_tag, entity_ids in DOMAIN_ENTITIES.items():
            for eid in entity_ids:
                assert eid in ENTITY_CATALOGUE, f"Entity {eid} not in catalogue"
                assert ENTITY_CATALOGUE[eid].domain_tag == domain_tag
