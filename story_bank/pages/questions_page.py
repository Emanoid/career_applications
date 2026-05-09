import streamlit as st

from questions.models import QuestionCreate, QuestionUpdate
from questions.service import QuestionService
from shared.auth.models import SessionUser
from shared.ui.components import empty_state, page_header, tags_row

_ADD_KEYS = ["add_q_text", "add_q_tag_search", "add_q_selected_tags", "add_q_new_tag"]


def _filtered_options(available: list[str], search: str, already_selected: list[str]) -> list[str]:
    """Return tags matching search, always including already-selected items."""
    matched = [t for t in available if not search or search.lower() in t.lower()]
    return sorted(set(matched) | set(already_selected))


def render(user: SessionUser, q_svc: QuestionService) -> None:
    col_back, _ = st.columns([1, 8])
    with col_back:
        if st.button("← Back", key="qbank_back", type="secondary"):
            st.session_state["story_bank_view"] = "list"
            st.rerun()

    page_header("Question Bank", subtitle="Behavioral interview questions, searchable and taggable.")

    available_tags = q_svc.get_available_tags()

    # ── Search + tag filter + add button ────────────────────────────────────
    col_search, col_tags_filter, col_add_btn = st.columns([3, 3, 1])
    with col_search:
        search_text = st.text_input(
            "Search questions",
            placeholder="Search by keyword…",
            label_visibility="collapsed",
        )
    with col_tags_filter:
        tag_filter = st.multiselect(
            "Filter by tags",
            options=available_tags,
            placeholder="Filter by tags…",
            label_visibility="collapsed",
        )
    with col_add_btn:
        if st.button("➕ Add", key="toggle_add_q", use_container_width=True):
            st.session_state["show_add_q"] = not st.session_state.get("show_add_q", False)
            if not st.session_state["show_add_q"]:
                for k in _ADD_KEYS:
                    st.session_state.pop(k, None)
            st.rerun()

    # ── Add question panel (no form — live tag search needs free reruns) ─────
    if st.session_state.get("show_add_q", False):
        with st.container(border=True):
            st.markdown("##### New Question")

            q_text = st.text_area(
                "Question *",
                placeholder="e.g., Tell me about a time you had to deliver under pressure.",
                height=80,
                key="add_q_text",
            )

            st.caption("Tags — type below to search, then select")
            add_tag_search = st.text_input(
                "Search tags",
                placeholder="Type to filter tags…",
                label_visibility="collapsed",
                key="add_q_tag_search",
            )
            current_add_sel = st.session_state.get("add_q_selected_tags", [])
            add_options = _filtered_options(available_tags, add_tag_search, current_add_sel)
            st.multiselect(
                "Select tags",
                options=add_options,
                placeholder="Select from filtered list…",
                label_visibility="collapsed",
                key="add_q_selected_tags",
            )
            st.text_input(
                "Create new tags (comma-separated)",
                placeholder="e.g., Ownership, Resilience",
                key="add_q_new_tag",
            )

            col_save, col_cancel, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button("Save Question", key="save_add_q", use_container_width=True):
                    text_val = st.session_state.get("add_q_text", "").strip()
                    extra = [t.strip() for t in st.session_state.get("add_q_new_tag", "").split(",") if t.strip()]
                    all_tags = sorted(set(st.session_state.get("add_q_selected_tags", [])) | set(extra))
                    if not text_val:
                        st.error("Question text is required.")
                    else:
                        q_svc.create(QuestionCreate(text=text_val, tags=all_tags))
                        for k in _ADD_KEYS:
                            st.session_state.pop(k, None)
                        st.session_state["show_add_q"] = False
                        st.rerun()
            with col_cancel:
                if st.button("Cancel", key="cancel_add_q", type="secondary", use_container_width=True):
                    for k in _ADD_KEYS:
                        st.session_state.pop(k, None)
                    st.session_state["show_add_q"] = False
                    st.rerun()

    st.markdown("---")

    # ── Question list ────────────────────────────────────────────────────────
    questions = q_svc.get_all(
        tag_filters=tag_filter if tag_filter else None,
        search_text=search_text if search_text.strip() else None,
    )

    count_label = f"{len(questions)} {'question' if len(questions) == 1 else 'questions'}"
    st.markdown(
        f"<p style='font-size:13px;color:var(--color-text-muted);margin:8px 0 12px'>{count_label}</p>",
        unsafe_allow_html=True,
    )

    if not questions:
        if search_text.strip() or tag_filter:
            empty_state("No questions match your search.", icon="🔍")
        else:
            empty_state(
                "No questions yet. Hit '➕ Add' to create your first one.",
                icon="❓",
            )
        return

    for q in questions:
        with st.expander(q.text[:120] + ("…" if len(q.text) > 120 else ""), expanded=False):
            st.markdown(
                f"<p style='font-size:15px;line-height:1.6;color:var(--color-text)'>{q.text}</p>",
                unsafe_allow_html=True,
            )
            tags_row(q.tags)

            col_edit, col_delete, _ = st.columns([1, 1, 5])
            with col_edit:
                if st.button("Edit", key=f"qedit_{q.id}", use_container_width=True):
                    # Seed edit state
                    st.session_state[f"edit_q_text_{q.id}"] = q.text
                    st.session_state[f"edit_q_selected_tags_{q.id}"] = [t for t in q.tags if t in available_tags]
                    st.session_state[f"edit_q_new_tag_{q.id}"] = ", ".join(t for t in q.tags if t not in available_tags)
                    st.session_state[f"editing_q_{q.id}"] = True
                    st.rerun()
            with col_delete:
                if st.button("Delete", key=f"qdel_{q.id}", use_container_width=True, type="secondary"):
                    st.session_state[f"confirm_del_q_{q.id}"] = True
                    st.rerun()

            # ── Inline edit (no form — live tag search) ──────────────────────
            if st.session_state.get(f"editing_q_{q.id}"):
                edit_tags = q_svc.get_available_tags()
                with st.container(border=True):
                    st.text_area(
                        "Question text *",
                        height=80,
                        key=f"edit_q_text_{q.id}",
                    )
                    st.caption("Tags — type below to search, then select")
                    st.text_input(
                        "Search tags",
                        placeholder="Type to filter tags…",
                        label_visibility="collapsed",
                        key=f"edit_q_tag_search_{q.id}",
                    )
                    current_edit_sel = st.session_state.get(f"edit_q_selected_tags_{q.id}", [])
                    edit_options = _filtered_options(
                        edit_tags,
                        st.session_state.get(f"edit_q_tag_search_{q.id}", ""),
                        current_edit_sel,
                    )
                    st.multiselect(
                        "Select tags",
                        options=edit_options,
                        placeholder="Select from filtered list…",
                        label_visibility="collapsed",
                        key=f"edit_q_selected_tags_{q.id}",
                    )
                    st.text_input(
                        "Create new tags (comma-separated)",
                        placeholder="e.g., Ownership",
                        key=f"edit_q_new_tag_{q.id}",
                    )

                    col_save, col_cancel_edit, _ = st.columns([1, 1, 4])
                    with col_save:
                        if st.button("Save", key=f"save_edit_q_{q.id}", use_container_width=True):
                            new_text = st.session_state.get(f"edit_q_text_{q.id}", "").strip()
                            extra = [t.strip() for t in st.session_state.get(f"edit_q_new_tag_{q.id}", "").split(",") if t.strip()]
                            merged = sorted(set(st.session_state.get(f"edit_q_selected_tags_{q.id}", [])) | set(extra))
                            if not new_text:
                                st.error("Question text is required.")
                            else:
                                q_svc.update(q.id, QuestionUpdate(text=new_text, tags=merged))
                                for k in [f"editing_q_{q.id}", f"edit_q_text_{q.id}",
                                          f"edit_q_tag_search_{q.id}", f"edit_q_selected_tags_{q.id}",
                                          f"edit_q_new_tag_{q.id}"]:
                                    st.session_state.pop(k, None)
                                st.rerun()
                    with col_cancel_edit:
                        if st.button("Cancel", key=f"cancel_edit_q_{q.id}", type="secondary", use_container_width=True):
                            for k in [f"editing_q_{q.id}", f"edit_q_text_{q.id}",
                                      f"edit_q_tag_search_{q.id}", f"edit_q_selected_tags_{q.id}",
                                      f"edit_q_new_tag_{q.id}"]:
                                st.session_state.pop(k, None)
                            st.rerun()

            # ── Delete confirmation ──────────────────────────────────────────
            if st.session_state.get(f"confirm_del_q_{q.id}"):
                st.warning("Delete this question? This cannot be undone.")
                col_yes, col_no, _ = st.columns([1, 1, 5])
                with col_yes:
                    if st.button("Yes, delete", key=f"qyes_{q.id}", type="primary"):
                        q_svc.delete(q.id)
                        st.session_state.pop(f"confirm_del_q_{q.id}", None)
                        st.rerun()
                with col_no:
                    if st.button("Cancel", key=f"qno_{q.id}", type="secondary"):
                        st.session_state.pop(f"confirm_del_q_{q.id}", None)
                        st.rerun()
