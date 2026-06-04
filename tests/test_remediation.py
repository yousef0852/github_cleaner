"""Tests for remediation plan builder."""

from datetime import datetime, timezone, timedelta

from contracts.repo_dto import RepoDTO
from contracts.scan_response import Classification, PublishReadiness, EffortHint
from scoring.remediation import build_remediation_plan
from scoring.aggregator import build_scan_result


def _breakdown(**kwargs):
    from contracts.scan_response import ScoreBreakdown

    defaults = {
        "documentation": 80.0,
        "activity": 80.0,
        "structure": 80.0,
        "naming": 80.0,
        "portfolio": 80.0,
        "structure_penalty_applied": 0.0,
    }
    defaults.update(kwargs)
    return ScoreBreakdown(**defaults)


def test_empty_repo_is_blocking_and_archive_readiness():
    repo = RepoDTO(
        name="empty",
        description=None,
        stars=0,
        forks=0,
        last_commit_at=None,
        language=None,
        has_readme=False,
        has_license=False,
        is_empty=True,
        is_fork=False,
        topics=[],
        default_branch=None,
    )
    issues = ["Repository is empty"]
    suggestions = ["Consider archiving or hiding this repo from profile"]
    plan = build_remediation_plan(
        repo, issues, suggestions, Classification.ARCHIVE, _breakdown()
    )
    assert "Repository is empty" in plan.blocking_issues
    assert plan.publish_readiness == PublishReadiness.ARCHIVE_CANDIDATE
    assert plan.effort_hint == EffortHint.LARGE


def test_missing_readme_in_blocking():
    repo = RepoDTO(
        name="x",
        description="short",
        stars=0,
        forks=0,
        last_commit_at=datetime.now(timezone.utc) - timedelta(days=30),
        language="Python",
        has_readme=False,
        has_license=True,
        is_empty=False,
        is_fork=False,
        topics=[],
        default_branch="main",
    )
    issues = ["Missing README"]
    plan = build_remediation_plan(repo, issues, [], Classification.CLEANUP, _breakdown())
    assert any("readme" in b.lower() for b in plan.blocking_issues)
    assert plan.publish_readiness in (
        PublishReadiness.NEEDS_WORK,
        PublishReadiness.ALMOST,
    )


def test_no_topics_issue_is_quick_win_not_blocker():
    repo = RepoDTO(
        name="proj",
        description="A long enough description here",
        stars=1,
        forks=0,
        last_commit_at=datetime.now(timezone.utc) - timedelta(days=30),
        language="Python",
        has_readme=True,
        has_license=True,
        is_empty=False,
        is_fork=False,
        topics=[],
        default_branch="main",
    )
    issues = ["No topics/tags for discoverability"]
    plan = build_remediation_plan(repo, issues, [], Classification.CLEANUP, _breakdown())
    assert issues[0] in plan.quick_wins
    assert issues[0] not in plan.blocking_issues


def test_inactive_issue_is_blocking():
    repo = RepoDTO(
        name="old",
        description="Something something ok",
        stars=0,
        forks=0,
        last_commit_at=datetime.now(timezone.utc) - timedelta(days=400),
        language="Python",
        has_readme=True,
        has_license=True,
        is_empty=False,
        is_fork=False,
        topics=["x"],
        default_branch="main",
    )
    issues = ["Inactive for over 12 months"]
    plan = build_remediation_plan(repo, issues, [], Classification.CLEANUP, _breakdown())
    assert issues[0] in plan.blocking_issues


def test_build_scan_result_includes_remediation():
    repo = RepoDTO(
        name="show",
        description="A long description for showcase",
        stars=20,
        forks=2,
        last_commit_at=datetime.now(timezone.utc) - timedelta(days=5),
        language="Python",
        has_readme=True,
        has_license=True,
        is_empty=False,
        is_fork=False,
        topics=["python", "api"],
        default_branch="main",
    )
    scan = build_scan_result([repo])
    assert len(scan.repos) == 1
    r0 = scan.repos[0]
    assert r0.remediation is not None
    assert isinstance(r0.remediation.effort_hint, EffortHint)
    assert isinstance(r0.remediation.publish_readiness, PublishReadiness)
    assert isinstance(r0.remediation.blocking_issues, list)
    assert isinstance(r0.remediation.quick_wins, list)
    assert isinstance(r0.remediation.recommended_order, list)
