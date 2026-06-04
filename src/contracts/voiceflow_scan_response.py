"""Flat scan payload for no-code agents (Voiceflow, etc.) — no nested objects or arrays."""

from __future__ import annotations

from pydantic import BaseModel, Field

from contracts.scan_response import Classification, ScanResponse


class VoiceflowScanResponse(BaseModel):
    """
    Scalar-only response: map each Voiceflow variable to a single field.
    Unused slots are empty strings (or 0 for counts).
    """

    total_repos: int = Field(0, ge=0)
    showcase_ready: int = Field(0, ge=0)
    needs_cleanup: int = Field(0, ge=0)
    archive_candidates: int = Field(0, ge=0)

    top_issue_1: str = ""
    top_issue_2: str = ""
    top_issue_3: str = ""

    recommended_next_step: str = ""

    archive_repo_1: str = ""
    archive_repo_2: str = ""

    cleanup_repo_1: str = ""
    cleanup_repo_2: str = ""

    showcase_repo_1: str = ""
    showcase_repo_2: str = ""


def _fill_slots(values: list[str], count: int) -> list[str]:
    out = list(values[:count])
    while len(out) < count:
        out.append("")
    return out


def build_voiceflow_scan_response(scan: ScanResponse) -> VoiceflowScanResponse:
    """Project a full ScanResponse into fixed Voiceflow-friendly keys."""
    s = scan.summary
    tops = _fill_slots(scan.top_issues, 3)

    archive_repos = [r for r in scan.repos if r.classification == Classification.ARCHIVE]
    archive_repos.sort(key=lambda r: r.score)
    archive_names = [r.name for r in archive_repos]

    cleanup_repos = [r for r in scan.repos if r.classification == Classification.CLEANUP]
    cleanup_repos.sort(key=lambda r: r.score)
    cleanup_names = [r.name for r in cleanup_repos]

    showcase_repos = [r for r in scan.repos if r.classification == Classification.SHOWCASE]
    showcase_repos.sort(key=lambda r: r.score, reverse=True)
    showcase_names = [r.name for r in showcase_repos]

    arch = _fill_slots(archive_names, 2)
    clean = _fill_slots(cleanup_names, 2)
    show = _fill_slots(showcase_names, 2)

    return VoiceflowScanResponse(
        total_repos=s.total_repos,
        showcase_ready=s.showcase_ready,
        needs_cleanup=s.needs_cleanup,
        archive_candidates=s.archive_candidates,
        top_issue_1=tops[0],
        top_issue_2=tops[1],
        top_issue_3=tops[2],
        recommended_next_step=scan.recommended_next_step or "",
        archive_repo_1=arch[0],
        archive_repo_2=arch[1],
        cleanup_repo_1=clean[0],
        cleanup_repo_2=clean[1],
        showcase_repo_1=show[0],
        showcase_repo_2=show[1],
    )
