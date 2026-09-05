"""Tests for ClaimVerifier — heuristic + LLM claim verification."""

from app.claim_verifier import HeuristicClaimVerifier, ClaimVerifier
from app.contracts import (
    EvidenceBundle, StaticEvidence, DynamicEvidence, QueryRequirements,
    EvidenceChunk,
)


def _make_bundle(dynamic_available=True):
    chunks = [EvidenceChunk(chunk_id="s1", content="PMFBY rules", source_type="static", title="t")]
    return EvidenceBundle(
        static=StaticEvidence(available=True, chunks=chunks, summary="rules"),
        dynamic=DynamicEvidence(
            available=dynamic_available,
            chunks=[EvidenceChunk(chunk_id="w1", content="current data", source_type="web", title="w")] if dynamic_available else [],
            reason=None if dynamic_available else "No web results",
        ),
        query_requirements=QueryRequirements(
            temporal_scope="current", geographic_scope="district",
            required_specificity="district", requires_dynamic=True,
        ),
        query="test",
    )


def test_heuristic_flags_dynamic_claims():
    h = HeuristicClaimVerifier()
    bundle = _make_bundle(dynamic_available=False)
    flagged = h.check("In 2026, PMFBY premium is 2% in Surat district.", bundle)
    assert len(flagged) > 0
    assert any(f.claim_type == "dynamic" for f in flagged)


def test_heuristic_no_flags_for_static():
    h = HeuristicClaimVerifier()
    bundle = _make_bundle(dynamic_available=True)
    flagged = h.check("PMFBY is a crop insurance scheme.", bundle)
    # Static claim, dynamic available — may or may not flag, but should not flag as unsupported
    assert all(f.claim_type != "dynamic" for f in flagged)


def test_verifier_fast_path_no_flags():
    from unittest.mock import MagicMock
    v = ClaimVerifier()
    v.heuristic = MagicMock(return_value=[])
    bundle = _make_bundle()
    _answer, vers, modified = v.verify("Simple answer.", bundle)
    assert modified is False
    assert vers == []


def test_verifier_rejects_unsupported_dynamic():
    v = ClaimVerifier()
    bundle = _make_bundle(dynamic_available=False)
    _answer, vers, _modified = v.verify(
        "In 2026, the premium is 2% and crops are cotton.", bundle
    )
    # Should have verifications
    assert len(vers) > 0
    # Unsupported dynamic claims should be flagged
    assert any(not v.is_supported for v in vers)
