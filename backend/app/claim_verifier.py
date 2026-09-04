"""Claim Verification — two-layer verification with filter outcomes."""

from __future__ import annotations

import hashlib
import logging
import re

from app.contracts import (
    ClaimVerification,
    EvidenceBundle,
    FilterOutcome,
    FlaggedClaim,
)

logger = logging.getLogger(__name__)

_YEAR_RE = re.compile(r"\b(20\d{2})\b")
_DISTRICT_NAMES = {
    "surat", "valsad", "navsari", "bardoli", "ahmedabad", "rajkot",
    "jamnagar", "bhuj", "gandhinagar", "vadodara", "anand", "nadiad",
}
_CURRENT_WORDS = {
    "en": ["currently", "now", "today", "current", "active", "present"],
    "hi": ["हाल", "अभी", "वर्तमान"],
    "gu": ["હાલ", "હાલમાં", "અત્યારે", "ચાલુ"],
}


def _claim_id(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences/clauses for claim extraction."""
    parts = re.split(r'(?<=[.!?])\s+|(?<=,)\s+', text)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 10]


class HeuristicClaimVerifier:
    """Detects potentially unsupported claims in LLM answer."""

    def check(self, answer: str, bundle: EvidenceBundle) -> list[FlaggedClaim]:
        flagged: list[FlaggedClaim] = []
        sentences = _split_sentences(answer)

        for sentence in sentences:
            claim_type = self._classify_claim(sentence, bundle)
            flag_reason = self._check_support(sentence, claim_type, bundle)

            if flag_reason:
                flagged.append(FlaggedClaim(
                    claim_id=_claim_id(sentence),
                    claim_text=sentence,
                    claim_type=claim_type,
                    flag_reason=flag_reason,
                    requires_evidence="dynamic" if claim_type == "dynamic" else "any",
                ))

        # HARD RULE: requires_dynamic + dynamic absent → flag ALL claims
        if bundle.query_requirements.requires_dynamic and not bundle.dynamic.available:
            already_flagged = {f.claim_id for f in flagged}
            for sentence in sentences:
                cid = _claim_id(sentence)
                if cid not in already_flagged:
                    flagged.append(FlaggedClaim(
                        claim_id=cid,
                        claim_text=sentence,
                        claim_type="dynamic",
                        flag_reason="requires_dynamic but dynamic evidence absent",
                        requires_evidence="dynamic",
                    ))

        return flagged

    def _classify_claim(self, sentence: str, bundle: EvidenceBundle) -> str:
        s = sentence.lower()

        # Year mention → dynamic
        if _YEAR_RE.search(s):
            return "dynamic"

        # District mention → dynamic
        if any(d in s for d in _DISTRICT_NAMES):
            return "dynamic"

        # Current words → dynamic
        for lang_words in _CURRENT_WORDS.values():
            if any(w in s for w in lang_words):
                return "dynamic"

        # Value/amount claim → mixed
        if re.search(r"\b(\d+%|\d+\.\d+|₹\d+|premium|amount|rate)\b", s):
            return "mixed"

        return "static"

    def _check_support(
        self, sentence: str, claim_type: str, bundle: EvidenceBundle,
    ) -> str | None:
        if claim_type == "dynamic" and not bundle.dynamic.available:
            return "dynamic claim but no dynamic evidence available"
        if claim_type == "mixed" and not bundle.dynamic.available:
            return "mixed claim with dynamic component but no dynamic evidence"
        return None


class LLMClaimVerifier:
    """Uses word overlap to verify flagged claims against minimum relevant evidence.

    MVP implementation — Phase 2 will add Gemini-based verification.
    """

    def verify(
        self,
        flagged_claims: list[FlaggedClaim],
        bundle: EvidenceBundle,
    ) -> list[ClaimVerification]:
        verifications = []
        for claim in flagged_claims:
            evidence_ids = self._find_supporting_evidence(claim, bundle)
            verifications.append(ClaimVerification(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                is_supported=len(evidence_ids) > 0,
                claim_type=claim.claim_type,
                source_type_needed=claim.requires_evidence,
                evidence_found=len(evidence_ids) > 0,
                evidence_ids=evidence_ids,
                rejection_reason=None if evidence_ids else f"No {claim.requires_evidence} evidence supports this claim",
                verification_confidence=0.8 if evidence_ids else 0.2,
            ))
        return verifications

    def _find_supporting_evidence(
        self, claim: FlaggedClaim, bundle: EvidenceBundle,
    ) -> list[str]:
        """Find evidence chunks that support this claim via word overlap."""
        ids: list[str] = []
        claim_words = set(claim.claim_text.lower().split())

        chunks = (
            bundle.dynamic.chunks if claim.requires_evidence == "dynamic"
            else bundle.static.chunks + bundle.dynamic.chunks
        )

        for chunk in chunks:
            chunk_words = set(chunk.content.lower().split())
            overlap = len(claim_words & chunk_words)
            if overlap >= 3:
                ids.append(chunk.chunk_id[:8])

        return ids


class ClaimVerifier:
    """Two-layer claim verification with explicit filter outcomes."""

    def __init__(self) -> None:
        self.heuristic = HeuristicClaimVerifier()
        self.llm = LLMClaimVerifier()

    def verify(
        self,
        answer: str,
        bundle: EvidenceBundle,
    ) -> tuple[str, list[ClaimVerification], bool]:
        flagged = self.heuristic.check(answer, bundle)

        if not flagged:
            return answer, [], False  # fast path

        verifications = self.llm.verify(flagged, bundle)

        outcomes = self._determine_outcomes(verifications, bundle)

        answer, was_modified = self._apply_outcomes(answer, outcomes, verifications)

        if was_modified:
            re_flagged = self.heuristic.check(answer, bundle)
            verifications = self.llm.verify(re_flagged, bundle) if re_flagged else []

        return answer, verifications, was_modified

    def _determine_outcomes(
        self,
        verifications: list[ClaimVerification],
        bundle: EvidenceBundle,
    ) -> dict[str, str]:
        outcomes: dict[str, str] = {}
        for v in verifications:
            if v.is_supported:
                outcomes[v.claim_id] = FilterOutcome.KEEP
            elif v.claim_type == "dynamic" and not bundle.dynamic.available:
                outcomes[v.claim_id] = FilterOutcome.ABSTAIN
            elif v.claim_type == "mixed":
                outcomes[v.claim_id] = FilterOutcome.REGENERATE
            else:
                outcomes[v.claim_id] = FilterOutcome.FILTER
        return outcomes

    def _apply_outcomes(
        self,
        answer: str,
        outcomes: dict[str, str],
        verifications: list[ClaimVerification],
    ) -> tuple[str, bool]:
        was_modified = False
        for v in verifications:
            outcome = outcomes.get(v.claim_id, FilterOutcome.KEEP)
            if outcome == FilterOutcome.FILTER:
                answer = answer.replace(v.claim_text, "").strip()
                was_modified = True
            elif outcome == FilterOutcome.ABSTAIN:
                caveat = "[Current/local information for this claim could not be verified]"
                answer = answer.replace(v.claim_text, caveat).strip()
                was_modified = True
            elif outcome == FilterOutcome.REGENERATE:
                caveat = f"{v.claim_text} (Note: this combines general rules with unverified current data)"
                answer = answer.replace(v.claim_text, caveat).strip()
                was_modified = True

        answer = re.sub(r'\s+', ' ', answer).strip()
        return answer, was_modified
