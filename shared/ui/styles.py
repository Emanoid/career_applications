import streamlit as st

_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Design tokens ── */
:root {
    --font-body: 'Inter', sans-serif;
    --color-primary: #4F46E5;
    --color-primary-hover: #4338CA;
    --color-primary-light: #EEF2FF;
    --color-surface: #F9FAFB;
    --color-border: #E5E7EB;
    --color-text: #111827;
    --color-text-muted: #6B7280;
    --color-success: #059669;
    --color-error: #DC2626;
    --radius: 8px;
    --radius-lg: 12px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.05);
}

/* ── Global font ── */
html, body, [class*="css"], .stApp {
    font-family: var(--font-body) !important;
}

/* ── Hide auto-generated Streamlit sidebar nav ── */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Sidebar ── */
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

/* ── Primary buttons ── */
.stButton > button[kind="primary"],
.stButton > button {
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
.stButton > button:hover {
    background-color: var(--color-primary-hover) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--color-text) !important;
    border: 1px solid var(--color-border) !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: var(--color-surface) !important;
    transform: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: var(--radius) !important;
    border: 1px solid var(--color-border) !important;
    font-family: var(--font-body) !important;
    font-size: 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--color-primary) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    border-radius: var(--radius) !important;
    border: 1px solid var(--color-border) !important;
}

/* ── Expanders (story cards) ── */
[data-testid="stExpander"] {
    border: 1px solid var(--color-border) !important;
    border-radius: var(--radius-lg) !important;
    margin-bottom: 12px !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 15px !important;
    color: var(--color-text) !important;
    padding: 14px 16px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: var(--color-surface) !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: #FFFFFF !important;
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
    color: var(--color-primary);
}
.tag-badge-muted {
    background-color: #F3F4F6;
    color: var(--color-text-muted);
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
}

/* ── Alert overrides ── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    font-size: 14px !important;
}
</style>
"""


def inject_global_css() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
