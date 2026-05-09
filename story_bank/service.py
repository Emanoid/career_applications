import re
from typing import Optional

from story_bank.models import DEFAULT_TAGS, Story, StoryCreate, StoryUpdate
from story_bank.repository import StoryRepository
from shared.db.client import get_db


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
    """Scoped to a single user_id at construction time — prevents cross-user data access."""

    def __init__(self, user_id: str) -> None:
        self._user_id = user_id
        self._repo = StoryRepository(get_db())

    _SEARCH_FIELDS = ("title", "situation", "task", "action", "result", "company", "location")

    def get_all(
        self,
        tag_filters: Optional[list[str]] = None,
        search_text: Optional[str] = None,
        newest_first: bool = True,
    ) -> list[Story]:
        stories = self._repo.get_by_user(self._user_id)

        if tag_filters:
            stories = [s for s in stories if any(t in s.tags for t in tag_filters)]

        if search_text and search_text.strip():
            pattern = _compile_search(search_text)
            stories = [
                s for s in stories
                if any(pattern.search(getattr(s, f) or "") for f in self._SEARCH_FIELDS)
            ]

        stories.sort(key=lambda s: s.updated_at, reverse=newest_first)
        return stories

    def get(self, story_id: str) -> Optional[Story]:
        return self._repo.get_by_id(story_id, self._user_id)

    def create(self, data: StoryCreate) -> Story:
        return self._repo.create(data, self._user_id)

    def update(self, story_id: str, data: StoryUpdate) -> Optional[Story]:
        return self._repo.update(story_id, data, self._user_id)

    def delete(self, story_id: str) -> bool:
        return self._repo.delete(story_id, self._user_id)

    def get_available_tags(self) -> list[str]:
        """Returns DEFAULT_TAGS merged with all tags the user has used, deduplicated and sorted."""
        stories = self._repo.get_by_user(self._user_id)
        user_tags: set[str] = set()
        for story in stories:
            user_tags.update(story.tags)
        return sorted(user_tags | set(DEFAULT_TAGS))
