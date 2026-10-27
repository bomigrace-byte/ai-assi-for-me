from fastapi import APIRouter, HTTPException, Query

from .analytics_snapshot import analytics_snapshot_store
from .api_data import github_data_store


router = APIRouter(prefix="/api/data", tags=["analytics"])


def _summary_for(summaries: dict[str, object], technology: str, period: str):
    result = summaries[period].get(technology)
    if result is None:
        raise HTTPException(status_code=404, detail="기술 데이터를 찾을 수 없습니다.")
    return result


@router.get("/summary")
def summary(
    technology: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    summaries = analytics_snapshot_store.get_or_build(github_data_store)["summaries"]
    return _summary_for(summaries, technology, period)


@router.get("/compare")
def compare(
    technologies: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    names = [name.strip() for name in technologies.split(",") if name.strip()]
    if len(names) < 2:
        raise HTTPException(status_code=422, detail="두 개 이상의 기술을 입력해야 합니다.")
    summaries = analytics_snapshot_store.get_or_build(github_data_store)["summaries"]
    return {
        "period": period,
        "results": [_summary_for(summaries, name, period) for name in names],
    }


@router.get("/ranking")
def ranking(
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
    limit: int = Query(default=5, ge=1, le=10),
) -> dict[str, object]:
    results = analytics_snapshot_store.get_or_build(github_data_store)["rankings"][period][:limit]
    return {
        "period": period,
        "limit": limit,
        "results": results,
    }


@router.get("/trends")
def trends(
    technology: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    summaries = analytics_snapshot_store.get_or_build(github_data_store)["summaries"]
    result = _summary_for(summaries, technology, period)
    return {
        "technology": technology,
        "period": period,
        "status": result["status"],
        "momentum_change_percent": result["momentum_change_percent"],
        "direction": {
            "accelerating": "increasing",
            "slowing": "decreasing",
            "stable": "stable",
        }.get(result["status"], "unknown"),
        "reason": result["reason"],
    }
