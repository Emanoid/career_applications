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

### 2026-05-09 — Related Questions Feature
**Done:**
- New `questions/` module: `models.py`, `repository.py`, `service.py`
  - Questions are **global/shared** across all users (not per-user scoped)
  - Fields: `text`, `tags` (same vocabulary as stories), `created_by`, timestamps
- `story_bank/models.py` — added `question_ids: list[str]` to `StoryCreate`, `StoryUpdate`, `Story`
- `story_bank/repository.py` — update method preserves `[]` correctly (empty list = clear, `None` = don't touch)
- `story_bank/pages/add_story.py` — question association section below form; live search via `st.multiselect` with `format_func`; inline "Create & Select" form using session state bridge (`add_story_q_ids`)
- `story_bank/pages/edit_story.py` — same pattern, keyed per `story_id` to avoid collisions; seeds session state from existing `story.question_ids` on first load
- `story_bank/pages/list_stories.py` — pre-fetches all referenced question IDs in one batch pass; renders associated questions below STAR sections
- `story_bank/pages/questions_page.py` — dedicated Question Bank view: search, tag filter, inline add, inline edit, delete with confirmation
- `pages/2_Story_Bank.py` — creates `QuestionService`, passes it to all sub-views; routes `view == "questions"` to questions page
- "❓ Questions" button added to story list header

**Decisions made:**
- Questions global (shared): behavioral questions like "tell me about a time…" are universal, not personal
- Tags for questions reuse `DEFAULT_TAGS` (same starting vocabulary) but tracked independently from story tags
- Session state bridge (`{key}_q_ids`) used to pass question selections across the form/non-form boundary in Streamlit
- Pre-fetch all question IDs at top of list render (avoids N×M reads)

## Adding a New App
1. Create `new_app/` package (`models.py`, `repository.py`, `service.py`, `pages/`)
2. Add `pages/N_New_App.py` — calls `inject_global_css()`, `require_auth()`, delegates to views
3. Register new Firestore collection (no migrations needed — schemaless)
4. Add link to `shared/ui/nav.py` `_NAV_ITEMS` list
5. Add a section to `README.md` under `## Apps`
