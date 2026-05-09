from datetime import datetime, timezone
from typing import Optional

from google.cloud.firestore import Client

from story_bank.models import Story, StoryCreate, StoryUpdate

COLLECTION = "stories"


class StoryRepository:
    def __init__(self, db: Client) -> None:
        self._col = db.collection(COLLECTION)

    def create(self, data: StoryCreate, user_id: str) -> Story:
        now = datetime.now(timezone.utc)
        payload = {
            **data.model_dump(),
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref = self._col.document()
        doc_ref.set(payload)
        return Story(id=doc_ref.id, **payload)

    def get_by_user(self, user_id: str) -> list[Story]:
        docs = self._col.where("user_id", "==", user_id).stream()
        return [Story(id=d.id, **d.to_dict()) for d in docs]

    def get_by_id(self, story_id: str, user_id: str) -> Optional[Story]:
        doc = self._col.document(story_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        if data.get("user_id") != user_id:
            return None
        return Story(id=doc.id, **data)

    def update(self, story_id: str, data: StoryUpdate, user_id: str) -> Optional[Story]:
        if self.get_by_id(story_id, user_id) is None:
            return None
        # None means "don't touch this field"; empty list [] means "clear it" — both work here
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        updates["updated_at"] = datetime.now(timezone.utc)
        self._col.document(story_id).update(updates)
        return self.get_by_id(story_id, user_id)

    def delete(self, story_id: str, user_id: str) -> bool:
        if self.get_by_id(story_id, user_id) is None:
            return False
        self._col.document(story_id).delete()
        return True
