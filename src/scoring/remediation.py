"""Deterministic remediation plan from issues, suggestions, and classification.

Substrings below are kept in sync with **scoring/issues.py** `detect_issues()` output text
so blockers / quick wins match what the API actually returns. Update both when copy changes.
"""

from __future__ import annotations

from contracts.repo_dto import RepoDTO
from contracts.scan_response import (
    Classification,
    EffortHint,
    PublishReadiness,
    RemediationPlan,
    ScoreBreakdown,
)

# Aligns with issues.py: empty, missing readme/license/gitignore/deps, short description, license metadata
_BLOCKING_SUBSTRINGS = (
    "repository is empty",
    "missing readme",  # "Missing README", "Missing README (root listing)"
    "missing license",  # "(root listing)" branch also catches via _is_blocking_issue
    "no license specified",
    "missing .gitignore",
    "missing dependency file at repo root",
    "very short description",  # "No or very short description"
    "inactive for over",  # f"Inactive for over {N} months"
    "poor or placeholder repo name",
)

# issues.py: docs/, src/, tests/ at root — labeled optional or tests-only
_OPTIONAL_STRUCTURE_SUBSTRINGS = (
    "optional for many projects",
    "optional unless publishing",
    "missing tests folder at repo root",
)

# issues.py suggestion-style phrases + topics gap (issue text from detect_issues)
_QUICK_WIN_SUBSTRINGS = (
    "add a readme",
    "add a license",
    "add a clear",
    "add repository topics",
    "add topics",
    "add .gitignore",
    "add a dependency file",
    "add a tests",
    "consider a docs",
    "consider a src",
    "rename repository",
    "add screenshots",
    "no topics/tags for discoverability",
)


def _is_blocking_issue(text: str) -> bool:
    lowered = text.lower()
    if any(s in lowered for s in _BLOCKING_SUBSTRINGS):
        return True
    # issues.py root listing lines: Missing README (root listing), Missing license (root listing), etc.
    if "(root listing)" in lowered and (
        "readme" in lowered or "license" in lowered or ".gitignore" in lowered
    ):
        return True
    return False


def _is_optional_structure_issue(text: str) -> bool:
    lowered = text.lower()
    return any(s in lowered for s in _OPTIONAL_STRUCTURE_SUBSTRINGS)


def _is_quick_win_text(text: str) -> bool:
    lowered = text.lower()
    return any(s in lowered for s in _QUICK_WIN_SUBSTRINGS)


def build_remediation_plan(
    repo: RepoDTO,
    issues: list[str],
    suggestions: list[str],
    classification: Classification,
    score_breakdown: ScoreBreakdown | None = None,
) -> RemediationPlan:
    """
    Partition issues/suggestions into blockers, quick wins, and ordered checklist.
    `score_breakdown` is reserved for future rules (e.g. dimension-specific hints).
    """
    _ = score_breakdown  # noqa: F841 — optional future use

    blocking_issues: list[str] = []
    quick_wins: list[str] = []
    rest: list[str] = []

    for issue in issues:
        if _is_blocking_issue(issue):
            blocking_issues.append(issue)
        elif _is_optional_structure_issue(issue):
            rest.append(issue)
        elif _is_quick_win_text(issue):
            quick_wins.append(issue)
        else:
            rest.append(issue)

    for sugg in suggestions:
        if sugg in quick_wins or sugg in blocking_issues:
            continue
        if _is_quick_win_text(sugg):
            quick_wins.append(sugg)
        else:
            rest.append(sugg)

    seen: set[str] = set()
    recommended_order: list[str] = []
    for item in blocking_issues + quick_wins + rest:
        if item not in seen:
            seen.add(item)
            recommended_order.append(item)

    if classification == Classification.ARCHIVE:
        effort_hint = EffortHint.LARGE
        publish_readiness = PublishReadiness.ARCHIVE_CANDIDATE
    elif repo.is_empty or any("repository is empty" in i.lower() for i in issues):
        effort_hint = EffortHint.LARGE
        publish_readiness = PublishReadiness.NEEDS_WORK
    elif len(blocking_issues) > 2:
        effort_hint = EffortHint.LARGE
        publish_readiness = PublishReadiness.NEEDS_WORK
    elif len(blocking_issues) >= 1:
        effort_hint = EffortHint.MEDIUM
        publish_readiness = (
            PublishReadiness.ALMOST if classification == Classification.SHOWCASE else PublishReadiness.NEEDS_WORK
        )
    elif len(quick_wins) > 2:
        effort_hint = EffortHint.MEDIUM
        publish_readiness = PublishReadiness.ALMOST
    elif classification == Classification.SHOWCASE and not blocking_issues:
        effort_hint = EffortHint.QUICK
        publish_readiness = PublishReadiness.READY
    elif classification == Classification.CLEANUP:
        effort_hint = EffortHint.MEDIUM
        publish_readiness = PublishReadiness.NEEDS_WORK if quick_wins else PublishReadiness.ALMOST
    else:
        effort_hint = EffortHint.QUICK
        publish_readiness = PublishReadiness.ALMOST

    return RemediationPlan(
        blocking_issues=blocking_issues,
        quick_wins=quick_wins,
        recommended_order=recommended_order,
        effort_hint=effort_hint,
        publish_readiness=publish_readiness,
    )
