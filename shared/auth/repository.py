from datetime import datetime, timezone

from google.cloud.firestore import Client

from shared.auth.models import UserProfile

COLLECTION = "users"


class UserRepository:
    def __init__(self, db: Client) -> None:
        self._col = db.collection(COLLECTION)

    def get(self, uid: str) -> UserProfile | None:
        doc = self._col.document(uid).get()
        if not doc.exists:
            return None
        return UserProfile(id=doc.id, **doc.to_dict())

    def create(self, uid: str, email: str, display_name: str | None = None) -> UserProfile:
        now = datetime.now(timezone.utc)
        payload = {
            "email": email,
            "display_name": display_name,
            "created_at": now,
            "updated_at": now,
        }
        self._col.document(uid).set(payload)
        return UserProfile(id=uid, **payload)

    def update_display_name(self, uid: str, display_name: str) -> None:
        self._col.document(uid).update({
            "display_name": display_name,
            "updated_at": datetime.now(timezone.utc),
        })
