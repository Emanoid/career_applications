import re
from typing import Optional

from questions.models import Question, QuestionCreate, QuestionUpdate
from questions.repository import QuestionRepository
from shared.db.client import get_db
from story_bank.models import DEFAULT_TAGS


class QuestionService:
    def __init__(self, user_id: str) -> None:
        self._user_id = user_id
        self._repo = QuestionRepository(get_db())

    def get_all(
        self,
        tag_filters: Optional[list[str]] = None,
        search_text: Optional[str] = None,
    ) -> list[Question]:
        questions = self._repo.get_all()
        if tag_filters:
            questions = [q for q in questions if any(t in q.tags for t in tag_filters)]
        if search_text and search_text.strip():
            pattern = re.compile(re.escape(search_text.strip()), re.IGNORECASE)
            questions = [q for q in questions if pattern.search(q.text)]
        return questions

    def get_by_ids(self, ids: list[str]) -> list[Question]:
        return self._repo.get_by_ids(ids)

    def get(self, question_id: str) -> Optional[Question]:
        return self._repo.get_by_id(question_id)

    def create(self, data: QuestionCreate) -> Question:
        return self._repo.create(data, self._user_id)

    def update(self, question_id: str, data: QuestionUpdate) -> Optional[Question]:
        return self._repo.update(question_id, data)

    def delete(self, question_id: str) -> bool:
        return self._repo.delete(question_id)

    def get_available_tags(self) -> list[str]:
        questions = self._repo.get_all()
        tags: set[str] = set()
        for q in questions:
            tags.update(q.tags)
        return sorted(tags | set(DEFAULT_TAGS))
