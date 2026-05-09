from typing import Optional

import streamlit as st

from questions.models import QuestionCreate
from questions.service import QuestionService
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


def _q_session_key(story_id: str) -> str:
    return f"edit_story_q_ids_{story_id}"

def _q_pending_key(story_id: str) -> str:
    return f"edit_story_q_ids_{story_id}_pending"


def render(user: SessionUser, svc: StoryService, q_svc: QuestionService, story_id: Optional[str]) -> None:
    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← Back", key="edit_back", type="secondary"):
            if story_id:
                st.session_state.pop(_q_session_key(story_id), None)
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

    q_key = _q_session_key(story_id)
    # Seed session state with existing question IDs on first load
    if q_key not in st.session_state:
        st.session_state[q_key] = story.question_ids or []

    page_header(f"Edit: {story.title}")

    available_tags = svc.get_available_tags()

    with st.form("edit_story_form", enter_to_submit=False):
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

    # ── Related questions (outside form so live search works) ────────────────
    st.markdown("---")
    st.markdown("#### Related Questions")
    st.caption("Type to search. Select questions that this story answers.")

    # Promote any pending ID additions before the widget renders
    pending = _q_pending_key(story_id)
    if pending in st.session_state:
        st.session_state[q_key] = st.session_state.pop(pending)

    all_questions = q_svc.get_all()
    q_map = {q.id: q.text for q in all_questions}

    st.multiselect(
        "Search & select questions",
        options=list(q_map.keys()),
        format_func=lambda qid: q_map.get(qid, qid),
        placeholder="Type to search behavioral questions…",
        label_visibility="collapsed",
        key=q_key,
    )

    with st.expander("➕ Create a new question and add it", expanded=False):
        available_q_tags = q_svc.get_available_tags()
        with st.form(f"add_q_inline_edit_{story_id}", clear_on_submit=True):
            new_q_text = st.text_area(
                "Question text *",
                placeholder="Tell me about a time you…",
                height=70,
            )
            new_q_tags = st.multiselect("Tags", options=available_q_tags, placeholder="Select tags…")
            new_q_extra_tags = st.text_input("Add new tags", placeholder="Comma-separated")
            create_q_submitted = st.form_submit_button("Create & Select", use_container_width=True)

        if create_q_submitted:
            extra = [t.strip() for t in new_q_extra_tags.split(",") if t.strip()]
            all_q_tags = sorted(set(new_q_tags) | set(extra))
            if not new_q_text.strip():
                st.error("Question text is required.")
            else:
                new_q = q_svc.create(QuestionCreate(text=new_q_text.strip(), tags=all_q_tags))
                current = list(st.session_state.get(q_key, []))
                if new_q.id not in current:
                    current.append(new_q.id)
                # Write to staging key — cannot set widget key after it has rendered
                st.session_state[_q_pending_key(story_id)] = current
                st.rerun()

    # ── Handle form submission ───────────────────────────────────────────────
    if submitted:
        new_tags = [t.strip() for t in new_tags_raw.split(",") if t.strip()]
        all_tags = sorted(set(selected_tags) | set(new_tags))
        question_ids = st.session_state.get(q_key, [])

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
                question_ids=question_ids,
            )
            svc.update(story_id, update)
            st.session_state.pop(q_key, None)
            st.success("Story updated!")
            st.session_state["story_bank_view"] = "list"
            st.session_state.pop("editing_story_id", None)
            st.rerun()
