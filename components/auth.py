"""
Login de administrador — mismo patrón internal_auth que el observatorio CCHEN.
Lee [internal_auth.users] de .streamlit/secrets.toml.
"""
import hashlib
import hmac
import streamlit as st

_SESSION_KEY = "rf_admin_username"


def _get_users() -> dict[str, dict]:
    try:
        block = st.secrets.get("internal_auth", {})
        raw_users = block.get("users", [])
    except Exception:
        return {}

    users: dict[str, dict] = {}
    if isinstance(raw_users, (list, tuple)):
        for item in raw_users:
            if not isinstance(item, dict):
                continue
            username = str(item.get("username", "")).strip().lower()
            if not username:
                continue
            users[username] = {
                "password": str(item.get("password", "")),
                "password_sha256": str(item.get("password_sha256", "")).strip().lower(),
                "name": str(item.get("name", username)),
                "role": str(item.get("role", "")),
            }
    return users


def _verify(raw_password: str, user_cfg: dict) -> bool:
    if not raw_password:
        return False
    stored_hash = user_cfg.get("password_sha256", "").strip().lower()
    if stored_hash:
        digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(digest, stored_hash)
    stored = user_cfg.get("password", "")
    return bool(stored) and hmac.compare_digest(raw_password, stored)


def is_admin_logged_in() -> bool:
    return bool(st.session_state.get(_SESSION_KEY))


def admin_logout() -> None:
    st.session_state.pop(_SESSION_KEY, None)


def require_admin_login() -> bool:
    """
    Muestra formulario de login si no está autenticado.
    Retorna True si el usuario ya está autenticado.
    """
    if is_admin_logged_in():
        return True

    st.markdown(
        "<div style='max-width:420px;margin:60px auto 0'>"
        "<h2 style='color:#003B6F;margin-bottom:4px'>Panel de Administración</h2>"
        "<p style='color:#64748B;font-size:0.9rem'>Seguimiento de Radiofarmacos · CCHEN</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form("rf_admin_login", clear_on_submit=True):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar", use_container_width=True)

    if submitted:
        users = _get_users()
        normalized = username.strip().lower()
        user_cfg = users.get(normalized)
        if user_cfg and _verify(password, user_cfg):
            st.session_state[_SESSION_KEY] = normalized
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    return False


def admin_name() -> str:
    username = st.session_state.get(_SESSION_KEY, "")
    users = _get_users()
    return users.get(username, {}).get("name", username)
