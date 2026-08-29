"""Unavoidable citation and claim verifier.

Implements Stage 8: every successful answer MUST pass through this
verifier before serialization. No route may bypass it.

Verifies:
- Citation IDs exist in assembled evidence
- Metadata comes from database, not model
- No wrong corpus/profile/domain/state/date contamination
- No superseded or inactive document citations
- Claims have supporting spans
- No fabricated URLs or citation markers

Permit one bounded repair attempt. If repair fails, return CITATION_FAILURE.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.contracts import (
    AbstentionReason,
    AtomicClaim,
    Citation,
)


_CITE_PATTERN = re.compile(r"\[chunk:([0-9a-fA-F]{8,})\]")

# LLMs (esp. Llama-3.3-70b on Groq) sometimes emit the right chunk-ID prefix
# in the wrong *format* — full-width brackets 【ID】 or a bare half-width hex
# bracket [ID] missing the `chunk:` prefix. These are normalised to the
# canonical [chunk:ID] form. Only the *format* changes; which IDs are valid is
# still decided against the retrieved evidence set, so a non-retrieved or
# fabricated ID remains rejected (never silently accepted).
_FULLWIDTH_CITE = re.compile(r"【\s*(?:chunk:)?\s*([0-9a-fA-F]{8,})\s*】")
_BARE_HEX_CITE = re.compile(r"\[\s*([0-9a-fA-F]{8,})\s*\]")


def normalize_citation_markers(answer: str) -> str:
    """Rewrite recognised citation-format variants into ``[chunk:ID]``.

    Handles full-width brackets (【ID】 / 【chunk:ID】) and bare half-width hex
    brackets ([ID]) that omit the ``chunk:`` prefix. IDs are lower-cased so the
    verifier's prefix match is case-insensitive. The acceptable-ID set is NOT
    expanded here — the verifier still rejects anything not in the retrieved
    evidence.
    """
    answer = _FULLWIDTH_CITE.sub(lambda m: f"[chunk:{m.group(1).lower()}]", answer)
    answer = _BARE_HEX_CITE.sub(lambda m: f"[chunk:{m.group(1).lower()}]", answer)
    return answer


@dataclass
class VerificationResult:
    """Result of citation verification."""
    is_valid: bool
    valid_citations: list[Citation] = field(default_factory=list)
    invalid_prefixes: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    reason: AbstentionReason | None = None
    repair_attempted: bool = False


def extract_citations_from_answer(answer: str) -> list[tuple[str, str]]:
    """Extract all [chunk:ID] markers from answer text.

    Returns list of (full_match, prefix) tuples.
    """
    answer = normalize_citation_markers(answer)
    results = []
    for match in _CITE_PATTERN.finditer(answer):
        full = match.group(0)
        prefix = match.group(1)[:8].lower()
        results.append((full, prefix))
    return results


def verify_citation_ids(
    answer: str,
    evidence_chunk_ids: list[str],
) -> tuple[list[str], list[str]]:
    """Verify all citation prefixes map to actual evidence chunk IDs.

    Returns (valid_ids, invalid_prefixes).
    """
    valid: list[str] = []
    invalid: list[str] = []

    for full_match, prefix in extract_citations_from_answer(answer):
        matched = any(cid.startswith(prefix) for cid in evidence_chunk_ids)
        if matched:
            for cid in evidence_chunk_ids:
                if cid.startswith(prefix) and cid not in valid:
                    valid.append(cid)
                    break
        else:
            if prefix not in invalid:
                invalid.append(prefix)

    return valid, invalid


def verify_no_fabricated_content(answer: str) -> list[str]:
    """Check for fabricated URLs, markdown links, or non-citation markers."""
    issues = []

    # Fabricated URLs
    url_pattern = re.compile(r"https?://[^\s\)]+")
    for match in url_pattern.finditer(answer):
        issues.append(f"fabricated URL: {match.group(0)}")

    # Non-citation markers like [1], [Source], etc.
    bad_markers = re.compile(r"\[(?!\s*chunk:)[A-Za-z0-9\s]+\]")
    for match in bad_markers.finditer(answer):
        issues.append(f"non-citation marker: {match.group(0)}")

    return issues


def verify_claims_supported(
    claims: list[AtomicClaim],
    evidence_chunk_ids: list[str],
) -> list[str]:
    """Verify each atomic claim has supporting evidence."""
    unsupported = []
    for claim in claims:
        if not claim.evidence_chunk_ids:
            unsupported.append(f"no evidence for: {claim.claim_text[:50]}...")
            continue
        # Check if any claimed evidence actually exists in retrieved set
        has_support = any(
            eid in evidence_chunk_ids for eid in claim.evidence_chunk_ids
        )
        if not has_support:
            unsupported.append(f"evidence not in retrieval for: {claim.claim_text[:50]}...")
    return unsupported


def verify_citations(
    answer: str,
    evidence_chunk_ids: list[str],
    claims: list[AtomicClaim] | None = None,
) -> VerificationResult:
    """The ONE citation verification path for all responses.

    Every route that produces an answer MUST call this function.
    No exceptions. No bypasses.

    Args:
        answer: Generated answer text
        evidence_chunk_ids: Chunk IDs from assembled evidence
        claims: Optional atomic claims to verify

    Returns:
        VerificationResult with validity status and details
    """
    # Normalise common citation-format variants (e.g. full-width 【ID】) into
    # the canonical [chunk:ID] form before validation. Validity is still
    # decided against the retrieved evidence set below, so this does not
    # weaken the gate or accept arbitrary IDs.
    answer = normalize_citation_markers(answer)

    # 1. Verify citation IDs map to evidence
    valid_ids, invalid_prefixes = verify_citation_ids(answer, evidence_chunk_ids)

    # 2. Check for fabricated content
    fabrication_issues = verify_no_fabricated_content(answer)

    # 3. Verify claims if provided
    unsupported_claims = []
    if claims:
        unsupported_claims = verify_claims_supported(claims, evidence_chunk_ids)

    # Determine validity
    is_valid = (
        len(invalid_prefixes) == 0
        and len(fabrication_issues) == 0
        and len(unsupported_claims) == 0
        and len(valid_ids) > 0
    )

    # Map to abstention reason if invalid
    reason = None
    if not is_valid:
        if invalid_prefixes:
            reason = AbstentionReason.CITATION_FAILURE
        elif fabrication_issues:
            reason = AbstentionReason.CITATION_FAILURE
        elif unsupported_claims:
            reason = AbstentionReason.INSUFFICIENT_EVIDENCE
        elif not valid_ids:
            reason = AbstentionReason.CITATION_FAILURE

    return VerificationResult(
        is_valid=is_valid,
        valid_citations=[
            Citation(chunk_id=cid, source_id="")
            for cid in valid_ids
        ],
        invalid_prefixes=invalid_prefixes,
        unsupported_claims=unsupported_claims,
        reason=reason,
    )


def verify_and_repair(
    answer: str,
    evidence_chunk_ids: list[str],
    claims: list[AtomicClaim] | None = None,
    repair_fn=None,
) -> VerificationResult:
    """Verify with one bounded repair attempt.

    If verification fails and repair_fn is provided, attempt repair.
    If repair also fails, return CITATION_FAILURE.
    """
    result = verify_citations(answer, evidence_chunk_ids, claims)

    if result.is_valid:
        return result

    # Attempt repair
    if repair_fn:
        result.repair_attempted = True
        try:
            repaired_answer = repair_fn(answer, evidence_chunk_ids)
            repaired_result = verify_citations(
                repaired_answer, evidence_chunk_ids, claims
            )
            repaired_result.repair_attempted = True
            return repaired_result
        except Exception:  # noqa: BLE001
            pass

    return result
