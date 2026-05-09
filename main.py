import streamlit as st

st.set_page_config(
    page_title="Career Suite",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from shared.auth.guard import SESSION_KEY

if st.session_state.get(SESSION_KEY):
    st.switch_page("pages/2_Story_Bank.py")
else:
    st.switch_page("pages/1_Login.py")
