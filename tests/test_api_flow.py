import os
import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from google.api_core.exceptions import ResourceExhausted

from backend import chat_api, conversation_api
from backend.ai_tools import dispatch_tool
from backend.analytics_snapshot import build_snapshot
from backend.api_data import github_data_store
from backend.api_data import demo_store
from backend.conversations import ConversationStore
from backend.main import app
from backend.models import TechnologyData


def github_rows():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        TechnologyData(
            technology="LangGraph",
            repository="langchain-ai/langgraph",
            date=date(2026, 1, 1) + timedelta(days=7 * index),
            week_start_epoch=1767225600 + 604800 * index,
            value=100 if index < 4 else 110,
            source="github",
            source_type="github_star_history",
            analysis_eligible=True,
            collected_at=now,
        )
        for index in range(8)
    ]


class ApiFlowTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.conversations = ConversationStore()
        self.patches = [
            patch.object(github_data_store, "all", return_value=github_rows()),
            patch.object(demo_store, "_rows", {}) if hasattr(demo_store, "_rows") else patch.object(demo_store, "all", return_value=[]),
            patch.object(chat_api, "conversation_store", self.conversations),
            patch.object(conversation_api, "conversation_store", self.conversations),
            patch.dict(os.environ, {"OPENAI_API_KEY": "", "ADMIN_API_KEY": "test-secret"}),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        chat_api.request_history.clear()

    def test_summary_route_and_validation(self):
        response = self.client.get("/api/data/summary", params={"technology": "LangGraph", "period": "4w"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accelerating")
        self.assertEqual(response.json()["momentum_change_percent"], 10.0)
        self.assertEqual(self.client.get("/api/data/summary", params={"technology": "LangGraph", "period": "30d"}).status_code, 422)

    def test_materialized_snapshot_serves_ranking_summary_compare_and_chat(self):
        snapshot = build_snapshot(github_rows())
        with patch("backend.analytics_snapshot.analytics_snapshot_store.get_or_build", return_value=snapshot), patch.object(github_data_store, "all", side_effect=AssertionError("raw scan")):
            ranking = self.client.get("/api/data/ranking", params={"period": "4w"})
            summary = self.client.get("/api/data/summary", params={"technology": "LangGraph", "period": "4w"})
            comparison = self.client.get("/api/data/compare", params={"technologies": "LangGraph,LangGraph", "period": "4w"})
            chat = self.client.post("/api/chat", headers={"X-Session-Token": "snapshot-chat"}, json={"message": "LangGraph 4주 성장세"})
        self.assertEqual(ranking.status_code, 200)
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(comparison.status_code, 200)
        self.assertEqual(chat.status_code, 200)
        self.assertEqual(chat.json()["tool_result"]["momentum_change_percent"], summary.json()["momentum_change_percent"])

    def test_chat_followup_saved_and_session_isolated(self):
        headers = {"X-Session-Token": "session-a"}
        with patch.object(chat_api, "dispatch_tool", wraps=dispatch_tool) as tool:
            first = self.client.post("/api/chat", headers=headers, json={"message": "LangGraph 4주 성장세 알려줘"})
            self.assertEqual(first.status_code, 200)
            self.assertEqual(tool.call_count, 1)
            conversation_id = first.json()["conversation_id"]
            second = self.client.post("/api/chat", headers=headers, json={"message": "그럼 4주는?", "conversation_id": conversation_id})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["tool_result"]["technology"], "LangGraph")
        self.assertEqual(second.json()["tool_result"]["period"], "4w")
        self.assertEqual(len(self.client.get(f"/api/conversations/{conversation_id}", headers=headers).json()["messages"]), 4)
        self.assertEqual(len(self.client.get("/api/conversations", headers=headers).json()), 1)
        self.assertEqual(self.client.get(f"/api/conversations/{conversation_id}", headers={"X-Session-Token": "session-b"}).status_code, 404)
        self.assertEqual(self.client.post("/api/chat", json={"message": "LangGraph"}).status_code, 401)
        self.assertEqual(self.client.post("/api/chat", headers=headers, json={"message": ""}).status_code, 422)

    def test_failed_chat_does_not_create_empty_conversation_or_change_history(self):
        headers = {"X-Session-Token": "failed-chat"}
        with patch.object(chat_api, "_openai_answer", side_effect=HTTPException(status_code=502, detail="upstream failed")):
            failed = self.client.post("/api/chat", headers=headers, json={"message": "LangGraph 성장세"})
        self.assertEqual(failed.status_code, 502)
        self.assertEqual(self.client.get("/api/conversations", headers=headers).json(), [])

        successful = self.client.post("/api/chat", headers=headers, json={"message": "LangGraph 4주 성장세"})
        conversation_id = successful.json()["conversation_id"]
        with patch.object(chat_api, "_openai_answer", side_effect=HTTPException(status_code=502, detail="upstream failed")):
            failed_followup = self.client.post("/api/chat", headers=headers, json={"message": "그럼 13주는?", "conversation_id": conversation_id})
        self.assertEqual(failed_followup.status_code, 502)
        conversation = self.client.get(f"/api/conversations/{conversation_id}", headers=headers).json()
        self.assertEqual(len(conversation["messages"]), 2)

    def test_data_write_needs_admin_key(self):
        payload = {"technology": "Example", "repository": "example/repo", "date": "2026-01-01", "week_start_epoch": 1767225600, "value": 1}
        self.assertEqual(self.client.post("/api/data", json=payload).status_code, 401)
        if hasattr(demo_store, "_rows"):
            response = self.client.post("/api/data", json=payload, headers={"X-Admin-Key": "test-secret"})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()["analysis_eligible"], False)
            rows = self.client.get("/api/data", params={"source": "manual_demo"}).json()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], response.json()["id"])

    def test_data_source_filter_avoids_unrelated_collection(self):
        with patch.object(demo_store, "all", side_effect=AssertionError("manual collection read")):
            response = self.client.get("/api/data", params={"source": "github"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 8)

        with patch.object(github_data_store, "all", side_effect=AssertionError("github collection read")):
            response = self.client.get("/api/data", params={"source": "manual_demo"})
        self.assertEqual(response.status_code, 200)

    def test_gateway_receives_bounded_history_and_backend_result_once(self):
        headers = {"X-Session-Token": "session-a"}
        first = self.client.post("/api/chat", headers=headers, json={"message": "LangGraph 4주 알려줘"})
        conversation_id = first.json()["conversation_id"]
        gateway = MagicMock()
        gateway.chat.completions.create.return_value.choices = [MagicMock(message=MagicMock(content="요약 답변"))]
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key", "OPENAI_BASE_URL": "https://example.invalid/v1"}), patch("openai.OpenAI", return_value=gateway), patch.object(chat_api, "dispatch_tool", wraps=dispatch_tool) as tool:
            response = self.client.post("/api/chat", headers=headers, json={"message": "그럼 4주는?", "conversation_id": conversation_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tool.call_count, 1)
        messages = gateway.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "LangGraph 4주 알려줘")
        self.assertIn("Backend 분석 결과(JSON)", messages[-1]["content"])

    def test_datastore_quota_has_distinct_error_and_cors(self):
        origin = "http://localhost:3000"
        quota = ResourceExhausted("Quota exceeded.")
        with patch.object(github_data_store, "all", side_effect=quota):
            response = self.client.get("/api/data/ranking", headers={"Origin": origin})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "DATASTORE_QUOTA_EXCEEDED")
        self.assertEqual(response.headers.get("access-control-allow-origin"), origin)

        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key", "OPENAI_BASE_URL": "https://example.invalid/v1"}), patch("openai.OpenAI"), patch.object(chat_api, "dispatch_tool", side_effect=quota):
            response = self.client.post("/api/chat", headers={"Origin": origin, "X-Session-Token": "quota-test"}, json={"message": "LangGraph 추세"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "DATASTORE_QUOTA_EXCEEDED")
        self.assertEqual(response.headers.get("access-control-allow-origin"), origin)

    def test_unhandled_error_keeps_allowed_origin_only(self):
        with patch.object(github_data_store, "all", side_effect=RuntimeError("test failure")):
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/api/data/ranking", headers={"Origin": "http://localhost:3000"})
            disallowed = client.get("/api/data/ranking", headers={"Origin": "https://untrusted.example"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertIsNone(disallowed.headers.get("access-control-allow-origin"))


if __name__ == "__main__":
    unittest.main()
