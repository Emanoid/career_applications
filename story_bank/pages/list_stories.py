import streamlit as st

from shared.auth.models import SessionUser
from shared.ui.components import (
    empty_state,
    page_header,
    section_header,
    star_section,
    story_meta,
    tags_row,
)
from story_bank.service import StoryService


def render(user: SessionUser, svc: StoryService) -> None:
    page_header("Story Bank", subtitle="Your STAR-format stories, ready for any interview.")

    # ── Sidebar filters ──────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        section_header("Filter Stories")
        available_tags = svc.get_available_tags()
        selected_tags = st.multiselect(
            "Filter by tags",
            options=available_tags,
            placeholder="All tags",
            label_visibility="collapsed",
        )
        st.markdown("---")
        if st.button("➕  Add New Story", use_container_width=True, key="sb_add_btn"):
            st.session_state["story_bank_view"] = "add"
            st.rerun()

    # ── Story list ───────────────────────────────────────────────────────────
    stories = svc.get_all(tag_filters=selected_tags if selected_tags else None)

    if not stories:
        if selected_tags:
            empty_state("No stories match the selected tags.", icon="🔍")
        else:
            empty_state(
                "No stories yet. Click 'Add New Story' to create your first one.",
                icon="📖",
            )
        return

    count_label = f"{len(stories)} {'story' if len(stories) == 1 else 'stories'}"
    if selected_tags:
        count_label += f" matching {', '.join(selected_tags)}"
    st.markdown(
        f"<p style='font-size:13px;color:#6B7280;margin-bottom:16px'>{count_label}</p>",
        unsafe_allow_html=True,
    )

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
