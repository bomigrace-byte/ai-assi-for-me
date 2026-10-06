from fastapi import APIRouter, HTTPException, Query

from .analytics import analyze_technology, rank_technologies
from .api_data import github_data_store


router = APIRouter(prefix="/api/data", tags=["analytics"])


def _technology_rows(technology: str):
    rows = [row for row in github_data_store.all() if row.technology == technology]
    if not rows:
        raise HTTPException(status_code=404, detail="기술 데이터를 찾을 수 없습니다.")
    return rows


@router.get("/summary")
def summary(
    technology: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    return analyze_technology(_technology_rows(technology), period).as_dict()


@router.get("/compare")
def compare(
    technologies: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    names = [name.strip() for name in technologies.split(",") if name.strip()]
    if len(names) < 2:
        raise HTTPException(status_code=422, detail="두 개 이상의 기술을 입력해야 합니다.")
    return {
        "period": period,
        "results": [analyze_technology(_technology_rows(name), period).as_dict() for name in names],
    }


@router.get("/ranking")
def ranking(
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
    limit: int = Query(default=5, ge=1, le=10),
) -> dict[str, object]:
    results = rank_technologies(github_data_store.all(), period=period, limit=limit)
    return {
        "period": period,
        "limit": limit,
        "results": [result.as_dict() for result in results],
    }


@router.get("/trends")
def trends(
    technology: str,
    period: str = Query(default="13w", pattern=r"^(4w|13w|26w|52w)$"),
) -> dict[str, object]:
    result = analyze_technology(_technology_rows(technology), period)
    return {
        "technology": technology,
        "period": period,
        "status": result.status,
        "momentum_change_percent": result.momentum_change_percent,
        "direction": {
            "accelerating": "increasing",
            "slowing": "decreasing",
            "stable": "stable",
        }.get(result.status, "unknown"),
        "reason": result.reason,
    }
