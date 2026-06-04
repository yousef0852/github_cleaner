"""Flat Voiceflow scan payload: mapper + API."""

from unittest.mock import patch

from contracts.repo_dto import RepoDTO
from contracts.scan_response import (
    Classification,
    RepoResult,
    ScanResponse,
    Summary,
)
from contracts.voiceflow_scan_response import build_voiceflow_scan_response
from fastapi.testclient import TestClient

from api.main import app

_MINIMAL_STRUCTURE_REPORT = {
    "has_files": {
        "readme": True,
        "license": False,
        "gitignore": True,
        "deps": False,
        "tests": False,
        "docs": False,
        "src_layout": False,
    },
    "has_folders": {"tests": False, "docs": False, "src": False},
    "has_files_and_folders": {},
}


def test_build_voiceflow_scan_response_sorts_lowest_score_first():
    """Archive/cleanup slots: lowest-scoring repos first (most urgent)."""
    scan = ScanResponse(
        summary=Summary(total_repos=2, showcase_ready=0, needs_cleanup=2, archive_candidates=0),
        top_issues=[],
        repos=[
            RepoResult(
                name="higher",
                score=55.0,
                classification=Classification.CLEANUP,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="lower",
                score=20.0,
                classification=Classification.CLEANUP,
                issues=[],
                suggestions=[],
            ),
        ],
        recommended_next_step="",
    )
    flat = build_voiceflow_scan_response(scan)
    assert flat.cleanup_repo_1 == "lower"
    assert flat.cleanup_repo_2 == "higher"


def test_build_voiceflow_scan_response_flattens_summary_and_slots():
    scan = ScanResponse(
        summary=Summary(
            total_repos=5,
            showcase_ready=1,
            needs_cleanup=2,
            archive_candidates=2,
        ),
        top_issues=["Issue A", "Issue B"],
        repos=[
            RepoResult(
                name="z-archive",
                score=10.0,
                classification=Classification.ARCHIVE,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="y-archive",
                score=12.0,
                classification=Classification.ARCHIVE,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="c-clean",
                score=40.0,
                classification=Classification.CLEANUP,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="d-clean",
                score=50.0,
                classification=Classification.CLEANUP,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="show",
                score=90.0,
                classification=Classification.SHOWCASE,
                issues=[],
                suggestions=[],
            ),
        ],
        recommended_next_step="Do the next thing",
    )
    flat = build_voiceflow_scan_response(scan)
    assert flat.total_repos == 5
    assert flat.showcase_ready == 1
    assert flat.needs_cleanup == 2
    assert flat.archive_candidates == 2
    assert flat.top_issue_1 == "Issue A"
    assert flat.top_issue_2 == "Issue B"
    assert flat.top_issue_3 == ""
    assert flat.recommended_next_step == "Do the next thing"
    assert flat.archive_repo_1 == "z-archive"
    assert flat.archive_repo_2 == "y-archive"
    assert flat.cleanup_repo_1 == "c-clean"
    assert flat.cleanup_repo_2 == "d-clean"
    assert flat.showcase_repo_1 == "show"
    assert flat.showcase_repo_2 == ""


def test_showcase_slots_highest_score_first():
    scan = ScanResponse(
        summary=Summary(total_repos=2, showcase_ready=2, needs_cleanup=0, archive_candidates=0),
        top_issues=[],
        repos=[
            RepoResult(
                name="second",
                score=70.0,
                classification=Classification.SHOWCASE,
                issues=[],
                suggestions=[],
            ),
            RepoResult(
                name="first",
                score=95.0,
                classification=Classification.SHOWCASE,
                issues=[],
                suggestions=[],
            ),
        ],
        recommended_next_step="",
    )
    flat = build_voiceflow_scan_response(scan)
    assert flat.showcase_repo_1 == "first"
    assert flat.showcase_repo_2 == "second"


def _two_sample_repos() -> list[RepoDTO]:
    return [
        RepoDTO(
            name="good-repo",
            description="A solid project",
            stars=10,
            forks=2,
            last_commit_at=None,
            language="Python",
            has_readme=True,
            has_license=True,
            is_empty=False,
            is_fork=False,
            topics=["python"],
            default_branch="main",
        ),
        RepoDTO(
            name="test",
            description=None,
            stars=0,
            forks=0,
            last_commit_at=None,
            language=None,
            has_readme=False,
            has_license=False,
            is_empty=False,
            is_fork=False,
            topics=[],
            default_branch=None,
        ),
    ]


@patch("api.routes.scan.inspect_repo")
@patch("api.routes.scan.fetch_repos_for_user")
def test_scan_voiceflow_returns_flat_json(mock_fetch, mock_inspect):
    mock_fetch.return_value = _two_sample_repos()
    mock_inspect.return_value = _MINIMAL_STRUCTURE_REPORT
    client = TestClient(app)
    resp = client.post(
        "/scan/voiceflow",
        json={
            "github_username": "octocat",
            "review_mode": "portfolio",
            "scan_scope": "public",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    # No nested summary or repos array
    assert "summary" not in data
    assert "repos" not in data
    assert "top_issues" not in data
    assert "total_repos" in data
    assert isinstance(data["total_repos"], int)
    assert "top_issue_1" in data
    assert "archive_repo_1" in data
    assert "cleanup_repo_1" in data
    assert "showcase_repo_1" in data
    assert "showcase_repo_2" in data
    assert "recommended_next_step" in data
