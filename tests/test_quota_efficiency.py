import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.api_data import _latest_snapshot_weeks
from backend.ingestion import GitHubIngestionService
from backend.main import app
from backend.models import TechnologyData


def weekly_row(week: int) -> TechnologyData:
    return TechnologyData(
        technology="LangGraph",
        repository="langchain-ai/langgraph",
        date=date.fromtimestamp(week),
        week_start_epoch=week,
        value=10,
        source="github",
        source_type="github_star_history",
        analysis_eligible=True,
        collected_at=datetime.now(timezone.utc),
    )


class QuotaEfficiencyTest(unittest.TestCase):
    def test_incremental_ingestion_skips_existing_weeks(self):
        client = MagicMock()
        rows = [weekly_row(1767571200 + 604800 * index) for index in range(3)]
        client.fetch_all.return_value = [object()] * 3
        client.filter_complete_weeks.return_value = [object()] * 3
        client.to_technology_data.return_value = rows
        store = MagicMock()
        store.upsert.return_value.created = True

        result = GitHubIngestionService(client, store).ingest_repository(
            "LangGraph", "langchain-ai/langgraph", after_week=rows[1].week_start_epoch,
        )
        self.assertEqual(result.created, 1)
        self.assertEqual(result.updated, 0)
        store.upsert.assert_called_once_with(rows[2])

    def test_snapshot_cursor_uses_latest_observed_week(self):
        snapshot = {"summaries": {"4w": {"LangGraph": {
            "repository": "langchain-ai/langgraph", "recent_end_week": 1768176000,
        }}}}
        self.assertEqual(_latest_snapshot_weeks(snapshot), {"langchain-ai/langgraph": 1768176000})

    def test_repeated_sync_does_not_rebuild_unchanged_analytics(self):
        snapshot = {"summaries": {"4w": {"LangGraph": {
            "repository": "langchain-ai/langgraph", "recent_end_week": 1768176000,
        }}}}
        ingestion = SimpleNamespace(fetched=3, complete=3, created=0, updated=0)
        result = SimpleNamespace(technology="LangGraph", repository="langchain-ai/langgraph", ingestion=ingestion, snapshot_stargazers=100)
        with patch.dict("os.environ", {"ADMIN_API_KEY": "test-secret"}), \
             patch("backend.api_data.GitHubHistoryClient"), \
             patch("backend.api_data.GitHubSyncService") as service, \
             patch("backend.api_data.analytics_snapshot_store") as analytics:
            analytics.get.return_value = snapshot
            service.return_value.sync_all.return_value = [result]
            response = TestClient(app).post("/api/data/sync/github", headers={"X-Admin-Key": "test-secret"})
        self.assertEqual(response.status_code, 200)
        service.return_value.sync_all.assert_called_once_with(latest_weeks={"langchain-ai/langgraph": 1768176000})
        analytics.rebuild.assert_not_called()


if __name__ == "__main__":
    unittest.main()
