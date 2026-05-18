"""Role definitions and authorization helpers.

Roles live in Firebase Auth custom claims — a Google-signed JWT claim that is
settable only via the Admin SDK, so a user cannot forge or change their own role.
"""

ADMIN = "admin"
EDITOR = "editor"

VALID_ROLES = (ADMIN, EDITOR)

# Least privilege: a missing or unrecognized claim falls back to editor.
DEFAULT_ROLE = EDITOR


def normalize_role(raw: object) -> str:
    """Return a valid role string; missing/unknown claims default to editor."""
    return raw if raw in VALID_ROLES else DEFAULT_ROLE


def role_satisfies(user_role: str, required_role: str | None) -> bool:
    """True if user_role meets required_role. admin satisfies any requirement."""
    if required_role is None:
        return True
    if user_role == ADMIN:
        return True
    return user_role == required_role
