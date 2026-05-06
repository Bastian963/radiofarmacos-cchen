-- ============================================================
-- Schema: Seguimiento de Radiofarmacos CCHEN
-- Prefijo rf_ para evitar colisión con tablas del observatorio
-- Aplicar en Supabase SQL Editor (Dashboard > SQL Editor)
-- ============================================================

-- Extensión UUID (ya habilitada en Supabase por defecto)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tabla 1: Catálogo de isótopos/radiofarmacos ──────────────

DROP TABLE IF EXISTS rf_envios;
DROP TABLE IF EXISTS rf_instituciones;
DROP TABLE IF EXISTS rf_isotopes;

CREATE TABLE IF NOT EXISTS rf_isotopes (
    isotope_id       SERIAL PRIMARY KEY,
    symbol           TEXT NOT NULL UNIQUE,
    nombre_completo  TEXT,
    vida_media_h     NUMERIC,
    unidad_actividad TEXT NOT NULL DEFAULT 'MBq',
    color_hex        TEXT NOT NULL DEFAULT '#003B6F',
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE rf_isotopes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "rf_isotopes_public_read"  ON rf_isotopes;
DROP POLICY IF EXISTS "rf_isotopes_auth_write"   ON rf_isotopes;

CREATE POLICY "rf_isotopes_public_read"
    ON rf_isotopes FOR SELECT USING (TRUE);

CREATE POLICY "rf_isotopes_auth_write"
    ON rf_isotopes FOR ALL
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');


-- ── Tabla 2: Instituciones (catálogo progresivo) ─────────────

CREATE TABLE IF NOT EXISTS rf_instituciones (
    institucion_id   SERIAL PRIMARY KEY,
    nombre           TEXT NOT NULL,
    nombre_corto     TEXT,
    tipo             TEXT NOT NULL DEFAULT 'hospital'
        CHECK (tipo IN ('hospital','clinica','CCHEN','laboratorio','otro')),
    region           TEXT,
    ciudad           TEXT,
    lat              NUMERIC(9,6),
    lon              NUMERIC(9,6),
    aprobada         BOOLEAN NOT NULL DEFAULT FALSE,
    es_origen        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rf_instituciones_aprobada ON rf_instituciones(aprobada);
CREATE INDEX IF NOT EXISTS idx_rf_instituciones_region   ON rf_instituciones(region);

ALTER TABLE rf_instituciones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "rf_instituciones_public_read"    ON rf_instituciones;
DROP POLICY IF EXISTS "rf_instituciones_public_insert"  ON rf_instituciones;
DROP POLICY IF EXISTS "rf_instituciones_auth_update"    ON rf_instituciones;

-- Conductores ven solo las aprobadas (para el dropdown)
CREATE POLICY "rf_instituciones_public_read"
    ON rf_instituciones FOR SELECT USING (aprobada = TRUE);

-- Conductores pueden proponer nuevas instituciones
CREATE POLICY "rf_instituciones_public_insert"
    ON rf_instituciones FOR INSERT WITH CHECK (TRUE);

-- Admin puede actualizar (aprobar, agregar lat/lon, etc.)
CREATE POLICY "rf_instituciones_auth_update"
    ON rf_instituciones FOR UPDATE
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');


-- ── Tabla 3: Envíos/Entregas (tabla principal) ───────────────

CREATE TABLE IF NOT EXISTS rf_envios (
    envio_id              SERIAL PRIMARY KEY,
    uuid                  UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    nombre_conductor      TEXT,
    institucion_conductor TEXT,
    origen_id             INTEGER REFERENCES rf_instituciones(institucion_id),
    destino_id            INTEGER REFERENCES rf_instituciones(institucion_id),
    isotopo_id            INTEGER REFERENCES rf_isotopes(isotope_id),
    isotopo_texto         TEXT,
    lote_numero           TEXT NOT NULL,
    actividad_mbq         NUMERIC(12,3),
    actividad_ref_dt      TIMESTAMP WITH TIME ZONE,
    salida_dt             TIMESTAMP WITH TIME ZONE,
    llegada_dt            TIMESTAMP WITH TIME ZONE NOT NULL,
    condicion_embalaje    TEXT NOT NULL DEFAULT 'ok'
        CHECK (condicion_embalaje IN ('ok','revisar','danado')),
    temperatura_c         NUMERIC(5,2),
    observaciones         TEXT,
    estado                TEXT NOT NULL DEFAULT 'entregado'
        CHECK (estado IN ('entregado','incidente','cancelado')),
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rf_envios_destino    ON rf_envios(destino_id);
CREATE INDEX IF NOT EXISTS idx_rf_envios_isotopo    ON rf_envios(isotopo_id);
CREATE INDEX IF NOT EXISTS idx_rf_envios_llegada    ON rf_envios(llegada_dt);
CREATE INDEX IF NOT EXISTS idx_rf_envios_estado     ON rf_envios(estado);
CREATE INDEX IF NOT EXISTS idx_rf_envios_conductor  ON rf_envios(nombre_conductor);

ALTER TABLE rf_envios ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "rf_envios_public_insert" ON rf_envios;
DROP POLICY IF EXISTS "rf_envios_auth_read"     ON rf_envios;
DROP POLICY IF EXISTS "rf_envios_auth_update"   ON rf_envios;

-- Conductores pueden registrar nuevas entregas (sin autenticación)
CREATE POLICY "rf_envios_public_insert"
    ON rf_envios FOR INSERT
    TO anon
    WITH CHECK (TRUE);

-- Solo admin lee y modifica los datos
CREATE POLICY "rf_envios_auth_read"
    ON rf_envios FOR SELECT
    TO authenticated
    USING (TRUE);

CREATE POLICY "rf_envios_auth_update"
    ON rf_envios FOR UPDATE
    TO authenticated
    USING (TRUE)
    WITH CHECK (TRUE);

-- ── Permisos de tabla (GRANT) ─────────────────────────────────────────────
-- RLS controla qué filas; GRANT controla qué operaciones puede intentar cada rol.
-- Sin estos GRANT, el anon key queda bloqueado a nivel de tabla incluso con
-- políticas RLS permisivas.

-- anon (conductores, formulario público)
GRANT SELECT ON rf_isotopes      TO anon;
GRANT SELECT ON rf_instituciones TO anon;
GRANT INSERT ON rf_instituciones TO anon;   -- agregar nueva institución al vuelo
GRANT INSERT ON rf_envios        TO anon;
GRANT USAGE, SELECT ON SEQUENCE rf_envios_envio_id_seq        TO anon;
GRANT USAGE, SELECT ON SEQUENCE rf_instituciones_institucion_id_seq TO anon;

-- authenticated (admin dashboard)
GRANT ALL ON rf_isotopes         TO authenticated;
GRANT ALL ON rf_instituciones    TO authenticated;
GRANT ALL ON rf_envios           TO authenticated;
GRANT ALL ON SEQUENCE rf_envios_envio_id_seq                  TO authenticated;
GRANT ALL ON SEQUENCE rf_instituciones_institucion_id_seq     TO authenticated;
GRANT ALL ON SEQUENCE rf_isotopes_isotope_id_seq              TO authenticated;
