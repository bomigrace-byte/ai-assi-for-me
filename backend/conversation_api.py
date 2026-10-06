from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from .conversations import Conversation, create_conversation_store, hash_session_token


router = APIRouter(prefix="/api/conversations", tags=["conversations"])
conversation_store = create_conversation_store()


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="새 대화", min_length=1, max_length=200)


def _session_hash(x_session_token: str | None) -> str:
    if not x_session_token:
        raise HTTPException(status_code=401, detail="X-Session-Token이 필요합니다.")
    return hash_session_token(x_session_token)


@router.post("", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreateRequest,
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
) -> Conversation:
    return conversation_store.create(_session_hash(x_session_token), payload.title)


@router.get("", response_model=list[Conversation])
def list_conversations(
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
) -> list[Conversation]:
    return conversation_store.list_for_session(_session_hash(x_session_token))


@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: str,
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
) -> Conversation:
    conversation = conversation_store.get_for_session(conversation_id, _session_hash(x_session_token))
    if conversation is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
) -> None:
    if not conversation_store.delete_for_session(conversation_id, _session_hash(x_session_token)):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
