import csv
import io
from datetime import date

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from .api_data import demo_store, github_data_store


router = APIRouter(prefix="/api/export", tags=["export"])


def filtered_rows(
    technology: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    metric: str = "weekly_new_stars",
):
    rows = demo_store.all() + github_data_store.all()
    return sorted(
        [
            row
            for row in rows
            if (technology is None or row.technology == technology)
            and (date_from is None or row.date >= date_from)
            and (date_to is None or row.date <= date_to)
            and row.metric == metric
        ],
        key=lambda row: row.date,
    )


@router.get("/json")
def export_json(
    technology: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    metric: str = Query(default="weekly_new_stars"),
) -> JSONResponse:
    rows = filtered_rows(technology, date_from, date_to, metric)
    return JSONResponse(
        content={
            "count": len(rows),
            "filters": {
                "technology": technology,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "metric": metric,
            },
            "rows": [row.model_dump(mode="json") for row in rows],
        }
    )


@router.get("/csv")
def export_csv(
    technology: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    metric: str = Query(default="weekly_new_stars"),
) -> StreamingResponse:
    rows = filtered_rows(technology, date_from, date_to, metric)
    output = io.StringIO(newline="")
    fields = [
        "id",
        "technology",
        "repository",
        "date",
        "week_start_epoch",
        "value",
        "metric",
        "source",
        "source_type",
        "analysis_eligible",
        "collected_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        data = row.model_dump(mode="json")
        writer.writerow({field: data.get(field) for field in fields})
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=ai-tech-trend-radar.csv"},
    )
