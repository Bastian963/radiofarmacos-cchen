"""
Aplicación de seguimiento de radiofarmacos CCHEN.
Enrutamiento por query param: ?view=form (default) | ?view=admin

Formulario conductores: http://[host]:8502/
Panel admin:           http://[host]:8502/?view=admin
"""
import streamlit as st

st.set_page_config(
    page_title="Radiofarmacos CCHEN",
    page_icon="☢️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

view = st.query_params.get("view", "form")

if view == "admin":
    from components.auth import require_admin_login
    if require_admin_login():
        from pages.admin import render
        render()
else:
    # Cualquier view desconocido cae en el formulario
    from pages.form import render
    render()
