from datetime import datetime, timezone
from typing import Optional

from google.cloud.firestore import Client

from story_bank.models import Story, StoryCreate, StoryUpdate

COLLECTION = "stories"

# Fields a caller may write. Server-managed fields (user_id, created_at,
# updated_at) are NOT in this set — they are set by the repository, never
# accepted from caller-supplied data.
_WRITABLE_FIELDS = frozenset(StoryCreate.model_fields)


class StoryRepository:
    """Plain Firestore CRUD. Authorization is enforced in StoryService."""

    def __init__(self, db: Client) -> None:
        self._col = db.collection(COLLECTION)

    def create(self, data: StoryCreate, user_id: str) -> Story:
        now = datetime.now(timezone.utc)
        fields = {k: v for k, v in data.model_dump().items() if k in _WRITABLE_FIELDS}
        payload = {
            **fields,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref = self._col.document()
        doc_ref.set(payload)
        return Story(id=doc_ref.id, **payload)

    def get_all(self) -> list[Story]:
        return [Story(id=d.id, **d.to_dict()) for d in self._col.stream()]

    def get_by_user(self, user_id: str) -> list[Story]:
        docs = self._col.where("user_id", "==", user_id).stream()
        return [Story(id=d.id, **d.to_dict()) for d in docs]

    def get_by_id(self, story_id: str) -> Optional[Story]:
        doc = self._col.document(story_id).get()
        if not doc.exists:
            return None
        return Story(id=doc.id, **doc.to_dict())

    def update(self, story_id: str, data: StoryUpdate) -> Optional[Story]:
        doc = self._col.document(story_id).get()
        if not doc.exists:
            return None
        # None means "don't touch this field"; the whitelist drops any field
        # not declared on StoryUpdate so a caller cannot write server fields.
        updates = {
            k: v for k, v in data.model_dump().items()
            if v is not None and k in _WRITABLE_FIELDS
        }
        updates["updated_at"] = datetime.now(timezone.utc)
        self._col.document(story_id).update(updates)
        return self.get_by_id(story_id)

    def delete(self, story_id: str) -> bool:
        doc = self._col.document(story_id).get()
        if not doc.exists:
            return False
        self._col.document(story_id).delete()
        return True
