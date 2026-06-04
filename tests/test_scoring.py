"""Tests for scoring engine."""

from datetime import datetime, timezone, timedelta

import pytest

from contracts.repo_dto import RepoDTO
from contracts.scan_response import Classification
from scoring.scorer import STRUCTURE_PENALTY_MAX_TOTAL, score_repo
from scoring.classifier import classify_repo
from scoring.issues import detect_issues
from scoring.suggestions import suggest_improvements
from scoring.aggregator import build_scan_result


def _repo(**kwargs) -> RepoDTO:
    defaults = {
        "name": "my-project",
        "description": "A useful project",
        "stars": 5,
        "forks": 1,
        "last_commit_at": datetime.now(timezone.utc) - timedelta(days=30),
        "language": "Python",
        "has_readme": True,
        "has_license": True,
        "is_empty": False,
        "is_fork": False,
        "topics": ["python"],
        "default_branch": "main",
    }
    defaults.update(kwargs)
    return RepoDTO(**defaults)


def test_score_repo_strong():
    r = _repo()
    assert score_repo(r) >= 70


def test_score_repo_empty():
    r = _repo(is_empty=True, has_readme=False, default_branch=None)
    assert score_repo(r) <= 30


def test_score_repo_no_readme():
    r = _repo(has_readme=False)
    assert score_repo(r) < score_repo(_repo(has_readme=True))


def test_classify_showcase():
    r = _repo()
    score = score_repo(r)
    assert classify_repo(score, r) == Classification.SHOWCASE


def test_classify_archive_empty():
    r = _repo(is_empty=True)
    assert classify_repo(0.0, r) == Classification.ARCHIVE


def test_classify_archive_low_score():
    r = _repo(has_readme=False, description=None, last_commit_at=None)
    score = score_repo(r)
    if score <= 30:
        assert classify_repo(score, r) == Classification.ARCHIVE


def test_detect_issues_missing_readme():
    r = _repo(has_readme=False)
    issues = detect_issues(r)
    assert "Missing README" in issues


def test_detect_issues_empty():
    r = _repo(is_empty=True)
    issues = detect_issues(r)
    assert "Repository is empty" in issues


def test_build_scan_result():
    repos = [
        _repo(name="good"),
        _repo(name="test", has_readme=False),
    ]
    result = build_scan_result(repos)
    assert result.summary.total_repos == 2
    assert len(result.repos) == 2
    assert result.recommended_next_step
    assert result.summary.showcase_ready + result.summary.needs_cleanup + result.summary.archive_candidates == 2


def _full_structure_report() -> dict:
    return {
        "has_files": {
            "readme": True,
            "license": True,
            "gitignore": True,
            "deps": True,
            "tests": True,
            "docs": True,
            "src_layout": True,
        },
        "has_folders": {"tests": True, "docs": True, "src": True},
        "has_files_and_folders": {},
    }


def test_detect_issues_uses_structure_report():
    r = _repo(has_readme=True, has_license=True, structure_report=_full_structure_report())
    issues = detect_issues(r)
    assert "Missing tests folder at repo root" not in issues
    assert "Missing dependency file at repo root" not in issues


def test_detect_issues_structure_gaps():
    sr = {
        "has_files": {
            "readme": False,
            "license": False,
            "gitignore": False,
            "deps": False,
            "tests": False,
            "docs": False,
            "src_layout": False,
        },
        "has_folders": {"tests": False, "docs": False, "src": False},
        "has_files_and_folders": {},
    }
    r = _repo(has_readme=True, has_license=True, structure_report=sr)
    issues = detect_issues(r)
    assert "Missing README (root listing)" in issues
    assert "Missing tests folder at repo root" in issues


def test_score_repo_structure_penalty():
    base = _repo()
    assert score_repo(base) == score_repo(_repo(structure_report=_full_structure_report()))
    good = score_repo(_repo(structure_report=_full_structure_report()))
    penalized = _repo(structure_report={
        "has_files": {k: False for k in ("readme", "license", "gitignore", "deps", "tests", "docs", "src_layout")},
        "has_folders": {"tests": False, "docs": False, "src": False},
        "has_files_and_folders": {},
    })
    bad = score_repo(penalized)
    assert bad < good
    # Raw penalties would exceed cap; total deduction is capped
    assert good - bad <= STRUCTURE_PENALTY_MAX_TOTAL + 0.01
