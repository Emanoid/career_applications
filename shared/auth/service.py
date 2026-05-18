from dataclasses import dataclass
from typing import Optional

import requests
from firebase_admin import auth as fb_auth

from shared.auth.models import RegisterRequest, SessionUser
from shared.auth.repository import UserRepository
from shared.auth.roles import normalize_role
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
        # get_db() also initializes the Firebase Admin app, which fb_auth needs.
        self._repo = UserRepository(get_db())

    @staticmethod
    def _role_from_token(id_token: str) -> Optional[str]:
        """Verify the ID token server-side and return its normalized role claim.

        Returns None if the token cannot be verified — the Admin SDK checks the
        Google signature and expiry, so a forged or tampered token is rejected.
        """
        try:
            decoded = fb_auth.verify_id_token(id_token)
        except Exception:
            return None
        return normalize_role(decoded.get("role"))

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

            id_token = data["idToken"]
            role = self._role_from_token(id_token)
            if role is None:
                return AuthResult(
                    success=False,
                    error="Could not verify your session. Please try again.",
                )

            profile = self._repo.get(data["localId"])
            return AuthResult(
                success=True,
                user=SessionUser(
                    uid=data["localId"],
                    email=data["email"],
                    display_name=profile.display_name if profile else None,
                    id_token=id_token,
                    role=role,
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

            id_token = data["idToken"]
            # A brand-new account has no role claim; normalize_role yields editor.
            role = self._role_from_token(id_token)
            if role is None:
                return AuthResult(
                    success=False,
                    error="Could not verify your session. Please try again.",
                )

            return AuthResult(
                success=True,
                user=SessionUser(
                    uid=uid,
                    email=req.email,
                    display_name=req.display_name,
                    id_token=id_token,
                    role=role,
                ),
            )
        except requests.RequestException:
            return AuthResult(success=False, error="Network error. Please check your connection.")

    def update_display_name(self, uid: str, display_name: str) -> None:
        self._repo.update_display_name(uid, display_name)

    def list_accounts(self) -> list[dict]:
        """Every Firebase Auth account with email, role, and uid (admin use only)."""
        accounts: list[dict] = []
        for u in fb_auth.list_users().iterate_all():
            claims = u.custom_claims or {}
            accounts.append({
                "Email": u.email or "—",
                "Role": normalize_role(claims.get("role")),
                "UID": u.uid,
            })
        accounts.sort(key=lambda a: a["Email"].lower())
        return accounts
