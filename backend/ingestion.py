from dataclasses import dataclass
from datetime import datetime

from .github_client import GitHubHistoryClient
from .storage import TechnologyDataStore


@dataclass(frozen=True)
class IngestionResult:
    fetched: int
    complete: int
    created: int
    updated: int


class GitHubIngestionService:
    def __init__(self, client: GitHubHistoryClient, store: TechnologyDataStore) -> None:
        self._client = client
        self._store = store

    def ingest_repository(
        self,
        technology: str,
        repository: str,
        now: datetime | None = None,
        max_pages: int | None = None,
    ) -> IngestionResult:
        fetched_rows = self._client.fetch_all(repository, max_pages=max_pages)
        complete_rows = self._client.filter_complete_weeks(fetched_rows, now=now)
        data_rows = self._client.to_technology_data(technology, repository, complete_rows)
        created = 0
        updated = 0
        for item in data_rows:
            result = self._store.upsert(item)
            if result.created:
                created += 1
            else:
                updated += 1
        return IngestionResult(
            fetched=len(fetched_rows),
            complete=len(complete_rows),
            created=created,
            updated=updated,
        )
