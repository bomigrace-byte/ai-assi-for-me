from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4
from google.cloud.firestore_v1 import FieldFilter

from pydantic import BaseModel, Field

from .firebase_client import get_firestore_client


class ConversationMessage(BaseModel):
    role: str = Field(pattern=r"^(user|assistant|system)$")
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    id: str
    title: str
    messages: list[ConversationMessage] = []
    session_hash: str
    created_at: datetime
    updated_at: datetime


def hash_session_token(token: str) -> str:
    if not token.strip():
        raise ValueError("session token must not be empty")
    return sha256(token.encode("utf-8")).hexdigest()


@dataclass
class ConversationStore:
    _items: dict[str, Conversation] = field(default_factory=dict)

    def create(self, session_hash: str, title: str = "새 대화", messages: list[ConversationMessage] | None = None) -> Conversation:
        now = datetime.now(timezone.utc)
        conversation = Conversation(
            id=str(uuid4()),
            title=title,
            messages=list(messages or []),
            session_hash=session_hash,
            created_at=now,
            updated_at=now,
        )
        self._items[conversation.id] = conversation
        return conversation

    def list_for_session(self, session_hash: str) -> list[Conversation]:
        return sorted(
            (item for item in self._items.values() if item.session_hash == session_hash),
            key=lambda item: item.updated_at,
            reverse=True,
        )

    def get_for_session(self, conversation_id: str, session_hash: str) -> Conversation | None:
        item = self._items.get(conversation_id)
        if item is None or item.session_hash != session_hash:
            return None
        return item

    def delete_for_session(self, conversation_id: str, session_hash: str) -> bool:
        if self.get_for_session(conversation_id, session_hash) is None:
            return False
        del self._items[conversation_id]
        return True

    def append_message(self, conversation_id: str, session_hash: str, message: ConversationMessage) -> Conversation | None:
        return self.append_messages(conversation_id, session_hash, [message])

    def append_messages(self, conversation_id: str, session_hash: str, messages: list[ConversationMessage]) -> Conversation | None:
        conversation = self.get_for_session(conversation_id, session_hash)
        if conversation is None:
            return None
        conversation.messages.extend(messages)
        conversation.updated_at = datetime.now(timezone.utc)
        return conversation


class FirestoreConversationStore:
    def __init__(self, client: Any, collection: str = "conversations") -> None:
        self._collection = client.collection(collection)

    def create(self, session_hash: str, title: str = "새 대화", messages: list[ConversationMessage] | None = None) -> Conversation:
        now = datetime.now(timezone.utc)
        conversation = Conversation(id=str(uuid4()), title=title, messages=list(messages or []), session_hash=session_hash, created_at=now, updated_at=now)
        self._collection.document(conversation.id).set(conversation.model_dump(mode="json"))
        return conversation

    def list_for_session(self, session_hash: str) -> list[Conversation]:
        documents = self._collection.where(filter=FieldFilter("session_hash", "==", session_hash)).stream()
        items = [Conversation.model_validate(document.to_dict()) for document in documents]
        return sorted(items, key=lambda item: item.updated_at, reverse=True)

    def get_for_session(self, conversation_id: str, session_hash: str) -> Conversation | None:
        document = self._collection.document(conversation_id).get()
        if not document.exists:
            return None
        item = Conversation.model_validate(document.to_dict())
        return item if item.session_hash == session_hash else None

    def delete_for_session(self, conversation_id: str, session_hash: str) -> bool:
        if self.get_for_session(conversation_id, session_hash) is None:
            return False
        self._collection.document(conversation_id).delete()
        return True

    def append_message(self, conversation_id: str, session_hash: str, message: ConversationMessage) -> Conversation | None:
        return self.append_messages(conversation_id, session_hash, [message])

    def append_messages(self, conversation_id: str, session_hash: str, messages: list[ConversationMessage]) -> Conversation | None:
        conversation = self.get_for_session(conversation_id, session_hash)
        if conversation is None:
            return None
        updated = conversation.model_copy(deep=True)
        updated.messages.extend(messages)
        updated.updated_at = datetime.now(timezone.utc)
        self._collection.document(conversation_id).set(updated.model_dump(mode="json"))
        return updated


def create_conversation_store() -> ConversationStore | FirestoreConversationStore:
    client = get_firestore_client()
    return FirestoreConversationStore(client) if client is not None else ConversationStore()
