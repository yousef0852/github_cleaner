"""Scan endpoint: run portfolio/cleanup analysis for a GitHub user."""

from fastapi import APIRouter, Depends, HTTPException

from contracts.scan_request import ScanRequest, ScanScope
from contracts.scan_response import ScanResponse
from contracts.voiceflow_scan_response import (
    VoiceflowScanResponse,
    build_voiceflow_scan_response,
)
from data.github_client import GitHubClient, GitHubClientError
from data.repo_fetcher import fetch_repos_for_user
from data.repo_inspector import inspect_repo
from scoring.aggregator import build_scan_result

from api.dependencies import get_github_client

# Limit Contents API calls per scan (rate limits). All repos are still scored; only
# the first N get structure_report; the rest get structure_report=None.
MAX_REPOS_TO_INSPECT = 40

router = APIRouter(prefix="/scan", tags=["scan"])


def _execute_scan(body: ScanRequest, github_client: GitHubClient) -> ScanResponse:
    """Shared pipeline: fetch, inspect, aggregate. Raises HTTPException on API errors."""
    include_private = body.scan_scope == ScanScope.ALL
    if include_private and not github_client.has_auth_token:
        raise HTTPException(
            status_code=400,
            detail="scan_scope 'all' requires GITHUB_TOKEN to be set",
        )
    try:
        repos = fetch_repos_for_user(
            body.github_username,
            include_private=include_private,
            github_client=github_client,
            check_readme=True,
        )
        for i, repo in enumerate(repos):
            if i >= MAX_REPOS_TO_INSPECT:
                repos[i] = repo.model_copy(update={"structure_report": None})
                continue
            try:
                report = inspect_repo(
                    body.github_username, repo.name, github_client
                )
            except GitHubClientError:
                report = None
            repos[i] = repo.model_copy(update={"structure_report": report})
    except Exception as e:
        if getattr(e, "status_code", None) == 404:
            raise HTTPException(status_code=404, detail="GitHub user not found") from e
        raise HTTPException(status_code=502, detail=f"GitHub API error: {e}") from e

    return build_scan_result(repos)


@router.post("", response_model=ScanResponse)
def run_scan(
    body: ScanRequest,
    github_client: GitHubClient = Depends(get_github_client),
) -> ScanResponse:
    """
    Scan a GitHub profile: fetch repos, score, classify, and return
    summary, top issues, per-repo results, and recommended next step.
    Read-only; no destructive actions.
    """
    return _execute_scan(body, github_client)


@router.post("/voiceflow", response_model=VoiceflowScanResponse)
def run_scan_voiceflow(
    body: ScanRequest,
    github_client: GitHubClient = Depends(get_github_client),
) -> VoiceflowScanResponse:
    """
    Same scan as ``POST /scan``, but response uses only flat string/number fields
    for no-code tools (e.g. Voiceflow) that struggle with nested JSON.
    """
    scan = _execute_scan(body, github_client)
    return build_voiceflow_scan_response(scan)
