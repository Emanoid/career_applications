# Career Suite

A growing collection of Streamlit web apps to support career progression. Each app is independently deployable but shares a common authentication layer, Firestore backend, and UI design system.

---

## Table of Contents

1. [Overview](#overview)
2. [Setup & Deployment](#setup--deployment)
   - [Prerequisites](#prerequisites)
   - [Firebase Configuration](#firebase-configuration)
   - [Local Development](#local-development)
   - [Deploying to Streamlit Community Cloud](#deploying-to-streamlit-community-cloud)
3. [Apps](#apps)
   - [Story Bank](#story-bank)
   - [Question Bank](#question-bank)
4. [Adding a New App](#adding-a-new-app)
5. [Development Notes](#development-notes)

---

## Overview

| App | Description | Status |
|-----|-------------|--------|
| Story Bank | STAR-format behavioral interview stories with question association | ✅ Live |
| Question Bank | Shared pool of behavioral interview questions, searchable by tag or keyword | ✅ Live |

All apps share:
- Firebase Authentication (email/password) with in-app registration
- Firestore database (per-user data isolation enforced at the service layer)
- Inter font + consistent design system (dark sidebar, indigo primary color)
- Dark / light mode toggle in the sidebar (🌙 / ☀️)

---

## Setup & Deployment

### Prerequisites

- Python 3.11+
- A Firebase project with:
  - **Firestore** database enabled (Native mode)
  - **Authentication** → Email/Password sign-in method enabled
  - A **service account** key (IAM & Admin → Service Accounts → Create Key → JSON)
  - The project's **Web API Key** (Project Settings → General)

Install dependencies:

```bash
pip install -r requirements.txt
```

### Firebase Configuration

You need two credentials:

| Secret | Where to find it |
|--------|-----------------|
| `credentials_json` | Full contents of the service account JSON file |
| `web_api_key` | Firebase console → Project Settings → General → Web API Key |

**Never commit these values.** They go in `.streamlit/secrets.toml` locally, and in the Streamlit Cloud secrets dashboard for production.

### Local Development

1. Copy the secrets template:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and fill in your Firebase credentials.
   > **Important:** use triple single-quotes (`'''`) for `credentials_json` — regular single quotes break TOML parsing for multi-line strings.
   ```toml
   [firebase]
   credentials_json = '''{
     "type": "service_account",
     "project_id": "YOUR_PROJECT_ID",
     ...
   }'''
   web_api_key = "AIzaSy..."
   ```

3. Run the app:
   ```bash
   streamlit run main.py
   ```

4. Open `http://localhost:8501` — you'll be redirected to the login page. Register a new account to get started.

### Deploying to Streamlit Community Cloud

1. Push this repository to GitHub (`.streamlit/secrets.toml` is gitignored — credentials never leave your machine).

2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub repo, and set the main file to `main.py`.

3. In the app's **Settings → Secrets**, paste the same `[firebase]` block you have locally (triple single-quotes included):
   ```toml
   [firebase]
   credentials_json = '''{
     "type": "service_account",
     ...
   }'''
   web_api_key = "AIzaSy..."
   ```

4. Deploy. The app reads from `st.secrets` in both environments — no `.env` file or environment variables needed.

---

## Apps

### Story Bank

**What it does:** A searchable, tag-filtered bank of behavioral interview stories in STAR format. Each story can be linked to one or more behavioral interview questions from the shared Question Bank. Before an interview, pull up your relevant stories by tag or question and refresh your memory.

**How to use it:**

1. **Add a story** — Click "➕ Add Story". Fill in the title, all four STAR fields, optional company/location, and tags.
2. **Link questions** — Below the story form, type to search the Question Bank and select which behavioral questions this story answers. You can also create a new question inline and it will be immediately selected.
3. **Browse stories** — The main list shows all stories sorted newest-first. Expand any story to see the full STAR breakdown and its linked questions.
4. **Search** — The search box matches against title, situation, task, action, result, company, and location. Case-insensitive substring match. Wildcards: `*` = any sequence, `_` = any single character (e.g. `lead*design`, `manag_r`).
5. **Filter by tag** — The tag multiselect below the search box narrows results; combines with keyword search.
6. **Sort** — Toggle "Newest first" / "Oldest first" via the sort dropdown.
7. **Custom tags** — Tags typed in the "Add new tags" field are saved and available in future stories automatically.
8. **Edit / Delete** — Each expanded story card has Edit and Delete buttons. Deletion requires confirmation.

**STAR Method:**

| Field | Prompt |
|-------|--------|
| **S**ituation | Where were you? What was the context or challenge? |
| **T**ask | What was your specific responsibility or goal? |
| **A**ction | What steps did **you** take? Be specific about your individual contributions. |
| **R**esult | What was the outcome? Quantify where possible (%, $, time saved). |

**Default tags:**
`Conflict Resolution`, `Cross-team Collaboration`, `Customer Focus`, `Delivering Under Pressure`, `Handling Failure`, `Influencing Without Authority`, `Leading System Design`, `Mentoring`, `Navigating Ambiguity`, `Process Improvement`, `Stakeholder Management`, `Technical Leadership`, `Trouble with Manager`

---

### Question Bank

**What it does:** A shared pool of behavioral interview questions (e.g. "Tell me about a time you…") that all users draw from. Questions are tagged and fully searchable. Any story can be linked to one or more questions.

**How to use it:**

1. **Open the Question Bank** — Click "❓ Questions" in the Story Bank header.
2. **Search questions** — Type in the keyword search box; the list filters instantly.
3. **Filter by tag** — Use the tag multiselect to narrow by theme.
4. **Add a question** — Click "➕ Add", fill in the question text, then use the tag search field to find and select existing tags. Type in "Create new tags" to add tags that don't exist yet.
5. **Edit a question** — Expand a question card and click Edit. The inline editor has its own live tag search.
6. **Delete a question** — Expand a question card, click Delete, and confirm.

**Note:** Questions are global — they are shared across all users of the app, not per-account. This reflects the nature of behavioral questions (they are universal, not personal).

---

## Firestore Collections

### `stories` (per-user)

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Firebase Auth UID — enforces per-user isolation |
| `title` | string | Story title |
| `situation` | string | S in STAR |
| `task` | string | T in STAR |
| `action` | string | A in STAR |
| `result` | string | R in STAR |
| `tags` | array | Tag labels |
| `question_ids` | array | IDs of linked questions from the Question Bank |
| `company` | string? | Company where the event occurred |
| `location` | string? | Geographic location |
| `created_at` | timestamp | Auto-set on creation |
| `updated_at` | timestamp | Auto-updated on edit |

### `questions` (global, shared)

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | The behavioral interview question |
| `tags` | array | Tag labels (same vocabulary as story tags) |
| `created_by` | string | UID of the user who created the question |
| `created_at` | timestamp | Auto-set on creation |
| `updated_at` | timestamp | Auto-updated on edit |

### `users` (per-user)

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | User's email |
| `display_name` | string? | Display name shown in the sidebar |
| `created_at` | timestamp | Account creation time |
| `updated_at` | timestamp | Last profile update |

---

## Adding a New App

Adding a new app to the suite requires exactly 5 steps and no changes to existing shared infrastructure:

**Step 1** — Create the app package:
```
new_app/
├── __init__.py
├── models.py        # Pydantic models (YourCreate, YourUpdate, Your)
├── repository.py    # Firestore CRUD — YourRepository(db)
├── service.py       # YourService(user_id) — scoped to one user
└── pages/
    ├── __init__.py
    ├── list.py      # render(user, svc) function
    ├── add.py
    └── edit.py
```

**Step 2** — Add a Streamlit page:
```python
# pages/N_New_App.py
import streamlit as st
st.set_page_config(page_title="New App — Career Suite", page_icon="...", layout="wide")

from shared.auth.guard import require_auth
from shared.ui.nav import render_sidebar
from shared.ui.styles import inject_global_css
from new_app.pages import list_view, add_view, edit_view
from new_app.service import NewService

inject_global_css()
user = require_auth()
render_sidebar(user)

svc = NewService(user.uid)
view = st.session_state.get("new_app_view", "list")
# route to correct view...
```

**Step 3** — Add a Firestore collection: No action required — Firestore creates collections on first write.

**Step 4** — Register the nav link in `shared/ui/nav.py`:
```python
_NAV_ITEMS = [
    ("📖", "Story Bank", "pages/2_Story_Bank.py"),
    ("🆕", "New App",    "pages/N_New_App.py"),   # add this line
    ("⚙️", "Settings",  "pages/3_Settings.py"),
]
```

**Step 5** — Add a section to this README under `## Apps`.

---

## Development Notes

**Project structure:**
```
career_applications/
├── main.py                  # Entry point — redirects to login or story bank
├── pages/                   # Streamlit multi-page routing
│   ├── 1_Login.py           # Sign in + register
│   ├── 2_Story_Bank.py      # Story bank hub + question bank routing
│   └── 3_Settings.py        # Account settings
├── shared/                  # Shared infrastructure — imported by all apps
│   ├── auth/                # Firebase Auth service, session guard, models
│   ├── db/                  # Firestore client singleton
│   ├── ui/                  # Styles (CSS + dark/light tokens), components, nav
│   └── config.py            # Settings (reads st.secrets → env vars → .env)
├── questions/               # Global question bank module
│   ├── models.py            # Question, QuestionCreate, QuestionUpdate
│   ├── repository.py        # Firestore CRUD (global `questions` collection)
│   └── service.py           # QuestionService — search, CRUD, tag aggregation
├── story_bank/              # Story bank app package
│   ├── models.py            # Pydantic models — Story carries question_ids
│   ├── repository.py        # Firestore CRUD
│   ├── service.py           # Business logic scoped to user_id
│   └── pages/               # list_stories, add_story, edit_story, questions_page
└── .streamlit/
    ├── config.toml          # Theme (base = "light", primaryColor = indigo)
    └── secrets.toml         # Local secrets (gitignored)
```

**Key design rules:**
- `questions/` is global — `QuestionService` is not user-scoped for reads (all users share one pool)
- `XxxService(user_id)` for per-user services — cross-user access is a construction-time error
- Session state staging key pattern (`*_pending`) used when a widget key must be updated after the widget has already rendered in a given script run
- `SessionUser` in `st.session_state` — never contains a password or hash
- `require_auth()` at the top of every protected page; `inject_global_css()` at the top of every page
- Dark/light mode driven by `st.session_state["dark_mode"]` — `inject_global_css()` injects the correct `:root` token block on every render; toggled via sidebar button
- `README.md` updated after every code change
