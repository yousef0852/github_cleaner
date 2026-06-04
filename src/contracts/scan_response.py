"""Output contract for the scan endpoint."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Classification(str, Enum):
    SHOWCASE = "showcase"
    CLEANUP = "cleanup"
    ARCHIVE = "archive"


class EffortHint(str, Enum):
    """Coarse effort estimate for addressing this repo’s issues (rule-based)."""

    QUICK = "quick"
    MEDIUM = "medium"
    LARGE = "large"


class PublishReadiness(str, Enum):
    """Whether the repo is plausibly ready to highlight publicly (deterministic, not legal advice)."""

    READY = "ready"
    ALMOST = "almost"
    NEEDS_WORK = "needs_work"
    ARCHIVE_CANDIDATE = "archive_candidate"


class Summary(BaseModel):
    """Aggregate counts for the scan result."""

    total_repos: int = Field(ge=0)
    showcase_ready: int = Field(ge=0)
    needs_cleanup: int = Field(ge=0)
    archive_candidates: int = Field(ge=0)


class ScoreBreakdown(BaseModel):
    """
    Sub-scores 0–100 for each scoring dimension (before structure penalty).
    `structure_penalty_applied` is NOT a 0–100 score: it is the number of points
    subtracted from the weighted total (after cap, same as scorer logic; max 25).
    """

    documentation: float = Field(..., ge=0, le=100)
    activity: float = Field(..., ge=0, le=100)
    structure: float = Field(..., ge=0, le=100)
    naming: float = Field(..., ge=0, le=100)
    portfolio: float = Field(..., ge=0, le=100)
    structure_penalty_applied: float = Field(
        ...,
        ge=0,
        le=25,
        description="Points subtracted from weighted score due to root structure checklist (capped).",
    )


class RemediationPlan(BaseModel):
    """
    Per-repository remediation: blockers, quick wins, ordered checklist, effort, publish readiness.
    Populated by scoring layer (Task 2+); optional on API until wired.
    """

    blocking_issues: list[str] = Field(
        default_factory=list,
        description="Issues that should be fixed before calling the repo public-ready.",
    )
    quick_wins: list[str] = Field(
        default_factory=list,
        description="Low-effort, high-impact actions.",
    )
    recommended_order: list[str] = Field(
        default_factory=list,
        description="Ordered checklist titles (blockers first, then quick wins, then rest).",
    )
    effort_hint: EffortHint = Field(
        default=EffortHint.MEDIUM,
        description="quick | medium | large — coarse hint from issue count / classification.",
    )
    publish_readiness: PublishReadiness = Field(
        default=PublishReadiness.NEEDS_WORK,
        description="ready | almost | needs_work | archive_candidate — from classification + blockers.",
    )


class RepoResult(BaseModel):
    """Per-repository result with score, classification, and recommendations."""

    name: str
    score: float = Field(ge=0, le=100)
    classification: Classification
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    structure_report: Optional[dict[str, Any]] = Field(
        default=None,
        description="Root-level structure evidence from repo inspector (if collected).",
    )
    score_breakdown: Optional[ScoreBreakdown] = Field(
        default=None,
        description="Per-dimension scores + structure penalty applied; null until scorer exposes breakdown.",
    )
    score_evidence: list[str] = Field(
        default_factory=list,
        description="Short deterministic reasons for the overall score (for agents/users).",
    )
    remediation: Optional[RemediationPlan] = Field(
        default=None,
        description="Structured cleanup plan (blockers, quick wins, order, effort, publish readiness).",
    )


class ScanResponse(BaseModel):
    """Full response for a GitHub profile scan."""

    summary: Summary
    top_issues: list[str] = Field(default_factory=list)
    repos: list[RepoResult] = Field(default_factory=list)
    recommended_next_step: str = ""
