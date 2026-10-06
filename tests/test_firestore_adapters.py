import unittest
from datetime import date, datetime, timezone

from backend.conversations import ConversationMessage, FirestoreConversationStore
from backend.models import TechnologyData, TechnologySnapshot
from backend.storage import FirestoreTechnologyDataStore, ProtectedRowError
from backend.snapshots import FirestoreTechnologySnapshotStore


class FakeDocument:
    def __init__(self, collection, document_id):
        self.collection = collection
        self.id = document_id

    def get(self):
        return FakeSnapshot(self.id, self.collection.items.get(self.id))

    def set(self, value):
        self.collection.items[self.id] = value

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
    def test_data_upsert_and_github_protection(self):
        store = FirestoreTechnologyDataStore(FakeClient())
        first = store.upsert(make_row()).item
        second = store.upsert(make_row()).item
        self.assertEqual(first.id, second.id)
        self.assertEqual(store.count(), 1)
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


if __name__ == "__main__":
    unittest.main()
