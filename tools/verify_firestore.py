"""Non-destructive Firestore connectivity smoke test."""

from datetime import datetime, timezone
from pathlib import Path
import sys
from uuid import uuid4

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.firebase_client import get_firestore_client


def main() -> int:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    client = get_firestore_client()
    if client is None:
        print("FIRESTORE_NOT_CONFIGURED")
        return 2
    document = client.collection("system_smoke_tests").document(f"local-{uuid4()}")
    payload = {"status": "ok", "created_at": datetime.now(timezone.utc).isoformat()}
    document.set(payload, timeout=10)
    loaded = document.get(timeout=10).to_dict()
    document.delete(timeout=10)
    if loaded != payload:
        raise RuntimeError("Firestore read-back mismatch")
    print("FIRESTORE_REMOTE_SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
