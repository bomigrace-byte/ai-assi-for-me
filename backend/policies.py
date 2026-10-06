from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .models import TechnologyData, utc_now


TrustedSource = Literal["github", "manual_demo"]


class DataWritePayload(BaseModel):
    """Client payload. Source metadata is deliberately ignored if supplied by a client."""

    model_config = ConfigDict(extra="ignore")

    technology: str = Field(min_length=1)
    repository: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    date: str
    week_start_epoch: int = Field(ge=0)
    value: int = Field(ge=0)
    memo: str | None = None
    api_version: str | None = None
    collected_at: datetime | None = None


def canonicalize_payload(payload: DataWritePayload, trusted_source: TrustedSource) -> TechnologyData:
    """Apply source metadata from the server-controlled route, never from request data."""

    source_type = "github_star_history" if trusted_source == "github" else "manual_entry"
    analysis_eligible = trusted_source == "github"
    collected_at = payload.collected_at or utc_now()
    return TechnologyData(
        technology=payload.technology,
        repository=payload.repository,
        date=payload.date,
        week_start_epoch=payload.week_start_epoch,
        value=payload.value,
        metric="weekly_new_stars",
        memo=payload.memo,
        source=trusted_source,
        source_type=source_type,
        analysis_eligible=analysis_eligible,
        api_version=payload.api_version,
        collected_at=collected_at,
    )
