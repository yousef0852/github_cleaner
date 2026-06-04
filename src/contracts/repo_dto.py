"""Data transfer object for repository metadata (from GitHub API)."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class RepoDTO(BaseModel):
    """Raw repository data as returned by the data layer."""

    name: str
    description: Optional[str] = None
    stars: int = Field(ge=0)
    forks: int = Field(ge=0)
    last_commit_at: Optional[datetime] = None
    language: Optional[str] = None
    has_readme: bool = False
    has_license: bool = False
    is_empty: bool = False
    is_fork: bool = False
    topics: list[str] = Field(default_factory=list)
    default_branch: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    structure_report: Optional[dict[str, Any]] = Field(
        default=None,
        description="Phase 2: root-level file/folder evidence from Contents API (set during scan).",
    )
