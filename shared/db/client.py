import json

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client

from shared.config import get_settings


def get_db() -> Client:
    """Return a Firestore client, initializing Firebase Admin SDK on first call."""
    if not firebase_admin._apps:
        cfg = get_settings()
        if not cfg.firebase_credentials_json:
            raise RuntimeError(
                "Firebase credentials not configured. "
                "Set firebase.credentials_json in .streamlit/secrets.toml "
                "or FIREBASE_CREDENTIALS_JSON env var."
            )
        cred_dict = json.loads(cfg.firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()
