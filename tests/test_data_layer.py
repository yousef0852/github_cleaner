"""Tests for data layer (GitHub client and repo fetcher)."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from contracts.repo_dto import RepoDTO
from data.github_client import GitHubClient, GitHubClientError
from data.repo_fetcher import _raw_to_dto, fetch_repos_for_user


def test_raw_to_dto():
    raw = {
        "name": "my-repo",
        "description": "A cool project",
        "stargazers_count": 10,
        "forks_count": 2,
        "pushed_at": "2024-01-15T12:00:00Z",
        "language": "Python",
        "license": {"key": "mit"},
        "fork": False,
        "size": 100,
        "topics": ["python", "api"],
        "default_branch": "main",
        "created_at": "2023-06-01T00:00:00Z",
        "updated_at": "2024-01-15T12:00:00Z",
    }
    dto = _raw_to_dto(raw, has_readme=True)
    assert dto.name == "my-repo"
    assert dto.description == "A cool project"
    assert dto.stars == 10
    assert dto.forks == 2
    assert dto.language == "Python"
    assert dto.has_readme is True
    assert dto.has_license is True
    assert dto.is_empty is False
    assert dto.is_fork is False
    assert dto.topics == ["python", "api"]


def test_raw_to_dto_empty_repo():
    raw = {
        "name": "empty",
        "description": None,
        "stargazers_count": 0,
        "forks_count": 0,
        "pushed_at": None,
        "language": None,
        "license": None,
        "fork": False,
        "size": 0,
        "topics": [],
        "default_branch": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    dto = _raw_to_dto(raw, has_readme=False)
    assert dto.is_empty is True
    assert dto.has_readme is False
    assert dto.has_license is False


def test_fetch_repos_for_user_mock():
    """Test fetch_repos_for_user with a mock client (no real API call)."""
    mock_client = MagicMock(spec=GitHubClient)
    mock_client.get_all_user_repos.return_value = [
        {
            "name": "test-repo",
            "description": "Test",
            "stargazers_count": 0,
            "forks_count": 0,
            "pushed_at": "2024-01-01T00:00:00Z",
            "language": "Python",
            "license": None,
            "fork": False,
            "size": 10,
            "topics": [],
            "default_branch": "main",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_client.repo_has_readme.return_value = True

    result = fetch_repos_for_user(
        "octocat",
        include_private=False,
        github_client=mock_client,
        check_readme=True,
    )
    assert len(result) == 1
    assert result[0].name == "test-repo"
    mock_client.get_all_user_repos.assert_called_once_with("octocat", include_private=False)
    mock_client.repo_has_readme.assert_called_once_with("octocat", "test-repo")
