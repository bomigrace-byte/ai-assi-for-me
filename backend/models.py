from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Metric = Literal["weekly_new_stars"]
Source = Literal["github", "manual_demo"]
SourceType = Literal["github_star_history", "manual_entry"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TechnologyData(BaseModel):
    """Canonical persistence model for one weekly analysis observation."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    technology: str = Field(min_length=1)
    repository: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    date: date
    week_start_epoch: int = Field(ge=0)
    value: int = Field(ge=0)
    metric: Metric = "weekly_new_stars"
    memo: str | None = None
    source: Source
    source_type: SourceType
    analysis_eligible: bool
    api_version: str | None = None
    collected_at: datetime
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_source_policy(self) -> "TechnologyData":
        expected = {
            "github": ("github_star_history", True),
            "manual_demo": ("manual_entry", False),
        }[self.source]
        if (self.source_type, self.analysis_eligible) != expected:
            raise ValueError("source, source_type, and analysis_eligible must follow server policy")
        return self

    @property
    def dedupe_key(self) -> str:
        return f"{self.repository}:{self.week_start_epoch}:{self.metric}"


class TechnologySnapshot(BaseModel):
    """Current cumulative stars, intentionally separate from weekly analysis rows."""

    model_config = ConfigDict(extra="forbid")

    technology: str = Field(min_length=1)
    repository: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    current_stargazer_count: int = Field(ge=0)
    collected_at: datetime


def example_github_row() -> TechnologyData:
    """Small deterministic fixture for model-level terminal verification."""
    now = utc_now()
    return TechnologyData(
        technology="LangGraph",
        repository="langchain-ai/langgraph",
        date=date(2026, 1, 4),
        week_start_epoch=1767484800,
        value=181,
        metric="weekly_new_stars",
        source="github",
        source_type="github_star_history",
        analysis_eligible=True,
        api_version="2026-03-10",
        collected_at=now,
        created_at=now,
        updated_at=now,
    )
