from dataclasses import dataclass
from hashlib import sha256
import time
from typing import Any

from .firebase_client import get_firestore_client
from .models import TechnologyData, utc_now


class ProtectedRowError(PermissionError):
    """Raised when a GitHub-collected row is changed outside synchronization."""


@dataclass(frozen=True)
class UpsertResult:
    item: TechnologyData
    created: bool


class TechnologyDataStore:
    """In-memory store used when Firestore credentials are not configured."""

    def __init__(self) -> None:
        self._rows: dict[str, TechnologyData] = {}

    def upsert(self, item: TechnologyData) -> UpsertResult:
        key = item.dedupe_key
        previous = self._rows.get(key)
        if previous is None:
            row_id = sha256(key.encode("utf-8")).hexdigest()[:24]
            persisted = item.model_copy(update={"id": row_id, "updated_at": utc_now()})
            self._rows[key] = persisted
            return UpsertResult(item=persisted, created=True)

        persisted = item.model_copy(
            update={"id": previous.id, "created_at": previous.created_at, "updated_at": utc_now()}
        )
        self._rows[key] = persisted
        return UpsertResult(item=persisted, created=False)

    def get(self, dedupe_key: str) -> TechnologyData | None:
        return self._rows.get(dedupe_key)

    def get_by_id(self, row_id: str) -> TechnologyData | None:
        return next((row for row in self._rows.values() if row.id == row_id), None)

    def all(self) -> list[TechnologyData]:
        return list(self._rows.values())

    def count(self) -> int:
        return len(self._rows)

    def update(self, dedupe_key: str, replacement: TechnologyData) -> TechnologyData:
        current = self._rows.get(dedupe_key)
        if current is None:
            raise KeyError(dedupe_key)
        if current.source == "github":
            raise ProtectedRowError("GitHub rows can only be changed by synchronization")
        if replacement.dedupe_key != dedupe_key:
            raise ValueError("replacement must keep the same dedupe key")
        persisted = replacement.model_copy(
            update={"id": current.id, "created_at": current.created_at, "updated_at": utc_now()}
        )
        self._rows[dedupe_key] = persisted
        return persisted

    def delete(self, dedupe_key: str) -> None:
        current = self._rows.get(dedupe_key)
        if current is None:
            raise KeyError(dedupe_key)
        if current.source == "github":
            raise ProtectedRowError("GitHub rows cannot be deleted by the general delete path")
        del self._rows[dedupe_key]


class FirestoreTechnologyDataStore:
    """Firestore-backed implementation with the same policy boundary as the memory store."""

    def __init__(self, client: Any, collection: str = "technology_data", cache_ttl_seconds: int = 30) -> None:
        self._collection = client.collection(collection)
        self._cache_ttl_seconds = cache_ttl_seconds
        self._all_cache: list[TechnologyData] | None = None
        self._all_cache_at = 0.0

    def _invalidate_cache(self) -> None:
        self._all_cache = None
        self._all_cache_at = 0.0

    def upsert(self, item: TechnologyData) -> UpsertResult:
        key = item.dedupe_key
        document = self._collection.document(sha256(key.encode("utf-8")).hexdigest()[:24])
        previous = document.get()
        previous_item = TechnologyData.model_validate(previous.to_dict()) if previous.exists else None
        persisted = item.model_copy(
            update={
                "id": document.id,
                "created_at": previous_item.created_at if previous_item else item.created_at,
                "updated_at": utc_now(),
            }
        )
        document.set(persisted.model_dump(mode="json"))
        self._invalidate_cache()
        return UpsertResult(item=persisted, created=not previous.exists)

    def get(self, dedupe_key: str) -> TechnologyData | None:
        document = self._collection.document(sha256(dedupe_key.encode("utf-8")).hexdigest()[:24]).get()
        return TechnologyData.model_validate(document.to_dict()) if document.exists else None

    def get_by_id(self, row_id: str) -> TechnologyData | None:
        document = self._collection.document(row_id).get()
        return TechnologyData.model_validate(document.to_dict()) if document.exists else None

    def all(self) -> list[TechnologyData]:
        now = time.monotonic()
        if self._all_cache is not None and now - self._all_cache_at < self._cache_ttl_seconds:
            return list(self._all_cache)
        rows = [TechnologyData.model_validate(document.to_dict()) for document in self._collection.stream()]
        self._all_cache = rows
        self._all_cache_at = now
        return list(rows)

    def count(self) -> int:
        return len(self.all())

    def update(self, dedupe_key: str, replacement: TechnologyData) -> TechnologyData:
        current = self.get(dedupe_key)
        if current is None:
            raise KeyError(dedupe_key)
        if current.source == "github":
            raise ProtectedRowError("GitHub rows can only be changed by synchronization")
        if replacement.dedupe_key != dedupe_key:
            raise ValueError("replacement must keep the same dedupe key")
        persisted = replacement.model_copy(update={"id": current.id, "created_at": current.created_at, "updated_at": utc_now()})
        self._collection.document(current.id).set(persisted.model_dump(mode="json"))
        self._invalidate_cache()
        return persisted

    def delete(self, dedupe_key: str) -> None:
        current = self.get(dedupe_key)
        if current is None:
            raise KeyError(dedupe_key)
        if current.source == "github":
            raise ProtectedRowError("GitHub rows cannot be deleted by the general delete path")
        self._collection.document(current.id).delete()
        self._invalidate_cache()


def create_technology_data_store(collection: str = "technology_data") -> TechnologyDataStore | FirestoreTechnologyDataStore:
    client = get_firestore_client()
    return FirestoreTechnologyDataStore(client, collection) if client is not None else TechnologyDataStore()
