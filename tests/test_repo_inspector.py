"""
Tests for repository content inspection (Phase 2).

Uses mocked client and fixed payloads only — no live GitHub API calls.
"""

from unittest.mock import MagicMock

from data.github_client import GitHubClient
from data.repo_inspector import (
    build_structure_report,
    get_repo_root_contents,
    inspect_repo,
)


# Fixed Contents API–style payloads (list of items with name, type)
CONTENTS_WITH_README_AND_SRC = [
    {"name": "README.md", "type": "file"},
    {"name": "LICENSE", "type": "file"},
    {"name": ".gitignore", "type": "file"},
    {"name": "pyproject.toml", "type": "file"},
    {"name": "src", "type": "dir"},
    {"name": "tests", "type": "dir"},
]

CONTENTS_EMPTY = []

CONTENTS_ONLY_DOCS = [
    {"name": "docs", "type": "dir"},
    {"name": "README.rst", "type": "file"},
]


def test_get_repo_root_contents_returns_list():
    """get_repo_root_contents returns a list when client returns directory listing."""
    mock_client = MagicMock(spec=GitHubClient)
    mock_client.get_repo_root_contents.return_value = CONTENTS_WITH_README_AND_SRC

    contents = get_repo_root_contents("owner", "repo", client=mock_client)

    assert isinstance(contents, list)
    assert len(contents) == 6
    assert all("name" in item and "type" in item for item in contents)
    mock_client.get_repo_root_contents.assert_called_once_with("owner", "repo")


def test_get_repo_root_contents_normalizes_single_file_response():
    """When API returns a single file (dict), we normalize to empty list."""
    mock_client = MagicMock(spec=GitHubClient)
    mock_client.get_repo_root_contents.return_value = {"name": "README.md", "type": "file"}

    contents = get_repo_root_contents("owner", "repo", client=mock_client)

    assert contents == []
    mock_client.get_repo_root_contents.assert_called_once_with("owner", "repo")


def test_build_structure_report_with_contents():
    """build_structure_report returns correct booleans for a rich root listing."""
    report = build_structure_report(CONTENTS_WITH_README_AND_SRC)

    assert isinstance(report, dict)
    assert report["has_files"]["readme"] is True
    assert report["has_files"]["license"] is True
    assert report["has_files"]["gitignore"] is True
    assert report["has_files"]["deps"] is True
    assert report["has_files"]["src_layout"] is True
    assert report["has_folders"]["tests"] is True
    assert report["has_folders"]["src"] is True
    assert "has_files_and_folders" in report


def test_build_structure_report_empty_list():
    """Empty contents list produces all-False structure report."""
    report = build_structure_report(CONTENTS_EMPTY)

    assert report["has_files"]["readme"] is False
    assert report["has_files"]["license"] is False
    assert report["has_files"]["gitignore"] is False
    assert report["has_files"]["deps"] is False
    assert report["has_folders"]["tests"] is False
    assert report["has_folders"]["docs"] is False
    assert report["has_folders"]["src"] is False


def test_build_structure_report_single_file_dict_normalized():
    """When contents is a dict (single-file API response), report is safe and all False."""
    report = build_structure_report({"name": "README.md", "type": "file"})

    assert isinstance(report, dict)
    assert "has_files" in report and "has_folders" in report
    assert report["has_files"]["readme"] is False
    assert report["has_folders"]["src"] is False


def test_build_structure_report_readme_rst_and_docs():
    """README.rst and docs/ folder are detected."""
    report = build_structure_report(CONTENTS_ONLY_DOCS)

    assert report["has_files"]["readme"] is True
    assert report["has_folders"]["docs"] is True
    assert report["has_files"]["license"] is False
    assert report["has_folders"]["src"] is False


def test_inspect_repo_returns_report():
    """inspect_repo calls client and returns structure report from root contents."""
    mock_client = MagicMock(spec=GitHubClient)
    mock_client.get_repo_root_contents.return_value = CONTENTS_WITH_README_AND_SRC

    report = inspect_repo("some-owner", "some-repo", client=mock_client)

    assert isinstance(report, dict)
    assert "has_files" in report
    assert "has_folders" in report
    assert "has_files_and_folders" in report
    assert report["has_files"]["readme"] is True
    assert report["has_folders"]["src"] is True
    mock_client.get_repo_root_contents.assert_called_once_with("some-owner", "some-repo")
