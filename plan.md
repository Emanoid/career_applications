# Plan — Role-Based Access Control & Security Hardening

## Status
Implemented on branch `feature/rbac`. All files compile and import clean. Not yet
run against a live Firebase project (no credentials available in this session).

## Decisions (confirmed with user, 2026-05-18)
1. Question Bank: global read, scoped write — editors edit/delete only their own (`created_by`); admins any.
2. `stories`: keep existing `user_id` field as the ownership key (no rename, no migration).
3. Backfill orphaned rows → assign to a supplied admin UID.
4. Implement all six sections in one pass.
5. `--backfill` covers questions (`created_by`) and stories (`user_id`).
6. Keep public registration; do NOT disable Firebase self-signup. New self-registered users default to `editor`.

## What was done
- `shared/auth/roles.py` (new) — role constants + `normalize_role` / `role_satisfies`.
- `SessionUser` carries verified `role` (default editor).
- `AuthService.login/register` verify the ID token (`verify_id_token`) and read the `role` claim.
- `require_auth(required_role=...)` — role gate on the login wall.
- `scripts/grant_role.py` (new) — sets role custom claim (preserves other claims); idempotent `--backfill`.
- `firestore.rules` (new) — deny-all client access.
- Repositories are plain CRUD with explicit writable-field whitelists.
- `StoryService` / `QuestionService` take `SessionUser`, enforce role/ownership; non-owner update/delete raises `PermissionError`.
- UI: role badge in sidebar; question Edit/Delete gated by ownership; admin-only User Accounts & Roles panel in Settings.
- README updated.

## Follow-up fixes (2026-05-18)
- grant_role.py bug: `--backfill` was mutually exclusive with role-setting, so
  `<email> admin --backfill` only backfilled and never set the role. Fixed —
  role and `--backfill` can now be combined; both run when both are given.
- XSS hardening: all user-controlled values interpolated into `unsafe_allow_html`
  are now `html.escape()`d — sidebar (nav.py), Settings, components.py
  (page_header/tag_badge/star_section/story_meta), list_stories.py search/tag
  summary + related questions, questions_page.py question text.

## UI copy scrub (2026-05-18)
- Removed the `grant_role.py` command from the Settings → User Accounts caption
  (end users should not see code/script references).
- Removed the "Created by another user — read-only" caption on questions the
  user cannot edit — controls are simply absent, revealing nothing about the
  access model.

## Manual steps left for the user
- Run `python scripts/grant_role.py <your-email> admin` to grant the first admin,
  then SIGN OUT AND BACK IN (role is read from a fresh token at login).
- (Optional) `python scripts/grant_role.py <admin-email> --backfill` if pre-existing un-owned rows exist.
- Deploy `firestore.rules` (Firebase CLI or Console → Firestore → Rules).
- Confirm the deployment is served over HTTPS.
- Self-signup toggle: Firebase Console → Authentication → Settings → User actions → "Enable create (sign-up)" (left enabled per decision 6).
- Smoke-test login/role flow against the live Firebase project.
