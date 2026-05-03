"""
Capa de acceso a datos para la app de seguimiento de radiofarmacos CCHEN.
Sigue el mismo patrón que Dashboard/data_loader.py: Supabase con secrets.toml,
fallback a env vars, paginación por bloques de 1000 filas.
"""
import logging
import os
from functools import lru_cache

import pandas as pd
import streamlit as st

_log = logging.getLogger(__name__)

PAGE_SIZE = 1000

try:
    from supabase import create_client
except ImportError:
    create_client = None


# ─── Credenciales ────────────────────────────────────────────────────────────

def _get_creds(service_role: bool = False) -> tuple[str, str]:
    try:
        url = st.secrets["supabase"]["url"]
        key_name = "service_role_key" if service_role else "anon_key"
        key = st.secrets["supabase"][key_name]
        return str(url).strip(), str(key).strip()
    except Exception:
        pass

    url = (os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_PUBLIC_URL") or "").strip()
    if service_role:
        key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or "").strip()
    else:
        key = (os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY") or "").strip()
    return url, key


@lru_cache(maxsize=1)
def _client():
    url, key = _get_creds(service_role=False)
    if not create_client or not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


@lru_cache(maxsize=1)
def _service_client():
    url, key = _get_creds(service_role=True)
    if not create_client or not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


# ─── Fetch paginado ───────────────────────────────────────────────────────────

def _fetch(table: str, order_by: str, use_service_role: bool = False) -> pd.DataFrame:
    cli = _service_client() if use_service_role else _client()
    if cli is None:
        raise RuntimeError("Supabase no disponible. Configura secrets.toml.")

    rows: list[dict] = []
    start = 0
    while True:
        resp = (
            cli.table(table)
            .select("*")
            .order(order_by)
            .range(start, start + PAGE_SIZE - 1)
            .execute()
        )
        batch = list(resp.data or [])
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    return pd.DataFrame(rows)


# ─── Loaders para catálogos (TTL largo, raramente cambian) ───────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_isotopes() -> pd.DataFrame:
    try:
        df = _fetch("rf_isotopes", "isotope_id")
        return df[df["activo"] == True].copy() if not df.empty else df
    except Exception as e:
        _log.warning("Error cargando rf_isotopes: %s", e)
        return pd.DataFrame(columns=["isotope_id", "symbol", "nombre_completo", "color_hex", "unidad_actividad"])


@st.cache_data(ttl=300, show_spinner=False)
def load_instituciones_aprobadas() -> pd.DataFrame:
    """Instituciones aprobadas visibles en el formulario (anon key, RLS filtra)."""
    try:
        df = _fetch("rf_instituciones", "institucion_id")
        return df.sort_values("nombre") if not df.empty else df
    except Exception as e:
        _log.warning("Error cargando rf_instituciones: %s", e)
        return pd.DataFrame(columns=["institucion_id", "nombre", "nombre_corto", "tipo", "region", "ciudad", "lat", "lon", "es_origen"])


@st.cache_data(ttl=60, show_spinner=False)
def load_instituciones_admin() -> pd.DataFrame:
    """Todas las instituciones incluyendo pendientes (service_role)."""
    try:
        cli = _service_client()
        if cli is None:
            raise RuntimeError("Service role no disponible")
        resp = (
            cli.table("rf_instituciones")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return pd.DataFrame(resp.data or [])
    except Exception as e:
        _log.warning("Error cargando instituciones admin: %s", e)
        return pd.DataFrame()


@st.cache_data(ttl=60, show_spinner=False)
def load_envios() -> pd.DataFrame:
    """Todos los envíos (service_role, solo admin)."""
    try:
        return _fetch("rf_envios", "llegada_dt", use_service_role=True)
    except Exception as e:
        _log.warning("Error cargando rf_envios: %s", e)
        return pd.DataFrame()


# ─── Escritura ────────────────────────────────────────────────────────────────

def insert_envio(data: dict) -> dict:
    """Inserta un envío usando anon key (RLS permite INSERT público)."""
    cli = _client()
    if cli is None:
        raise RuntimeError("Supabase no disponible.")
    resp = cli.table("rf_envios").insert(data).execute()
    if resp.data:
        return resp.data[0]
    raise RuntimeError("No se recibió confirmación de Supabase.")


def insert_institucion_nueva(data: dict) -> dict:
    """Inserta institución propuesta por conductor (aprobada=FALSE, anon key)."""
    cli = _client()
    if cli is None:
        raise RuntimeError("Supabase no disponible.")
    data.setdefault("aprobada", False)
    data.setdefault("es_origen", False)
    resp = cli.table("rf_instituciones").insert(data).execute()
    if resp.data:
        load_instituciones_aprobadas.clear()
        return resp.data[0]
    raise RuntimeError("No se pudo agregar la institución.")


def aprobar_institucion(institucion_id: int, lat: float | None = None, lon: float | None = None) -> None:
    """Admin aprueba una institución pendiente (service_role)."""
    cli = _service_client()
    if cli is None:
        raise RuntimeError("Service role no disponible.")
    payload: dict = {"aprobada": True}
    if lat is not None:
        payload["lat"] = lat
    if lon is not None:
        payload["lon"] = lon
    cli.table("rf_instituciones").update(payload).eq("institucion_id", institucion_id).execute()
    load_instituciones_admin.clear()
    load_instituciones_aprobadas.clear()


def update_envio_estado(envio_id: int, estado: str) -> None:
    """Admin actualiza estado de un envío."""
    cli = _service_client()
    if cli is None:
        raise RuntimeError("Service role no disponible.")
    cli.table("rf_envios").update({"estado": estado}).eq("envio_id", envio_id).execute()
    load_envios.clear()


def insert_isotope(data: dict) -> dict:
    """Admin agrega un nuevo isótopo al catálogo."""
    cli = _service_client()
    if cli is None:
        raise RuntimeError("Service role no disponible.")
    resp = cli.table("rf_isotopes").insert(data).execute()
    if resp.data:
        load_isotopes.clear()
        return resp.data[0]
    raise RuntimeError("No se pudo agregar el isótopo.")
