"""Materialized public analytics; one Firestore document replaces a full collection scan."""

import logging
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from typing import Any

from .analytics import PERIOD_WEEKS, analyze_technology, rank_technologies
from .firebase_client import get_firestore_client
from .models import TechnologyData

logger = logging.getLogger(__name__)

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
    def __init__(self, client: Any | None = None, cache_ttl_seconds: int = 600) -> None:
        self._document = client.collection("analytics_snapshots").document("current") if client else None
        self._build_lock = Lock()
        self._cache_ttl_seconds = cache_ttl_seconds
        self._cached: dict[str, Any] | None = None
        self._cached_at = 0.0
        self._missing_at = 0.0

    @property
    def persistent(self) -> bool:
        return self._document is not None

    def get(self) -> dict[str, Any] | None:
        if self._document is None:
            return None
        with self._build_lock:
            if self._cached is not None and monotonic() - self._cached_at < self._cache_ttl_seconds:
                return self._cached
            if self._missing_at and monotonic() - self._missing_at < 60:
                return None
            logger.info("firestore_read collection=analytics_snapshots estimated_documents=1")
            document = self._document.get()
            value = document.to_dict() if document.exists else None
            if value and value.get("version") == 1:
                self._cached = value
                self._cached_at = monotonic()
                self._missing_at = 0.0
                return value
            self._missing_at = monotonic()
            return None

    def save(self, snapshot: dict[str, Any]) -> None:
        if self._document is not None:
            self._document.set(snapshot)
            with self._build_lock:
                self._cached = snapshot
                self._cached_at = monotonic()
                self._missing_at = 0.0

    def get_or_build(self, data_store: Any) -> dict[str, Any]:
        # In-memory development mode tracks current rows without a Firestore snapshot.
        if not self.persistent:
            return build_snapshot(data_store.all())
        snapshot = self.get()
        if snapshot is None:
            raise AnalyticsSnapshotUnavailable("분석 결과가 아직 준비되지 않았습니다. 관리자 동기화가 필요합니다.")
        return snapshot

    def rebuild(self, data_store: Any) -> None:
        self.save(build_snapshot(data_store.all()))


class AnalyticsSnapshotUnavailable(RuntimeError):
    """A public request must never trigger a full Firestore collection scan."""


analytics_snapshot_store = AnalyticsSnapshotStore(get_firestore_client())
