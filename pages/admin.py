"""
Dashboard de administración — diseño pastel CCHEN 360.
Accesible en /?view=admin
"""
from __future__ import annotations

import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import data_loader as dl
from components.auth import admin_logout, admin_name
from components.chile_map import render_choropleth, render_marker_map

# ── Paleta pastel ──────────────────────────────────────────────────────────────
P_BLUE    = "#90CDF4"
P_TEAL    = "#81E6D9"
P_GREEN   = "#9AE6B4"
P_YELLOW  = "#FAF089"
P_ROSE    = "#FEB2B2"
P_PURPLE  = "#D6BCFA"
P_ORANGE  = "#FBD38D"
P_PINK    = "#F687B3"

BG_BLUE   = "#EBF8FF"
BG_TEAL   = "#E6FFFA"
BG_GREEN  = "#F0FFF4"
BG_YELLOW = "#FFFFF0"
BG_ROSE   = "#FFF5F5"
BG_PURPLE = "#FAF5FF"

DARK_BLUE  = "#2B6CB0"
DARK_TEAL  = "#2C7A6A"
DARK_GREEN = "#276749"
DARK_ROSE  = "#C53030"
DARK_PUR   = "#553C9A"

PASTEL_CHART = [P_BLUE, P_TEAL, P_ROSE, P_YELLOW, P_PURPLE, P_ORANGE, P_GREEN, P_PINK]

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"

ADMIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1200px !important; }
#MainMenu, footer { visibility: hidden; }
button[data-testid="baseButton-primary"] {
    border-radius: 10px !important; font-weight: 600 !important;
}
button[data-testid="baseButton-secondary"] {
    border-radius: 10px !important;
}
div[data-testid="stTabs"] button {
    font-weight: 500 !important; font-size: 0.9rem !important;
}
</style>
"""


# ── Helpers HTML ───────────────────────────────────────────────────────────────

def _kpi_card(label: str, value, sub: str = "", bg: str = BG_BLUE,
              accent: str = P_BLUE, text_color: str = DARK_BLUE, icon: str = "") -> str:
    sub_html = f'<div style="font-size:0.72rem;color:#718096;margin-top:2px">{sub}</div>' if sub else ""
    icon_html = f'<div style="font-size:1.4rem;margin-bottom:6px">{icon}</div>' if icon else ""
    return (
        f"<div style='background:{bg};border-radius:16px;padding:18px 20px 16px;"
        f"border:1.5px solid {accent};box-shadow:0 2px 8px rgba(0,0,0,0.04);"
        f"flex:1;min-width:0'>"
        f"{icon_html}"
        f"<div style='font-size:2rem;font-weight:800;color:{text_color};line-height:1.1'>{value}</div>"
        f"<div style='font-size:0.72rem;color:#4A5568;margin-top:6px;font-weight:600;"
        f"text-transform:uppercase;letter-spacing:0.5px'>{label}</div>"
        f"{sub_html}"
        f"</div>"
    )


def _kpi_row(*cards: str) -> None:
    st.markdown(
        '<div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">'
        + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def _section(title: str, icon: str = "") -> None:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;margin:28px 0 16px'>"
        f"<div style='width:4px;height:22px;"
        f"background:linear-gradient(180deg,{P_BLUE},{P_TEAL});"
        f"border-radius:3px;flex-shrink:0'></div>"
        f"<span style='font-size:1rem;font-weight:700;color:#1A202C'>{icon} {title}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _make_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


# ── Preparación ───────────────────────────────────────────────────────────────

def _prep(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    for col in ("llegada_dt", "salida_dt", "actividad_ref_dt", "created_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    if "llegada_dt" in df.columns:
        df["fecha"] = df["llegada_dt"].dt.tz_convert("America/Santiago").dt.normalize()
        df["fecha_str"] = df["llegada_dt"].dt.tz_convert("America/Santiago").dt.strftime("%d/%m/%Y %H:%M")
    return df


# ── Secciones ─────────────────────────────────────────────────────────────────

def _header() -> None:
    st.markdown(ADMIN_CSS, unsafe_allow_html=True)

    col_logo, col_title, col_user = st.columns([1, 4, 1])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=90)
        else:
            st.markdown(
                f"<span style='font-size:1.2rem;font-weight:800;color:{DARK_BLUE}'>"
                f"CCHEN <span style='color:{P_BLUE}'>360</span></span>",
                unsafe_allow_html=True,
            )
    with col_title:
        st.markdown(
            f"<div style='padding-top:4px'>"
            f"<h2 style='margin:0;font-size:1.4rem;color:#1A202C;font-weight:800'>"
            f"Panel de Radiofarmacos</h2>"
            f"<p style='margin:2px 0 0;font-size:0.82rem;color:#718096'>"
            f"Seguimiento de distribución · CCHEN</p></div>",
            unsafe_allow_html=True,
        )
    with col_user:
        st.caption(f"👤 {admin_name()}")
        if st.button("Salir", key="rf_logout"):
            admin_logout()
            st.rerun()

    st.markdown(
        f"<div style='height:3px;background:linear-gradient(90deg,{P_BLUE},{P_TEAL},{P_GREEN});"
        f"border-radius:2px;margin:8px 0 20px'></div>",
        unsafe_allow_html=True,
    )


def _section_kpis(envios: pd.DataFrame, pendientes: int) -> None:
    now = pd.Timestamp.now(tz="UTC")
    last30 = envios[envios["llegada_dt"] >= now - pd.Timedelta(days=30)] if not envios.empty else envios

    total      = len(last30)
    n_destinos = int(last30["destino_id"].nunique()) if not last30.empty else 0
    n_isos     = int(last30["isotopo_id"].nunique()) if not last30.empty else 0
    n_inc      = int((last30["estado"] == "incidente").sum()) if not last30.empty else 0

    _kpi_row(
        _kpi_card("Entregas (30 días)", total,      icon="📦", bg=BG_BLUE,   accent=P_BLUE,   text_color=DARK_BLUE),
        _kpi_card("Destinos únicos",    n_destinos, icon="🏥", bg=BG_TEAL,   accent=P_TEAL,   text_color=DARK_TEAL),
        _kpi_card("Radiofarmacos",      n_isos,     icon="☢️", bg=BG_YELLOW, accent=P_YELLOW, text_color="#744210"),
        _kpi_card("Incidentes",         n_inc,      icon="⚠️",
                  bg=BG_ROSE if n_inc else BG_GREEN,
                  accent=P_ROSE if n_inc else P_GREEN,
                  text_color=DARK_ROSE if n_inc else DARK_GREEN,
                  sub="Requiere atención" if n_inc else "Sin incidentes"),
    )

    if pendientes > 0:
        st.markdown(
            f"<div style='background:#FFFFF0;border:1.5px solid {P_YELLOW};border-radius:12px;"
            f"padding:10px 16px;font-size:0.88rem;color:#744210;margin-bottom:16px'>"
            f"⚠️ <b>{pendientes} institución(es)</b> pendientes de aprobación — "
            f"ver sección <i>Gestión de instituciones</i></div>",
            unsafe_allow_html=True,
        )


def _section_map(envios: pd.DataFrame, instituciones: pd.DataFrame) -> None:
    _section("Distribución geográfica", "🗺️")
    tab1, tab2 = st.tabs(["📍 Por institución", "🗾 Por región"])
    with tab1:
        render_marker_map(envios, instituciones)
    with tab2:
        render_choropleth(envios, instituciones)


def _section_stats(envios: pd.DataFrame, instituciones: pd.DataFrame, isotopes: pd.DataFrame) -> None:
    _section("Estadísticas", "📊")

    if envios.empty:
        st.info("Sin datos de entregas aún.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        dest_counts = (
            envios.merge(instituciones[["institucion_id","nombre"]], left_on="destino_id",
                         right_on="institucion_id", how="left")
            .groupby("nombre").size().reset_index(name="n")
            .sort_values("n", ascending=True).tail(10)
        )
        if not dest_counts.empty:
            fig = go.Figure(go.Bar(
                x=dest_counts["n"], y=dest_counts["nombre"],
                orientation="h",
                marker=dict(
                    color=PASTEL_CHART[:len(dest_counts)],
                    line=dict(width=0),
                ),
                text=dest_counts["n"],
                textposition="outside",
            ))
            fig.update_layout(
                title=dict(text="Top instituciones destino", font=dict(size=13, color="#1A202C")),
                height=300, margin=dict(t=40,b=0,l=0,r=30),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(showgrid=True, gridcolor="#F7FAFC", zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False),
                font=dict(family="Inter", size=11),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        iso_counts = envios.groupby("isotopo_id").size().reset_index(name="n")
        iso_counts = iso_counts.merge(isotopes[["isotope_id","symbol"]], left_on="isotopo_id",
                                       right_on="isotope_id", how="left")
        iso_counts["symbol"] = iso_counts["symbol"].fillna("Otro")
        if not iso_counts.empty:
            fig = go.Figure(go.Pie(
                labels=iso_counts["symbol"], values=iso_counts["n"],
                marker=dict(colors=PASTEL_CHART[:len(iso_counts)],
                            line=dict(color="white", width=2)),
                hole=0.45,
                textinfo="percent+label",
                textfont=dict(size=11),
            ))
            fig.update_layout(
                title=dict(text="Por radiofármaco", font=dict(size=13, color="#1A202C")),
                height=300, margin=dict(t=40,b=0,l=0,r=0),
                paper_bgcolor="white",
                showlegend=False,
                font=dict(family="Inter"),
                annotations=[dict(text=f"<b>{iso_counts['n'].sum()}</b><br>total",
                                  x=0.5, y=0.5, font_size=14, showarrow=False,
                                  font=dict(color="#1A202C"))],
            )
            st.plotly_chart(fig, use_container_width=True)

    # Serie temporal
    if "fecha" in envios.columns:
        _section("Tendencia de entregas", "📈")

        freq_label = st.radio("Agrupación", ["Diaria", "Semanal", "Mensual"],
                               horizontal=True, key="rf_freq")
        freq_map = {"Diaria": "D", "Semanal": "W", "Mensual": "ME"}

        # Por isótopo
        if not isotopes.empty:
            merged_ts = envios.merge(isotopes[["isotope_id","symbol"]], left_on="isotopo_id",
                                      right_on="isotope_id", how="left")
            merged_ts["symbol"] = merged_ts["symbol"].fillna("Otro")
            ts_iso = (merged_ts.set_index("fecha")
                      .groupby([pd.Grouper(freq=freq_map[freq_label]), "symbol"])
                      .size().reset_index(name="n"))
            ts_iso["fecha"] = ts_iso["fecha"].dt.strftime("%Y-%m-%d")

            if not ts_iso.empty:
                iso_list = ts_iso["symbol"].unique().tolist()
                color_map = {iso: PASTEL_CHART[i % len(PASTEL_CHART)] for i, iso in enumerate(iso_list)}
                fig = px.area(
                    ts_iso, x="fecha", y="n", color="symbol",
                    color_discrete_map=color_map,
                    labels={"fecha": "", "n": "Entregas", "symbol": "Radiofármaco"},
                    height=260,
                )
                fig.update_traces(line=dict(width=2))
                fig.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=10,b=0,l=0,r=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left"),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#F7FAFC"),
                    font=dict(family="Inter", size=11),
                )
                st.plotly_chart(fig, use_container_width=True)


def _section_feed(envios: pd.DataFrame, instituciones: pd.DataFrame, isotopes: pd.DataFrame) -> None:
    _section("Últimas entregas", "🕐")

    if envios.empty:
        st.info("Sin entregas registradas aún.")
        return

    recent = envios.sort_values("llegada_dt", ascending=False).head(8)
    recent = recent.merge(instituciones[["institucion_id","nombre"]].rename(columns={"nombre":"destino"}),
                           left_on="destino_id", right_on="institucion_id", how="left")
    recent = recent.merge(isotopes[["isotope_id","symbol","color_hex"]],
                           left_on="isotopo_id", right_on="isotope_id", how="left")
    recent["symbol"] = recent["symbol"].fillna(recent.get("isotopo_texto","")).fillna("—")
    recent["color_hex"] = recent["color_hex"].fillna("#90CDF4")

    estado_icons = {"entregado": "✅", "incidente": "⚠️", "cancelado": "❌"}

    for _, row in recent.iterrows():
        hora = row.get("fecha_str", "—")
        icon = estado_icons.get(row.get("estado",""), "📦")
        color = row.get("color_hex", "#90CDF4")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:12px;padding:10px 14px;"
            f"background:white;border-radius:12px;margin-bottom:6px;"
            f"border:1.5px solid #EDF2F7;box-shadow:0 1px 4px rgba(0,0,0,0.04)'>"
            f"<div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0'></div>"
            f"<div style='flex:1;min-width:0'>"
            f"<div style='font-size:0.88rem;font-weight:600;color:#2D3748;"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
            f"{row.get('nombre_conductor','—')}</div>"
            f"<div style='font-size:0.78rem;color:#718096'>"
            f"{row.get('destino','—')} · {row.get('symbol','—')}</div>"
            f"</div>"
            f"<div style='text-align:right;flex-shrink:0'>"
            f"<div style='font-size:0.75rem;color:#A0AEC0'>{hora}</div>"
            f"<div style='font-size:1rem'>{icon}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


def _section_table(envios: pd.DataFrame, instituciones: pd.DataFrame, isotopes: pd.DataFrame) -> None:
    _section("Registro completo", "📋")

    if envios.empty:
        st.info("Sin entregas registradas.")
        return

    with st.expander("Filtros", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            estado_filter = st.multiselect("Estado", ["entregado","incidente","cancelado"],
                                            default=["entregado","incidente"], key="rf_estado_f")
        with col2:
            fecha_desde = st.date_input("Desde", value=None, key="rf_desde")
        with col3:
            fecha_hasta = st.date_input("Hasta", value=None, key="rf_hasta")

    filtered = envios.copy()
    if estado_filter:
        filtered = filtered[filtered["estado"].isin(estado_filter)]
    if fecha_desde and "llegada_dt" in filtered.columns:
        filtered = filtered[filtered["llegada_dt"].dt.date >= fecha_desde]
    if fecha_hasta and "llegada_dt" in filtered.columns:
        filtered = filtered[filtered["llegada_dt"].dt.date <= fecha_hasta]

    display = (filtered
        .merge(instituciones[["institucion_id","nombre"]].rename(columns={"nombre":"destino"}),
               left_on="destino_id", right_on="institucion_id", how="left")
        .merge(isotopes[["isotope_id","symbol"]], left_on="isotopo_id", right_on="isotope_id", how="left"))
    display["radiofarmaco"] = display["symbol"].fillna(display.get("isotopo_texto",""))
    display["llegada"] = (display["llegada_dt"].dt.tz_convert("America/Santiago").dt.strftime("%d/%m/%Y %H:%M")
                          if "llegada_dt" in display.columns else "")

    cols = ["envio_id","llegada","nombre_conductor","destino","radiofarmaco",
            "lote_numero","actividad_mbq","condicion_embalaje","estado","observaciones"]
    cols = [c for c in cols if c in display.columns]

    st.dataframe(display[cols], use_container_width=True, height=380)

    col_dl, col_upd = st.columns([2, 1])
    with col_dl:
        st.download_button("⬇️ Descargar CSV", data=_make_csv(display[cols]),
                           file_name=f"radiofarmacos_{datetime.date.today()}.csv", mime="text/csv")
    with col_upd:
        with st.popover("✏️ Cambiar estado"):
            eid = st.number_input("ID envío", min_value=1, step=1, key="rf_upd_id")
            nest = st.selectbox("Estado", ["entregado","incidente","cancelado"], key="rf_upd_est")
            if st.button("Actualizar", key="rf_upd_btn"):
                try:
                    dl.update_envio_estado(int(eid), nest)
                    st.success("✓ Actualizado")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


def _section_pendientes(instituciones_admin: pd.DataFrame) -> None:
    _section("Gestión de instituciones", "🏥")

    pendientes = (instituciones_admin[instituciones_admin["aprobada"] == False]
                  if not instituciones_admin.empty else pd.DataFrame())

    if pendientes.empty:
        st.markdown(
            f"<div style='background:{BG_GREEN};border:1.5px solid {P_GREEN};border-radius:12px;"
            f"padding:12px 16px;color:{DARK_GREEN};font-size:0.9rem'>"
            f"✅ Sin instituciones pendientes de revisión.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background:{BG_YELLOW};border:1.5px solid {P_YELLOW};border-radius:12px;"
            f"padding:12px 16px;color:#744210;font-size:0.9rem;margin-bottom:12px'>"
            f"⚠️ <b>{len(pendientes)}</b> institución(es) propuestas por conductores esperan aprobación.</div>",
            unsafe_allow_html=True,
        )
        for _, row in pendientes.iterrows():
            with st.expander(f"📍 {row['nombre']} — {row.get('ciudad','')} ({row.get('region','')})", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    lat_v = st.number_input("Latitud", value=float(row["lat"]) if row.get("lat") else -33.45,
                                             step=0.001, format="%.6f", key=f"rf_lat_{row['institucion_id']}")
                with c2:
                    lon_v = st.number_input("Longitud", value=float(row["lon"]) if row.get("lon") else -70.65,
                                             step=0.001, format="%.6f", key=f"rf_lon_{row['institucion_id']}")
                ca, cb = st.columns(2)
                with ca:
                    if st.button("✓ Aprobar", key=f"rf_apro_{row['institucion_id']}", type="primary"):
                        try:
                            dl.aprobar_institucion(int(row["institucion_id"]), lat=lat_v, lon=lon_v)
                            st.success("Aprobada.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                with cb:
                    st.caption(f"Tipo: {row.get('tipo','—')} · {str(row.get('created_at',''))[:10]}")

    # Agregar isótopo
    _section("Catálogo de isótopos", "⚗️")
    with st.expander("Agregar nuevo isótopo"):
        c1, c2 = st.columns(2)
        with c1:
            i_sym  = st.text_input("Símbolo *", placeholder="Ej: Ho-166", key="rf_iso_sym")
            i_vmh  = st.number_input("Vida media (h)", min_value=0.0, step=0.1, key="rf_iso_vmh")
        with c2:
            i_nom  = st.text_input("Nombre completo", placeholder="Ej: DOTMP de Holmio-166", key="rf_iso_nom")
            i_col  = st.color_picker("Color en mapa", value="#90CDF4", key="rf_iso_col")
        if st.button("Agregar isótopo", key="rf_iso_add"):
            if not i_sym.strip():
                st.warning("El símbolo es requerido.")
            else:
                try:
                    dl.insert_isotope({"symbol": i_sym.strip(), "nombre_completo": i_nom.strip() or None,
                                       "vida_media_h": float(i_vmh) if i_vmh else None,
                                       "color_hex": i_col, "unidad_actividad": "MBq", "activo": True})
                    st.success(f"✓ '{i_sym.strip()}' agregado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

def render(ctx: dict | None = None) -> None:
    _header()

    with st.spinner("Cargando datos…"):
        envios_raw       = dl.load_envios()
        instituciones    = dl.load_instituciones_aprobadas()
        instituciones_adm= dl.load_instituciones_admin()
        isotopes         = dl.load_isotopes()

    envios = _prep(envios_raw.copy())

    pendientes = int((instituciones_adm["aprobada"] == False).sum()) if not instituciones_adm.empty else 0

    _section_kpis(envios, pendientes)
    _section_map(envios, instituciones)
    _section_stats(envios, instituciones, isotopes)
    _section_feed(envios, instituciones, isotopes)
    _section_table(envios, instituciones, isotopes)
    _section_pendientes(instituciones_adm)
