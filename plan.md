# Career Applications Suite — Plan

## Goal
Build a series of Streamlit web apps to support career progression, starting with a behavioral interview story bank.

## Architecture
- **Framework:** Streamlit (Community Cloud deployment)
- **Database:** Firestore (Firebase Admin SDK)
- **Auth:** Firebase Authentication (email/password) via REST API
- **Pattern:** UI → Service → Repository (3 layers); `shared/` is cross-cutting, apps are isolated packages

## Apps Planned
- [x] Story Bank (behavioral interview story bank, STAR format)
- [ ] Job Tracker (application pipeline tracking)
- [ ] Resume Builder (tailored resume sections)

## Progress Log

### 2026-05-08 — Initial Build
**Done:**
- Project scaffold: `.gitignore`, `requirements.txt`, `.streamlit/config.toml`
- `shared/` layer: config, db singleton, Firebase Auth REST service, session guard, UI components/styles/nav
- `story_bank/` layer: models (STAR fields, DEFAULT_TAGS), repository, service, list/add/edit page views
- Streamlit pages: Login (sign in + register tabs), Story Bank, Settings, main landing
- Custom CSS: Inter font, design tokens, dark sidebar, styled buttons/inputs/expanders

**Architecture decisions made:**
- Firebase Auth REST API for auth (not bcrypt + Firestore passwords)
- `StoryService(user_id)` scoped at init — cross-user access is a construction-time error
- `SessionUser` in session_state — never contains password or password hash
- `get_available_tags()` merges DEFAULT_TAGS + user's historical tags — custom tags persist automatically
- Confirmation modal before delete (avoid accidental data loss)

**Next steps:**
- User fills in `.streamlit/secrets.toml` with Firebase credentials and runs locally to verify
- Deploy to Streamlit Community Cloud

## Adding a New App
1. Create `new_app/` package (`models.py`, `repository.py`, `service.py`, `pages/`)
2. Add `pages/N_New_App.py` — calls `inject_global_css()`, `require_auth()`, delegates to views
3. Register new Firestore collection (no migrations needed — schemaless)
4. Add link to `shared/ui/nav.py` `_NAV_ITEMS` list
5. Add a section to `README.md` under `## Apps`
