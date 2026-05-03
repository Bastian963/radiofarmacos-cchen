"""CSS helpers para formulario mobile-first."""
import streamlit as st

MOBILE_CSS = """
<style>
/* Inputs y selectboxes más grandes para touch */
div[data-testid="stSelectbox"] > div > div {
    min-height: 52px;
    font-size: 1.05rem;
}
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stNumberInput"] input {
    min-height: 52px;
    font-size: 1.05rem;
    padding: 8px 12px;
}
div[data-testid="stTextArea"] textarea {
    font-size: 1.0rem;
}
/* Radio como botones grandes */
div[data-testid="stRadio"] > div {
    flex-direction: row;
    gap: 8px;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] label {
    padding: 12px 18px;
    border: 2px solid #003B6F;
    border-radius: 10px;
    min-width: 90px;
    text-align: center;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.15s;
}
/* Botón primario a ancho completo y más alto */
button[data-testid="baseButton-primary"] {
    min-height: 58px;
    font-size: 1.15rem;
    border-radius: 12px;
    width: 100%;
}
/* Ocultar sidebar en la vista formulario */
section[data-testid="stSidebar"] {
    display: none !important;
}
/* Quitar padding lateral excesivo en mobile */
.block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 600px;
}
</style>
"""

VIEWPORT_META = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'


def inject_mobile_css() -> None:
    st.markdown(VIEWPORT_META, unsafe_allow_html=True)
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
