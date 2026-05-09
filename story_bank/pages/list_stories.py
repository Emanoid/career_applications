import streamlit as st

from questions.service import QuestionService
from shared.auth.models import SessionUser
from shared.ui.components import (
    empty_state,
    page_header,
    star_section,
    story_meta,
    tags_row,
)
from story_bank.service import StoryService

_SORT_OPTIONS = {
    "Newest first": True,
    "Oldest first": False,
}


def render(user: SessionUser, svc: StoryService, q_svc: QuestionService) -> None:
    # ── Header row: title + action buttons ──────────────────────────────────
    col_title, col_qbank, col_add = st.columns([5, 1, 1])
    with col_title:
        page_header("Story Bank", subtitle="Your STAR-format stories, ready for any interview.")
    with col_qbank:
        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
        if st.button("❓ Questions", key="sb_qbank_btn", use_container_width=True, type="secondary"):
            st.session_state["story_bank_view"] = "questions"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_add:
        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
        if st.button("➕ Add Story", key="sb_add_btn", use_container_width=True):
            st.session_state["story_bank_view"] = "add"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Search + sort row ────────────────────────────────────────────────────
    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search_text = st.text_input(
            "Search",
            placeholder="Search title, situation, action, result…",
            label_visibility="collapsed",
        )
    with col_sort:
        sort_label = st.selectbox(
            "Sort",
            options=list(_SORT_OPTIONS.keys()),
            label_visibility="collapsed",
        )

    # ── Tag filter ───────────────────────────────────────────────────────────
    available_tags = svc.get_available_tags()
    selected_tags = st.multiselect(
        "Filter by tags",
        options=available_tags,
        placeholder="Filter by tags — select one or more…",
        label_visibility="collapsed",
    )

    # ── Story list ───────────────────────────────────────────────────────────
    newest_first = _SORT_OPTIONS[sort_label]
    stories = svc.get_all(
        tag_filters=selected_tags if selected_tags else None,
        search_text=search_text if search_text.strip() else None,
        newest_first=newest_first,
    )

    if not stories:
        if search_text.strip() or selected_tags:
            empty_state("No stories match your search.", icon="🔍")
        else:
            empty_state(
                "No stories yet. Hit '➕ Add Story' to create your first one.",
                icon="📖",
            )
        return

    parts = [f"{len(stories)} {'story' if len(stories) == 1 else 'stories'}"]
    if search_text.strip():
        parts.append(f'matching "{search_text.strip()}"')
    if selected_tags:
        parts.append(f"tagged: {', '.join(selected_tags)}")
    st.markdown(
        f"<p style='font-size:13px;color:var(--color-text-muted);margin:8px 0 12px'>{' · '.join(parts)}</p>",
        unsafe_allow_html=True,
    )

    # Pre-fetch all questions in one pass to avoid N×M reads
    all_q_ids = list({qid for s in stories for qid in (s.question_ids or [])})
    q_by_id = {q.id: q for q in q_svc.get_by_ids(all_q_ids)} if all_q_ids else {}

    for story in stories:
        with st.expander(story.title, expanded=False):
            story_meta(story.company, story.location, story.updated_at)
            tags_row(story.tags)
            st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
            star_section("S — Situation", story.situation)
            star_section("T — Task", story.task)
            star_section("A — Action", story.action)
            star_section("R — Result", story.result)
            st.markdown("</div>", unsafe_allow_html=True)

            # Related questions
            story_questions = [q_by_id[qid] for qid in (story.question_ids or []) if qid in q_by_id]
            if story_questions:
                st.markdown('<p class="related-q-label">Related Questions</p>', unsafe_allow_html=True)
                for q in story_questions:
                    tag_badges = "".join(
                        f'<span class="related-q-tag">{t}</span>' for t in q.tags
                    )
                    st.markdown(
                        f'<p class="related-q-item">'
                        f'<span class="related-q-bullet">•</span>{q.text}{tag_badges}</p>',
                        unsafe_allow_html=True,
                    )

            col_edit, col_delete, col_spacer = st.columns([1, 1, 5])
            with col_edit:
                if st.button("Edit", key=f"edit_{story.id}", use_container_width=True):
                    st.session_state["story_bank_view"] = "edit"
                    st.session_state["editing_story_id"] = story.id
                    st.rerun()
            with col_delete:
                if st.button("Delete", key=f"del_{story.id}", use_container_width=True, type="secondary"):
                    st.session_state[f"confirm_delete_{story.id}"] = True
                    st.rerun()

            if st.session_state.get(f"confirm_delete_{story.id}"):
                st.warning(f"Delete **{story.title}**? This cannot be undone.")
                col_yes, col_no, _ = st.columns([1, 1, 5])
                with col_yes:
                    if st.button("Yes, delete", key=f"yes_{story.id}", type="primary"):
                        svc.delete(story.id)
                        del st.session_state[f"confirm_delete_{story.id}"]
                        st.rerun()
                with col_no:
                    if st.button("Cancel", key=f"no_{story.id}", type="secondary"):
                        del st.session_state[f"confirm_delete_{story.id}"]
                        st.rerun()
