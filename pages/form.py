"""
Formulario mobile-first para conductores.
Diseño con paleta pastel CCHEN 360.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from components.mobile_css import inject_mobile_css
import data_loader as dl

TZ = ZoneInfo("America/Santiago")
BLUE      = "#2B6CB0"
BLUE_SOFT = "#EBF8FF"
TEAL      = "#2C7A6A"
GRAY      = "#4A5568"
LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo.png"


def _now_cl() -> datetime.datetime:
    return datetime.datetime.now(tz=TZ)


def _header() -> None:
    if LOGO_PATH.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown(
            f"<div style='text-align:center;padding:8px 0 0'>"
            f"<span style='font-size:1.6rem;font-weight:800;color:{BLUE};"
            f"letter-spacing:-1px'>CCHEN <span style='color:#90CDF4'>360</span></span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<div style='text-align:center;padding:6px 0 12px'>"
        f"<div style='display:inline-block;background:{BLUE_SOFT};border-radius:20px;"
        f"padding:5px 16px;font-size:0.82rem;font-weight:600;color:{BLUE};"
        f"letter-spacing:0.5px'>REGISTRO DE ENTREGA</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _progress_bar(step: int) -> None:
    steps = ["Quién eres", "Datos del envío", "Condición"]
    dots = ""
    for i, label in enumerate(steps, 1):
        active = i == step
        done   = i < step
        color  = BLUE if (active or done) else "#CBD5E0"
        bg     = BLUE_SOFT if active else ("white" if not done else BLUE_SOFT)
        border = f"2px solid {BLUE}" if active else ("2px solid #CBD5E0" if not done else f"2px solid {BLUE}")
        num    = "✓" if done else str(i)
        dots  += (
            f"<div style='display:flex;flex-direction:column;align-items:center;flex:1'>"
            f"<div style='width:28px;height:28px;border-radius:50%;{border};"
            f"background:{bg};display:flex;align-items:center;justify-content:center;"
            f"font-size:0.75rem;font-weight:700;color:{color}'>{num}</div>"
            f"<span style='font-size:0.65rem;color:{color};margin-top:3px;"
            f"font-weight:{'600' if active else '400'};text-align:center'>{label}</span>"
            f"</div>"
        )
        if i < len(steps):
            dots += f"<div style='flex:1;height:2px;background:{'#BEE3F8' if done or active else '#E2E8F0'};margin-top:14px'></div>"

    st.markdown(
        f"<div style='display:flex;align-items:flex-start;gap:0;margin:0 0 20px;padding:12px 8px;"
        f"background:white;border-radius:14px;border:1px solid #EBF4FF'>{dots}</div>",
        unsafe_allow_html=True,
    )


def _card_start(color: str = "#EBF8FF", border: str = "#BEE3F8") -> None:
    st.markdown(
        f"<div style='background:{color};border:1.5px solid {border};"
        f"border-radius:16px;padding:16px 14px 4px;margin-bottom:12px'>",
        unsafe_allow_html=True,
    )


def _card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def _section_label(icon: str, text: str) -> None:
    st.markdown(
        f"<p style='font-size:0.82rem;font-weight:700;color:{BLUE};"
        f"text-transform:uppercase;letter-spacing:0.6px;margin:0 0 10px'>"
        f"{icon} {text}</p>",
        unsafe_allow_html=True,
    )


def _confirmation_screen(envio: dict, instituciones_df, isotopes_df) -> None:
    inst_nombre = "—"
    if envio.get("destino_id") and not instituciones_df.empty:
        row = instituciones_df[instituciones_df["institucion_id"] == envio["destino_id"]]
        if not row.empty:
            inst_nombre = row.iloc[0]["nombre"]

    isotopo_label = envio.get("isotopo_texto") or "—"
    if envio.get("isotopo_id") and not isotopes_df.empty:
        row = isotopes_df[isotopes_df["isotope_id"] == envio["isotopo_id"]]
        if not row.empty:
            isotopo_label = row.iloc[0]["symbol"]

    ref = str(envio.get("uuid", ""))[:8].upper()

    st.markdown(
        f"<div style='text-align:center;padding:24px 0 8px'>"
        f"<div style='width:56px;height:56px;border-radius:50%;background:#F0FFF4;"
        f"border:2px solid #9AE6B4;display:flex;align-items:center;justify-content:center;"
        f"margin:0 auto 12px'>"
        f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' "
        f"fill='none' stroke='#276749' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
        f"<polyline points='20 6 9 17 4 12'/></svg></div>"
        f"<h3 style='color:#276749;margin:0 0 4px'>Entrega registrada</h3>"
        f"<p style='color:#4A5568;font-size:0.9rem;margin:0'>Todo quedó guardado correctamente.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='background:white;border-radius:16px;padding:20px;"
        f"border:1.5px solid #C6F6D5;margin:16px 0'>"
        f"<p style='font-size:0.72rem;font-weight:700;color:#276749;"
        f"text-transform:uppercase;letter-spacing:0.6px;margin:0 0 12px'>Comprobante</p>"
        f"<div style='background:#F0FFF4;border-radius:10px;padding:10px 14px;margin-bottom:14px'>"
        f"<span style='font-family:monospace;font-size:1.2rem;font-weight:800;"
        f"color:#276749;letter-spacing:2px'>RF-{ref}</span>"
        f"</div>"
        f"<table style='width:100%;border-collapse:collapse;font-size:0.9rem'>"
        f"<tr><td style='padding:5px 0;color:#718096;width:40%'>Conductor</td>"
        f"<td style='padding:5px 0;font-weight:600;color:#2D3748'>{envio.get('nombre_conductor','')}</td></tr>"
        f"<tr><td style='padding:5px 0;color:#718096'>Destino</td>"
        f"<td style='padding:5px 0;font-weight:600;color:#2D3748'>{inst_nombre}</td></tr>"
        f"<tr><td style='padding:5px 0;color:#718096'>Radiofármaco</td>"
        f"<td style='padding:5px 0;font-weight:600;color:#2D3748'>{isotopo_label}</td></tr>"
        f"<tr><td style='padding:5px 0;color:#718096'>Lote</td>"
        f"<td style='padding:5px 0;font-weight:600;color:#2D3748'>{envio.get('lote_numero','')}</td></tr>"
        f"</table>"
        f"<p style='font-size:0.75rem;color:#A0AEC0;margin:12px 0 0;text-align:center'>"
        f"Guarda el código RF-{ref} para consultas.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if st.button("Registrar otra entrega", use_container_width=True):
        for key in [k for k in st.session_state if k.startswith("rf_form_") or k.startswith("rf_ni_")]:
            del st.session_state[key]
        st.session_state.pop("rf_submitted_envio", None)
        st.rerun()


def render() -> None:
    inject_mobile_css()

    if "rf_submitted_envio" in st.session_state:
        _header()
        instituciones_df = dl.load_instituciones_aprobadas()
        isotopes_df = dl.load_isotopes()
        _confirmation_screen(st.session_state["rf_submitted_envio"], instituciones_df, isotopes_df)
        return

    _header()

    step = st.session_state.get("rf_step", 1)
    _progress_bar(step)

    with st.spinner(""):
        instituciones_df = dl.load_instituciones_aprobadas()
        isotopes_df = dl.load_isotopes()

    # ── PASO 1: Identificación ──────────────────────────────
    if step == 1:
        _section_label("", "¿Quién eres?")

        # Pre-llenado con la última sesión del conductor
        nombre_prev = st.session_state.get("rf_conductor_nombre", "")
        inst_prev   = st.session_state.get("rf_conductor_inst", "")

        nombre_conductor = st.text_input(
            "Nombre completo *",
            value=nombre_prev,
            key="rf_form_nombre",
            placeholder="Ej: Juan Pérez González",
        )
        institucion_conductor = st.text_input(
            "Tu institución",
            value=inst_prev,
            key="rf_form_inst_conductor",
            placeholder="Ej: Hospital San Juan de Dios",
        )

        if nombre_prev:
            st.caption("Tus datos se recordaron de la última vez.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Continuar", use_container_width=True, type="primary"):
            if not nombre_conductor.strip():
                st.error("Ingresa tu nombre para continuar.")
            else:
                # Guardar en memoria persistente (sobrevive al reset del formulario)
                st.session_state["rf_conductor_nombre"] = nombre_conductor.strip()
                st.session_state["rf_conductor_inst"]   = institucion_conductor.strip()
                st.session_state["rf_step"] = 2
                st.rerun()

    # ── PASO 2: Destino + producto ──────────────────────────
    elif step == 2:
        _section_label("", "¿Qué y adónde?")

        # Institución destino
        inst_opts = ["— Selecciona hospital / clínica —"]
        inst_map: dict[str, int] = {}
        if not instituciones_df.empty:
            for _, row in instituciones_df.iterrows():
                lbl = f"{row['nombre']} ({row.get('region','')})" if row.get("region") else row["nombre"]
                inst_opts.append(lbl)
                inst_map[lbl] = int(row["institucion_id"])
        inst_opts.append("＋ Agregar nueva institución")

        destino_sel = st.selectbox("Institución destino *", inst_opts, key="rf_form_destino_sel")

        nueva_inst_id: int | None = st.session_state.get("rf_form_nueva_inst_id")
        if destino_sel == "＋ Agregar nueva institución":
            with st.expander("Datos de la nueva institución", expanded=True):
                ni_nombre = st.text_input("Nombre completo *", key="rf_ni_nombre")
                ni_ciudad = st.text_input("Ciudad", key="rf_ni_ciudad")
                ni_region = st.selectbox("Región", [
                    "— Selecciona —", "Arica y Parinacota", "Tarapacá", "Antofagasta",
                    "Atacama", "Coquimbo", "Valparaíso", "Metropolitana", "O'Higgins",
                    "Maule", "Ñuble", "Biobío", "Araucanía", "Los Ríos",
                    "Los Lagos", "Aysén", "Magallanes",
                ], key="rf_ni_region")
                ni_tipo = st.selectbox("Tipo", ["hospital", "clinica", "laboratorio", "otro"], key="rf_ni_tipo")
                if st.button("Agregar institución", key="rf_add_inst"):
                    if not ni_nombre.strip():
                        st.warning("El nombre es requerido.")
                    else:
                        try:
                            nueva = dl.insert_institucion_nueva({
                                "nombre": ni_nombre.strip(),
                                "ciudad": ni_ciudad.strip() or None,
                                "region": ni_region if ni_region != "— Selecciona —" else None,
                                "tipo": ni_tipo,
                            })
                            st.session_state["rf_form_nueva_inst_id"]     = nueva.get("institucion_id")
                            st.session_state["rf_form_nueva_inst_nombre"] = ni_nombre.strip()
                            st.success(f"'{ni_nombre.strip()}' agregada — quedará disponible tras aprobación.")
                        except Exception as e:
                            st.error(f"Error: {e}")
            nueva_inst_id = st.session_state.get("rf_form_nueva_inst_id")
            if nueva_inst_id:
                st.info(f"Se usará: {st.session_state.get('rf_form_nueva_inst_nombre','')}")

        # Isótopo
        iso_opts = ["— Selecciona radiofármaco —"]
        iso_map: dict[str, int] = {}
        if not isotopes_df.empty:
            for _, row in isotopes_df.iterrows():
                lbl = row["symbol"]
                if row.get("nombre_completo"):
                    lbl += f" — {row['nombre_completo']}"
                iso_opts.append(lbl)
                iso_map[lbl] = int(row["isotope_id"])
        iso_opts.append("Otro (especificar)")

        isotopo_sel = st.selectbox("Radiofármaco *", iso_opts, key="rf_form_isotopo_sel")
        if isotopo_sel == "Otro (especificar)":
            st.text_input("Especifica el radiofármaco", key="rf_form_isotopo_otro")

        st.text_input(
            "N° de lote / cápsula *",
            key="rf_form_lote",
            placeholder="Ej: CCH-2026-0042",
            help="Tal como aparece en la etiqueta del paquete",
        )

        # ── Datos técnicos opcionales ───────────────────────
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        with st.expander("Datos técnicos — ver etiqueta del paquete (opcional)"):
            now_cl = _now_cl()

            actividad_mbq = st.number_input(
                "Actividad (MBq)", min_value=0.0, step=1.0, format="%.1f",
                key="rf_form_actividad",
                help="1 MBq = 0.027 mCi",
            )
            if actividad_mbq > 0:
                st.caption(f"≈ {actividad_mbq/37:.2f} mCi")

            st.markdown("**Fecha y hora de referencia de actividad**")
            c1, c2 = st.columns(2)
            with c1:
                st.date_input("Fecha ref.", value=now_cl.date(),
                              key="rf_form_ref_date", label_visibility="collapsed")
            with c2:
                st.time_input("Hora ref.", value=now_cl.time().replace(second=0, microsecond=0),
                              key="rf_form_ref_time", label_visibility="collapsed")

            st.markdown("**Hora de salida de CCHEN**")
            c3, c4 = st.columns(2)
            with c3:
                st.date_input("Fecha salida", value=now_cl.date(),
                              key="rf_form_sal_date", label_visibility="collapsed")
            with c4:
                st.time_input("Hora salida", value=now_cl.time().replace(second=0, microsecond=0),
                              key="rf_form_sal_time", label_visibility="collapsed")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("Volver", use_container_width=True):
                st.session_state["rf_step"] = 1
                st.rerun()
        with col_next:
            if st.button("Continuar", use_container_width=True, type="primary"):
                lote_numero = st.session_state.get("rf_form_lote", "").strip()
                errs = []
                if destino_sel == "— Selecciona hospital / clínica —":
                    errs.append("Selecciona la institución destino.")
                if destino_sel == "＋ Agregar nueva institución" and not nueva_inst_id:
                    errs.append("Agrega la institución antes de continuar.")
                if isotopo_sel == "— Selecciona radiofármaco —":
                    errs.append("Selecciona el radiofármaco.")
                if not lote_numero:
                    errs.append("El número de lote es requerido.")
                if errs:
                    for e in errs:
                        st.error(e)
                else:
                    now_cl2 = _now_cl()
                    ref_date  = st.session_state.get("rf_form_ref_date",  now_cl2.date())
                    ref_time  = st.session_state.get("rf_form_ref_time",  now_cl2.time().replace(second=0, microsecond=0))
                    sal_date  = st.session_state.get("rf_form_sal_date",  now_cl2.date())
                    sal_time  = st.session_state.get("rf_form_sal_time",  now_cl2.time().replace(second=0, microsecond=0))
                    st.session_state["rf_form_ref_dt"] = datetime.datetime.combine(ref_date, ref_time, tzinfo=TZ).isoformat()
                    st.session_state["rf_form_sal_dt"] = datetime.datetime.combine(sal_date,  sal_time,  tzinfo=TZ).isoformat()
                    st.session_state["rf_step"] = 3
                    st.rerun()

    # ── PASO 3: Condición ───────────────────────────────────
    elif step == 3:
        _section_label("", "Condición de entrega")

        # 1. Condición del embalaje — lo primero y más importante
        condicion_map = {"OK": "ok", "Revisar": "revisar", "Dañado": "danado"}
        condicion_sel = st.radio(
            "Estado del embalaje *",
            list(condicion_map.keys()),
            horizontal=True,
            key="rf_form_condicion",
        )

        # 2. Temperatura (opcional)
        temperatura_c = st.number_input(
            "Temperatura (°C) — opcional",
            min_value=-30.0, max_value=60.0,
            step=0.5, format="%.1f",
            value=None,
            key="rf_form_temp",
        )

        # 3. Observaciones (opcional)
        observaciones = st.text_area(
            "Observaciones — opcional",
            height=80,
            key="rf_form_obs",
            placeholder="Incidencias, condiciones especiales, etc.",
        )

        # 4. Hora de llegada — al fondo, auto = ahora
        now_cl = _now_cl()
        hora_str = now_cl.strftime("%H:%M")
        st.markdown(
            f"<div style='background:#F7FAFC;border-radius:10px;padding:10px 14px;"
            f"font-size:0.85rem;color:#4A5568;margin:8px 0 4px'>"
            f"Hora de llegada registrada: <b>{hora_str}</b></div>",
            unsafe_allow_html=True,
        )
        modificar_hora = st.checkbox("Modificar hora de llegada", key="rf_form_mod_hora")
        if modificar_hora:
            c1, c2 = st.columns(2)
            with c1:
                ll_date = st.date_input("Fecha llegada", value=now_cl.date(),
                                        key="rf_form_ll_date", label_visibility="collapsed")
            with c2:
                ll_time = st.time_input("Hora llegada",
                                        value=now_cl.time().replace(second=0, microsecond=0),
                                        key="rf_form_ll_time", label_visibility="collapsed")
        else:
            ll_date = now_cl.date()
            ll_time = now_cl.time().replace(second=0, microsecond=0)

        st.divider()

        col_back, _ = st.columns([1, 2])
        with col_back:
            if st.button("Volver", use_container_width=True):
                st.session_state["rf_step"] = 2
                st.rerun()

        if st.button("Registrar entrega", use_container_width=True, type="primary"):
            instituciones_df2 = dl.load_instituciones_aprobadas()
            origen_id: int | None = None
            if not instituciones_df2.empty:
                cchen = instituciones_df2[instituciones_df2.get("es_origen", False) == True]
                if not cchen.empty:
                    origen_id = int(cchen.iloc[0]["institucion_id"])

            destino_sel2 = st.session_state.get("rf_form_destino_sel", "")
            inst_map2: dict[str, int] = {}
            if not instituciones_df2.empty:
                for _, row in instituciones_df2.iterrows():
                    lbl = f"{row['nombre']} ({row.get('region','')})" if row.get("region") else row["nombre"]
                    inst_map2[lbl] = int(row["institucion_id"])
            final_destino = (st.session_state.get("rf_form_nueva_inst_id")
                             if destino_sel2 == "＋ Agregar nueva institución"
                             else inst_map2.get(destino_sel2))

            isotopo_sel2 = st.session_state.get("rf_form_isotopo_sel", "")
            iso_map2: dict[str, int] = {}
            if not isotopes_df.empty:
                for _, row in isotopes_df.iterrows():
                    lbl = row["symbol"]
                    if row.get("nombre_completo"):
                        lbl += f" — {row['nombre_completo']}"
                    iso_map2[lbl] = int(row["isotope_id"])
            isotopo_id2    = iso_map2.get(isotopo_sel2)
            isotopo_texto2 = (st.session_state.get("rf_form_isotopo_otro")
                              if isotopo_sel2 == "Otro (especificar)" else None)

            payload = {
                "nombre_conductor":      st.session_state.get("rf_conductor_nombre", ""),
                "institucion_conductor": st.session_state.get("rf_conductor_inst") or None,
                "origen_id":             origen_id,
                "destino_id":            final_destino,
                "isotopo_id":            isotopo_id2,
                "isotopo_texto":         isotopo_texto2 or None,
                "lote_numero":           st.session_state.get("rf_form_lote", "").strip(),
                "actividad_mbq":         float(st.session_state.get("rf_form_actividad", 0)) or None,
                "actividad_ref_dt":      st.session_state.get("rf_form_ref_dt"),
                "salida_dt":             st.session_state.get("rf_form_sal_dt"),
                "llegada_dt":            datetime.datetime.combine(ll_date, ll_time, tzinfo=TZ).isoformat(),
                "condicion_embalaje":    condicion_map[condicion_sel],
                "temperatura_c":         float(temperatura_c) if temperatura_c is not None else None,
                "observaciones":         observaciones.strip() or None,
                "estado":                "entregado",
            }

            with st.spinner("Guardando…"):
                try:
                    result = dl.insert_envio(payload)
                    # Limpiar formulario pero conservar nombre y institución del conductor
                    for key in [k for k in st.session_state
                                if k.startswith("rf_form_") or k.startswith("rf_ni_")]:
                        del st.session_state[key]
                    st.session_state.pop("rf_step", None)
                    st.session_state["rf_submitted_envio"] = result
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
