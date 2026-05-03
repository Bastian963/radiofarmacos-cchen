"""
Formulario mobile-first para conductores.
Accessible en /?view=form (o simplemente /)
Sin autenticación — cualquier conductor puede registrar una entrega.
"""
from __future__ import annotations

import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from components.mobile_css import inject_mobile_css
import data_loader as dl

TZ = ZoneInfo("America/Santiago")
BLUE = "#003B6F"
RED = "#C8102E"


def _now_cl() -> datetime.datetime:
    return datetime.datetime.now(tz=TZ)


def _header() -> None:
    st.markdown(
        f"<div style='text-align:center;padding:18px 0 8px'>"
        f"<div style='font-size:2rem'>☢️</div>"
        f"<h2 style='color:{BLUE};margin:4px 0 2px;font-size:1.4rem'>Registro de Entrega</h2>"
        f"<p style='color:#64748B;font-size:0.85rem;margin:0'>Radiofarmacos · CCHEN</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.divider()


def _step_badge(n: int, label: str) -> None:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;margin:16px 0 8px'>"
        f"<div style='background:{BLUE};color:white;border-radius:50%;width:24px;height:24px;"
        f"display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:700;flex-shrink:0'>{n}</div>"
        f"<span style='color:#0F172A;font-weight:600;font-size:0.95rem'>{label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _confirmation_screen(envio: dict, instituciones_df, isotopes_df) -> None:
    inst_nombre = "—"
    if envio.get("destino_id"):
        row = instituciones_df[instituciones_df["institucion_id"] == envio["destino_id"]]
        if not row.empty:
            inst_nombre = row.iloc[0]["nombre"]

    isotopo_label = envio.get("isotopo_texto") or "—"
    if envio.get("isotopo_id"):
        row = isotopes_df[isotopes_df["isotope_id"] == envio["isotopo_id"]]
        if not row.empty:
            isotopo_label = row.iloc[0]["symbol"]

    st.success("**Entrega registrada exitosamente**")
    st.markdown(
        f"<div style='background:#F0F9FF;border-radius:12px;padding:16px;border-left:4px solid {BLUE}'>"
        f"<p style='margin:0 0 6px;color:#64748B;font-size:0.8rem;font-weight:600;text-transform:uppercase'>Comprobante</p>"
        f"<p style='font-family:monospace;font-size:1.05rem;font-weight:700;color:{BLUE};margin:0 0 12px'>"
        f"RF-{str(envio.get('uuid',''))[:8].upper()}</p>"
        f"<table style='width:100%;border-collapse:collapse;font-size:0.9rem'>"
        f"<tr><td style='padding:3px 0;color:#64748B'>Conductor</td>"
        f"<td style='padding:3px 0;font-weight:500'>{envio.get('nombre_conductor','')}</td></tr>"
        f"<tr><td style='padding:3px 0;color:#64748B'>Destino</td>"
        f"<td style='padding:3px 0;font-weight:500'>{inst_nombre}</td></tr>"
        f"<tr><td style='padding:3px 0;color:#64748B'>Radiofarmaco</td>"
        f"<td style='padding:3px 0;font-weight:500'>{isotopo_label}</td></tr>"
        f"<tr><td style='padding:3px 0;color:#64748B'>Lote</td>"
        f"<td style='padding:3px 0;font-weight:500'>{envio.get('lote_numero','')}</td></tr>"
        f"<tr><td style='padding:3px 0;color:#64748B'>Llegada</td>"
        f"<td style='padding:3px 0;font-weight:500'>{envio.get('llegada_dt','')}</td></tr>"
        f"</table></div>",
        unsafe_allow_html=True,
    )
    st.caption("Guarda el código de referencia para consultas.")
    if st.button("Registrar otra entrega", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("rf_form_"):
                del st.session_state[key]
        st.session_state.pop("rf_submitted_envio", None)
        st.rerun()


def render() -> None:
    inject_mobile_css()
    _header()

    # Pantalla de confirmación si ya se envió
    if "rf_submitted_envio" in st.session_state:
        instituciones_df = dl.load_instituciones_aprobadas()
        isotopes_df = dl.load_isotopes()
        _confirmation_screen(st.session_state["rf_submitted_envio"], instituciones_df, isotopes_df)
        return

    # ── Cargar catálogos ─────────────────────────────────────
    with st.spinner("Cargando formulario…"):
        instituciones_df = dl.load_instituciones_aprobadas()
        isotopes_df = dl.load_isotopes()

    # ── Sección 1: Identificación del conductor ──────────────
    _step_badge(1, "¿Quién eres?")

    nombre_conductor = st.text_input(
        "Tu nombre completo *",
        key="rf_form_nombre",
        placeholder="Ej: Juan Pérez González",
    )
    institucion_conductor = st.text_input(
        "Institución a la que perteneces",
        key="rf_form_inst_conductor",
        placeholder="Ej: Hospital San Juan de Dios",
    )

    # ── Sección 2: Datos del envío ───────────────────────────
    _step_badge(2, "Datos del envío")

    # Destino
    inst_opts = ["— Selecciona institución destino —"]
    inst_map: dict[str, int] = {}
    if not instituciones_df.empty:
        for _, row in instituciones_df.iterrows():
            label = f"{row['nombre']} ({row.get('region', '')})" if row.get("region") else row["nombre"]
            inst_opts.append(label)
            inst_map[label] = int(row["institucion_id"])
    inst_opts.append("+ Agregar nueva institución")

    destino_sel = st.selectbox("Institución destino *", inst_opts, key="rf_form_destino_sel")
    destino_id: int | None = inst_map.get(destino_sel)

    # Agregar nueva institución
    nueva_inst_id: int | None = None
    if destino_sel == "+ Agregar nueva institución":
        with st.expander("Datos de la nueva institución", expanded=True):
            ni_nombre = st.text_input("Nombre completo *", key="rf_ni_nombre", placeholder="Hospital Regional de…")
            ni_ciudad = st.text_input("Ciudad", key="rf_ni_ciudad")
            ni_region = st.selectbox(
                "Región",
                ["— Selecciona —", "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama",
                 "Coquimbo", "Valparaíso", "Metropolitana", "O'Higgins", "Maule",
                 "Ñuble", "Biobío", "Araucanía", "Los Ríos", "Los Lagos",
                 "Aysén", "Magallanes"],
                key="rf_ni_region",
            )
            ni_tipo = st.selectbox("Tipo", ["hospital", "clinica", "laboratorio", "otro"], key="rf_ni_tipo")
            if st.button("Agregar institución al sistema", key="rf_add_inst"):
                if not ni_nombre.strip():
                    st.warning("El nombre de la institución es requerido.")
                else:
                    try:
                        nueva = dl.insert_institucion_nueva({
                            "nombre": ni_nombre.strip(),
                            "ciudad": ni_ciudad.strip() or None,
                            "region": ni_region if ni_region != "— Selecciona —" else None,
                            "tipo": ni_tipo,
                        })
                        nueva_inst_id = nueva.get("institucion_id")
                        st.session_state["rf_form_nueva_inst_id"] = nueva_inst_id
                        st.session_state["rf_form_nueva_inst_nombre"] = ni_nombre.strip()
                        st.success(f"✓ '{ni_nombre.strip()}' agregada. Quedará disponible tras revisión del administrador.")
                    except Exception as e:
                        st.error(f"Error al agregar institución: {e}")

        nueva_inst_id = st.session_state.get("rf_form_nueva_inst_id")
        if nueva_inst_id:
            st.info(f"Se usará: {st.session_state.get('rf_form_nueva_inst_nombre', '')}")

    # Isótopo
    iso_opts = ["— Selecciona radiofarmaco —"]
    iso_map: dict[str, int] = {}
    if not isotopes_df.empty:
        for _, row in isotopes_df.iterrows():
            label = f"{row['symbol']}"
            if row.get("nombre_completo"):
                label += f" — {row['nombre_completo']}"
            iso_opts.append(label)
            iso_map[label] = int(row["isotope_id"])
    iso_opts.append("Otro (especificar)")

    isotopo_sel = st.selectbox("Radiofarmaco *", iso_opts, key="rf_form_isotopo_sel")
    isotopo_id: int | None = iso_map.get(isotopo_sel)
    isotopo_texto: str | None = None
    if isotopo_sel == "Otro (especificar)":
        isotopo_texto = st.text_input("Especifica el radiofarmaco", key="rf_form_isotopo_otro",
                                      placeholder="Ej: Ho-166 DOTMP")

    lote_numero = st.text_input("Número de lote / cápsula *", key="rf_form_lote",
                                 placeholder="Ej: CCH-2026-0042")

    actividad_mbq = st.number_input(
        "Actividad (MBq)", min_value=0.0, step=1.0, format="%.1f", key="rf_form_actividad"
    )
    if actividad_mbq > 0:
        st.caption(f"≈ {actividad_mbq / 37:.2f} mCi")

    now_cl = _now_cl()
    col_ref_d, col_ref_t = st.columns(2)
    with col_ref_d:
        ref_date = st.date_input("Fecha ref. actividad", value=now_cl.date(), key="rf_form_ref_date")
    with col_ref_t:
        ref_time = st.time_input("Hora ref.", value=now_cl.time().replace(second=0, microsecond=0), key="rf_form_ref_time")
    actividad_ref_dt = datetime.datetime.combine(ref_date, ref_time, tzinfo=TZ).isoformat()

    col_sal_d, col_sal_t = st.columns(2)
    with col_sal_d:
        salida_date = st.date_input("Fecha salida de CCHEN", value=now_cl.date(), key="rf_form_sal_date")
    with col_sal_t:
        salida_time = st.time_input("Hora salida", value=now_cl.time().replace(second=0, microsecond=0), key="rf_form_sal_time")
    salida_dt = datetime.datetime.combine(salida_date, salida_time, tzinfo=TZ).isoformat()

    col_ll_d, col_ll_t = st.columns(2)
    with col_ll_d:
        llegada_date = st.date_input("Fecha llegada (hoy)", value=now_cl.date(), key="rf_form_ll_date")
    with col_ll_t:
        llegada_time = st.time_input("Hora llegada", value=now_cl.time().replace(second=0, microsecond=0), key="rf_form_ll_time")
    llegada_dt = datetime.datetime.combine(llegada_date, llegada_time, tzinfo=TZ).isoformat()

    # ── Sección 3: Condición de entrega ──────────────────────
    _step_badge(3, "Condición de entrega")

    condicion_map = {"✓ OK": "ok", "⚠ Revisar": "revisar", "✗ Dañado": "danado"}
    condicion_sel = st.radio(
        "Estado del embalaje *",
        list(condicion_map.keys()),
        horizontal=True,
        key="rf_form_condicion",
    )
    condicion_embalaje = condicion_map[condicion_sel]

    temperatura_c = st.number_input(
        "Temperatura (°C) — opcional",
        min_value=-30.0, max_value=60.0, step=0.5, format="%.1f",
        value=None,
        key="rf_form_temp",
    )

    observaciones = st.text_area(
        "Observaciones",
        height=80,
        key="rf_form_obs",
        placeholder="Incidencias, condiciones especiales de transporte, etc.",
    )

    st.divider()

    # ── Validación y envío ────────────────────────────────────
    if st.button("📦 Registrar entrega", use_container_width=True, type="primary"):
        errors: list[str] = []
        if not nombre_conductor.strip():
            errors.append("Tu nombre es requerido.")
        if destino_sel == "— Selecciona institución destino —":
            errors.append("Selecciona o agrega la institución destino.")
        if destino_sel == "+ Agregar nueva institución" and not nueva_inst_id:
            errors.append("Agrega la nueva institución antes de enviar.")
        if isotopo_sel == "— Selecciona radiofarmaco —":
            errors.append("Selecciona el radiofarmaco.")
        if not lote_numero.strip():
            errors.append("El número de lote es requerido.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            # Origen: buscar CCHEN (es_origen=TRUE)
            origen_id: int | None = None
            if not instituciones_df.empty:
                cchen_rows = instituciones_df[instituciones_df.get("es_origen", False) == True]
                if not cchen_rows.empty:
                    origen_id = int(cchen_rows.iloc[0]["institucion_id"])

            final_destino_id = nueva_inst_id if (destino_sel == "+ Agregar nueva institución") else destino_id

            payload: dict = {
                "nombre_conductor": nombre_conductor.strip(),
                "institucion_conductor": institucion_conductor.strip() or None,
                "origen_id": origen_id,
                "destino_id": final_destino_id,
                "isotopo_id": isotopo_id,
                "isotopo_texto": isotopo_texto or None,
                "lote_numero": lote_numero.strip(),
                "actividad_mbq": float(actividad_mbq) if actividad_mbq else None,
                "actividad_ref_dt": actividad_ref_dt if actividad_mbq else None,
                "salida_dt": salida_dt,
                "llegada_dt": llegada_dt,
                "condicion_embalaje": condicion_embalaje,
                "temperatura_c": float(temperatura_c) if temperatura_c is not None else None,
                "observaciones": observaciones.strip() or None,
                "estado": "entregado",
            }

            with st.spinner("Guardando…"):
                try:
                    result = dl.insert_envio(payload)
                    st.session_state["rf_submitted_envio"] = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
