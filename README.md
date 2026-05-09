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
4. [Adding a New App](#adding-a-new-app)
5. [Development Notes](#development-notes)

---

## Overview

| App | Description | Status |
|-----|-------------|--------|
| Story Bank | STAR-format behavioral interview stories | ✅ Live |

All apps share:
- Firebase Authentication (email/password) with in-app registration
- Firestore database (per-user data isolation enforced at the service layer)
- Inter font + consistent design system (dark sidebar, indigo primary color)

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

2. Edit `.streamlit/secrets.toml` and fill in your Firebase credentials:
   ```toml
   [firebase]
   credentials_json = '{"type":"service_account","project_id":"YOUR_PROJECT",...}'
   web_api_key = "AIzaSy..."
   ```

3. Run the app:
   ```bash
   streamlit run main.py
   ```

4. Open `http://localhost:8501` — you'll be redirected to the login page. Register a new account to get started.

### Deploying to Streamlit Community Cloud

1. Push this repository to GitHub (the `.streamlit/secrets.toml` is gitignored — your credentials stay local).

2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub repo, and set the main file to `main.py`.

3. In the app's **Settings → Secrets**, paste the same content you have in your local `secrets.toml`:
   ```toml
   [firebase]
   credentials_json = '{"type":"service_account",...}'
   web_api_key = "AIzaSy..."
   ```

4. Deploy. The app will be live at your assigned `share.streamlit.io` URL.

---

## Apps

### Story Bank

**What it does:** A searchable, tag-filtered bank of behavioral interview stories in STAR format. Before an interview, pull up your relevant stories by tag and refresh your memory — no more drawing blanks under pressure.

**How to use it:**

1. **Add a story** — Click "Add New Story" in the sidebar. Fill in the title, all four STAR fields, and any relevant tags. Add context (company, location) if helpful.
2. **Browse stories** — The main view lists all your stories newest-first. Each story expands to show the full STAR breakdown.
3. **Filter by tag** — Use the "Filter by tags" multiselect in the sidebar to narrow down stories by theme. Useful for interview prep ("show me all my Conflict Resolution stories").
4. **Custom tags** — Any tag you type in the "Add new tags" field is saved and will appear in the tag picker for future stories.
5. **Edit / Delete** — Each story has Edit and Delete buttons. Deletion requires a confirmation step.

**STAR Method:**
| Field | Prompt |
|-------|--------|
| **S**ituation | Where were you? What was the context or challenge? |
| **T**ask | What was your specific responsibility or goal? |
| **A**ction | What steps did **you** take? Be specific about your individual contributions. |
| **R**esult | What was the outcome? Quantify where possible (%, $, time saved). |

**Default tags:**
`Conflict Resolution`, `Cross-team Collaboration`, `Customer Focus`, `Delivering Under Pressure`, `Handling Failure`, `Influencing Without Authority`, `Leading System Design`, `Mentoring`, `Navigating Ambiguity`, `Process Improvement`, `Stakeholder Management`, `Technical Leadership`, `Trouble with Manager`

**Data stored in Firestore (`stories` collection):**

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Firebase Auth UID |
| `title` | string | Story title |
| `situation` | string | S in STAR |
| `task` | string | T in STAR |
| `action` | string | A in STAR |
| `result` | string | R in STAR |
| `tags` | array | Tag labels |
| `company` | string? | Company where event occurred |
| `location` | string? | Geographic location |
| `created_at` | timestamp | Auto-set on creation |
| `updated_at` | timestamp | Auto-updated on edit |

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

**Step 5** — Add a `### New App` section to this README under `## Apps`.

---

## Development Notes

**Project structure:**
```
career_applications/
├── main.py                  # Entry point — redirects to login or story bank
├── pages/                   # Streamlit multi-page routing
│   ├── 1_Login.py           # Sign in + register
│   ├── 2_Story_Bank.py      # Story bank hub
│   └── 3_Settings.py        # Account settings
├── shared/                  # Shared infrastructure — imported by all apps
│   ├── auth/                # Firebase Auth service, session guard, models
│   ├── db/                  # Firestore client singleton
│   ├── ui/                  # Styles (CSS), components, nav
│   └── config.py            # Settings (reads st.secrets → env vars → .env)
├── story_bank/              # Story bank app package
│   ├── models.py            # Pydantic models
│   ├── repository.py        # Firestore CRUD
│   ├── service.py           # Business logic (scoped to user_id)
│   └── pages/               # Streamlit view functions
└── .streamlit/
    ├── config.toml          # Streamlit theme
    └── secrets.toml         # Local secrets (gitignored)
```

**Key design rules:**
- Apps never import from each other — only from `shared/`
- `XxxService(user_id)` is always scoped to one user at construction time
- `SessionUser` stored in `st.session_state` — never contains a password or hash
- `require_auth()` called at the top of every protected page
- `inject_global_css()` called at the top of every page
- `README.md` updated after every code change
- All work on branch `feature/filing-reminders` — user manually merges to main
