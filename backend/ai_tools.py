from typing import Any

from .analytics import analyze_technology
from .analytics_snapshot import analytics_snapshot_store
from .api_data import github_data_store


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_technology_summary",
            "description": "Return backend-calculated summary and momentum for one technology.",
            "parameters": {"type": "object", "properties": {"technology": {"type": "string"}, "period": {"type": "string", "enum": ["4w", "13w", "26w", "52w"]}}, "required": ["technology", "period"], "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_technologies",
            "description": "Compare backend-calculated weekly new stars and momentum for technologies.",
            "parameters": {"type": "object", "properties": {"technologies": {"type": "array", "items": {"type": "string"}}, "period": {"type": "string", "enum": ["4w", "13w", "26w", "52w"]}}, "required": ["technologies", "period"], "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_trend_changes",
            "description": "Return backend-calculated increasing, decreasing, stable, or insufficient trend.",
            "parameters": {"type": "object", "properties": {"technology": {"type": "string"}, "period": {"type": "string", "enum": ["4w", "13w", "26w", "52w"]}}, "required": ["technology", "period"], "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_technology_history",
            "description": "Return backend-stored weekly_new_stars observations for one technology.",
            "parameters": {"type": "object", "properties": {"technology": {"type": "string"}, "weeks": {"type": "integer", "minimum": 1, "maximum": 52}}, "required": ["technology", "weeks"], "additionalProperties": False},
        },
    },
]


def _rows_for(technology: str):
    return github_data_store.for_technology(technology)


def _summary(summaries: dict[str, dict[str, Any]], technology: str, period: str) -> dict[str, Any]:
    return summaries.get(technology) or analyze_technology([], period).as_dict()


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "get_technology_summary":
        summaries = analytics_snapshot_store.get_or_build(github_data_store)["summaries"][arguments["period"]]
        return _summary(summaries, arguments["technology"], arguments["period"])
    if name == "compare_technologies":
        summaries = analytics_snapshot_store.get_or_build(github_data_store)["summaries"][arguments["period"]]
        return {
            "period": arguments["period"],
            "results": [
                _summary(summaries, technology, arguments["period"])
                for technology in arguments["technologies"]
            ],
        }
    if name == "get_trend_changes":
        result = dispatch_tool("get_technology_summary", arguments)
        return {
            "technology": result["technology"],
            "period": result["period"],
            "status": result["status"],
            "momentum_change_percent": result["momentum_change_percent"],
            "reason": result["reason"],
        }
    if name == "get_technology_history":
        rows = sorted(_rows_for(arguments["technology"]), key=lambda row: row.week_start_epoch)[-arguments["weeks"] :]
        return {"technology": arguments["technology"], "weeks": len(rows), "rows": [row.model_dump(mode="json") for row in rows]}
    raise ValueError(f"unknown tool: {name}")
