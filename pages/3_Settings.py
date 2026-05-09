import streamlit as st

st.set_page_config(
    page_title="Settings — Career Suite",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from shared.auth.guard import require_auth, set_session_user
from shared.auth.models import SessionUser
from shared.auth.service import AuthService
from shared.ui.components import page_header, section_header
from shared.ui.nav import render_sidebar
from shared.ui.styles import inject_global_css

inject_global_css()

user = require_auth()
render_sidebar(user)

page_header("Settings", subtitle="Manage your account.")

svc = AuthService()

section_header("Profile")

with st.form("update_profile_form", enter_to_submit=False):
    new_display_name = st.text_input(
        "Display Name",
        value=user.display_name or "",
        placeholder="Your name as shown in the app",
    )
    submitted = st.form_submit_button("Save", use_container_width=False)

if submitted:
    if new_display_name.strip():
        svc.update_display_name(user.uid, new_display_name.strip())
        updated_user = SessionUser(
            uid=user.uid,
            email=user.email,
            display_name=new_display_name.strip(),
            id_token=user.id_token,
        )
        set_session_user(updated_user)
        st.success("Display name updated.")
        st.rerun()
    else:
        st.error("Display name cannot be empty.")

st.markdown("---")
st.markdown(
    f"<p style='font-size:13px;color:#6B7280'>Signed in as <strong>{user.email}</strong></p>",
    unsafe_allow_html=True,
)
