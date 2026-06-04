"""Detect issues per repository (deterministic)."""

from datetime import datetime, timezone
from contracts.repo_dto import RepoDTO

INACTIVE_MONTHS = 12
MIN_DESCRIPTION_LEN = 10

JUNK_NAMES = (
    "test", "tmp", "temp", "foo", "bar", "asdf", "qwerty",
    "demo", "sample", "playground", "scratch", "my-repo",
    "myrepo", "project1", "project2", "untitled",
)


def detect_issues(repo: RepoDTO) -> list[str]:
    """Return list of human-readable issues for this repo."""
    issues: list[str] = []

    # structure_report is already the dict from inspect_repo (has_files / has_folders / …).
    # Do NOT pass it through build_structure_report — that expects raw API contents (list).
    if repo.structure_report:
        hf = repo.structure_report.get("has_files") or {}
        hfo = repo.structure_report.get("has_folders") or {}
        if not hf.get("readme"):
            issues.append("Missing README (root listing)")
        if not hf.get("license"):
            issues.append("Missing license (root listing)")
        if not hf.get("gitignore"):
            issues.append("Missing .gitignore (root listing)")
        if not hf.get("deps"):
            issues.append("Missing dependency file at repo root")
        if not hfo.get("tests"):
            issues.append("Missing tests folder at repo root")
        if not hfo.get("docs"):
            issues.append("No docs/ folder at repo root (optional for many projects)")
        if not hf.get("src_layout"):
            issues.append("No src/ layout at repo root (optional unless publishing a library)")

    if repo.is_empty:
        issues.append("Repository is empty")
        return issues

    if not repo.has_readme:
        issues.append("Missing README")

    if not repo.description or len(repo.description.strip()) < MIN_DESCRIPTION_LEN:
        issues.append("No or very short description")

    if repo.last_commit_at:
        now = datetime.now(timezone.utc)
        months = (now - repo.last_commit_at).days / 30
        if months > INACTIVE_MONTHS:
            issues.append(f"Inactive for over {INACTIVE_MONTHS} months")

    name_lower = (repo.name or "").strip().lower()
    if any(
        name_lower == j or name_lower.startswith(j + "-") or name_lower.endswith("-" + j)
        for j in JUNK_NAMES
    ):
        issues.append("Poor or placeholder repo name")

    if not repo.has_license:
        issues.append("No license specified")

    if repo.is_fork and repo.stars == 0 and repo.forks == 0:
        issues.append("Fork with no visible engagement")

    if not repo.topics and repo.description:
        issues.append("No topics/tags for discoverability")

    return issues
