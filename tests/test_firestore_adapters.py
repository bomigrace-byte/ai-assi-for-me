import unittest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

from backend.conversations import ConversationMessage, ConversationStore, FirestoreConversationStore
from backend.models import TechnologyData, TechnologySnapshot
from backend.storage import FirestoreTechnologyDataStore, ProtectedRowError
from backend.snapshots import FirestoreTechnologySnapshotStore
from backend.analytics_snapshot import AnalyticsSnapshotStore


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.id = document_id

    def get(self):
        return FakeSnapshot(self.id, self.collection.items.get(self.id))

    def set(self, value):
        self.collection.items[self.id] = value
        self.collection.write_count += 1

    def delete(self):
        self.collection.items.pop(self.id, None)


class FakeSnapshot:
    def __init__(self, document_id, value):
        self.id = document_id
        self._value = value
        self.exists = value is not None

    def to_dict(self):
        return self._value


class FakeCollection:
    def __init__(self):
        self.items = {}
        self.write_count = 0

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def stream(self):
        return [FakeSnapshot(document_id, value) for document_id, value in self.items.items()]


class FakeClient:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, FakeCollection())


def make_row(source="github", eligible=True):
    now = datetime.now(timezone.utc)
    return TechnologyData(
        technology="LangGraph",
        repository="langchain-ai/langgraph",
        date=date(2026, 1, 5),
        week_start_epoch=1767571200,
        value=42,
        metric="weekly_new_stars",
        source=source,
        source_type="github_star_history" if source == "github" else "manual_entry",
        analysis_eligible=eligible,
        collected_at=now,
        created_at=now,
        updated_at=now,
    )


class FirestoreAdapterTest(unittest.TestCase):
    def test_materialized_analytics_reads_one_document_without_streaming_raw_rows(self):
        client = FakeClient()
        store = AnalyticsSnapshotStore(client)
        raw = MagicMock()
        raw.all.return_value = [make_row()]
        first = store.get_or_build(raw)
        self.assertEqual(first["summaries"]["13w"]["LangGraph"]["technology"], "LangGraph")
        self.assertEqual(client.collection("analytics_snapshots").write_count, 1)
        raw.all.side_effect = AssertionError("unexpected raw collection scan")
        with patch.object(client.collection("analytics_snapshots"), "stream", side_effect=AssertionError("snapshot collection scan")):
            self.assertEqual(store.get_or_build(raw)["summaries"], first["summaries"])

    def test_filtered_history_queries_only_requested_technology(self):
        client = MagicMock()
        store = FirestoreTechnologyDataStore(client)
        query = client.collection.return_value.where.return_value
        query.stream.return_value = [FakeSnapshot("row", make_row().model_dump(mode="json"))]
        with patch.object(store._collection, "stream", side_effect=AssertionError("full scan")):
            rows = store.for_technology("LangGraph")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].technology, "LangGraph")
        self.assertEqual(store._collection.where.call_args.kwargs["filter"].field_path, "technology")

    def test_conversation_list_queries_only_the_session(self):
        client = MagicMock()
        conversations = FirestoreConversationStore(client)
        conversation = ConversationStore().create("session-a", "test")
        query = client.collection.return_value.where.return_value
        query.stream.return_value = [FakeSnapshot(conversation.id, conversation.model_dump(mode="json"))]
        with patch.object(conversations._collection, "stream", side_effect=AssertionError("full scan")):
            items = conversations.list_for_session("session-a")
        self.assertEqual(len(items), 1)
        self.assertEqual(conversations._collection.where.call_args.kwargs["filter"].field_path, "session_hash")

    def test_data_upsert_and_github_protection(self):
        client = FakeClient()
        store = FirestoreTechnologyDataStore(client)
        first = store.upsert(make_row()).item
        second = store.upsert(make_row()).item
        self.assertEqual(first.id, second.id)
        self.assertEqual(store.count(), 1)
        cached_store = FirestoreTechnologyDataStore(client)
        with patch.object(client.collection("technology_data"), "stream", wraps=client.collection("technology_data").stream) as stream:
            cached_store.all()
            cached_store.all()
        self.assertEqual(stream.call_count, 1)
        self.assertEqual(cached_store._cache_ttl_seconds, 3600)
        with self.assertRaises(ProtectedRowError):
            store.delete(first.dedupe_key)

    def test_snapshot_and_conversation_isolation(self):
        client = FakeClient()
        snapshots = FirestoreTechnologySnapshotStore(client)
        now = datetime.now(timezone.utc)
        snapshot = TechnologySnapshot(technology="LangGraph", repository="langchain-ai/langgraph", current_stargazer_count=100, collected_at=now)
        snapshots.upsert(snapshot)
        self.assertEqual(snapshots.get(snapshot.repository).current_stargazer_count, 100)

        conversations = FirestoreConversationStore(client)
        item = conversations.create("session-a", "test")
        conversations.append_message(item.id, "session-a", ConversationMessage(role="user", content="hello"))
        self.assertIsNone(conversations.get_for_session(item.id, "session-b"))
        self.assertEqual(len(conversations.get_for_session(item.id, "session-a").messages), 1)

    def test_conversation_exchange_is_saved_in_one_write(self):
        client = FakeClient()
        conversations = FirestoreConversationStore(client)
        exchange = [ConversationMessage(role="user", content="질문"), ConversationMessage(role="assistant", content="답변")]
        item = conversations.create("session-a", "첫 질문", messages=exchange)
        collection = client.collection("conversations")
        self.assertEqual(collection.write_count, 1)
        self.assertEqual(len(conversations.get_for_session(item.id, "session-a").messages), 2)

        conversations.append_messages(item.id, "session-a", exchange)
        self.assertEqual(collection.write_count, 2)
        self.assertEqual(len(conversations.get_for_session(item.id, "session-a").messages), 4)
        self.assertIsNone(conversations.append_messages(item.id, "session-b", exchange))
        self.assertEqual(collection.write_count, 2)


if __name__ == "__main__":
    unittest.main()
