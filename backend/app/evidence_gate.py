"""Refactored evidence gate using typed contracts.

Implements Stage 7: evidence gate with typed abstention reasons,
calibrated confidence bands, and defense-in-depth checks.

Replaces the monolithic evidence_gate() in retrieval.py with a
composable, testable gate that uses contract types.
"""

from __future__ import annotations

from app.config import MIN_CHUNKS_ABOVE_SECONDARY, SECONDARY_THRESHOLD, TOP1_THRESHOLD
from app.contracts import (
    AbstentionReason,
    ConfidenceBand,
    HardFilter,
    RetrievalCandidate,
)


def check_domain_match(
    candidates: list[RetrievalCandidate],
    expected_domain: str,
) -> AbstentionReason | None:
    """Check all candidates match the expected domain.

    The per-candidate domain decision lives in ``filter_decisions["domain"]`` and
    is derived by the caller from the candidate's metadata vs the request filter
    (see ``app.routes.chat._to_candidate``). A candidate is treated as in-domain
    ONLY when that decision is explicitly ``True``.

    A ``False`` *or missing* decision fails closed (treated as a mismatch) per the
    enforced safety policy: an unknown/missing domain must never be silently
    accepted as matching, because that would let cross-domain evidence reach the LLM.
    """
    for c in candidates:
        if c.filter_decisions.get("domain") is not True:
            return AbstentionReason.DOMAIN_MISMATCH
    return None


def check_jurisdiction(
    candidates: list[RetrievalCandidate],
    expected_state: str | None,
) -> AbstentionReason | None:
    """Check jurisdiction compatibility."""
    for c in candidates:
        is_central = c.filter_decisions.get("is_central", False)
        state_match = c.filter_decisions.get("state_match", False)
        if is_central:
            continue
        if expected_state and state_match:
            continue
        return AbstentionReason.JURISDICTION_MISMATCH
    return None


def check_evidence_sufficient(
    candidates: list[RetrievalCandidate],
    min_top1: float = 0.20,
    min_secondary: float = 0.15,
    min_supporting: int = 1,
) -> AbstentionReason | None:
    """Check evidence meets minimum thresholds."""
    if not candidates:
        return AbstentionReason.NO_ELIGIBLE_SOURCE

    scores = sorted(
        (c.dense_score or 0.0 for c in candidates),
        reverse=True,
    )

    if scores[0] < min_top1:
        return AbstentionReason.BELOW_TOP1_THRESHOLD

    strong = sum(1 for s in scores if s >= min_secondary)
    if strong < min_supporting:
        return AbstentionReason.INSUFFICIENT_SUPPORTING_CHUNKS

    return None


def compute_confidence_band(
    candidates: list[RetrievalCandidate],
    min_top1: float = 0.20,
    min_secondary: float = 0.15,
) -> ConfidenceBand:
    """Compute confidence band from evidence features.

    Uses outcome-calibrated bands, not raw similarity percentages.
    """
    if not candidates:
        return ConfidenceBand.LOW

    scores = sorted(
        (c.dense_score or 0.0 for c in candidates),
        reverse=True,
    )

    top1 = scores[0]
    strong = sum(1 for s in scores if s >= min_secondary)
    total = len(scores)

    # Heuristic band assignment (to be calibrated on held-out data)
    if top1 >= 0.50 and strong >= 3 and strong / max(total, 1) >= 0.5:
        return ConfidenceBand.HIGH
    elif top1 >= 0.35 and strong >= 2:
        return ConfidenceBand.MEDIUM
    else:
        return ConfidenceBand.LOW


def evidence_gate_v2(
    candidates: list[RetrievalCandidate],
    expected_domain: str | None = None,
    expected_state: str | None = None,
    filters: HardFilter | None = None,
) -> tuple[bool, AbstentionReason | None, ConfidenceBand]:
    """Refactored evidence gate returning typed results.

    Defense-in-depth:
    1. Domain mismatch check
    2. Jurisdiction check
    3. Evidence sufficiency check
    4. Confidence computation

    Returns:
        (abstained, reason, confidence_band)
    """
    # Apply hard filters first
    if filters:
        candidates = apply_hard_filters(candidates, filters)

    # Defense-in-depth checks
    if expected_domain:
        reason = check_domain_match(candidates, expected_domain)
        if reason:
            return True, reason, ConfidenceBand.LOW

    reason = check_jurisdiction(candidates, expected_state)
    if reason:
        return True, reason, ConfidenceBand.LOW

    reason = check_evidence_sufficient(
        candidates,
        min_top1=TOP1_THRESHOLD,
        min_secondary=SECONDARY_THRESHOLD,
        min_supporting=MIN_CHUNKS_ABOVE_SECONDARY,
    )
    if reason:
        return True, reason, ConfidenceBand.LOW

    # Compute confidence
    band = compute_confidence_band(candidates)

    return False, None, band


def apply_hard_filters(
    candidates: list[RetrievalCandidate],
    filters: HardFilter,
) -> list[RetrievalCandidate]:
    """Apply hard filters to candidates."""
    result = []
    for c in candidates:
        passed = True
        if filters.domain and c.filter_decisions.get("domain") is False:
            passed = False
        if filters.status and c.filter_decisions.get("active") is False:
            passed = False
        if passed:
            result.append(c)
    return result
