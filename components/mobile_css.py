"""CSS helpers — diseño mobile-first con paleta CCHEN pastel."""
import streamlit as st

MOBILE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Layout mobile ─────────────────────────────── */
.block-container {
    padding: 0.8rem 1rem 2rem !important;
    max-width: 520px !important;
}
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Inputs grandes para touch ─────────────────── */
div[data-testid="stSelectbox"] > div > div {
    min-height: 54px;
    font-size: 1.05rem;
    border-radius: 12px !important;
    border: 1.5px solid #BEE3F8 !important;
    background: #F8FBFF !important;
}
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stNumberInput"] input {
    min-height: 54px;
    font-size: 1.05rem;
    border-radius: 12px !important;
    border: 1.5px solid #BEE3F8 !important;
    background: #F8FBFF !important;
    padding: 8px 14px !important;
}
div[data-testid="stTextArea"] textarea {
    font-size: 1rem;
    border-radius: 12px !important;
    border: 1.5px solid #BEE3F8 !important;
    background: #F8FBFF !important;
}
div[data-testid="stTextInput"] > div > div > input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3182CE !important;
    box-shadow: 0 0 0 3px rgba(49,130,206,0.15) !important;
    outline: none !important;
}

/* ── Labels ────────────────────────────────────── */
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stRadio"] label:first-child {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #4A5568 !important;
    margin-bottom: 4px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.4px !important;
}

/* ── Radio como botones grandes ────────────────── */
div[data-testid="stRadio"] > div {
    flex-direction: row;
    gap: 8px;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] > div > label {
    padding: 12px 20px !important;
    border: 2px solid #BEE3F8 !important;
    border-radius: 12px !important;
    min-width: 90px !important;
    text-align: center !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    background: white !important;
    transition: all 0.15s !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    color: #2D3748 !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #EBF8FF !important;
    border-color: #3182CE !important;
    color: #2B6CB0 !important;
}

/* ── Botón primario ────────────────────────────── */
button[data-testid="baseButton-primary"] {
    min-height: 58px !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    width: 100% !important;
    background: linear-gradient(135deg, #2B6CB0, #3182CE) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(49,130,206,0.35) !important;
    letter-spacing: 0.3px !important;
}
button[data-testid="baseButton-secondary"] {
    min-height: 50px !important;
    font-size: 1rem !important;
    border-radius: 12px !important;
    width: 100% !important;
    border: 2px solid #BEE3F8 !important;
    color: #2B6CB0 !important;
    background: white !important;
}

/* ── Divider ───────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #EBF4FF !important;
    margin: 1rem 0 !important;
}

/* ── Expander ──────────────────────────────────── */
div[data-testid="stExpander"] {
    border: 1.5px solid #BEE3F8 !important;
    border-radius: 12px !important;
    background: #F8FBFF !important;
}
</style>
"""

VIEWPORT_META = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'


def inject_mobile_css() -> None:
    st.markdown(VIEWPORT_META, unsafe_allow_html=True)
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
