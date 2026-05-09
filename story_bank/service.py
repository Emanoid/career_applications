from typing import Optional

from story_bank.models import DEFAULT_TAGS, Story, StoryCreate, StoryUpdate
from story_bank.repository import StoryRepository
from shared.db.client import get_db


class StoryService:
    """Scoped to a single user_id at construction time — prevents cross-user data access."""

    def __init__(self, user_id: str) -> None:
        self._user_id = user_id
        self._repo = StoryRepository(get_db())

    def get_all(self, tag_filters: Optional[list[str]] = None) -> list[Story]:
        stories = self._repo.get_by_user(self._user_id)
        if tag_filters:
            stories = [s for s in stories if any(t in s.tags for t in tag_filters)]
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
