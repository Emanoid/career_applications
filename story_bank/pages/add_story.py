import streamlit as st

from questions.models import QuestionCreate
from questions.service import QuestionService
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

_Q_SESSION_KEY = "add_story_q_ids"
_Q_PENDING_KEY = "add_story_q_ids_pending"


def render(user: SessionUser, svc: StoryService, q_svc: QuestionService) -> None:
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Back", key="add_back", type="secondary"):
            st.session_state.pop(_Q_SESSION_KEY, None)
            st.session_state["story_bank_view"] = "list"
            st.rerun()

    page_header("New Story", subtitle="Document your experience using the STAR method.")

    available_tags = svc.get_available_tags()

    with st.form("add_story_form", clear_on_submit=True, enter_to_submit=False):
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

    # ── Related questions (outside form so live search works) ────────────────
    st.markdown("---")
    st.markdown("#### Related Questions")
    st.caption("Type to search. Select questions that this story answers.")

    # Promote any pending ID additions before the widget renders
    if _Q_PENDING_KEY in st.session_state:
        st.session_state[_Q_SESSION_KEY] = st.session_state.pop(_Q_PENDING_KEY)

    all_questions = q_svc.get_all()
    q_map = {q.id: q.text for q in all_questions}

    selected_q_ids = st.multiselect(
        "Search & select questions",
        options=list(q_map.keys()),
        default=st.session_state.get(_Q_SESSION_KEY, []),
        format_func=lambda qid: q_map.get(qid, qid),
        placeholder="Type to search behavioral questions…",
        label_visibility="collapsed",
        key=_Q_SESSION_KEY,
    )

    with st.expander("➕ Create a new question and add it", expanded=False):
        available_q_tags = q_svc.get_available_tags()
        with st.form("add_q_inline_form", clear_on_submit=True):
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
                current = list(st.session_state.get(_Q_SESSION_KEY, []))
                if new_q.id not in current:
                    current.append(new_q.id)
                # Write to staging key — cannot set widget key after it has rendered
                st.session_state[_Q_PENDING_KEY] = current
                st.rerun()

    # ── Handle form submission ───────────────────────────────────────────────
    if submitted:
        new_tags = [t.strip() for t in new_tags_raw.split(",") if t.strip()]
        all_tags = sorted(set(selected_tags) | set(new_tags))
        question_ids = st.session_state.get(_Q_SESSION_KEY, [])

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
                question_ids=question_ids,
            )
            svc.create(data)
            st.session_state.pop(_Q_SESSION_KEY, None)
            st.success("Story saved!")
            st.session_state["story_bank_view"] = "list"
            st.rerun()
