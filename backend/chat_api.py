import time
from collections import defaultdict, deque
import json
import os
import re
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .ai_tools import dispatch_tool
from .ai_tools import TOOL_SCHEMAS
from .conversation_api import conversation_store
from .conversations import ConversationMessage, hash_session_token
from .catalog import TRACKED_TECHNOLOGIES


router = APIRouter(prefix="/api/chat", tags=["chat"])
MAX_MESSAGE_LENGTH = 2000
MAX_REQUESTS_PER_HOUR = 20
request_history: dict[str, deque[float]] = defaultdict(deque)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    conversation_id: str | None = None
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None


def _session_hash(token: str | None) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="X-Session-Token이 필요합니다.")
    return hash_session_token(token)


def _check_rate_limit(session_hash: str) -> None:
    now = time.time()
    history = request_history[session_hash]
    while history and now - history[0] > 3600:
        history.popleft()
    if len(history) >= MAX_REQUESTS_PER_HOUR:
        raise HTTPException(status_code=429, detail="Chat 요청 한도를 초과했습니다.")
    history.append(now)


def _select_tool(request: ChatRequest) -> tuple[str, dict[str, Any]]:
    if request.tool_name:
        return request.tool_name, request.tool_arguments or {}
    period_match = re.search(r"(4|13|26|52)\s*(?:주|w)", request.message, re.IGNORECASE)
    period = f"{period_match.group(1)}w" if period_match else "13w"
    technologies = [technology for technology, _ in TRACKED_TECHNOLOGIES if technology.lower() in request.message.lower()]
    comparison = any(word in request.message.lower() for word in ("비교", "중", "vs", "어느 쪽"))
    if len(technologies) >= 2 and comparison:
        return "compare_technologies", {"technologies": technologies[:2], "period": period}
    if technologies:
        tool = "get_trend_changes" if any(word in request.message for word in ("성장", "추세", "변화", "가속", "둔화")) else "get_technology_summary"
        return tool, {"technology": technologies[0], "period": period}
    return "get_technology_history", {"technology": "", "weeks": 13}


def _answer(tool_name: str, result: dict[str, Any], period: str | None = None) -> str:
    if tool_name == "get_technology_history":
        if not result.get("rows"):
            return "아직 분석 데이터가 없습니다. GitHub 동기화 후 다시 질문해 주세요."
        return f"{result['technology']}의 주별 신규 Star 관측 {result['weeks']}개를 확인했습니다."
    if tool_name == "compare_technologies":
        items = result.get("results", [])
        details = "; ".join(f"{item.get('technology')}: {item.get('weekly_new_stars_average')} Star/주, Momentum {item.get('momentum_change_percent')}%, 관측 {item.get('observed_recent')}주" for item in items)
        return f"최근 {period or result.get('period')} 기준 비교 결과입니다. {details}. 각 결과의 관측 주 수와 데이터 상태를 함께 확인하세요."
    status = result.get("status", "insufficient_data")
    reason = result.get("reason", "데이터가 부족합니다.")
    observed = result.get("observed_recent", 0)
    return f"{result.get('technology', '기술')}의 최근 {period or result.get('period')} 관측 {observed}주 상태는 {status}입니다. {reason}"


def _openai_answer(message: str, fallback_tool: str, fallback_arguments: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    """Use OpenAI Function Calling when configured; otherwise stay deterministic locally."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        result = dispatch_tool(fallback_tool, fallback_arguments)
        return fallback_tool, result, _answer(fallback_tool, result, fallback_arguments.get("period"))

    try:
        from openai import OpenAI

        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        client = OpenAI(api_key=api_key, base_url=base_url)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "한국어로 답하세요. 수치와 판단은 반드시 제공된 Backend Tool 결과만 사용하고, 금융 투자 조언은 하지 마세요."},
            {"role": "user", "content": message},
        ]
        # Some OpenAI-compatible gateways expose GPT-5 but only accept the
        # broadly supported Chat Completions fields. Keep gateway requests
        # conservative while retaining the native parameter for direct OpenAI.
        request_options: dict[str, Any] = {"temperature": 0}
        if base_url:
            request_options["max_tokens"] = 500
        elif model.startswith("gpt-5"):
            request_options["max_completion_tokens"] = 500
        else:
            request_options["max_tokens"] = 500
        first = client.chat.completions.create(model=model, messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto", **request_options)
        assistant = first.choices[0].message
        calls = assistant.tool_calls or []
        if not calls:
            result = dispatch_tool(fallback_tool, fallback_arguments)
            return fallback_tool, result, assistant.content or _answer(fallback_tool, result, fallback_arguments.get("period"))
        call = calls[0]
        tool_name = call.function.name
        arguments = json.loads(call.function.arguments or "{}")
        result = dispatch_tool(tool_name, arguments)
        messages.append({"role": "assistant", "content": assistant.content, "tool_calls": [call.model_dump()]})
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})
        final = client.chat.completions.create(model=model, messages=messages, tools=TOOL_SCHEMAS, tool_choice="none", **request_options)
        return tool_name, result, final.choices[0].message.content or _answer(tool_name, result, arguments.get("period"))
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail=f"AI Tool 호출 결과를 해석하지 못했습니다: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI 호출에 실패했습니다: {exc}") from exc


@router.post("")
def chat(
    request: ChatRequest,
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
) -> dict[str, Any]:
    session_hash = _session_hash(x_session_token)
    _check_rate_limit(session_hash)
    if request.conversation_id:
        conversation = conversation_store.get_for_session(request.conversation_id, session_hash)
        if conversation is None:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    else:
        conversation = conversation_store.create(session_hash, request.message[:60])

    tool_name, arguments = _select_tool(request)
    try:
        tool_result = dispatch_tool(tool_name, arguments)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    tool_name, tool_result, answer = _openai_answer(request.message, tool_name, arguments)
    conversation_store.append_message(conversation.id, session_hash, ConversationMessage(role="user", content=request.message))
    conversation_store.append_message(conversation.id, session_hash, ConversationMessage(role="assistant", content=answer))
    return {
        "conversation_id": conversation.id,
        "tool_name": tool_name,
        "tool_result": tool_result,
        "answer": answer,
    }
