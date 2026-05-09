import streamlit as st

from shared.auth.models import SessionUser

SESSION_KEY = "session_user"


def require_auth() -> SessionUser:
    """
    Call at the top of every protected page.
    Redirects to login if the user is not authenticated, halting page rendering.
    """
    user: SessionUser | None = st.session_state.get(SESSION_KEY)
    if user is None:
        st.switch_page("pages/1_Login.py")
        st.stop()
    return user


def set_session_user(user: SessionUser) -> None:
    st.session_state[SESSION_KEY] = user


def clear_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def get_session_user() -> SessionUser | None:
    return st.session_state.get(SESSION_KEY)
