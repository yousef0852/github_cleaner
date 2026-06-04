"""Classify repository into showcase | cleanup | archive."""

from contracts.repo_dto import RepoDTO
from contracts.scan_response import Classification

# Score thresholds
SHOWCASE_MIN_SCORE = 70.0
CLEANUP_MAX_SCORE = 69.9  # below showcase
ARCHIVE_MAX_SCORE = 30.0  # at or below this → archive


def classify_repo(score: float, repo: RepoDTO) -> Classification:
    """
    Map score and repo traits to classification.
    - showcase: strong project (score >= 70, not empty)
    - cleanup: fixable (score 31–69 or has clear improvement path)
    - archive: should be hidden or archived (score <= 30 or empty/junk)
    """
    if repo.is_empty:
        return Classification.ARCHIVE
    if score <= ARCHIVE_MAX_SCORE:
        return Classification.ARCHIVE
    if score >= SHOWCASE_MIN_SCORE:
        return Classification.SHOWCASE
    return Classification.CLEANUP
