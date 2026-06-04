"""Scoring engine: deterministic scoring, classification, issues, suggestions."""

from .scorer import score_repo, score_repo_with_breakdown
from .classifier import classify_repo
from .issues import detect_issues
from .suggestions import suggest_improvements
from .aggregator import build_scan_result
from .remediation import build_remediation_plan

__all__ = [
    "score_repo",
    "score_repo_with_breakdown",
    "classify_repo",
    "detect_issues",
    "suggest_improvements",
    "build_scan_result",
    "build_remediation_plan",
]
