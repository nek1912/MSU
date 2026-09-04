"""Integration tests for EvidenceController + ClaimVerifier end-to-end flow."""

from app.contracts import (
    RAGResult, EvidenceChunk, ConfidenceBand, AbstentionReason,
    QueryRequirements,
)
from app.evidence_controller import EvidenceController, QueryRequirementClassifier
from app.claim_verifier import ClaimVerifier


controller = EvidenceController()
classifier = QueryRequirementClassifier()
verifier = ClaimVerifier()


# ---------------------------------------------------------------------------
# Step 1: static=6, dynamic=0 — must NOT produce confident current/local answer
# ---------------------------------------------------------------------------

def test_no_confident_answer_when_dynamic_absent():
    """static=6, dynamic=0 must not produce a confident current/local factual answer."""
    static = RAGResult(
        chunks=[
            EvidenceChunk(chunk_id=f"s{i}", content=f"PMFBY rule {i}", source_type="static", title="Guidelines")
            for i in range(6)
        ],
        abstained=False, band=ConfidenceBand.HIGH, domain="pmfby",
    )
    web = RAGResult(chunks=[], abstained=True, band=ConfidenceBand.LOW, domain="pmfby")

    reqs = classifier.classify("હાલમાં Surat જિલ્લામાં PMFBY notified crops", "gu")
    bundle = controller.build_bundle(static, web, reqs, "current crops in Surat")

    assert bundle.dynamic.available is False
    assert reqs.requires_dynamic is True

    # Heuristic verifier must flag ALL sentences as unsupported dynamic claims
    flagged = verifier.heuristic.check(
        "In 2026, PMFBY premium is 2% in Surat district.", bundle
    )
    assert len(flagged) > 0
    assert all(f.requires_evidence == "dynamic" for f in flagged)

    # Full verification pass: nothing should pass through as supported
    answer_text = "In 2026, PMFBY premium is 2% in Surat district."
    answer, vers, modified = verifier.verify(answer_text, bundle)
    assert modified is True
    assert any(not v.is_supported for v in vers)


# ---------------------------------------------------------------------------
# Step 2: Mixed static valid + dynamic unsupported — flag unsupported dynamic
# ---------------------------------------------------------------------------

def test_mixed_static_valid_dynamic_unsupported():
    """Static-only facts pass; dynamic claims get flagged when dynamic evidence absent."""
    static = RAGResult(
        chunks=[
            EvidenceChunk(chunk_id="s1", content="PMFBY is a crop insurance scheme under Govt of India.",
                          source_type="static", title="PMFBY Guidelines"),
        ],
        abstained=False, band=ConfidenceBand.HIGH, domain="pmfby",
    )
    web = RAGResult(chunks=[], abstained=True, band=ConfidenceBand.LOW, domain="pmfby")

    reqs = classifier.classify("What is PMFBY and what is the current premium?", "en")
    bundle = controller.build_bundle(static, web, reqs, "What is PMFBY and what is the current premium?")

    # Dynamic evidence must be absent
    assert bundle.dynamic.available is False

    flagged = verifier.heuristic.check(
        "PMFBY is a crop insurance scheme. Currently the premium is 2%.", bundle
    )
    # At least one flag for the "Currently" sentence
    assert len(flagged) >= 1
    dynamic_flags = [f for f in flagged if f.claim_type == "dynamic"]
    assert len(dynamic_flags) >= 1


# ---------------------------------------------------------------------------
# Step 3: Historical query — should NOT require dynamic evidence
# ---------------------------------------------------------------------------

def test_historical_query_no_dynamic_required():
    """A query about past guidelines should be classified as not requiring dynamic."""
    reqs = classifier.classify("2023 PMFBY guidelines for Gujarat", "en")

    assert reqs.temporal_scope == "historical"
    assert reqs.requires_dynamic is False

    static = RAGResult(
        chunks=[
            EvidenceChunk(chunk_id="s1", content="2023 PMFBY guidelines applied from Oct 2022.",
                          source_type="static", title="2023 Guidelines"),
        ],
        abstained=False, band=ConfidenceBand.HIGH, domain="pmfby",
    )
    web = RAGResult(chunks=[], abstained=True, band=ConfidenceBand.LOW, domain="pmfby")

    bundle = controller.build_bundle(static, web, reqs, "2023 PMFBY guidelines")
    assert bundle.query_requirements.requires_dynamic is False

    # Verifier should NOT flag static claims as needing dynamic evidence
    flagged = verifier.heuristic.check(
        "PMFBY is a crop insurance scheme.", bundle
    )
    dynamic_flags = [f for f in flagged if f.claim_type == "dynamic"]
    assert len(dynamic_flags) == 0


# ---------------------------------------------------------------------------
# Step 4: Retrieval failure handling — pipeline failure returns abstained
# ---------------------------------------------------------------------------

def test_retrieval_failure_produces_abstained_result():
    """When retrieval returns no chunks and abstained=True, bundle should reflect this."""
    static = RAGResult(
        chunks=[], abstained=True, reason=AbstentionReason.NO_ELIGIBLE_SOURCE,
        band=ConfidenceBand.LOW, domain="pmfby",
    )
    web = RAGResult(
        chunks=[], abstained=True, reason=AbstentionReason.PROVIDER_UNAVAILABLE,
        band=ConfidenceBand.LOW, domain="pmfby",
    )

    reqs = classifier.classify("PMFBY scheme details", "en")
    bundle = controller.build_bundle(static, web, reqs, "PMFBY scheme details")

    # Both pipelines failed
    assert bundle.static.available is False
    assert bundle.dynamic.available is False
    assert len(bundle.static.chunks) == 0
    assert len(bundle.dynamic.chunks) == 0

    # Verifier must not crash on empty bundle
    answer, vers, modified = verifier.verify("Some answer.", bundle)
    # No claims to flag since answer is short static
    assert isinstance(vers, list)


def test_retrieval_failure_preserves_reason():
    """Abstention reason from failed retrieval should be preserved in dynamic evidence."""
    web = RAGResult(
        chunks=[], abstained=True, reason=AbstentionReason.PROVIDER_UNAVAILABLE,
        band=ConfidenceBand.LOW, domain="pmfby",
    )
    static = RAGResult(
        chunks=[], abstained=True, band=ConfidenceBand.LOW, domain="pmfby",
    )
    reqs = QueryRequirements(
        temporal_scope="current", geographic_scope="district",
        required_specificity="district", requires_dynamic=True,
    )
    bundle = controller.build_bundle(static, web, reqs, "current data")

    assert bundle.dynamic.available is False
    assert bundle.dynamic.reason is not None
