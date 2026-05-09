import streamlit as st

_TOKENS_LIGHT = """
:root {
    --font-body: 'Inter', sans-serif;
    --radius: 8px;
    --radius-lg: 12px;
    --color-primary: #4F46E5;
    --color-primary-hover: #4338CA;
    --color-primary-light: #EEF2FF;
    --color-primary-light-text: #4338CA;
    --color-bg: #FFFFFF;
    --color-surface: #F9FAFB;
    --color-card-bg: #FFFFFF;
    --color-border: #E5E7EB;
    --color-text: #111827;
    --color-text-muted: #6B7280;
    --color-badge-muted-bg: #F3F4F6;
    --color-badge-muted-text: #6B7280;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.10), 0 2px 4px -2px rgba(0,0,0,0.05);
}
"""

_TOKENS_DARK = """
:root {
    --font-body: 'Inter', sans-serif;
    --radius: 8px;
    --radius-lg: 12px;
    --color-primary: #4F46E5;
    --color-primary-hover: #6366F1;
    --color-primary-light: rgba(99, 102, 241, 0.20);
    --color-primary-light-text: #A5B4FC;
    --color-bg: #0E1117;
    --color-surface: #262730;
    --color-card-bg: #1A1C24;
    --color-border: #374151;
    --color-text: #F9FAFB;
    --color-text-muted: #9CA3AF;
    --color-badge-muted-bg: #1F2937;
    --color-badge-muted-text: #9CA3AF;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.30), 0 1px 2px rgba(0,0,0,0.20);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.40), 0 2px 4px -2px rgba(0,0,0,0.20);
}
"""

_STRUCTURAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Global font & background ── */
html, body, [class*="css"], .stApp {
    font-family: var(--font-body) !important;
    background-color: var(--color-bg) !important;
}

/* ── Top toolbar / header bar ── */
[data-testid="stHeader"],
header[data-testid="stHeader"] {
    background-color: var(--color-bg) !important;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    background-color: var(--color-bg) !important;
}

/* ── Main content text (scoped to stMain to protect sidebar) ── */
[data-testid="stMain"] p,
[data-testid="stMain"] li,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] span {
    color: var(--color-text) !important;
}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {
    color: var(--color-text) !important;
}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {
    color: var(--color-text-muted) !important;
}

/* ── Hide auto-generated Streamlit sidebar nav ── */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Sidebar (always dark indigo regardless of theme) ── */
[data-testid="stSidebar"] {
    background-color: #1E1B4B !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #C7D2FE !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

/* ── Buttons — cover all Streamlit variants (kind attr + legacy class) ── */
.stButton > button,
[data-testid="stFormSubmitButton"] button,
button[kind="primary"],
button[kind="primaryFormSubmit"] {
    background-color: var(--color-primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: background-color 0.15s ease, transform 0.1s ease !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover {
    background-color: var(--color-primary-hover) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"],
button[kind="secondary"],
button[kind="secondaryFormSubmit"] {
    background-color: transparent !important;
    color: var(--color-text) !important;
    border: 1px solid var(--color-border) !important;
}
.stButton > button[kind="secondary"]:hover,
button[kind="secondary"]:hover,
button[kind="secondaryFormSubmit"]:hover {
    background-color: var(--color-surface) !important;
    transform: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--color-border) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--color-text-muted) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background-color: var(--color-surface) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius) !important;
    color: var(--color-text) !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background-color: var(--color-surface) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--color-border) !important;
    color: var(--color-text) !important;
}
[data-baseweb="tag"] {
    background-color: var(--color-primary-light) !important;
    color: var(--color-primary-light-text) !important;
}

/* ── Dropdown menus (selectbox / multiselect options) ── */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul {
    background-color: var(--color-card-bg) !important;
    border: 1px solid var(--color-border) !important;
}
[data-baseweb="option"] {
    background-color: var(--color-card-bg) !important;
    color: var(--color-text) !important;
}
[data-baseweb="option"]:hover {
    background-color: var(--color-surface) !important;
}

/* ── Expanders (story / question cards) ── */
[data-testid="stExpander"] {
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-lg) !important;
    margin-bottom: 12px !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
    background: var(--color-card-bg) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 15px !important;
    color: var(--color-text) !important;
    padding: 14px 16px !important;
    background: var(--color-card-bg) !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: var(--color-surface) !important;
}
[data-testid="stExpanderDetails"] {
    background-color: var(--color-card-bg) !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: var(--color-card-bg) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 24px !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Dividers ── */
hr {
    border-color: var(--color-border) !important;
    margin: 16px 0 !important;
}

/* ── Labels ── */
label[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stMultiSelect label {
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--color-text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ── Tag badge component ── */
.tag-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 500;
    margin: 2px 3px 2px 0;
    font-family: var(--font-body);
}
.tag-badge-primary {
    background-color: var(--color-primary-light);
    color: var(--color-primary-light-text);
}
.tag-badge-muted {
    background-color: var(--color-badge-muted-bg);
    color: var(--color-badge-muted-text);
}

/* ── STAR section cards ── */
.star-section {
    background: var(--color-surface);
    border-left: 3px solid var(--color-primary);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.star-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--color-primary);
    margin-bottom: 4px;
}
.star-content {
    font-size: 14px;
    line-height: 1.7;
    color: var(--color-text);
}

/* ── Meta row (company, location, date) ── */
.story-meta {
    font-size: 13px;
    color: var(--color-text-muted);
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}
.story-meta span {
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ── Related questions row ── */
.related-q-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 16px 0 6px;
}
.related-q-item {
    font-size: 14px;
    color: var(--color-text);
    margin: 4px 0;
}
.related-q-bullet {
    color: var(--color-text-muted);
    margin-right: 6px;
}
.related-q-tag {
    display: inline-block;
    background: var(--color-primary-light);
    color: var(--color-primary-light-text);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
    margin-left: 4px;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--color-text-muted);
}
.empty-state .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}
.empty-state p {
    font-size: 16px;
    margin: 0;
    color: var(--color-text-muted);
}

/* ── Alert overrides ── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-size: 14px !important;
}
"""


def inject_global_css() -> None:
    dark = st.session_state.get("dark_mode", False)
    tokens = _TOKENS_DARK if dark else _TOKENS_LIGHT
    st.markdown(f"<style>{tokens}{_STRUCTURAL_CSS}</style>", unsafe_allow_html=True)
