from datetime import date, datetime, timezone
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .models import TechnologyData


GITHUB_API_VERSION = "2026-03-10"


class GitHubAPIError(RuntimeError):
    def __init__(self, status_code: int, message: str, retry_after: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class StarHistoryRow(BaseModel):
    week: int = Field(ge=0)
    total: int = Field(ge=0)
    days: list[int] = Field(min_length=7, max_length=7)


class GitHubHistoryClient:
    def __init__(
        self,
        token: str | None = None,
        client: httpx.Client | None = None,
        per_page: int = 30,
    ) -> None:
        self._client = client or httpx.Client(timeout=30.0)
        self._owns_client = client is None
        self._token = token
        self._per_page = per_page

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def fetch_page(self, repository: str, page: int = 1) -> list[StarHistoryRow]:
        response = self._client.get(
            f"https://api.github.com/repos/{repository}/stargazers/history",
            params={"per_page": self._per_page, "page": page},
            headers=self._headers(),
        )
        self._raise_for_status(response)
        payload: Any = response.json()
        if not isinstance(payload, list):
            raise GitHubAPIError(502, "GitHub history response must be a JSON array")
        return [StarHistoryRow.model_validate(row) for row in payload]

    def fetch_current_stargazers(self, repository: str) -> int:
        response = self._client.get(
            f"https://api.github.com/repos/{repository}",
            headers=self._headers(),
        )
        self._raise_for_status(response)
        payload: Any = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("stargazers_count"), int):
            raise GitHubAPIError(502, "GitHub repository response has no valid stargazers_count")
        return payload["stargazers_count"]

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "AI-Tech-Trend-Radar",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        return headers

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise GitHubAPIError(
                response.status_code,
                f"GitHub history request failed: {response.status_code}",
                response.headers.get("Retry-After"),
            )

    def fetch_all(self, repository: str, max_pages: int | None = None) -> list[StarHistoryRow]:
        rows: list[StarHistoryRow] = []
        page = 1
        while True:
            page_rows = self.fetch_page(repository, page)
            if not page_rows:
                return rows
            rows.extend(page_rows)
            if len(page_rows) < self._per_page or (max_pages is not None and page >= max_pages):
                return rows
            page += 1

    def to_technology_data(
        self,
        technology: str,
        repository: str,
        rows: list[StarHistoryRow],
        collected_at: datetime | None = None,
    ) -> list[TechnologyData]:
        collected = collected_at or datetime.now(timezone.utc)
        return [
            TechnologyData(
                technology=technology,
                repository=repository,
                date=datetime.fromtimestamp(row.week, tz=timezone.utc).date(),
                week_start_epoch=row.week,
                value=row.total,
                metric="weekly_new_stars",
                source="github",
                source_type="github_star_history",
                analysis_eligible=True,
                api_version=GITHUB_API_VERSION,
                collected_at=collected,
            )
            for row in rows
        ]

    @staticmethod
    def filter_complete_weeks(
        rows: list[StarHistoryRow],
        now: datetime | None = None,
    ) -> list[StarHistoryRow]:
        """Keep only API buckets whose seven-day interval has fully elapsed."""
        current = now or datetime.now(timezone.utc)
        cutoff = int(current.timestamp()) - (7 * 24 * 60 * 60)
        return [row for row in rows if row.week <= cutoff]
