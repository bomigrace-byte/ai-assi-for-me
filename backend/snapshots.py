from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .firebase_client import get_firestore_client
from .github_client import GitHubHistoryClient
from .models import TechnologySnapshot


class TechnologySnapshotStore:
    def __init__(self) -> None:
        self._items: dict[str, TechnologySnapshot] = {}

    def upsert(self, snapshot: TechnologySnapshot) -> TechnologySnapshot:
        self._items[snapshot.repository] = snapshot
        return snapshot

    def get(self, repository: str) -> TechnologySnapshot | None:
        return self._items.get(repository)

    def all(self) -> list[TechnologySnapshot]:
        return list(self._items.values())


class FirestoreTechnologySnapshotStore:
    def __init__(self, client: Any, collection: str = "technology_snapshots") -> None:
        self._collection = client.collection(collection)

    def upsert(self, snapshot: TechnologySnapshot) -> TechnologySnapshot:
        self._collection.document(snapshot.repository.replace("/", "__")).set(snapshot.model_dump(mode="json"))
        return snapshot

    def get(self, repository: str) -> TechnologySnapshot | None:
        document = self._collection.document(repository.replace("/", "__")).get()
        return TechnologySnapshot.model_validate(document.to_dict()) if document.exists else None

    def all(self) -> list[TechnologySnapshot]:
        return [TechnologySnapshot.model_validate(document.to_dict()) for document in self._collection.stream()]


def create_snapshot_store() -> TechnologySnapshotStore | FirestoreTechnologySnapshotStore:
    client = get_firestore_client()
    return FirestoreTechnologySnapshotStore(client) if client is not None else TechnologySnapshotStore()


@dataclass(frozen=True)
class SnapshotService:
    client: GitHubHistoryClient
    store: TechnologySnapshotStore

    def collect(self, technology: str, repository: str) -> TechnologySnapshot:
        snapshot = TechnologySnapshot(
            technology=technology,
            repository=repository,
            current_stargazer_count=self.client.fetch_current_stargazers(repository),
            collected_at=datetime.now(timezone.utc),
        )
        return self.store.upsert(snapshot)
