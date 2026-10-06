"""Lazy Firebase Admin / Firestore client initialization."""

import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore


REQUIRED_FIREBASE_VARS = ("FIREBASE_PROJECT_ID", "FIREBASE_CLIENT_EMAIL", "FIREBASE_PRIVATE_KEY")


def firestore_is_configured() -> bool:
    enabled = os.getenv("FIRESTORE_ENABLED", "auto").strip().lower()
    present = [bool(os.getenv(name, "").strip()) for name in REQUIRED_FIREBASE_VARS]
    if enabled in {"0", "false", "no", "off"}:
        return False
    if enabled in {"1", "true", "yes", "on"} and not all(present):
        raise RuntimeError("FIRESTORE_ENABLED=true requires all Firebase credentials")
    if any(present) and not all(present):
        raise RuntimeError("Firebase credentials are incomplete")
    return all(present)


def get_firestore_client() -> Any:
    if not firestore_is_configured():
        return None
    if not firebase_admin._apps:
        private_key = os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n")
        credential = credentials.Certificate(
            {
                "type": "service_account",
                "project_id": os.environ["FIREBASE_PROJECT_ID"],
                "private_key": private_key,
                "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        firebase_admin.initialize_app(credential)
    return firestore.client()
