import streamlit as st

from shared.auth.models import SessionUser
from shared.ui.components import page_header
from story_bank.models import StoryCreate
from story_bank.service import StoryService

_STAR_HINTS = {
    "situation": "Describe the context. Where were you? What was the challenge or opportunity?",
    "task": "What was your specific responsibility or goal in this situation?",
    "action": "What steps did YOU take? Be specific about your individual contributions.",
    "result": "What was the outcome? Quantify where possible (%, $, time saved, etc.).",
}


def render(user: SessionUser, svc: StoryService) -> None:
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Back", key="add_back", type="secondary"):
            st.session_state["story_bank_view"] = "list"
            st.rerun()

    page_header("New Story", subtitle="Document your experience using the STAR method.")

    available_tags = svc.get_available_tags()

    with st.form("add_story_form", clear_on_submit=True):
        title = st.text_input("Story Title *", placeholder="e.g., Led migration of monolith to microservices")

        st.markdown("---")
        st.markdown("#### STAR Method")

        situation = st.text_area(
            "Situation *",
            placeholder=_STAR_HINTS["situation"],
            height=100,
        )
        task = st.text_area(
            "Task *",
            placeholder=_STAR_HINTS["task"],
            height=80,
        )
        action = st.text_area(
            "Action *",
            placeholder=_STAR_HINTS["action"],
            height=120,
        )
        result = st.text_area(
            "Result *",
            placeholder=_STAR_HINTS["result"],
            height=100,
        )

        st.markdown("---")
        st.markdown("#### Context & Tags")

        col_company, col_location = st.columns(2)
        with col_company:
            company = st.text_input("Company", placeholder="e.g., Google")
        with col_location:
            location = st.text_input("Location", placeholder="e.g., New York / Remote")

        selected_tags = st.multiselect(
            "Tags",
            options=available_tags,
            placeholder="Select or search tags…",
        )
        new_tags_raw = st.text_input(
            "Add new tags",
            placeholder="Comma-separated, e.g.: Rapid Prototyping, Data Migration",
            help="These tags will be saved and available in future stories.",
        )

        submitted = st.form_submit_button("Save Story", use_container_width=True)

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
            data = StoryCreate(
                title=title.strip(),
                situation=situation.strip(),
                task=task.strip(),
                action=action.strip(),
                result=result.strip(),
                tags=all_tags,
                company=company.strip() or None,
                location=location.strip() or None,
            )
            svc.create(data)
            st.success("Story saved!")
            st.session_state["story_bank_view"] = "list"
            st.rerun()
