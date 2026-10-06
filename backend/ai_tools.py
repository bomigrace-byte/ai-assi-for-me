from typing import Any

from .analytics import analyze_technology, rank_technologies
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
    return [row for row in github_data_store.all() if row.technology == technology]


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "get_technology_summary":
        rows = _rows_for(arguments["technology"])
        return analyze_technology(rows, arguments["period"]).as_dict()
    if name == "compare_technologies":
        return {
            "period": arguments["period"],
            "results": [
                analyze_technology(_rows_for(technology), arguments["period"]).as_dict()
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
