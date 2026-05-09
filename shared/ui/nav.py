import streamlit as st

from shared.auth.guard import clear_session
from shared.auth.models import SessionUser

_NAV_ITEMS = [
    ("📖", "Story Bank", "pages/2_Story_Bank.py"),
    ("⚙️", "Settings", "pages/3_Settings.py"),
]

_NAV_CSS = """
<style>
.nav-app-name {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
}
.nav-tagline {
    font-size: 12px;
    color: #A5B4FC;
    margin: 0 0 24px 0;
}
.nav-user-section {
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 20px;
}
.nav-user-name {
    font-size: 14px;
    font-weight: 600;
    color: #FFFFFF;
    margin: 0;
}
.nav-user-email {
    font-size: 12px;
    color: #A5B4FC;
    margin: 0;
}
.nav-section-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #818CF8;
    margin: 16px 0 4px 0;
}

/* Style st.page_link items in sidebar */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] span {
    color: #C7D2FE !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-decoration: none !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover a,
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover span {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] {
    border-radius: 8px !important;
    padding: 2px 0 !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    background: rgba(255,255,255,0.08) !important;
}

/* Logout link style */
.nav-logout-link {
    display: block;
    padding: 8px 12px;
    border-radius: 8px;
    color: #F87171 !important;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    margin-top: 4px;
    transition: background 0.15s;
    text-decoration: none;
}
.nav-logout-link:hover {
    background: rgba(248,113,113,0.12);
}
</style>
"""


def render_sidebar(user: SessionUser) -> None:
    st.sidebar.markdown(_NAV_CSS, unsafe_allow_html=True)

    # App branding
    st.sidebar.markdown(
        '<p class="nav-app-name">Career Suite</p>'
        '<p class="nav-tagline">Your career, organized.</p>',
        unsafe_allow_html=True,
    )

    # User info
    display = user.display_name or user.email.split("@")[0]
    st.sidebar.markdown(
        f'<div class="nav-user-section">'
        f'<p class="nav-user-name">{display}</p>'
        f'<p class="nav-user-email">{user.email}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Navigation links — st.page_link renders as proper anchor tags, not buttons
    st.sidebar.markdown('<p class="nav-section-label">Apps</p>', unsafe_allow_html=True)
    for icon, label, page in _NAV_ITEMS:
        st.sidebar.page_link(page, label=label, icon=icon)

    # Logout (needs session action so stays as a button, styled minimally)
    st.sidebar.markdown("---")
    if st.sidebar.button("Sign Out", key="nav_logout", use_container_width=False):
        clear_session()
        st.switch_page("pages/1_Login.py")
