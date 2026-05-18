"""Manage role custom claims and backfill ownership fields.

Roles are stored as Firebase Auth custom claims — a Google-signed JWT claim that
can be set only with the Admin SDK, so users cannot forge or change their own.

Usage:
    python scripts/grant_role.py <email> <admin|editor>
    python scripts/grant_role.py <admin_email> --backfill
    python scripts/grant_role.py <admin_email> <admin|editor> --backfill   # does both

The script reads Firebase credentials the same way the app does (env vars,
.env, or .streamlit/secrets.toml). The target user must sign out and back in
for a new role to take effect — the role is read from a freshly issued token.
"""

import argparse
import sys
from pathlib import Path

# Allow `python scripts/grant_role.py` to import the `shared` package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from firebase_admin import auth  # noqa: E402

from shared.auth.roles import VALID_ROLES  # noqa: E402
from shared.db.client import get_db  # noqa: E402


def _set_role(email: str, role: str) -> None:
    get_db()  # initializes the Firebase Admin app
    user = auth.get_user_by_email(email)

    # Preserve any existing claims; only (re)set `role`.
    claims = dict(user.custom_claims or {})
    claims["role"] = role
    auth.set_custom_user_claims(user.uid, claims)

    print(f"Set role '{role}' for {email} (uid={user.uid}).")
    print("The user must sign out and back in for the new role to take effect.")


def _backfill(admin_email: str) -> None:
    """Idempotently stamp ownership on un-owned rows, assigning them to an admin.

    Re-running is safe: rows that already have an owner are skipped.
    """
    db = get_db()
    admin = auth.get_user_by_email(admin_email)
    admin_uid = admin.uid

    targets = [
        ("questions", "created_by"),
        ("stories", "user_id"),
    ]
    for collection, owner_field in targets:
        fixed = 0
        for doc in db.collection(collection).stream():
            data = doc.to_dict() or {}
            if not data.get(owner_field):
                doc.reference.update({owner_field: admin_uid})
                fixed += 1
        print(f"{collection}: stamped {owner_field} on {fixed} un-owned row(s).")

    print(f"Orphaned rows assigned to admin {admin_email} (uid={admin_uid}).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage Firebase role custom claims.",
    )
    parser.add_argument(
        "email",
        help="Target user email (or the admin email to assign orphans to with --backfill).",
    )
    parser.add_argument(
        "role",
        nargs="?",
        choices=sorted(VALID_ROLES),
        help="Role to grant. Optional when --backfill is given.",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Stamp ownership fields on un-owned questions/stories rows, "
             "assigning them to <email>. Idempotent. Can be combined with a role.",
    )
    args = parser.parse_args()

    if not args.role and not args.backfill:
        parser.error("provide a role, --backfill, or both")

    # When both are given, set the role first, then backfill.
    if args.role:
        _set_role(args.email, args.role)
    if args.backfill:
        _backfill(args.email)


if __name__ == "__main__":
    main()
