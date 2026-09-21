"""Tests for entity_id assignment in ingest_seed DOC_META."""

from __future__ import annotations

from app.entity_catalogue import ENTITY_CATALOGUE


def _get_doc_meta() -> dict[str, dict]:
    """Import DOC_META without triggering supabase/config at module level.

    The ingest_seed module has top-level imports (supabase, app.config) that
    may fail outside a runtime context.  We extract only the DOC_META dict
    literal by tracking brace nesting from the ``DOC_META = {`` line.
    """
    from pathlib import Path

    source = (Path(__file__).resolve().parent.parent / "ingest_seed.py").read_text()
    lines = source.splitlines()

    # Find the start of DOC_META
    start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("DOC_META"):
            start_idx = i
            break
    assert start_idx is not None, "DOC_META not found in ingest_seed.py"

    # Track brace nesting to find the end of the dict
    depth = 0
    block_lines: list[str] = []
    for line in lines[start_idx:]:
        block_lines.append(line)
        depth += line.count("{") - line.count("}")
        if depth == 0:
            break

    ns: dict = {}
    exec("\n".join(block_lines), ns)  # noqa: S102
    return ns["DOC_META"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDocMetaHasEntityId:
    """Every DOC_META entry must carry an 'entity_id' key (value may be None)."""

    def test_all_entries_have_entity_id_key(self) -> None:
        doc_meta = _get_doc_meta()
        for doc_id, meta in doc_meta.items():
            assert "entity_id" in meta, (
                f"Document {doc_id!r} is missing 'entity_id' key in DOC_META"
            )

    def test_entity_id_values_are_valid_or_none(self) -> None:
        doc_meta = _get_doc_meta()
        valid_ids = set(ENTITY_CATALOGUE.keys())
        for doc_id, meta in doc_meta.items():
            eid = meta["entity_id"]
            if eid is not None:
                assert eid in valid_ids, (
                    f"Document {doc_id!r} has entity_id={eid!r} "
                    f"which is not in ENTITY_CATALOGUE. "
                    f"Valid IDs: {sorted(valid_ids)}"
                )


class TestPmfbyDocumentsEntityId:
    """All PMFBY-domain documents should map to entity_id='pmfby'."""

    PMFBY_DOC_IDS = [
        "operational_guidelines_pmfby",
        "Affordable Crop Insurance for Every Farmer",
        "aws_gui_cre",
        "GuidlinesforAWSandWeather Data-15.04",
        "National Agricultural Insurance Scheme (NAIS)- Scheme and Operational Modalities",
        "New Schemes-english_",
        "PMFBY_Features",
        "PMFBY_WINDS_Manual_2023_for_Hyperlocal_Weather_Data_Procurement_120923",
        "PMFBY-Advertisement",
        "PRESS_Bhima",
        "Revamped Operational Guidelines_17th August 2020",
        "RWBCIS_Revised_Guidelines_1",
        "Sop For Bank Branch Users For Implementation Of Pmfby Rwbcis During Kharif 2021",
        "Unified Package Insurance Scheme (UPIS)-Operational Guidelines (OGs)",
        "Weather Based Crop Insurance Scheme (WBCIS)-Operational Guidelines (OGs)",
        "YESTECH_Manual_2023_v2",
    ]

    def test_all_pmfby_docs_have_pmfby_entity(self) -> None:
        doc_meta = _get_doc_meta()
        for doc_id in self.PMFBY_DOC_IDS:
            assert doc_id in doc_meta, f"Missing DOC_META entry: {doc_id!r}"
            assert doc_meta[doc_id]["entity_id"] == "pmfby", (
                f"Document {doc_id!r} should have entity_id='pmfby', "
                f"got {doc_meta[doc_id]['entity_id']!r}"
            )


class TestPacsGovernanceEntityIds:
    """PACS governance documents map to specific entity IDs."""

    EXPECTED_MAPPINGS = {
        "Model Byelaws 05.01.2023": "model-pacs-bye-laws",
        "Model_HR_Policy_V21": "pacs-membership",
        "PACS_HR_Policy": "pacs-membership",
        "Central_Registrar_Order": "mscs-act-2002",
        "Cooperative_Member_Introduction": "pacs-membership",
        "Gujarat_Cooperative_Act_1961": "state-coop-act",
        "MoC_Young_Professionals_YPs": "pacs-membership",
        "Cooperative_Sugar_Mills_CSM_Scheme": "pacs-membership",
    }

    def test_pacs_governance_mappings(self) -> None:
        doc_meta = _get_doc_meta()
        for doc_id, expected_eid in self.EXPECTED_MAPPINGS.items():
            assert doc_id in doc_meta, f"Missing DOC_META entry: {doc_id!r}"
            assert doc_meta[doc_id]["entity_id"] == expected_eid, (
                f"Document {doc_id!r}: expected entity_id={expected_eid!r}, "
                f"got {doc_meta[doc_id]['entity_id']!r}"
            )


class TestNullEntityIds:
    """Financial inclusion and schemes docs without clear entity → None."""

    NULL_ENTITY_DOCS = [
        "NSFI_2025_30",
        "RBI_FAME_Financial_Awareness_Messages",
        "RBI_BEAWARE_Financial_Fraud_Awareness",
        "Introduction_To_Insurance_IRDAI",
        "IntroductionToInsurance",
        "GUIDE310113_F",
        "RBI_BEAWARE_Financial_Fraud",
        "RBI_FAME_Financial_Awareness",
        "RBI_Financial_Education_NSFE",
        "Cooperative_Sugar_Mills_Scheme",
    ]

    def test_no_entity_for_unmapped_docs(self) -> None:
        doc_meta = _get_doc_meta()
        for doc_id in self.NULL_ENTITY_DOCS:
            assert doc_id in doc_meta, f"Missing DOC_META entry: {doc_id!r}"
            assert doc_meta[doc_id]["entity_id"] is None, (
                f"Document {doc_id!r} should have entity_id=None, "
                f"got {doc_meta[doc_id]['entity_id']!r}"
            )
