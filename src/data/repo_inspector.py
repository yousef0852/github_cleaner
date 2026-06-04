"""
Repository content inspection (Phase 2).

Inspect repo structure and key files via GitHub API or clone — no scoring here,
only evidence (file inventory, layout) for use by the scoring layer later.
"""

"""
Decision: Use the GitHub Contents API as the default method for Phase 2 repository inspection.

Rationale: our current goal is lightweight, read-only structure analysis for scoring and agent responses, not full local repository analysis. The Contents API is simpler, safer, faster to integrate with the existing data layer, and avoids the operational complexity of local cloning.

Future plan: add optional shallow clone only for advanced checks that require deeper file-level inspection, such as secret scanning, richer documentation analysis, or nested structure evaluation.
"""
from data.github_client import GitHubClient
from typing import Any

# task 1: Decide how to get repo contents (Contents API vs shallow clone).
#         Document the choice in this docstring or a short comment above.

# task 2: Add a function that, given owner + repo (+ client or clone path),
#         returns the list of files and folders at the repo root (e.g. names + type).
#         If API: use GET /repos/{owner}/{repo}/contents/ for root.
#         If clone: list the top-level directory.
def get_repo_root_contents(owner: str, repo: str, client: GitHubClient | None = None) -> list[dict[str, Any]]:
    """
    Get the root contents of a repository (list of items with name, type).
    If the API returns a single file (dict), normalizes to empty list so callers stay safe.
    """
    client = client or GitHubClient()
    raw = client.get_repo_root_contents(owner, repo)
    return raw if isinstance(raw, list) else []
# task 3: Define the file inventory to detect (constants or small config):
#         README (README.md, README.rst, …), LICENSE, .gitignore,
#         requirements.txt / pyproject.toml / package.json, tests/, docs/, src/.

def _ensure_contents_list(contents: list[dict[str, Any]] | dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize API response: directory = list, single file = dict. Always return a list for safe iteration."""
    if isinstance(contents, list):
        return contents
    return []


def has_file(contents: list[dict[str, Any]], filename: str) -> bool:
    """
    Check if a file exists in the repository.
    """
    contents = _ensure_contents_list(contents)
    return any(item.get("name") == filename for item in contents)

def has_folder(contents: list[dict[str, Any]], foldername: str) -> bool:
    """
    Check if a folder exists in the repository.
    """
    contents = _ensure_contents_list(contents)
    return any(item.get("name") == foldername and item.get("type") == "dir" for item in contents)

def has_readme(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a README file exists in the repository.
    """
    return has_file(contents, 'README.md') or has_file(contents, 'README.rst')

def has_license(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a LICENSE file exists in the repository.
    """
    return has_file(contents, 'LICENSE') or has_file(contents, 'LICENSE.md')

def has_gitignore(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a .gitignore file exists in the repository.
    """
    return has_file(contents, '.gitignore')

def has_deps(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a requirements.txt or pyproject.toml or package.json file exists in the repository.
    """
    return has_file(contents, 'requirements.txt') or has_file(contents, 'pyproject.toml') or has_file(contents, 'package.json')

def has_tests(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a tests/ folder exists in the repository.
    """
    return has_folder(contents, 'tests')

def has_docs(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a docs/ folder exists in the repository.
    """
    return has_folder(contents, 'docs')

def has_src_layout(contents: list[dict[str, Any]]) -> bool:
    """
    Check if a src/ folder exists in the repository.
    """
    return has_folder(contents, 'src')

# task 4: Implement "has file / has folder" checks using the root list
#         (and one level deeper if needed): has_readme, has_license, has_gitignore,
#         has_deps, has_tests, has_docs, has_src_layout.

def build_structure_report(contents: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    """
    Build a structure report for a repository.
    contents: list from Contents API (directory), or dict (single file) — normalized to list internally.
    """
    contents = _ensure_contents_list(contents)
    return {
        'has_files': {
            'readme': has_readme(contents),
            'license': has_license(contents),
            'gitignore': has_gitignore(contents),
            'deps': has_deps(contents),
            'tests': has_tests(contents),
            'docs': has_docs(contents),
            'src_layout': has_src_layout(contents),
        },
        'has_folders': {
            'tests': has_folder(contents, 'tests'),
            'docs': has_folder(contents, 'docs'),
            'src': has_folder(contents, 'src'),
        },
        'has_files_and_folders': {
            'readme': has_file(contents, 'README.md'),
            'license': has_file(contents, 'LICENSE'),
            'gitignore': has_file(contents, '.gitignore'),
            'deps': has_file(contents, 'requirements.txt') or has_file(contents, 'pyproject.toml') or has_file(contents, 'package.json'),
            'tests': has_folder(contents, 'tests'),
            'docs': has_folder(contents, 'docs'),
            'src': has_folder(contents, 'src'),
        },
    }

# task 5: Build a structure report (dict or dataclass) per repo with all
#         booleans and any extra info (e.g. which README file was found).
#         This is the evidence object for scoring later.
def inspect_repo(owner: str, repo: str, client: GitHubClient | None = None) -> dict[str, Any]:
    """
    Inspect a repository and return a structure report.
    """
    return build_structure_report(get_repo_root_contents(owner, repo, client))
