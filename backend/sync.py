from dataclasses import dataclass
from datetime import datetime

from .catalog import TRACKED_TECHNOLOGIES
from .github_client import GitHubHistoryClient
from .ingestion import GitHubIngestionService, IngestionResult
from .snapshots import SnapshotService, TechnologySnapshotStore
from .storage import TechnologyDataStore


@dataclass(frozen=True)
class RepositorySyncResult:
    technology: str
    repository: str
    ingestion: IngestionResult
    snapshot_stargazers: int


class GitHubSyncService:
    def __init__(
        self,
        client: GitHubHistoryClient,
        data_store: TechnologyDataStore,
        snapshot_store: TechnologySnapshotStore,
    ) -> None:
        self._client = client
        self._ingestion = GitHubIngestionService(client, data_store)
        self._snapshots = SnapshotService(client, snapshot_store)

    def sync_all(self, now: datetime | None = None) -> list[RepositorySyncResult]:
        results: list[RepositorySyncResult] = []
        for technology, repository in TRACKED_TECHNOLOGIES:
            ingestion = self._ingestion.ingest_repository(technology, repository, now=now)
            snapshot = self._snapshots.collect(technology, repository)
            results.append(
                RepositorySyncResult(
                    technology=technology,
                    repository=repository,
                    ingestion=ingestion,
                    snapshot_stargazers=snapshot.current_stargazer_count,
                )
            )
        return results
