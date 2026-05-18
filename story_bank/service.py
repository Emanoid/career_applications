import re
from typing import Optional

from shared.auth.models import SessionUser
from shared.auth.roles import ADMIN
from shared.db.client import get_db
from story_bank.models import DEFAULT_TAGS, Story, StoryCreate, StoryUpdate
from story_bank.repository import StoryRepository


def _compile_search(text: str) -> re.Pattern:
    """
    Build a case-insensitive regex from a user search string.
    * → match any sequence of characters
    _ → match any single character
    Everything else is treated as a literal substring.
    re.search is used (not fullmatch), so plain text always does substring matching.
    """
    escaped = re.escape(text.strip())
    pattern = escaped.replace(r"\*", ".*").replace(r"\_", ".")
    return re.compile(pattern, re.IGNORECASE)


class StoryService:
    """Authorization boundary for stories.

    admin  — full access to every story.
    editor — sees and manages only stories they own (user_id == their uid).
    """

    _SEARCH_FIELDS = ("title", "situation", "task", "action", "result", "company", "location")

    def __init__(self, user: SessionUser) -> None:
        self._user = user
        self._repo = StoryRepository(get_db())

    @property
    def _is_admin(self) -> bool:
        return self._user.role == ADMIN

    def _visible_stories(self) -> list[Story]:
        if self._is_admin:
            return self._repo.get_all()
        return self._repo.get_by_user(self._user.uid)

    def _require_owner(self, story_id: str) -> None:
        """Raise PermissionError if an editor tries to modify a story they don't own."""
        if self._is_admin:
            return
        story = self._repo.get_by_id(story_id)
        if story is None:
            return  # nonexistent — repo update/delete reports not-found
        if story.user_id != self._user.uid:
            raise PermissionError("You do not have permission to modify this story.")

    def get_all(
        self,
        tag_filters: Optional[list[str]] = None,
        question_filters: Optional[list[str]] = None,
        search_text: Optional[str] = None,
        newest_first: bool = True,
    ) -> list[Story]:
        stories = self._visible_stories()

        if tag_filters:
            stories = [s for s in stories if any(t in s.tags for t in tag_filters)]

        if question_filters:
            stories = [
                s for s in stories
                if any(qid in (s.question_ids or []) for qid in question_filters)
            ]

        if search_text and search_text.strip():
            pattern = _compile_search(search_text)
            stories = [
                s for s in stories
                if any(pattern.search(getattr(s, f) or "") for f in self._SEARCH_FIELDS)
            ]

        stories.sort(key=lambda s: s.updated_at, reverse=newest_first)
        return stories

    def get(self, story_id: str) -> Optional[Story]:
        story = self._repo.get_by_id(story_id)
        if story is None:
            return None
        if not self._is_admin and story.user_id != self._user.uid:
            return None
        return story

    def create(self, data: StoryCreate) -> Story:
        # Owner is always the creator — never taken from caller input.
        return self._repo.create(data, self._user.uid)

    def update(self, story_id: str, data: StoryUpdate) -> Optional[Story]:
        self._require_owner(story_id)
        return self._repo.update(story_id, data)

    def delete(self, story_id: str) -> bool:
        self._require_owner(story_id)
        return self._repo.delete(story_id)

    def get_available_tags(self) -> list[str]:
        """DEFAULT_TAGS merged with all tags on visible stories, deduplicated and sorted."""
        user_tags: set[str] = set()
        for story in self._visible_stories():
            user_tags.update(story.tags)
        return sorted(user_tags | set(DEFAULT_TAGS))
