"""
Dashboard de administración para el seguimiento de radiofarmacos CCHEN.
Accesible en /?view=admin (requiere login con [internal_auth]).
Firma render(ctx=None) compatible con futura integración al observatorio.
"""
from __future__ import annotations

import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import data_loader as dl
from components.auth import admin_logout, admin_name
from components.chile_map import render_choropleth, render_marker_map

BLUE = "#003B6F"
RED = "#C8102E"
GREEN = "#00A896"
AMBER = "#F4A60D"
PALETTE = [BLUE, RED, GREEN, AMBER, "#7B2D8B", "#E76F51", "#52B788", "#264653"]


# ─── Helpers de presentación ─────────────────────────────────────────────────

def _kpi(label: str, value, sub: str = "", color: str = BLUE) -> str:
    sub_html = (
        f'<div style="font-size:0.71rem;color:#94A3B8;margin-top:3px">{sub}</div>'
    ) if sub else ""
    return (
        f"<div style='flex:1;min-width:0;background:white;border-radius:14px;padding:18px 16px 16px;"
        f"border:1px solid rgba(0,59,111,0.07);border-top:3px solid {color};"
        f"box-shadow:0 2px 12px rgba(0,30,66,0.06)'>"
        f"<div style='font-size:1.85rem;font-weight:700;color:{color};line-height:1.1'>{value}</div>"
        f"<div style='font-size:0.7rem;color:#64748B;margin-top:7px;font-weight:500;"
        f"text-transform:uppercase;letter-spacing:0.6px'>{label}</div>"
        f"{sub_html}</div>"
    )


def _kpi_row(*cards: str) -> None:
    html = '<div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap">' + "".join(cards) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _sec(title: str) -> None:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:9px;margin-bottom:14px;margin-top:20px'>"
        f"<div style='width:3px;height:18px;background:linear-gradient(180deg,{BLUE},{RED});"
        f"border-radius:2px;flex-shrink:0'></div>"
        f"<span style='color:#0F172A;font-size:0.9rem;font-weight:600'>{title}</span></div>",
        unsafe_allow_html=True,
    )


def _make_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# ─── Preparación de datos ────────────────────────────────────────────────────

