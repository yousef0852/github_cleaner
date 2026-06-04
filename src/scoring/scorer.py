"""Deterministic scoring (0–100) for a repository based on RepoDTO."""

from datetime import datetime, timezone

from contracts.repo_dto import RepoDTO
from contracts.scan_response import ScoreBreakdown

# Weights for composite score (sum = 1.0)
WEIGHT_DOCUMENTATION = 0.25
WEIGHT_ACTIVITY = 0.25
WEIGHT_STRUCTURE = 0.20
WEIGHT_NAMING = 0.15
WEIGHT_PORTFOLIO_VALUE = 0.15

# Activity: months since last commit
ACTIVITY_STALE_MONTHS = 12
ACTIVITY_OLD_MONTHS = 6
ACTIVITY_RECENT_DAYS = 90

# Root structure penalties (applied only when structure_report is present).
STRUCTURE_PENALTY_README = 5.0
STRUCTURE_PENALTY_LICENSE = 5.0
STRUCTURE_PENALTY_GITIGNORE = 4.0
STRUCTURE_PENALTY_DEPS = 5.0
STRUCTURE_PENALTY_TESTS = 4.0
STRUCTURE_PENALTY_DOCS = 2.0
STRUCTURE_PENALTY_SRC_LAYOUT = 2.0
STRUCTURE_PENALTY_MAX_TOTAL = 25.0


def _score_documentation(repo: RepoDTO) -> float:
    """0–100: README, description, license."""
    score = 0.0
    if repo.has_readme:
        score += 40.0
    if repo.description and len(repo.description.strip()) >= 10:
        score += 35.0
    elif repo.description:
        score += 15.0
    if repo.has_license:
        score += 25.0
    return min(100.0, score)


def _score_activity(repo: RepoDTO) -> float:
    """0–100: Recency of last commit."""
    if repo.is_empty or repo.last_commit_at is None:
        return 0.0
    now = datetime.now(timezone.utc)
    delta = now - repo.last_commit_at
    days = delta.days
    if days <= ACTIVITY_RECENT_DAYS:
        return 100.0
    if days <= ACTIVITY_OLD_MONTHS * 30:
        return 70.0
    if days <= ACTIVITY_STALE_MONTHS * 30:
        return 40.0
    return 10.0


def _score_structure(repo: RepoDTO) -> float:
    """0–100: Non-empty, default branch, topics."""
    if repo.is_empty:
        return 0.0
    score = 50.0
    if repo.default_branch:
        score += 30.0
    if repo.topics:
        score += min(20.0, len(repo.topics) * 5.0)
    return min(100.0, score)


def _score_naming(repo: RepoDTO) -> float:
    """0–100: Clean repo name (no random/test patterns)."""
    name = (repo.name or "").strip().lower()
    if not name:
        return 0.0
    junk = (
        "test", "tmp", "temp", "foo", "bar", "asdf",
        "qwerty", "demo", "sample", "playground", "scratch",
        "my-repo", "myrepo", "project1", "project2", "untitled",
    )
    if any(name == j or name.startswith(j + "-") or name.endswith("-" + j) for j in junk):
        return 30.0
    if len(name) <= 2 or len(name) > 50:
        return 50.0
    if "-" in name or "_" in name or name.isalnum():
        return 100.0
    return 80.0


def _score_portfolio_value(repo: RepoDTO) -> float:
    """0–100: Looks like a real project (stars, forks, not a fork, has content)."""
    if repo.is_empty:
        return 0.0
    score = 50.0
    if repo.is_fork:
        score -= 20.0
    if repo.stars > 0:
        score += min(25.0, repo.stars * 5.0)
    if repo.forks > 0:
        score += min(15.0, repo.forks * 3.0)
    if repo.language:
        score += 10.0
    return max(0.0, min(100.0, score))


