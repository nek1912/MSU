"""PHASE 11: Multilingual evaluation cases.

Manually reviewed test cases for English, Hindi, and Gujarati.
Each case tests: native query → correct English evidence → correct page → correct grounded answer.

The source corpus is always English. The query is in the user's language.
"""
from dataclasses import dataclass


@dataclass
class EvalCase:
    """One multilingual evaluation case."""
    case_id: str
    language: str  # en, hi, gu
    query_native: str
    query_english_gloss: str  # for human review
    expected_domain: str
    expected_evidence_keywords: list[str]  # keywords that should appear in retrieved chunks
    expected_page: int | None = None
    expected_section: str | None = None
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# ENGLISH CASES (baseline)
# ═══════════════════════════════════════════════════════════════════════════

ENGLISH_CASES = [
    EvalCase(
        case_id="en-001",
        language="en",
        query_native="What is PMFBY eligibility?",
        query_english_gloss="PMFBY eligibility question",
        expected_domain="pmfby",
        expected_evidence_keywords=["eligible", "farmer", "crop"],
        expected_page=1,
        expected_section="Eligibility",
    ),
    EvalCase(
        case_id="en-002",
        language="en",
        query_native="How do I file a PMFBY claim?",
        query_english_gloss="PMFBY claim filing process",
        expected_domain="pmfby",
        expected_evidence_keywords=["claim", "notification", "damage"],
    ),
    EvalCase(
        case_id="en-003",
        language="en",
        query_native="What are the rules for cooperative societies?",
        query_english_gloss="Cooperative society governance rules",
        expected_domain="cooperative",
        expected_evidence_keywords=["cooperative", "society", "members"],
    ),
    EvalCase(
        case_id="en-004",
        language="en",
        query_native="How does PACS provide credit to farmers?",
        query_english_gloss="PACS credit facility for farmers",
        expected_domain="pacs",
        expected_evidence_keywords=["PACS", "credit", "loan"],
    ),
    EvalCase(
        case_id="en-005",
        language="en",
        query_native="What is PMJDY account?",
        query_english_gloss="Pradhan Mantri Jan Dhan Yojana account",
        expected_domain="finlit",
        expected_evidence_keywords=["PMJDY", "account", "bank"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════
# HINDI CASES
# ═══════════════════════════════════════════════════════════════════════════

HINDI_CASES = [
    EvalCase(
        case_id="hi-001",
        language="hi",
        query_native="पीएमएफबीवाई के लिए कौन पात्र है?",
        query_english_gloss="Who is eligible for PMFBY?",
        expected_domain="pmfby",
        expected_evidence_keywords=["eligible", "farmer", "crop"],
        expected_page=1,
        expected_section="Eligibility",
    ),
    EvalCase(
        case_id="hi-002",
        language="hi",
        query_native="पीएमएफबीवाई दावा कैसे दायर करें?",
        query_english_gloss="How to file PMFBY claim?",
        expected_domain="pmfby",
        expected_evidence_keywords=["claim", "notification", "damage"],
    ),
    EvalCase(
        case_id="hi-003",
        language="hi",
        query_native="सहकारी समितियों के नियम क्या हैं?",
        query_english_gloss="What are the rules for cooperative societies?",
        expected_domain="cooperative",
        expected_evidence_keywords=["cooperative", "society", "members"],
    ),
    EvalCase(
        case_id="hi-004",
        language="hi",
        query_native="पीएसीएस किसानों को ऋण कैसे देता है?",
        query_english_gloss="How does PACS provide credit to farmers?",
        expected_domain="pacs",
        expected_evidence_keywords=["PACS", "credit", "loan"],
    ),
    EvalCase(
        case_id="hi-005",
        language="hi",
        query_native="पीएमजेडीवाई खाता क्या है?",
        query_english_gloss="What is PMJDY account?",
        expected_domain="finlit",
        expected_evidence_keywords=["PMJDY", "account", "bank"],
    ),
]

# ═══════════════════════════════════════════════════════════════════════════
# GUJARATI CASES
# ═══════════════════════════════════════════════════════════════════════════

GUJARATI_CASES = [
    EvalCase(
        case_id="gu-001",
        language="gu",
        query_native="પીએમએફબીવાઈ માટે કોણ પાત્ર છે?",
        query_english_gloss="Who is eligible for PMFBY?",
        expected_domain="pmfby",
        expected_evidence_keywords=["eligible", "farmer", "crop"],
        expected_page=1,
        expected_section="Eligibility",
    ),
    EvalCase(
        case_id="gu-002",
        language="gu",
        query_native="પીએમએફબીવાઈ દાવો કેવી રીતે દાખલ કરવો?",
        query_english_gloss="How to file PMFBY claim?",
        expected_domain="pmfby",
        expected_evidence_keywords=["claim", "notification", "damage"],
    ),
    EvalCase(
        case_id="gu-003",
        language="gu",
        query_native="સહકારી સમિતિઓના નિયમો શું છે?",
        query_english_gloss="What are the rules for cooperative societies?",
        expected_domain="cooperative",
        expected_evidence_keywords=["cooperative", "society", "members"],
    ),
    EvalCase(
        case_id="gu-004",
        language="gu",
        query_native="પીએસીએસ ખેડૂતોને ઋણ કેવી રીતે આપે છે?",
        query_english_gloss="How does PACS provide credit to farmers?",
        expected_domain="pacs",
        expected_evidence_keywords=["PACS", "credit", "loan"],
    ),
    EvalCase(
        case_id="gu-005",
        language="gu",
        query_native="પીએમજેડીવાઈ ખાતું શું છે?",
        query_english_gloss="What is PMJDY account?",
        expected_domain="finlit",
        expected_evidence_keywords=["PMJDY", "account", "bank"],
    ),
]

# All cases combined
ALL_CASES = ENGLISH_CASES + HINDI_CASES + GUJARATI_CASES


def get_cases_by_language(lang: str) -> list[EvalCase]:
    """Get evaluation cases for a specific language."""
    return [c for c in ALL_CASES if c.language == lang]
