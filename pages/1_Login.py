import streamlit as st

st.set_page_config(
    page_title="Sign In — Career Suite",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from shared.auth.guard import SESSION_KEY, set_session_user
from shared.auth.models import RegisterRequest
from shared.auth.service import AuthService
from shared.ui.styles import inject_global_css

inject_global_css()

# Redirect if already logged in
if st.session_state.get(SESSION_KEY):
    st.switch_page("pages/2_Story_Bank.py")

# ── Page layout ──────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;padding:40px 0 20px'>"
    "<h1 style='font-size:32px;font-weight:700;margin-bottom:6px'>Career Suite</h1>"
    "<p style='color:#6B7280;font-size:15px'>Track stories. Ace interviews. Own your career.</p>"
    "</div>",
    unsafe_allow_html=True,
)

tab_signin, tab_register = st.tabs(["Sign In", "Create Account"])

svc = AuthService()

# ── Sign In tab ───────────────────────────────────────────────────────────────
with tab_signin:
    with st.form("signin_form"):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please enter your email and password.")
        else:
            with st.spinner("Signing in…"):
                result = svc.login(email.strip(), password)
            if result.success:
                set_session_user(result.user)
                st.switch_page("pages/2_Story_Bank.py")
            else:
                st.error(result.error)

# ── Register tab ──────────────────────────────────────────────────────────────
with tab_register:
    with st.form("register_form"):
        reg_display_name = st.text_input("Display Name", placeholder="Jane Smith")
        reg_email = st.text_input("Email address", placeholder="you@example.com", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pw",
                                     help="Minimum 6 characters")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pw2")
        reg_submitted = st.form_submit_button("Create Account", use_container_width=True)

    if reg_submitted:
        errors = []
        if not reg_email:
            errors.append("Email is required.")
        if not reg_password:
            errors.append("Password is required.")
        elif len(reg_password) < 6:
            errors.append("Password must be at least 6 characters.")
        elif reg_password != reg_password_confirm:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            with st.spinner("Creating your account…"):
                req = RegisterRequest(
                    email=reg_email.strip(),
                    password=reg_password,
                    display_name=reg_display_name.strip() or None,
                )
                result = svc.register(req)
            if result.success:
                set_session_user(result.user)
                st.success("Account created! Redirecting…")
                st.switch_page("pages/2_Story_Bank.py")
            else:
                st.error(result.error)
