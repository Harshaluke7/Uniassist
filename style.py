import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

/* ── Base & Page Background ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background: #f8fafc !important;
    color: #1e293b !important;
}

[data-testid="stMain"] {
    background: #f8fafc !important;
}

[data-testid="stAppViewContainer"] .block-container {
    padding: 2rem 3rem 3rem;
    max-width: 1200px;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Sora', sans-serif;
    color: #0f172a !important;
    font-weight: 700;
    letter-spacing: -0.3px;
}

p, span, label, [data-testid="stMarkdownContainer"] {
    color: #334155;
}

/* ── Form Labels ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: #1e293b !important;
    font-weight: 600;
    font-size: 14px;
}

/* ── Inputs & Textareas ── */
input, textarea {
    color: #0f172a !important;
    background: #ffffff !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-size: 14.5px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
}

/* ── Disabled Inputs (Fixes invisible text on white) ── */
input:disabled, textarea:disabled,
[data-testid="stTextInput"] input:disabled,
[data-testid="stTextArea"] textarea:disabled {
    background: #f1f5f9 !important;
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    opacity: 1 !important;
    border: 1.5px solid #e2e8f0 !important;
    cursor: not-allowed;
}

/* ── Dropdowns & Selectboxes (Fixes dark text on dark bg) ── */
[data-baseweb="select"] {
    background: #ffffff !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] * {
    color: #0f172a !important;
}

/* Dropdown popover menu options */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"] {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
}

[role="option"] {
    background: #ffffff !important;
    color: #0f172a !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #eef2ff !important;
    color: #4f46e5 !important;
}

/* ── Data Editor (Grid) ── */
[data-testid="stDataEditor"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

/* ── Modern Buttons ── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    min-height: 42px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button p,
[data-testid="stFormSubmitButton"] > button p {
    color: #ffffff !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: #4338ca !important;
    border-color: #4338ca !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
}

/* Secondary Buttons */
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1.5px solid #cbd5e1 !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"] p {
    color: #334155 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 26px !important;
}

/* ── Modern Analysis Card ── */
.summary-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 16px 0 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.summary-title {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

.summary-item {
    background: #f8fafc;
    border: 1px solid #f1f5f9;
    border-radius: 10px;
    padding: 12px 16px;
}

.summary-label {
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
    margin-bottom: 4px;
}

.summary-value {
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
}

/* ── Alerts & Info ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    font-size: 14px;
}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)
