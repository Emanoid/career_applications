from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    tags: list[str] = Field(default_factory=list)


class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[list[str]] = None


class Question(QuestionCreate):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
