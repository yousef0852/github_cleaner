"""Input contract for the scan endpoint."""

from enum import Enum

from pydantic import BaseModel, Field


class ReviewMode(str, Enum):
    PORTFOLIO = "portfolio"
    CLEANUP = "cleanup"


class ScanScope(str, Enum):
    PUBLIC = "public"
    ALL = "all"


class ScanRequest(BaseModel):
    """Request body for GitHub profile scan."""

    github_username: str = Field(..., min_length=1, max_length=39)
    review_mode: ReviewMode = Field(default=ReviewMode.PORTFOLIO)
    scan_scope: ScanScope = Field(default=ScanScope.PUBLIC)
