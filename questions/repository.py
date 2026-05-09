from datetime import datetime, timezone
from typing import Optional

from google.cloud.firestore import Client

from questions.models import Question, QuestionCreate, QuestionUpdate

COLLECTION = "questions"


class QuestionRepository:
    def __init__(self, db: Client) -> None:
        self._col = db.collection(COLLECTION)

    def create(self, data: QuestionCreate, created_by: str) -> Question:
        now = datetime.now(timezone.utc)
        payload = {
            **data.model_dump(),
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref = self._col.document()
        doc_ref.set(payload)
        return Question(id=doc_ref.id, **payload)

    def get_all(self) -> list[Question]:
        docs = self._col.stream()
        return [Question(id=d.id, **d.to_dict()) for d in docs]

    def get_by_ids(self, ids: list[str]) -> list[Question]:
        results = []
        for qid in ids:
            doc = self._col.document(qid).get()
            if doc.exists:
                results.append(Question(id=doc.id, **doc.to_dict()))
        return results

    def get_by_id(self, question_id: str) -> Optional[Question]:
        doc = self._col.document(question_id).get()
        if not doc.exists:
            return None
        return Question(id=doc.id, **doc.to_dict())

    def update(self, question_id: str, data: QuestionUpdate) -> Optional[Question]:
        doc = self._col.document(question_id).get()
        if not doc.exists:
            return None
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        updates["updated_at"] = datetime.now(timezone.utc)
        self._col.document(question_id).update(updates)
        return self.get_by_id(question_id)

    def delete(self, question_id: str) -> bool:
        doc = self._col.document(question_id).get()
        if not doc.exists:
            return False
        self._col.document(question_id).delete()
        return True
