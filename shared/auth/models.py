from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Firestore document at users/{firebase_uid}. Does not store credentials."""

    id: str
    email: str
    display_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SessionUser(BaseModel):
    """Stored in st.session_state. Never contains a password or password hash."""

    uid: str
    email: str
    display_name: Optional[str] = None
    id_token: str


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = Field(None, max_length=100)
