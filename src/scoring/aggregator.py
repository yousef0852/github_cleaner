"""Build full scan result: summary, top issues, recommended next step."""

from collections import Counter

from contracts.repo_dto import RepoDTO
from contracts.scan_response import (
    Classification,
    RepoResult,
    ScanResponse,
    Summary,
)
from .classifier import classify_repo
from .issues import detect_issues
from .remediation import build_remediation_plan
from .scorer import score_repo_with_breakdown
from .suggestions import suggest_improvements


def _top_issues_across_repos(repo_results: list[RepoResult], limit: int = 10) -> list[str]:
    """Aggregate most common issues across all repos."""
    counter: Counter[str] = Counter()
    for r in repo_results:
        for issue in r.issues:
            counter[issue] += 1
    return [issue for issue, _ in counter.most_common(limit)]


def _recommended_next_step(summary: Summary, repo_results: list[RepoResult]) -> str:
    """Single recommended next step based on scan outcome."""
    if summary.total_repos == 0:
        return "No repositories found. Check the username or scan scope."
    if summary.archive_candidates >= summary.total_repos / 2:
        return "Many repos are archive candidates. Consider archiving low-value repos to strengthen your profile."
    if summary.needs_cleanup > summary.showcase_ready:
        return "Focus on cleaning up repos: add READMEs and descriptions, then add topics and licenses."
    if summary.showcase_ready > 0:
        return "Pin your best repos on your profile and ensure their READMEs clearly explain the project."
    return "Add READMEs and descriptions to your most visible repos first."


def build_scan_result(repos: list[RepoDTO]) -> ScanResponse:
    """
    Score, classify, detect issues/suggestions for each repo;
    build summary and top issues.
    """
    results: list[RepoResult] = []
    for repo in repos:
        score, breakdown, evidence = score_repo_with_breakdown(repo)
        classification = classify_repo(score, repo)
        issues = detect_issues(repo)
        suggestions = suggest_improvements(repo, classification)
        remediation = build_remediation_plan(
            repo, issues, suggestions, classification, breakdown
        )
        results.append(
            RepoResult(
                name=repo.name,
                score=score,
                classification=classification,
                issues=issues,
                suggestions=suggestions,
                structure_report=repo.structure_report,
                score_breakdown=breakdown,
                score_evidence=evidence,
                remediation=remediation,
            )
        )

    showcase = sum(1 for r in results if r.classification == Classification.SHOWCASE)
    cleanup = sum(1 for r in results if r.classification == Classification.CLEANUP)
    archive = sum(1 for r in results if r.classification == Classification.ARCHIVE)

    summary = Summary(
        total_repos=len(results),
        showcase_ready=showcase,
        needs_cleanup=cleanup,
        archive_candidates=archive,
    )
    top_issues = _top_issues_across_repos(results)
    recommended = _recommended_next_step(summary, results)

    return ScanResponse(
        summary=summary,
        top_issues=top_issues,
        repos=results,
        recommended_next_step=recommended,
    )
