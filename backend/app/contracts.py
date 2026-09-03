"""Immutable typed contracts for the RAG refactor.

Every component in the pipeline consumes and produces these types.
One canonical taxonomy across manifests, ingestion, database constraints,
routing, retrieval, evaluation, and citations.

Unknown state, applicability, status, or effective date must fail closed
for safety-sensitive legal answers.
"""

from __future__ import annotations

import hashlib
from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Embedding Profile
# ---------------------------------------------------------------------------

class EmbeddingProfile(BaseModel):
    """Immutable description of an embedding model configuration.

    The fingerprint is computed from all fields and must match at startup.
    Any mismatch refuses retrieval.
    """
    provider: str
    model_id: str
    model_revision: str | None = None
    dimension: int
    vector_dtype: str = "float32"
    distance_metric: str = "cosine"
    document_task: str = "retrieval.passage"
    query_task: str = "retrieval.query"
    normalization: str = "l2"
    preprocessing_version: str = "v1"

    @field_validator("dimension")
    @classmethod
    def positive_dimension(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("dimension must be positive")
        return v

    def fingerprint(self) -> str:
        """Deterministic fingerprint from all profile fields."""
        raw = "|".join([
            self.provider, self.model_id, self.model_revision or "",
            str(self.dimension), self.vector_dtype, self.distance_metric,
            self.document_task, self.query_task, self.normalization,
            self.preprocessing_version,
        ])
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Document Metadata
# ---------------------------------------------------------------------------

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class AuthorityTier(str, Enum):
    PRIMARY = "primary"          # Central/state act, gazette notification
    SECONDARY = "secondary"      # Official circular, rule
    TERTIARY = "tertiary"        # News, analysis, third-party
    UNKNOWN = "unknown"


class JurisdictionLevel(str, Enum):
    CENTRAL = "central"
    STATE = "state"
    UNKNOWN = "unknown"


class DocumentMetadata(BaseModel):
    """Authoritative metadata for a single document version."""
    source_id: str = Field(..., min_length=1)
    document_id: str = Field(..., min_length=1)
    version_id: str = Field(..., min_length=1)
    title: str
    issuer: str = ""
    official_url: str = ""
    official_domain: str = ""
    checksum: str = ""
    domain: str
    jurisdiction_level: JurisdictionLevel = JurisdictionLevel.UNKNOWN
    state: str | None = None
    language: str = "en"
    publication_date: date | None = None
    effective_start: date | None = None
    effective_end: date | None = None
    status: DocumentStatus = DocumentStatus.UNKNOWN
    authority_tier: AuthorityTier = AuthorityTier.UNKNOWN
    supersedes: str | None = None
    superseded_by: str | None = None
    parser_profile: str = "pdfplumber-v1"
    metadata_schema_version: str = "v1"

    @field_validator("state")
    @classmethod
    def normalize_state(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v

    def is_active_as_of(self, as_of: date | None = None) -> bool:
        """Check if document is active on a given date."""
        if self.status not in (DocumentStatus.ACTIVE, DocumentStatus.UNKNOWN):
            return False
        if as_of and self.effective_start and as_of < self.effective_start:
            return False
        if as_of and self.effective_end and as_of > self.effective_end:
            return False
        return True


# ---------------------------------------------------------------------------
# Chunk Metadata
# ---------------------------------------------------------------------------

class ChunkMetadata(BaseModel):
    """Deterministic metadata for a single chunk."""
    chunk_id: str = Field(..., min_length=1)
    document_version_id: str = Field(..., min_length=1)
    ordinal: int = Field(..., ge=0)
    content_hash: str = ""
    page_start: int | None = None
    page_end: int | None = None
    heading_path: str = ""
    section_number: str = ""
    language: str = "en"
    token_count: int = 0
    chunker_version: str = "v1"


# ---------------------------------------------------------------------------
# Query Contracts
# ---------------------------------------------------------------------------

class NormalizedQuery(BaseModel):
    """Normalized query with transformation lineage."""
    original_text: str
    normalized_text: str
    language: str = "en"
    script: str = "latn"
    transformation_lineage: list[str] = Field(default_factory=list)
    negation_detected: bool = False
    dates_mentioned: list[str] = Field(default_factory=list)
    amounts_mentioned: list[str] = Field(default_factory=list)
    sections_mentioned: list[str] = Field(default_factory=list)
    states_mentioned: list[str] = Field(default_factory=list)
    schemes_mentioned: list[str] = Field(default_factory=list)


class HardFilter(BaseModel):
    """Filters applied inside both candidate queries before ranking."""
    domain: str | None = None
    jurisdiction_level: JurisdictionLevel | None = None
    state: str | None = None
    status: DocumentStatus = DocumentStatus.ACTIVE
    as_of_date: date | None = None
    authority_tier_min: AuthorityTier | None = None
    corpus_version: str | None = None
    embedding_profile_fingerprint: str | None = None


# ---------------------------------------------------------------------------
# Retrieval Contracts
# ---------------------------------------------------------------------------

class RetrievalComponent(str, Enum):
    DENSE = "dense"
    LEXICAL = "lexical"
    RERANKED = "reranked"


class RetrievalCandidate(BaseModel):
    """A single retrieval candidate with component-level diagnostics."""
    chunk_id: str
    document_id: str
    source_id: str
    dense_rank: int | None = None
    dense_score: float | None = None
    lexical_rank: int | None = None
    lexical_score: float | None = None
    rrf_contribution: float | None = None
    fused_score: float | None = None
    final_rank: int | None = None
    matched_aliases: list[str] = Field(default_factory=list)
    filter_decisions: dict[str, bool] = Field(default_factory=dict)
    corpus_version: str = ""
    index_fingerprint: str = ""
    config_version: str = ""
    latency_ms: float = 0.0


# ---------------------------------------------------------------------------
# Evidence & Abstention
# ---------------------------------------------------------------------------

class AbstentionReason(str, Enum):
    NO_ELIGIBLE_SOURCE = "NO_ELIGIBLE_SOURCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CORPUS_INSUFFICIENT = "CORPUS_INSUFFICIENT"
    AMBIGUOUS_JURISDICTION = "AMBIGUOUS_JURISDICTION"
    UNKNOWN_EFFECTIVE_STATUS = "UNKNOWN_EFFECTIVE_STATUS"
    STALE_OR_SUPERSEDED = "STALE_OR_SUPERSEDED"
    CONFLICTING_AUTHORITIES = "CONFLICTING_AUTHORITIES"
    CITATION_FAILURE = "CITATION_FAILURE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    TRANSCRIPTION_UNCERTAIN = "TRANSCRIPTION_UNCERTAIN"
    DOMAIN_MISMATCH = "DOMAIN_MISMATCH"
    JURISDICTION_MISMATCH = "JURISDICTION_MISMATCH"
    BELOW_TOP1_THRESHOLD = "BELOW_TOP1_THRESHOLD"
    INSUFFICIENT_SUPPORTING_CHUNKS = "INSUFFICIENT_SUPPORTING_CHUNKS"


class ConfidenceBand(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------------------------------------------------------------
# Citation & Answer
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Unified RAG Evidence & Results
# ---------------------------------------------------------------------------

class EvidenceChunk(BaseModel):
    """A single evidence chunk used by both static and web RAG pipelines."""
    chunk_id: str
    content: str
    source_type: Literal["static", "web"]
    title: str = ""
    url: str = ""
    page: int | None = None
    section: str = ""
    domain: str = ""
    jurisdiction: str = ""
    state: str | None = None
    dense_score: float | None = None
    bm25_score: float | None = None
    rerank_score: float | None = None
    trust_score: float | None = None
    metadata: dict = Field(default_factory=dict)


class RAGResult(BaseModel):
    """Aggregated result from a RAG retrieval pipeline."""
    chunks: list[EvidenceChunk] = Field(default_factory=list)
    abstained: bool = False
    reason: AbstentionReason | None = None
    band: ConfidenceBand | None = None
    domain: str = ""
    metadata: dict = Field(default_factory=dict)


class RAGResponse(BaseModel):
    """Unified API response for the /chat endpoint."""
    answer: str
    language: str = "en"
    domain: str = ""
    confidence: float = 0.0
    confidence_level: ConfidenceBand = ConfidenceBand.LOW
    citations: list[dict] = Field(default_factory=list)
    abstained: bool = False
    speech_text: str = ""
    speech_segments: list[dict] = Field(default_factory=list)
    follow_up_question: str | None = None
    mode: str = "rag"
    conversation_id: str = ""


# ---------------------------------------------------------------------------
# Citation & Answer
# ---------------------------------------------------------------------------

class AtomicClaim(BaseModel):
    """A single factual claim in the answer."""
    claim_text: str
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    is_supported: bool = False


class Citation(BaseModel):
    """A citation mapping back to retrieved evidence."""
    chunk_id: str
    source_id: str
    title: str = ""
    section: str = ""
    page: int | None = None
    quote_snippet: str = ""


class Answer(BaseModel):
    """Complete answer with citations, claims, and provenance."""
    answer_text: str
    language: str = "en"
    domain: str = ""
    confidence: ConfidenceBand = ConfidenceBand.LOW
    citations: list[Citation] = Field(default_factory=list)
    atomic_claims: list[AtomicClaim] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    abstained: bool = False
    abstention_reason: AbstentionReason | None = None
    follow_up_question: str | None = None


# ---------------------------------------------------------------------------
# Evaluation Provenance
# ---------------------------------------------------------------------------

class EvaluationRunProvenance(BaseModel):
    """Immutable record of an evaluation run."""
    run_id: str
    git_commit: str
    dependency_lock_hash: str = ""
    migration_head: str = ""
    corpus_manifest_hash: str = ""
    evaluation_hash: str = ""
    embedding_profile: EmbeddingProfile | None = None
    retrieval_config: dict = Field(default_factory=dict)
    provider_versions: dict[str, str] = Field(default_factory=dict)
    timestamp: str = ""
    raw_metrics: dict[str, float] = Field(default_factory=dict)
    failed_case_rankings: list[dict] = Field(default_factory=list)
