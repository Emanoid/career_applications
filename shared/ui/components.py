import html
from typing import Optional

import streamlit as st


def page_header(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(
        f"<h1 style='font-size:28px;font-weight:700;margin-bottom:4px'>{html.escape(title)}</h1>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f"<p style='font-size:15px;color:var(--color-text-muted);margin-top:0;margin-bottom:20px'>"
            f"{html.escape(subtitle)}</p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='margin:0 0 24px 0'>", unsafe_allow_html=True)


def tag_badge(label: str, variant: str = "primary") -> str:
    css_class = "tag-badge-primary" if variant == "primary" else "tag-badge-muted"
    return f'<span class="tag-badge {css_class}">{html.escape(label)}</span>'


def tags_row(tags: list[str]) -> None:
    if not tags:
        return
    badges = "".join(tag_badge(t) for t in tags)
    st.markdown(f'<div style="margin:8px 0">{badges}</div>', unsafe_allow_html=True)


def star_section(label: str, content: str) -> None:
    st.markdown(
        f'<div class="star-section"><div class="star-label">{html.escape(label)}</div>'
        f'<div class="star-content">{html.escape(content)}</div></div>',
        unsafe_allow_html=True,
    )


def story_meta(company: Optional[str], location: Optional[str], updated_at) -> None:
    parts = []
    if company:
        parts.append(f"<span>🏢 {html.escape(company)}</span>")
    if location:
        parts.append(f"<span>📍 {html.escape(location)}</span>")
    if updated_at:
        date_str = updated_at.strftime("%b %d, %Y") if hasattr(updated_at, "strftime") else str(updated_at)
        parts.append(f"<span>🕐 {date_str}</span>")
    if parts:
        st.markdown(
            f'<div class="story-meta">{"".join(parts)}</div>',
            unsafe_allow_html=True,
        )


def empty_state(message: str, icon: str = "📭") -> None:
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-icon">{icon}</div>'
        f"<p>{message}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


def section_header(text: str) -> None:
    st.markdown(
        f"<h2 style='font-size:18px;font-weight:600;color:var(--color-text);margin:20px 0 12px 0'>{text}</h2>",
        unsafe_allow_html=True,
    )
