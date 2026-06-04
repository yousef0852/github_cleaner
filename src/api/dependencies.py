"""FastAPI dependencies: config and GitHub client."""

from data.github_client import GitHubClient


def get_github_client() -> GitHubClient:
    """Provide a shared GitHub client (read-only)."""
    return GitHubClient()
