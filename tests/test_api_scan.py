"""Tests for scan API endpoint (mocked GitHub)."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from contracts.repo_dto import RepoDTO

from api.routes.scan import MAX_REPOS_TO_INSPECT


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_repos():
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


MINIMAL_STRUCTURE_REPORT = {
    "has_files": {"readme": True, "license": False, "gitignore": True, "deps": False, "tests": False, "docs": False, "src_layout": False},
    "has_folders": {"tests": False, "docs": False, "src": False},
    "has_files_and_folders": {},
}


@patch("api.routes.scan.inspect_repo")
@patch("api.routes.scan.fetch_repos_for_user")
def test_scan_success(mock_fetch, mock_inspect, client, sample_repos):
    mock_fetch.return_value = sample_repos
    mock_inspect.return_value = MINIMAL_STRUCTURE_REPORT
    resp = client.post(
        "/scan",
        json={
            "github_username": "octocat",
            "review_mode": "portfolio",
            "scan_scope": "public",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert data["summary"]["total_repos"] == 2
    assert "repos" in data
    assert len(data["repos"]) == 2
    assert "recommended_next_step" in data
    assert "top_issues" in data
    assert data["repos"][0]["structure_report"] == MINIMAL_STRUCTURE_REPORT
    assert data["repos"][1]["structure_report"] == MINIMAL_STRUCTURE_REPORT
    assert data["repos"][0]["remediation"] is not None
    assert "blocking_issues" in data["repos"][0]["remediation"]
    assert "publish_readiness" in data["repos"][0]["remediation"]
    assert mock_inspect.call_count == 2
    assert mock_inspect.call_args_list[0].args[0:2] == ("octocat", "good-repo")
    assert mock_inspect.call_args_list[1].args[0:2] == ("octocat", "test")


@patch("api.routes.scan.fetch_repos_for_user")
def test_scan_user_not_found(mock_fetch, client):
    from data.github_client import GitHubClientError
    mock_fetch.side_effect = GitHubClientError("Not found", status_code=404)
    resp = client.post(
        "/scan",
        json={"github_username": "nonexistent-user-xyz-123", "review_mode": "portfolio", "scan_scope": "public"},
    )
    assert resp.status_code == 404


def test_scan_validation(client):
    resp = client.post("/scan", json={"github_username": ""})
    assert resp.status_code == 422


def _minimal_repo(name: str) -> RepoDTO:
    return RepoDTO(
        name=name,
        description="ok description here",
        stars=0,
        forks=0,
        last_commit_at=None,
        language="Python",
        has_readme=True,
        has_license=True,
        is_empty=False,
        is_fork=False,
        topics=[],
        default_branch="main",
    )


@patch("api.routes.scan.inspect_repo")
@patch("api.routes.scan.fetch_repos_for_user")
def test_scan_inspects_at_most_max_repos(mock_fetch, mock_inspect, client):
    """All repos are scored; Contents API (inspect_repo) only for first MAX_REPOS_TO_INSPECT."""
    n = MAX_REPOS_TO_INSPECT + 5
    mock_fetch.return_value = [_minimal_repo(f"repo-{i}") for i in range(n)]
    mock_inspect.return_value = MINIMAL_STRUCTURE_REPORT
    resp = client.post(
        "/scan",
        json={"github_username": "biguser", "review_mode": "portfolio", "scan_scope": "public"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]["total_repos"] == n
    assert mock_inspect.call_count == MAX_REPOS_TO_INSPECT
    assert data["repos"][MAX_REPOS_TO_INSPECT - 1]["structure_report"] is not None
    assert data["repos"][MAX_REPOS_TO_INSPECT]["structure_report"] is None


def test_root_lists_entrypoints(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "github-cleaner"
    assert "scan_voiceflow" in data


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
