import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.catalog import TRACKED_TECHNOLOGIES
from backend.github_client import GitHubHistoryClient
from backend.ingestion import GitHubIngestionService
from backend.storage import TechnologyDataStore


def main() -> None:
    client = GitHubHistoryClient(token=os.getenv("GITHUB_TOKEN"), per_page=30)
    store = TechnologyDataStore()
    service = GitHubIngestionService(client, store)
    now = datetime.now(timezone.utc)
    results = []
    try:
        for technology, repository in TRACKED_TECHNOLOGIES:
            result = service.ingest_repository(technology, repository, now=now, max_pages=4)
            results.append(
                {
                    "technology": technology,
                    "repository": repository,
                    "fetched": result.fetched,
                    "complete": result.complete,
                    "pass_104": result.complete >= 104,
                }
            )
    finally:
        client.close()
    print(json.dumps({"results": results, "all_pass": all(item["pass_104"] for item in results)}, indent=2))


if __name__ == "__main__":
    main()
