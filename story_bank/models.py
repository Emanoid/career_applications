from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

DEFAULT_TAGS: list[str] = [
    "Conflict Resolution",
    "Cross-team Collaboration",
    "Customer Focus",
    "Delivering Under Pressure",
    "Handling Failure",
    "Influencing Without Authority",
    "Leading System Design",
    "Mentoring",
    "Navigating Ambiguity",
    "Process Improvement",
    "Stakeholder Management",
    "Technical Leadership",
    "Trouble with Manager",
]


class StoryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    situation: str = Field(..., min_length=1)
    task: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    result: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    company: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    question_ids: list[str] = Field(default_factory=list)


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    tags: Optional[list[str]] = None
    company: Optional[str] = None
    location: Optional[str] = None
    question_ids: Optional[list[str]] = None


class Story(StoryCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