def _prep_envios(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    for col in ("llegada_dt", "salida_dt", "actividad_ref_dt", "created_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    if "llegada_dt" in df.columns:
        df["fecha"] = df["llegada_dt"].dt.tz_convert("America/Santiago").dt.normalize()
    return df


# ─── Secciones del dashboard ─────────────────────────────────────────────────

def _section_kpis(envios: pd.DataFrame, instituciones: pd.DataFrame, pendientes: int) -> None:
    now = pd.Timestamp.now(tz="UTC")
    last30 = envios[envios["llegada_dt"] >= now - pd.Timedelta(days=30)] if not envios.empty else envios

    total = len(last30)
    n_destinos = last30["destino_id"].nunique() if not last30.empty else 0
    n_radiofarmacos = (
        last30["isotopo_id"].nunique() + (last30["isotopo_texto"].notna().sum() > 0)
        if not last30.empty else 0
    )
    n_incidentes = int((last30["estado"] == "incidente").sum()) if not last30.empty else 0

    _kpi_row(
        _kpi("Entregas (30 días)", total, color=BLUE),
        _kpi("Destinos únicos", n_destinos, color=GREEN),
        _kpi("Radiofarmacos", n_radiofarmacos, color=AMBER),
        _kpi("Incidentes", n_incidentes,
             sub="requiere atención" if n_incidentes else "",
             color=RED if n_incidentes else "#94A3B8"),
    )

    if pendientes > 0:
        st.warning(
            f"⚠️ **{pendientes} institución(es) pendiente(s) de aprobación** — "
            "ver sección 'Gestión de instituciones' más abajo."
        )


def _section_map(envios: pd.DataFrame, instituciones: pd.DataFrame) -> None:
    _sec("Distribución geográfica")
    tab_markers, tab_region = st.tabs(["Mapa por institución", "Mapa por región"])

    with tab_markers:
        render_marker_map(envios, instituciones)

    with tab_region:
        render_choropleth(envios, instituciones)


def _section_stats(envios: pd.DataFrame, instituciones: pd.DataFrame, isotopes: pd.DataFrame) -> None:
    _sec("Estadísticas")

    if envios.empty:
        st.info("Sin datos de entregas aún.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        # Top instituciones destino
        dest_counts = (
            envios.merge(
                instituciones[["institucion_id", "nombre"]],
                left_on="destino_id", right_on="institucion_id", how="left",
            )
            .groupby("nombre")
            .size()
            .reset_index(name="n")
            .sort_values("n", ascending=False)
            .head(10)
        )
        if not dest_counts.empty:
            fig = px.bar(
                dest_counts,
                x="n", y="nombre", orientation="h",
                labels={"n": "Entregas", "nombre": ""},
                color_discrete_sequence=[BLUE],
                title="Top 10 instituciones destino",
                height=320,
            )
            fig.update_layout(margin={"t": 36, "b": 0, "l": 0, "r": 0}, yaxis={"autorange": "reversed"})
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Entregas por isótopo
        iso_counts = envios.groupby("isotopo_id").size().reset_index(name="n")
        iso_counts = iso_counts.merge(
            isotopes[["isotope_id", "symbol", "color_hex"]],
            left_on="isotopo_id", right_on="isotope_id", how="left",
        )
        iso_counts["symbol"] = iso_counts["symbol"].fillna("Otro")
        if not iso_counts.empty:
            fig = px.pie(
                iso_counts,
                names="symbol", values="n",
                color="symbol",
                color_discrete_map=dict(zip(iso_counts["symbol"], iso_counts["color_hex"].fillna(BLUE))),
                title="Distribución por radiofarmaco",
                height=320,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(margin={"t": 36, "b": 0, "l": 0, "r": 0}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Serie temporal
    if "fecha" in envios.columns:
        _sec("Tendencia de entregas")
        freq = st.radio("Agrupación", ["Diaria", "Semanal", "Mensual"], horizontal=True, key="rf_admin_freq")
        freq_map = {"Diaria": "D", "Semanal": "W", "Mensual": "ME"}
        ts = (
            envios.set_index("fecha")
            .resample(freq_map[freq])
            .size()
            .reset_index(name="n")
        )
        ts["fecha"] = ts["fecha"].dt.strftime("%Y-%m-%d")
        if not ts.empty:
            fig = px.line(
                ts, x="fecha", y="n",
                labels={"fecha": "", "n": "Entregas"},
                markers=True,
                color_discrete_sequence=[BLUE],
                height=280,
            )
            fig.update_layout(margin={"t": 10, "b": 0, "l": 0, "r": 0})
            st.plotly_chart(fig, use_container_width=True)


def _section_table(envios: pd.DataFrame, instituciones: pd.DataFrame, isotopes: pd.DataFrame) -> None:
    _sec("Registro de entregas")

    if envios.empty:
        st.info("Sin entregas registradas.")
        return

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        estado_filter = st.multiselect(
            "Estado", ["entregado", "incidente", "cancelado"],
            default=["entregado", "incidente"], key="rf_admin_estado_filter"
        )
    with col_f2:
        fecha_desde = st.date_input("Desde", value=None, key="rf_admin_desde")
    with col_f3:
        fecha_hasta = st.date_input("Hasta", value=None, key="rf_admin_hasta")

    filtered = envios.copy()
    if estado_filter:
        filtered = filtered[filtered["estado"].isin(estado_filter)]
    if fecha_desde and "llegada_dt" in filtered.columns:
        filtered = filtered[filtered["llegada_dt"].dt.date >= fecha_desde]
    if fecha_hasta and "llegada_dt" in filtered.columns:
        filtered = filtered[filtered["llegada_dt"].dt.date <= fecha_hasta]

    # Enriquecer con nombres
    display = filtered.merge(
        instituciones[["institucion_id", "nombre"]].rename(columns={"nombre": "destino"}),
        left_on="destino_id", right_on="institucion_id", how="left",
    ).merge(
        isotopes[["isotope_id", "symbol"]],
        left_on="isotopo_id", right_on="isotope_id", how="left",
    )
    display["radiofarmaco"] = display["symbol"].fillna(display.get("isotopo_texto", ""))
    display["llegada"] = (
        display["llegada_dt"].dt.tz_convert("America/Santiago").dt.strftime("%d/%m/%Y %H:%M")
        if "llegada_dt" in display.columns else ""
    )

    cols_show = ["envio_id", "llegada", "nombre_conductor", "destino",
                 "radiofarmaco", "lote_numero", "actividad_mbq",
                 "condicion_embalaje", "estado", "observaciones"]
    cols_show = [c for c in cols_show if c in display.columns]

    st.dataframe(display[cols_show], use_container_width=True, height=400)

    col_dl, col_estado = st.columns([2, 1])
    with col_dl:
        st.download_button(
            "Descargar CSV",
            data=_make_csv(display[cols_show]),
            file_name=f"radiofarmacos_{datetime.date.today()}.csv",
            mime="text/csv",
        )

    # Cambio de estado
    with col_estado:
        with st.expander("Cambiar estado de envío"):
            envio_id = st.number_input("ID envío", min_value=1, step=1, key="rf_admin_envio_id")
            nuevo_estado = st.selectbox("Nuevo estado", ["entregado", "incidente", "cancelado"], key="rf_admin_nuevo_estado")
            if st.button("Actualizar", key="rf_admin_update_estado"):
                try:
                    dl.update_envio_estado(int(envio_id), nuevo_estado)
                    st.success("Estado actualizado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


def _section_pendientes(instituciones_admin: pd.DataFrame) -> None:
    _sec("Gestión de instituciones")

    pendientes = instituciones_admin[instituciones_admin["aprobada"] == False] if not instituciones_admin.empty else pd.DataFrame()

    if pendientes.empty:
        st.success("Sin instituciones pendientes de revisión.")
    else:
        st.info(f"{len(pendientes)} institución(es) propuesta(s) por conductores esperan aprobación.")
        for _, row in pendientes.iterrows():
            with st.expander(f"📍 {row['nombre']} — {row.get('ciudad', '')} ({row.get('region', '')})", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    lat_val = st.number_input(
                        "Latitud", value=float(row["lat"]) if row.get("lat") else -33.45,
                        step=0.001, format="%.6f", key=f"rf_lat_{row['institucion_id']}"
                    )
                with col2:
                    lon_val = st.number_input(
                        "Longitud", value=float(row["lon"]) if row.get("lon") else -70.65,
                        step=0.001, format="%.6f", key=f"rf_lon_{row['institucion_id']}"
                    )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Aprobar", key=f"rf_aprobar_{row['institucion_id']}", type="primary"):
                        try:
                            dl.aprobar_institucion(int(row["institucion_id"]), lat=lat_val, lon=lon_val)
                            st.success(f"'{row['nombre']}' aprobada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                with col_b:
                    st.caption(f"Tipo: {row.get('tipo','—')} · Propuesta: {row.get('created_at','')[:10] if row.get('created_at') else '—'}")

    # Panel de agregar isótopo
    _sec("Agregar isótopo al catálogo")
    with st.expander("Nuevo isótopo"):
        i_symbol = st.text_input("Símbolo *", placeholder="Ej: Ho-166", key="rf_admin_iso_symbol")
        i_nombre = st.text_input("Nombre completo", placeholder="Ej: DOTMP de Holmio-166", key="rf_admin_iso_nombre")
        i_vmh = st.number_input("Vida media (horas)", min_value=0.0, step=0.1, key="rf_admin_iso_vmh")
        i_color = st.color_picker("Color en mapa", value="#003B6F", key="rf_admin_iso_color")
        if st.button("Agregar isótopo", key="rf_admin_add_iso"):
            if not i_symbol.strip():
                st.warning("El símbolo es requerido.")
            else:
                try:
                    dl.insert_isotope({
                        "symbol": i_symbol.strip(),
                        "nombre_completo": i_nombre.strip() or None,
                        "vida_media_h": float(i_vmh) if i_vmh else None,
                        "color_hex": i_color,
                        "unidad_actividad": "MBq",
                        "activo": True,
                    })
                    st.success(f"Isótopo '{i_symbol.strip()}' agregado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def render(ctx: dict | None = None) -> None:
    # Header
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(
            f"<h2 style='color:{BLUE};margin-bottom:2px'>Panel de Radiofarmacos</h2>"
            f"<p style='color:#64748B;font-size:0.85rem;margin:0'>CCHEN · Seguimiento de distribución</p>",
            unsafe_allow_html=True,
        )
    with col_logout:
        st.caption(f"👤 {admin_name()}")
        if st.button("Salir", key="rf_logout"):
            admin_logout()
            st.rerun()

    st.divider()

    # Cargar datos
    with st.spinner("Cargando datos…"):
        envios_raw = dl.load_envios()
        instituciones = dl.load_instituciones_aprobadas()
        instituciones_admin = dl.load_instituciones_admin()
        isotopes = dl.load_isotopes()

    envios = _prep_envios(envios_raw.copy())

    pendientes_count = int(
        (instituciones_admin["aprobada"] == False).sum()
        if not instituciones_admin.empty else 0
    )

    # Secciones
    _section_kpis(envios, instituciones, pendientes_count)
    _section_map(envios, instituciones)
    _section_stats(envios, instituciones, isotopes)
    _section_table(envios, instituciones, isotopes)
    _section_pendientes(instituciones_admin)
