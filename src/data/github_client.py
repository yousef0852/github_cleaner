"""HTTP client for GitHub REST API. Read-only operations only."""

import os
from typing import Any

import httpx

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubClientError(Exception):
    """Raised when a GitHub API request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class GitHubClient:
    """Read-only client for GitHub REST API."""

    def __init__(
        self,
        base_url: str = GITHUB_API_BASE,
        token: str | None = None,
        timeout: float = 60.0,
    ):
        self._base = base_url.rstrip("/")
        self._token = token or os.environ.get("GITHUB_TOKEN")
        self._timeout = timeout
        self._headers = dict(DEFAULT_HEADERS)
        if self._token:
            self._headers["Authorization"] = f"Bearer {self._token}"

    @property
    def has_auth_token(self) -> bool:
        """True if a GitHub token is configured (for private scope and rate limits)."""
        return bool(self._token)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        url = f"{self._base}{path}" if path.startswith("/") else f"{self._base}/{path}"
        with httpx.Client(
            headers=self._headers,
            timeout=self._timeout,
        ) as client:
            return client.request(method, url, params=params or {})

    def get_user_repos(
        self,
        username: str,
        *,
        type_: str = "owner",
        per_page: int = 100,
        sort: str = "updated",
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        List repositories for a user.
        type_: 'all' | 'owner' | 'member'; use 'owner' for public-only when no token.
        """
        path = f"/users/{username}/repos"
        params = {
            "type": type_,
            "per_page": per_page,
            "sort": sort,
            "page": page,
        }
        resp = self._request("GET", path, params=params)
        if resp.status_code == 404:
            raise GitHubClientError(f"User not found: {username}", status_code=404)
        if resp.status_code != 200:
            raise GitHubClientError(
                f"GitHub API error: {resp.text}",
                status_code=resp.status_code,
            )
        return resp.json()

    def get_all_user_repos(
        self,
        username: str,
        *,
        include_private: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Fetch all repositories for a user (paginated).
        include_private: if True, requires token and fetches all repos.
        """
        type_ = "all" if include_private and self._token else "owner"
        all_repos: list[dict[str, Any]] = []
        page = 1
        while True:
            batch = self.get_user_repos(username, type_=type_, page=page)
            if not batch:
                break
            all_repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return all_repos

    def repo_has_readme(self, owner: str, repo: str) -> bool:
        """Check if repository has a README (any variant)."""
        path = f"/repos/{owner}/{repo}/readme"
        resp = self._request("GET", path)
        return resp.status_code == 200

    def get_repo_root_contents(self, owner: str, repo: str, path: str = "") -> list[dict[str, Any]]:
        """Get the root contents of a repository."""
        path = f"/repos/{owner}/{repo}/contents/{path}".rstrip("/")
        resp = self._request("GET", path)
        if resp.status_code == 404:
            raise GitHubClientError(f"Repository not found: {owner}/{repo}", status_code=404)
        if resp.status_code != 200:
            raise GitHubClientError(
                f"GitHub API error: {resp.text}",
                status_code=resp.status_code,
            )
        return resp.json()