def _structure_penalty_applied(repo: RepoDTO) -> float:
    """Points subtracted from weighted total (capped). 0 if no structure_report."""
    if not repo.structure_report:
        return 0.0
    hf = repo.structure_report.get("has_files") or {}
    hfo = repo.structure_report.get("has_folders") or {}
    raw = 0.0
    if not hf.get("readme"):
        raw += STRUCTURE_PENALTY_README
    if not hf.get("license"):
        raw += STRUCTURE_PENALTY_LICENSE
    if not hf.get("gitignore"):
        raw += STRUCTURE_PENALTY_GITIGNORE
    if not hf.get("deps"):
        raw += STRUCTURE_PENALTY_DEPS
    if not hfo.get("tests"):
        raw += STRUCTURE_PENALTY_TESTS
    if not hfo.get("docs"):
        raw += STRUCTURE_PENALTY_DOCS
    if not hf.get("src_layout"):
        raw += STRUCTURE_PENALTY_SRC_LAYOUT
    return min(raw, STRUCTURE_PENALTY_MAX_TOTAL)


def build_score_evidence(repo: RepoDTO, breakdown: ScoreBreakdown) -> list[str]:
    """Short deterministic lines explaining drivers of the overall score."""
    evidence: list[str] = []

    if breakdown.documentation < 50:
        evidence.append(
            "Documentation: strengthen README, description, or license (metadata + root listing)."
        )
    elif breakdown.documentation >= 85:
        evidence.append("Documentation: README, description, and license look solid.")

    if breakdown.activity < 40:
        if repo.last_commit_at is None and not repo.is_empty:
            evidence.append("Activity: no commit date available or repository appears inactive.")
        else:
            evidence.append(
                "Activity: last commit is old or missing; portfolio may look stale."
            )
    elif breakdown.activity >= 80:
        evidence.append("Activity: recent commits.")

    if breakdown.structure < 50:
        evidence.append(
            "Structure: default branch, topics, or metadata signals could be stronger."
        )

    if breakdown.naming < 70:
        evidence.append(
            "Naming: repo name looks generic, like a placeholder, or awkward length."
        )

    if breakdown.portfolio < 50:
        evidence.append(
            "Portfolio value: fork with low engagement, or missing language/social proof."
        )

    if breakdown.structure_penalty_applied > 0:
        evidence.append(
            f"Root structure checklist: overall score reduced by "
            f"{breakdown.structure_penalty_applied:.0f} point(s) (capped; see issues / structure_report)."
        )

    return evidence[:8]


def score_repo_with_breakdown(repo: RepoDTO) -> tuple[float, ScoreBreakdown, list[str]]:
    """
    Weighted composite score, dimension breakdown, and evidence lines.
    Final score matches historical score_repo behavior (single implementation).
    """
    doc = _score_documentation(repo)
    act = _score_activity(repo)
    struct = _score_structure(repo)
    name = _score_naming(repo)
    port = _score_portfolio_value(repo)

    weighted_total = (
        WEIGHT_DOCUMENTATION * doc
        + WEIGHT_ACTIVITY * act
        + WEIGHT_STRUCTURE * struct
        + WEIGHT_NAMING * name
        + WEIGHT_PORTFOLIO_VALUE * port
    )
    weighted_total = round(weighted_total, 1)

    penalty = _structure_penalty_applied(repo)
    final = max(0.0, min(100.0, weighted_total - penalty))

    breakdown = ScoreBreakdown(
        documentation=round(doc, 1),
        activity=round(act, 1),
        structure=round(struct, 1),
        naming=round(name, 1),
        portfolio=round(port, 1),
        structure_penalty_applied=round(penalty, 1),
    )
    evidence = build_score_evidence(repo, breakdown)
    return final, breakdown, evidence


def score_repo(repo: RepoDTO) -> float:
    """
    Compute overall score 0–100 for a repository.
    Delegates to score_repo_with_breakdown (single source of truth).
    """
    final, _, _ = score_repo_with_breakdown(repo)
    return final
