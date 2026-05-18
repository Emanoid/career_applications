from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from shared.auth.roles import DEFAULT_ROLE


class UserProfile(BaseModel):
    """Firestore document at users/{firebase_uid}. Does not store credentials."""

    id: str
    email: str
    display_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SessionUser(BaseModel):
    """Stored in st.session_state. Never contains a password or password hash.

    `role` is derived from the verified ID token's custom claim, not from user
    input — see AuthService.login. Defaults to editor (least privilege).
    """

    uid: str
    email: str
    display_name: Optional[str] = None
    id_token: str
    role: str = DEFAULT_ROLE


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = Field(None, max_length=100)
