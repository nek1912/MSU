"""Tests for EvidenceAssessment models."""
from app.contracts import SourceRole, EvidenceSufficiency, EvidenceAssessment


def test_source_role_values():
    assert SourceRole.STATIC_PRIMARY.value == "static_primary"
    assert SourceRole.WEB_PRIMARY.value == "web_primary"
    assert SourceRole.BALANCED.value == "balanced"


def test_evidence_sufficiency_values():
    assert EvidenceSufficiency.SUFFICIENT.value == "sufficient"
    assert EvidenceSufficiency.PARTIAL.value == "partial"
    assert EvidenceSufficiency.INSUFFICIENT.value == "insufficient"
    assert EvidenceSufficiency.EMPTY.value == "empty"


def test_evidence_assessment_model():
    assessment = EvidenceAssessment(
        source_role=SourceRole.WEB_PRIMARY,
        sufficiency=EvidenceSufficiency.PARTIAL,
        static_quality="low",
        web_quality="high",
        assessment_text="Dynamic evidence is stronger.",
    )
    assert assessment.source_role == SourceRole.WEB_PRIMARY
    assert assessment.sufficiency == EvidenceSufficiency.PARTIAL
