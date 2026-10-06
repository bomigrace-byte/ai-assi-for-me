import hmac
import os

from fastapi import Header, HTTPException


def validate_admin_key(provided_key: str | None, expected_key: str | None = None) -> bool:
    """Validate an admin key without revealing whether a value was close."""
    expected = expected_key if expected_key is not None else os.getenv("ADMIN_API_KEY")
    if not provided_key or not expected:
        return False
    return hmac.compare_digest(provided_key, expected)


def require_admin_key(x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")) -> None:
    if not validate_admin_key(x_admin_key):
        raise HTTPException(status_code=401, detail="유효한 관리자 키가 필요합니다.")
