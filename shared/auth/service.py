from dataclasses import dataclass
from typing import Optional

import requests

from shared.auth.models import RegisterRequest, SessionUser
from shared.auth.repository import UserRepository
from shared.config import get_settings
from shared.db.client import get_db

_FIREBASE_AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

_AUTH_ERROR_MESSAGES: dict[str, str] = {
    "EMAIL_EXISTS": "An account with this email already exists.",
    "INVALID_EMAIL": "Invalid email address.",
    "WEAK_PASSWORD": "Password must be at least 6 characters.",
    "EMAIL_NOT_FOUND": "No account found with this email.",
    "INVALID_PASSWORD": "Incorrect password.",
    "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
    "USER_DISABLED": "This account has been disabled.",
    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Please try again later.",
}


@dataclass
class AuthResult:
    success: bool
    user: Optional[SessionUser] = None
    error: Optional[str] = None


class AuthService:
    def __init__(self) -> None:
        self._api_key = get_settings().firebase_web_api_key
        self._repo = UserRepository(get_db())

    def login(self, email: str, password: str) -> AuthResult:
        try:
            resp = requests.post(
                f"{_FIREBASE_AUTH_BASE}:signInWithPassword",
                params={"key": self._api_key},
                json={"email": email, "password": password, "returnSecureToken": True},
                timeout=10,
            )
            data = resp.json()
            if not resp.ok:
                code = data.get("error", {}).get("message", "UNKNOWN_ERROR")
                msg = _AUTH_ERROR_MESSAGES.get(code, "Authentication failed. Please try again.")
                return AuthResult(success=False, error=msg)

            profile = self._repo.get(data["localId"])
            return AuthResult(
                success=True,
                user=SessionUser(
                    uid=data["localId"],
                    email=data["email"],
                    display_name=profile.display_name if profile else None,
                    id_token=data["idToken"],
                ),
            )
        except requests.RequestException:
            return AuthResult(success=False, error="Network error. Please check your connection.")

    def register(self, req: RegisterRequest) -> AuthResult:
        try:
            resp = requests.post(
                f"{_FIREBASE_AUTH_BASE}:signUp",
                params={"key": self._api_key},
                json={"email": req.email, "password": req.password, "returnSecureToken": True},
                timeout=10,
            )
            data = resp.json()
            if not resp.ok:
                code = data.get("error", {}).get("message", "UNKNOWN_ERROR")
                msg = _AUTH_ERROR_MESSAGES.get(code, "Registration failed. Please try again.")
                return AuthResult(success=False, error=msg)

            uid = data["localId"]
            self._repo.create(uid, email=req.email, display_name=req.display_name)

            return AuthResult(
                success=True,
                user=SessionUser(
                    uid=uid,
                    email=req.email,
                    display_name=req.display_name,
                    id_token=data["idToken"],
                ),
            )
        except requests.RequestException:
            return AuthResult(success=False, error="Network error. Please check your connection.")

    def update_display_name(self, uid: str, display_name: str) -> None:
        self._repo.update_display_name(uid, display_name)
