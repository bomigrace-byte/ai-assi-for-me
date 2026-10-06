from fastapi import APIRouter, Depends, HTTPException, status

from .models import TechnologyData
from .policies import DataWritePayload, canonicalize_payload
from .security import require_admin_key
from .storage import ProtectedRowError, create_technology_data_store
from .sync import GitHubSyncService
from .github_client import GitHubAPIError, GitHubHistoryClient
from .snapshots import create_snapshot_store
import os
from datetime import date
from fastapi import Query


router = APIRouter(prefix="/api/data", tags=["data"])
demo_store = create_technology_data_store("technology_data_manual")
github_data_store = create_technology_data_store("technology_data")
snapshot_store = create_snapshot_store()


@router.post("", response_model=TechnologyData, status_code=status.HTTP_201_CREATED)
def create_manual_demo(
    payload: DataWritePayload,
    _admin: None = Depends(require_admin_key),
) -> TechnologyData:
    item = canonicalize_payload(payload, "manual_demo")
    return demo_store.upsert(item).item


@router.get("", response_model=list[TechnologyData])
def list_data(
    technology: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    metric: str = Query(default="weekly_new_stars"),
    source: str | None = None,
) -> list[TechnologyData]:
    rows = demo_store.all() + github_data_store.all()
    filtered = [
        row
        for row in rows
        if (technology is None or row.technology == technology)
        and (date_from is None or row.date >= date_from)
        and (date_to is None or row.date <= date_to)
        and row.metric == metric
        and (source is None or row.source == source)
    ]
    return sorted(filtered, key=lambda row: row.date)


@router.get("/snapshots")
def list_snapshots(technology: str | None = None) -> list[dict[str, object]]:
    snapshots = snapshot_store.all()
    if technology:
        snapshots = [item for item in snapshots if item.technology == technology]
    return [item.model_dump(mode="json") for item in snapshots]


@router.put("/{row_id}", response_model=TechnologyData)
def update_data(
    row_id: str,
    payload: DataWritePayload,
    _admin: None = Depends(require_admin_key),
) -> TechnologyData:
    current = demo_store.get_by_id(row_id)
    if current is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    item = canonicalize_payload(payload, "manual_demo")
    try:
        return demo_store.update(current.dedupe_key, item)
    except ProtectedRowError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.delete("/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data(
    row_id: str,
    _admin: None = Depends(require_admin_key),
) -> None:
    current = demo_store.get_by_id(row_id)
    if current is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    try:
        demo_store.delete(current.dedupe_key)
    except ProtectedRowError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/sync/github", tags=["sync"])
def sync_github(_admin: None = Depends(require_admin_key)) -> dict[str, object]:
    client = GitHubHistoryClient(token=os.getenv("GITHUB_TOKEN"))
    try:
        try:
            results = GitHubSyncService(client, github_data_store, snapshot_store).sync_all()
        except GitHubAPIError as exc:
            status_code = 429 if exc.status_code in {403, 429} else 502
            detail = {"message": str(exc), "retry_after": exc.retry_after}
            raise HTTPException(status_code=status_code, detail=detail) from exc
        return {
            "repositories": len(results),
            "completed": len(results),
            "results": [
                {
                    "technology": result.technology,
                    "repository": result.repository,
                    "fetched": result.ingestion.fetched,
                    "complete": result.ingestion.complete,
                    "created": result.ingestion.created,
                    "updated": result.ingestion.updated,
                    "current_stargazer_count": result.snapshot_stargazers,
                }
                for result in results
            ],
        }
    finally:
        client.close()
