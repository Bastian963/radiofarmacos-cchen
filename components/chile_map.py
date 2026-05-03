"""
Mapas de Chile para el dashboard de radiofarmacos.
Usa plotly scatter_mapbox con carto-positron (sin token Mapbox).
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BLUE = "#003B6F"
RED = "#C8102E"

COLOR_MAP = {
    "CCHEN":       RED,
    "hospital":    BLUE,
    "clinica":     "#00A896",
    "laboratorio": "#7B2D8B",
    "otro":        "#F4A60D",
}

_CHILE_GEOJSON_URL = (
    "https://raw.githubusercontent.com/fcortes/Chile-GeoJSON/master/Regional.geojson"
)


@st.cache_data(ttl=86400, show_spinner=False)
def _load_chile_geojson() -> dict:
    import requests
    try:
        r = requests.get(_CHILE_GEOJSON_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def render_marker_map(envios_df: pd.DataFrame, instituciones_df: pd.DataFrame) -> None:
    """Mapa de burbujas: tamaño proporcional a n° de entregas por institución."""
    if instituciones_df.empty:
        st.info("Sin datos de instituciones para mostrar en el mapa.")
        return

    inst = instituciones_df.copy()

    if not envios_df.empty:
        counts = (
            envios_df.groupby("destino_id")
            .size()
            .reset_index(name="n_envios")
        )
        inst = inst.merge(counts, left_on="institucion_id", right_on="destino_id", how="left")
    inst["n_envios"] = inst.get("n_envios", 0).fillna(0).astype(int)
    inst["tipo"] = inst.get("tipo", "otro").fillna("otro")

    # Solo instituciones con coordenadas
    map_df = inst.dropna(subset=["lat", "lon"]).copy()
    if map_df.empty:
        st.info("Las instituciones aún no tienen coordenadas. Agrega lat/lon desde el panel de administración.")
        return

    map_df["size_col"] = map_df["n_envios"].clip(lower=1)
    map_df["label"] = map_df.apply(
        lambda r: f"{r['nombre']}<br>Región: {r.get('region','—')}<br>Entregas: {r['n_envios']}", axis=1
    )

    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="size_col",
        color="tipo",
        hover_name="nombre",
        custom_data=["n_envios", "region", "ciudad"],
        size_max=40,
        zoom=3.8,
        center={"lat": -33.45, "lon": -70.65},
        mapbox_style="carto-positron",
        color_discrete_map=COLOR_MAP,
        height=520,
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Región: %{customdata[1]}<br>Ciudad: %{customdata[2]}<br>Entregas: %{customdata[0]}<extra></extra>"
    )

    # Líneas de ruta (últimas 30 entregas con coordenadas)
    if not envios_df.empty:
        recent = envios_df.sort_values("llegada_dt", ascending=False).head(30)
        for _, row in recent.iterrows():
            orig = inst[inst["institucion_id"] == row.get("origen_id")]
            dest = inst[inst["institucion_id"] == row.get("destino_id")]
            if orig.empty or dest.empty:
                continue
            o, d = orig.iloc[0], dest.iloc[0]
            if pd.isna(o.get("lat")) or pd.isna(d.get("lat")):
                continue
            fig.add_scattermapbox(
                lat=[o["lat"], d["lat"]],
                lon=[o["lon"], d["lon"]],
                mode="lines",
                line={"width": 1.5, "color": f"rgba(0,59,111,0.25)"},
                showlegend=False,
                hoverinfo="skip",
            )

    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        legend={"title": "Tipo", "bgcolor": "rgba(255,255,255,0.8)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_choropleth(envios_df: pd.DataFrame, instituciones_df: pd.DataFrame) -> None:
    """Choropleth de Chile coloreado por número de entregas por región."""
    if envios_df.empty or instituciones_df.empty:
        st.info("Sin datos suficientes para el mapa regional.")
        return

    geojson = _load_chile_geojson()
    if not geojson:
        st.warning("No se pudo cargar el GeoJSON de regiones de Chile (requiere conexión a internet).")
        return

    merged = envios_df.merge(
        instituciones_df[["institucion_id", "region"]],
        left_on="destino_id",
        right_on="institucion_id",
        how="left",
    )
    region_counts = (
        merged.dropna(subset=["region"])
        .groupby("region")
        .size()
        .reset_index(name="n_envios")
    )

    if region_counts.empty:
        st.info("No hay entregas con información de región todavía.")
        return

    fig = px.choropleth_mapbox(
        region_counts,
        geojson=geojson,
        featureidkey="properties.Region",
        locations="region",
        color="n_envios",
        color_continuous_scale=[[0, "#E3EEF9"], [0.5, "#6BAED6"], [1, BLUE]],
        labels={"n_envios": "Entregas"},
        mapbox_style="carto-positron",
        zoom=3.5,
        center={"lat": -35.5, "lon": -71.5},
        height=500,
        opacity=0.7,
    )
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        coloraxis_colorbar={"title": "Entregas", "len": 0.5},
    )
    st.plotly_chart(fig, use_container_width=True)
