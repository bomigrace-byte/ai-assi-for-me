from dataclasses import dataclass
from statistics import fmean
from typing import Literal

from .models import TechnologyData


PERIOD_WEEKS = {"4w": 4, "13w": 13, "26w": 26, "52w": 52}
MOMENTUM_THRESHOLD_PERCENT = 10.0
MomentumStatus = Literal[
    "accelerating",
    "slowing",
    "stable",
    "insufficient_baseline",
    "insufficient_data",
]


@dataclass(frozen=True)
class AnalysisResult:
    technology: str
    repository: str
    period: str
    weeks: int
    observed_recent: int
    observed_previous: int
    weekly_new_stars_total: int | None
    weekly_new_stars_average: float | None
    weekly_new_stars_max: int | None
    weekly_new_stars_min: int | None
    momentum_change_percent: float | None
    status: MomentumStatus
    recent_start_week: int | None
    recent_end_week: int | None
    reason: str

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


def period_size(period: str) -> int:
    try:
        return PERIOD_WEEKS[period]
    except KeyError as exc:
        raise ValueError(f"unsupported period: {period}") from exc


def analysis_rows(rows: list[TechnologyData]) -> list[TechnologyData]:
    return sorted(
        (
            row
            for row in rows
            if row.source == "github"
            and row.source_type == "github_star_history"
            and row.analysis_eligible is True
            and row.metric == "weekly_new_stars"
        ),
        key=lambda row: row.week_start_epoch,
    )


def _empty_result(
    technology: str,
    repository: str,
    period: str,
    weeks: int,
    recent: list[TechnologyData],
    previous: list[TechnologyData],
) -> AnalysisResult:
    return AnalysisResult(
        technology=technology,
        repository=repository,
        period=period,
        weeks=weeks,
        observed_recent=len(recent),
        observed_previous=len(previous),
        weekly_new_stars_total=None,
        weekly_new_stars_average=None,
        weekly_new_stars_max=None,
        weekly_new_stars_min=None,
        momentum_change_percent=None,
        status="insufficient_data",
        recent_start_week=recent[0].week_start_epoch if recent else None,
        recent_end_week=recent[-1].week_start_epoch if recent else None,
        reason=f"최근·직전 각 {weeks}개의 완결 주 관측치가 필요합니다.",
    )


def analyze_technology(rows: list[TechnologyData], period: str) -> AnalysisResult:
    weeks = period_size(period)
    eligible = analysis_rows(rows)
    if not eligible:
        return _empty_result("unknown", "unknown", period, weeks, [], [])
    technology = eligible[0].technology
    repository = eligible[0].repository
    recent = eligible[-weeks:]
    previous = eligible[-(weeks * 2) : -weeks]
    if len(recent) < weeks or len(previous) < weeks:
        return _empty_result(technology, repository, period, weeks, recent, previous)

    recent_values = [row.value for row in recent]
    previous_values = [row.value for row in previous]
    recent_avg = fmean(recent_values)
    previous_avg = fmean(previous_values)
    if previous_avg == 0:
        status: MomentumStatus = "insufficient_baseline"
        change = None
        reason = "직전 기간 평균 신규 Star가 0이어서 Momentum을 계산하지 않습니다."
    else:
        change = (recent_avg - previous_avg) / previous_avg * 100
        if change > MOMENTUM_THRESHOLD_PERCENT:
            status = "accelerating"
        elif change < -MOMENTUM_THRESHOLD_PERCENT:
            status = "slowing"
        else:
            status = "stable"
        reason = f"최근 {weeks}주 평균 {recent_avg:.1f}, 직전 {weeks}주 평균 {previous_avg:.1f} 기준입니다."

    return AnalysisResult(
        technology=technology,
        repository=repository,
        period=period,
        weeks=weeks,
        observed_recent=len(recent),
        observed_previous=len(previous),
        weekly_new_stars_total=sum(recent_values),
        weekly_new_stars_average=recent_avg,
        weekly_new_stars_max=max(recent_values),
        weekly_new_stars_min=min(recent_values),
        momentum_change_percent=change,
        status=status,
        recent_start_week=recent[0].week_start_epoch,
        recent_end_week=recent[-1].week_start_epoch,
        reason=reason,
    )


def rank_technologies(
    rows: list[TechnologyData],
    period: str = "13w",
    limit: int = 5,
) -> list[AnalysisResult]:
    by_repository: dict[str, list[TechnologyData]] = {}
    for row in analysis_rows(rows):
        by_repository.setdefault(row.repository, []).append(row)
    results = [analyze_technology(repository_rows, period) for repository_rows in by_repository.values()]
    eligible = [
        result
        for result in results
        if result.status in {"accelerating", "slowing", "stable"}
    ]
    return sorted(
        eligible,
        key=lambda result: (
            -(result.weekly_new_stars_average or 0),
            -(result.momentum_change_percent or 0),
        ),
    )[:limit]
