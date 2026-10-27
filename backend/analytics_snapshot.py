"""Materialized public analytics; one Firestore document replaces a full collection scan."""

from datetime import datetime, timezone
from threading import Lock
from typing import Any

from .analytics import PERIOD_WEEKS, analyze_technology, rank_technologies
from .firebase_client import get_firestore_client
from .models import TechnologyData


def build_snapshot(rows: list[TechnologyData]) -> dict[str, Any]:
    by_technology: dict[str, list[TechnologyData]] = {}
    for row in rows:
        if row.source == "github":
            by_technology.setdefault(row.technology, []).append(row)
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summaries": {
            period: {
                technology: analyze_technology(items, period).as_dict()
                for technology, items in by_technology.items()
            }
            for period in PERIOD_WEEKS
        },
        "rankings": {
            period: [item.as_dict() for item in rank_technologies(rows, period, limit=10)]
            for period in PERIOD_WEEKS
        },
    }


class AnalyticsSnapshotStore:
    def __init__(self, client: Any | None = None) -> None:
        self._document = client.collection("analytics_snapshots").document("current") if client else None
        self._build_lock = Lock()

    @property
    def persistent(self) -> bool:
        return self._document is not None

    def get(self) -> dict[str, Any] | None:
        if self._document is None:
            return None
        document = self._document.get()
        value = document.to_dict() if document.exists else None
        return value if value and value.get("version") == 1 else None

    def save(self, snapshot: dict[str, Any]) -> None:
        if self._document is not None:
            self._document.set(snapshot)

    def get_or_build(self, data_store: Any) -> dict[str, Any]:
        # In-memory development mode tracks current rows without a Firestore snapshot.
        if not self.persistent:
            return build_snapshot(data_store.all())
        with self._build_lock:
            snapshot = self.get()
            if snapshot is not None:
                return snapshot
            snapshot = build_snapshot(data_store.all())
            self.save(snapshot)
            return snapshot

    def rebuild(self, data_store: Any) -> None:
        self.save(build_snapshot(data_store.all()))


analytics_snapshot_store = AnalyticsSnapshotStore(get_firestore_client())
