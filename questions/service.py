import re
from typing import Optional

from questions.models import Question, QuestionCreate, QuestionUpdate
from questions.repository import QuestionRepository
from shared.auth.models import SessionUser
from shared.auth.roles import ADMIN
from shared.db.client import get_db
from story_bank.models import DEFAULT_TAGS


class QuestionService:
    """Authorization boundary for the shared question bank.

    Reads are global — every user sees the whole pool (questions are universal,
    not personal). Writes are scoped: an editor may edit/delete only questions
    they created; an admin may modify any.
    """

    def __init__(self, user: SessionUser) -> None:
        self._user = user
        self._repo = QuestionRepository(get_db())

    @property
    def _is_admin(self) -> bool:
        return self._user.role == ADMIN

    def can_edit(self, question: Question) -> bool:
        """True if the current user may edit/delete this question (for UI gating)."""
        return self._is_admin or question.created_by == self._user.uid

    def _require_owner(self, question_id: str) -> None:
        """Raise PermissionError if an editor tries to modify a question they didn't create."""
        if self._is_admin:
            return
        question = self._repo.get_by_id(question_id)
        if question is None:
            return  # nonexistent — repo update/delete reports not-found
        if question.created_by != self._user.uid:
            raise PermissionError("You do not have permission to modify this question.")

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
        # created_by is always the creator — never taken from caller input.
        return self._repo.create(data, self._user.uid)

    def update(self, question_id: str, data: QuestionUpdate) -> Optional[Question]:
        self._require_owner(question_id)
        return self._repo.update(question_id, data)

    def delete(self, question_id: str) -> bool:
        self._require_owner(question_id)
        return self._repo.delete(question_id)

    def get_available_tags(self) -> list[str]:
        questions = self._repo.get_all()
        tags: set[str] = set()
        for q in questions:
            tags.update(q.tags)
        return sorted(tags | set(DEFAULT_TAGS))
