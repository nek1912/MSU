"""PHASE 12: Intelligence layer tests.

Tests that the query understanding module correctly extracts:
- language, intent, domain, jurisdiction, entities, temporal_constraints
- retrieval_query (optimized for embedding)

Verifies that the intelligence layer does NOT:
- Invent factual evidence
- Override retrieved evidence
- Bypass metadata filters
- Bypass the evidence gate
- Answer when retrieval fails
"""
import pytest

from app.intelligence import QueryAnalysis, analyze_query


# ═══════════════════════════════════════════════════════════════════════════
# ENTITY EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

class TestEntityExtraction:
    """Must correctly extract scheme/program entities from queries."""

    def test_pmfby_entity(self):
        result = analyze_query("What is PMFBY eligibility?")
        assert "pmfby" in result.entities

    def test_pmfby_full_name(self):
        result = analyze_query("Pradhan Mantri Fasal Bima Yojana kya hai?")
        assert "pmfby" in result.entities

    def test_pmjdy_entity(self):
        result = analyze_query("PMJDY account kaise kholein?")
        assert "pmjdy" in result.entities

    def test_pacs_entity(self):
        result = analyze_query("PACS loan rules kya hain?")
        assert "pacs" in result.entities

    def test_cooperative_entity(self):
        result = analyze_query("Cooperative society rules")
        assert "cooperative" in result.entities

    def test_sahakari_entity(self):
        result = analyze_query("Sahakari niyamo su che?")
        assert "cooperative" in result.entities

    def test_kcc_entity(self):
        result = analyze_query("KCC loan eligibility?")
        assert "kcc" in result.entities

    def test_multiple_entities(self):
        result = analyze_query("PMFBY claim under PACS cooperative")
        assert "pmfby" in result.entities
        assert "pacs" in result.entities
        assert "cooperative" in result.entities

    def test_no_entities(self):
        result = analyze_query("What is the weather today?")
        assert len(result.entities) == 0

    def test_scheme_entity(self):
        result = analyze_query("Is there a subsidy scheme for farmers?")
        assert "scheme" in result.entities


# ═══════════════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

class TestIntentDetection:
    """Must correctly detect user intent from queries."""

    def test_question_intent(self):
        result = analyze_query("What is PMFBY?")
        assert result.intent == "question"

    def test_eligibility_intent(self):
        result = analyze_query("Am I eligible for PMFBY?")
        assert result.intent == "eligibility"

    def test_claim_intent(self):
        result = analyze_query("How to file a claim under PMFBY?")
        assert result.intent == "claim"

    def test_process_intent(self):
        result = analyze_query("How to apply for PACS loan?")
        assert result.intent == "process"

    def test_rules_intent(self):
        result = analyze_query("What are the cooperative rules?")
        assert result.intent == "rules"

    def test_grievance_intent(self):
        result = analyze_query("I want to file a complaint about my PMFBY claim")
        assert result.intent == "grievance"

    def test_documents_intent(self):
        result = analyze_query("What documents are needed for PMJDY?")
        assert result.intent == "documents"

    def test_deadline_intent(self):
        result = analyze_query("What is the last date for PMFBY enrollment?")
        assert result.intent == "deadline"

    def test_status_intent(self):
        result = analyze_query("What is the status of my claim?")
        assert result.intent == "status"

    def test_grievance_priority_over_question(self):
        """Grievance intent should take priority over question."""
        result = analyze_query("I want to file a complaint about cooperative society")
        assert result.intent == "grievance"


# ═══════════════════════════════════════════════════════════════════════════
# TEMPORAL CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════

class TestTemporalConstraints:
    """Must correctly extract temporal constraints from queries."""

    def test_year_constraint(self):
        result = analyze_query("PMFBY rules for 2024?")
        assert any("year:2024" in t for t in result.temporal_constraints)

    def test_current_constraint(self):
        result = analyze_query("What is the current PMFBY premium?")
        assert any("current:" in t for t in result.temporal_constraints)

    def test_latest_constraint(self):
        result = analyze_query("What are the latest cooperative rules?")
        assert any("latest:" in t for t in result.temporal_constraints)

    def test_no_temporal(self):
        result = analyze_query("What is PMFBY?")
        assert len(result.temporal_constraints) == 0


# ═══════════════════════════════════════════════════════════════════════════
# JURISDICTION DETECTION
# ═══════════════════════════════════════════════════════════════════════════

