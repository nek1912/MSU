"""PHASE 9: Confidence calibration evaluation data schema.

Collects retrieval scores, rank, reranker score, number of agreeing evidence chunks,
domain match, metadata validity, evidence-gate result, answerability, human correctness.

Until calibrated, confidence is an internal diagnostic — not a user-facing probability.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ConfidenceEvalRecord(BaseModel):
    """One evaluation record for confidence calibration.
    
    Collected per /chat request during evaluation runs.
    """
    # Request context
    request_id: str = Field(description="Unique request identifier")
    question: str = Field(description="User question")
    language: Literal["en", "hi"]
    domain: str = Field(description="Classified domain")
    state: str | None = Field(default=None, description="Jurisdiction state")

    # Retrieval metrics
    retrieval_scores: list[float] = Field(
        description="Similarity scores of retrieved chunks, descending")
    retrieval_rank: int = Field(
        description="Rank of top chunk (1-indexed)")
    num_chunks_retrieved: int = Field(
        description="Number of chunks retrieved")
    reranker_score: float | None = Field(
        default=None, description="Reranker score if enabled")

    # Evidence quality
    num_agreeing_chunks: int = Field(
        description="Chunks above SECONDARY_THRESHOLD")
    domain_match: bool = Field(
        description="Whether all chunks match expected domain")
    metadata_valid: bool = Field(
        description="Whether jurisdiction/state/date filters passed")

    # Gate result
    gate_result: Literal["pass", "abstain"]
    gate_reason: str | None = Field(
        default=None, description="Abstention reason if applicable")
    gate_confidence: float = Field(
        description="Raw confidence from evidence gate (heuristic)")

    # Answerability
    answerable: bool = Field(
        description="Whether the question is answerable from corpus")

    # Human judgment
    human_correctness: Literal["correct", "partial", "incorrect", "abstain_correct", "abstain_incorrect"] = Field(
        description="Human judgment of answer correctness")
    human_notes: str | None = Field(
        default=None, description="Optional human notes")

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Record creation timestamp")


class ConfidenceCalibrationStats(BaseModel):
    """Aggregated statistics for confidence calibration analysis."""
    total_records: int
    answerable_count: int
    unanswerable_count: int

    # Gate performance
    gate_pass_count: int
    gate_abstain_count: int
    true_positive: int  # answerable + gate pass
    true_negative: int  # unanswerable + gate abstain
    false_positive: int  # unanswerable + gate pass (hallucination risk)
    false_negative: int  # answerable + gate abstain (missed answer)

    # Metrics
    precision: float = Field(description="TP / (TP + FP)")
    recall: float = Field(description="TP / (TP + FN)")
    f1: float = Field(description="2 * precision * recall / (precision + recall)")

    # Confidence distribution
    mean_confidence: float
    std_confidence: float
    median_confidence: float

    # Per-domain breakdown
    domain_stats: dict[str, dict] = Field(
        default_factory=dict,
        description="Per-domain statistics")


def compute_calibration_stats(records: list[ConfidenceEvalRecord]) -> ConfidenceCalibrationStats:
    """Compute calibration statistics from evaluation records."""
    if not records:
        return ConfidenceCalibrationStats(
            total_records=0, answerable_count=0, unanswerable_count=0,
            gate_pass_count=0, gate_abstain_count=0,
            true_positive=0, true_negative=0,
            false_positive=0, false_negative=0,
            precision=0.0, recall=0.0, f1=0.0,
            mean_confidence=0.0, std_confidence=0.0, median_confidence=0.0,
        )

    answerable = [r for r in records if r.answerable]
    unanswerable = [r for r in records if not r.answerable]
    gate_pass = [r for r in records if r.gate_result == "pass"]
    gate_abstain = [r for r in records if r.gate_result == "abstain"]

    tp = sum(1 for r in records if r.answerable and r.gate_result == "pass")
    tn = sum(1 for r in records if not r.answerable and r.gate_result == "abstain")
    fp = sum(1 for r in records if not r.answerable and r.gate_result == "pass")
    fn = sum(1 for r in records if r.answerable and r.gate_result == "abstain")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    confs = [r.gate_confidence for r in records]
    mean_c = sum(confs) / len(confs) if confs else 0.0
    std_c = (sum((c - mean_c) ** 2 for c in confs) / len(confs)) ** 0.5 if len(confs) > 1 else 0.0
    sorted_confs = sorted(confs)
    median_c = sorted_confs[len(sorted_confs) // 2] if sorted_confs else 0.0

    # Per-domain stats
    domains = {r.domain for r in records}
    domain_stats = {}
    for d in domains:
        dr = [r for r in records if r.domain == d]
        d_tp = sum(1 for r in dr if r.answerable and r.gate_result == "pass")
        d_tn = sum(1 for r in dr if not r.answerable and r.gate_result == "abstain")
        d_fp = sum(1 for r in dr if not r.answerable and r.gate_result == "pass")
        d_fn = sum(1 for r in dr if r.answerable and r.gate_result == "abstain")
        domain_stats[d] = {
            "total": len(dr),
            "tp": d_tp, "tn": d_tn, "fp": d_fp, "fn": d_fn,
        }

    return ConfidenceCalibrationStats(
        total_records=len(records),
        answerable_count=len(answerable),
        unanswerable_count=len(unanswerable),
        gate_pass_count=len(gate_pass),
        gate_abstain_count=len(gate_abstain),
        true_positive=tp,
        true_negative=tn,
        false_positive=fp,
        false_negative=fn,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        mean_confidence=round(mean_c, 4),
        std_confidence=round(std_c, 4),
        median_confidence=round(median_c, 4),
        domain_stats=domain_stats,
    )
