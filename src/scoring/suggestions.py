"""Generate improvement suggestions per repository (deterministic)."""

from contracts.repo_dto import RepoDTO
from contracts.scan_response import Classification


def suggest_improvements(repo: RepoDTO, classification: Classification) -> list[str]:
    """Return actionable suggestions for this repo."""
    suggestions: list[str] = []

    if repo.structure_report:
        hf = repo.structure_report.get("has_files") or {}
        hfo = repo.structure_report.get("has_folders") or {}
        if not hf.get("readme"):
            suggestions.append("Add a README with project overview and setup instructions")
        if not hf.get("license"):
            suggestions.append("Add a license file (e.g. MIT, Apache 2.0)")
        if not hf.get("gitignore"):
            suggestions.append("Add a .gitignore file to exclude sensitive files")
        if not hf.get("deps"):
            suggestions.append("Add a dependency file (e.g. requirements.txt, pyproject.toml, package.json)")
        if not hfo.get("tests"):
            suggestions.append("Add a tests/ folder at the repository root")
        if not hfo.get("docs"):
            suggestions.append("Consider a docs/ folder if the project needs user-facing documentation")
        if not hf.get("src_layout"):
            suggestions.append("Consider a src/ layout for library-style projects")

    if classification == Classification.ARCHIVE:
        suggestions.append("Consider archiving or hiding this repo from profile")
        return suggestions

    if not repo.has_readme:
        suggestions.append("Add a README with project overview and setup instructions")

    if not repo.description or len(repo.description.strip()) < 10:
        suggestions.append("Add a clear, concise repository description")

    name_lower = (repo.name or "").strip().lower()
    junk = ("test", "tmp", "temp", "foo", "bar", "demo", "sample", "my-repo", "untitled")
    if any(name_lower == j or name_lower.startswith(j + "-") for j in junk):
        suggestions.append("Rename repository to something descriptive and professional")

    if not repo.has_license:
        suggestions.append("Add a license file (e.g. MIT, Apache 2.0)")

    if not repo.topics:
        suggestions.append("Add repository topics for discoverability")

    if repo.has_readme and not repo.topics:
        suggestions.append("Add screenshots or badges to README if applicable")

    return suggestions[:5]  # Cap to avoid overwhelming