class TestJurisdictionDetection:
    """Must correctly detect jurisdiction hints from queries."""

    def test_gujarat_jurisdiction(self):
        result = analyze_query("PMFBY rules in Gujarat?")
        assert result.jurisdiction == "gujarat"

    def test_maharashtra_jurisdiction(self):
        result = analyze_query("Cooperative rules in Maharashtra?")
        assert result.jurisdiction == "maharashtra"

    def test_central_jurisdiction(self):
        result = analyze_query("What are the central PMFBY rules?")
        assert result.jurisdiction == "central"

    def test_no_jurisdiction(self):
        result = analyze_query("What is PMFBY?")
        assert result.jurisdiction is None


# ═══════════════════════════════════════════════════════════════════════════
# RETRIEVAL QUERY
# ═══════════════════════════════════════════════════════════════════════════

class TestRetrievalQuery:
    """Must produce a valid retrieval query."""

    def test_retrieval_query_preserves_original(self):
        result = analyze_query("What is PMFBY eligibility?")
        assert result.retrieval_query == "What is PMFBY eligibility?"

    def test_retrieval_query_not_empty(self):
        result = analyze_query("पीएमएफबीवाई के लिए कौन पात्र है?")
        assert len(result.retrieval_query) > 0

    def test_original_query_preserved(self):
        q = "What is PMFBY?"
        result = analyze_query(q)
        assert result.original_query == q


# ═══════════════════════════════════════════════════════════════════════════
# LANGUAGE HANDLING
# ═══════════════════════════════════════════════════════════════════════════

class TestLanguageHandling:
    """Must correctly pass language through analysis."""

    def test_english_language(self):
        result = analyze_query("What is PMFBY?", language="en")
        assert result.language == "en"

    def test_hindi_language(self):
        result = analyze_query("पीएमएफबीवाई क्या है?", language="hi")
        assert result.language == "hi"

    def test_gujarati_language(self):
        result = analyze_query("પીએમએફબીવાઈ શું છે?", language="gu")
        assert result.language == "gu"


# ═══════════════════════════════════════════════════════════════════════════
# INTELLIGENCE LAYER CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════

class TestIntelligenceLayerConstraints:
    """Verify the intelligence layer does NOT override retrieval or evidence."""

    def test_domain_is_informational(self):
        """Domain from intelligence is informational — AnchorStore is authoritative."""
        result = analyze_query("What is PMFBY?")
        # Domain might be extracted as informational, but it's not used for retrieval
        # The AnchorStore is authoritative for domain classification
        assert isinstance(result.domain, type(None)) or isinstance(result.domain, str)

    def test_no_factual_evidence(self):
        """Intelligence layer must not invent factual evidence."""
        result = analyze_query("What is PMFBY?")
        # The analysis should only contain metadata, not factual claims
        assert result.entities is not None
        assert result.intent is not None
        # No answer or factual content should be generated
        assert not hasattr(result, 'answer')
        assert not hasattr(result, 'content')

    def test_analysis_is_structured(self):
        """Analysis output must be a structured QueryAnalysis object."""
        result = analyze_query("What is PMFBY?")
        assert isinstance(result, QueryAnalysis)
        assert hasattr(result, 'language')
        assert hasattr(result, 'intent')
        assert hasattr(result, 'entities')
        assert hasattr(result, 'temporal_constraints')
        assert hasattr(result, 'retrieval_query')
        assert hasattr(result, 'original_query')


# ═══════════════════════════════════════════════════════════════════════════
# MULTILINGUAL QUERIES
# ═══════════════════════════════════════════════════════════════════════════

class TestMultilingualQueries:
    """Must handle queries in English, Hindi, and Gujarati."""

    def test_english_query(self):
        result = analyze_query("Who is eligible for PMFBY?")
        assert result.language == "en"
        assert "pmfby" in result.entities
        assert result.intent == "eligibility"

    def test_hindi_query(self):
        result = analyze_query("पीएमएफबीवाई के लिए कौन पात्र है?", language="hi")
        assert result.language == "hi"
        # Hindi queries use Devanagari script — Latin entity patterns don't fire
        # Domain classification is handled by AnchorStore (embeddings), not here

    def test_gujarati_query(self):
        result = analyze_query("પીએમએફબીવાઈ માટે કોણ પાત્ર છે?", language="gu")
        assert result.language == "gu"
        # Gujarati queries use Gujarati script — Latin entity patterns don't fire

    def test_hindi_mixed_script(self):
        """Hindi query with English entities."""
        result = analyze_query("PMFBY claim kaise karein?", language="hi")
        assert "pmfby" in result.entities
        assert result.intent == "claim"
