import streamlit as st

st.set_page_config(
    page_title="Story Bank — Career Suite",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from shared.auth.guard import require_auth
from shared.ui.nav import render_sidebar
from shared.ui.styles import inject_global_css
from story_bank.pages import add_story, edit_story, list_stories
from story_bank.service import StoryService

inject_global_css()

user = require_auth()
render_sidebar(user)

svc = StoryService(user.uid)

view = st.session_state.get("story_bank_view", "list")

if view == "add":
    add_story.render(user, svc)
elif view == "edit":
    story_id = st.session_state.get("editing_story_id")
    edit_story.render(user, svc, story_id)
else:
    list_stories.render(user, svc)
