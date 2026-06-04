"""Fetch repository metadata from GitHub and map to RepoDTO."""

from datetime import datetime
from typing import Any

from contracts.repo_dto import RepoDTO
from data.github_client import GitHubClient


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _raw_to_dto(raw: dict[str, Any], has_readme: bool) -> RepoDTO:
    """Map GitHub API repo object to RepoDTO."""
    size = raw.get("size") or 0
    return RepoDTO(
        name=raw.get("name") or "",
        description=raw.get("description") or None,
        stars=raw.get("stargazers_count") or 0,
        forks=raw.get("forks_count") or 0,
        last_commit_at=_parse_iso(raw.get("pushed_at")),
        language=raw.get("language") or None,
        has_readme=has_readme,
        has_license=bool(raw.get("license")),
        is_empty=size == 0,
        is_fork=raw.get("fork") is True,
        topics=raw.get("topics") or [],
        default_branch=raw.get("default_branch") or None,
        created_at=_parse_iso(raw.get("created_at")),
        updated_at=_parse_iso(raw.get("updated_at")),
    )


def fetch_repos_for_user(
    username: str,
    *,
    include_private: bool = False,
    github_client: GitHubClient | None = None,
    check_readme: bool = True,
) -> list[RepoDTO]:
    """
    Fetch all repositories for a user and return as list of RepoDTO.
    include_private: if True, uses token and fetches all repos (scope 'all').
    check_readme: if True, performs a HEAD/GET per repo to detect README (more API calls).
    """
    client = github_client or GitHubClient()
    raw_repos = client.get_all_user_repos(username, include_private=include_private)
    owner = username

    dtos: list[RepoDTO] = []
    for raw in raw_repos:
        repo_name = raw.get("name") or ""
        has_readme = False
        if check_readme and repo_name:
            has_readme = client.repo_has_readme(owner, repo_name)
        dtos.append(_raw_to_dto(raw, has_readme))

    return dtos
