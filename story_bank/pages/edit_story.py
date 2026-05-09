from typing import Optional

import streamlit as st

from shared.auth.models import SessionUser
from shared.ui.components import page_header
from story_bank.models import StoryUpdate
from story_bank.service import StoryService

_STAR_HINTS = {
    "situation": "Describe the context and challenge.",
    "task": "Your specific responsibility or goal.",
    "action": "Steps YOU took — be specific.",
    "result": "The outcome, quantified where possible.",
}


def render(user: SessionUser, svc: StoryService, story_id: Optional[str]) -> None:
    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← Back", key="edit_back", type="secondary"):
            st.session_state["story_bank_view"] = "list"
            st.session_state.pop("editing_story_id", None)
            st.rerun()

    if not story_id:
        st.error("No story selected for editing.")
        return

    story = svc.get(story_id)
    if story is None:
        st.error("Story not found.")
        return

    page_header(f"Edit: {story.title}")

    available_tags = svc.get_available_tags()

    with st.form("edit_story_form"):
        title = st.text_input("Story Title *", value=story.title)

        st.markdown("---")
        st.markdown("#### STAR Method")

        situation = st.text_area("Situation *", value=story.situation, height=100)
        task = st.text_area("Task *", value=story.task, height=80)
        action = st.text_area("Action *", value=story.action, height=120)
        result = st.text_area("Result *", value=story.result, height=100)

        st.markdown("---")
        st.markdown("#### Context & Tags")

        col_company, col_location = st.columns(2)
        with col_company:
            company = st.text_input("Company", value=story.company or "")
        with col_location:
            location = st.text_input("Location", value=story.location or "")

        current_tags = story.tags or []
        selected_tags = st.multiselect(
            "Tags",
            options=available_tags,
            default=[t for t in current_tags if t in available_tags],
        )
        preselected_custom = [t for t in current_tags if t not in available_tags]
        new_tags_raw = st.text_input(
            "Add new tags",
            value=", ".join(preselected_custom),
            placeholder="Comma-separated new tags",
            help="These tags will be saved and available in future stories.",
        )

        submitted = st.form_submit_button("Save Changes", use_container_width=True)

    if submitted:
        new_tags = [t.strip() for t in new_tags_raw.split(",") if t.strip()]
        all_tags = sorted(set(selected_tags) | set(new_tags))

        errors = []
        if not title.strip():
            errors.append("Title is required.")
        if not situation.strip():
            errors.append("Situation is required.")
        if not task.strip():
            errors.append("Task is required.")
        if not action.strip():
            errors.append("Action is required.")
        if not result.strip():
            errors.append("Result is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            update = StoryUpdate(
                title=title.strip(),
                situation=situation.strip(),
                task=task.strip(),
                action=action.strip(),
                result=result.strip(),
                tags=all_tags,
                company=company.strip() or None,
                location=location.strip() or None,
            )
            svc.update(story_id, update)
            st.success("Story updated!")
            st.session_state["story_bank_view"] = "list"
            st.session_state.pop("editing_story_id", None)
            st.rerun()
