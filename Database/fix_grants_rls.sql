-- ============================================================
-- FIX: Permisos faltantes para anon en tablas rf_*
-- Pegar y ejecutar en Supabase > SQL Editor
-- ============================================================

-- anon (conductores — formulario público, sin autenticación)
GRANT SELECT ON rf_isotopes      TO anon;
GRANT SELECT ON rf_instituciones TO anon;
GRANT INSERT ON rf_instituciones TO anon;
GRANT INSERT ON rf_envios        TO anon;
GRANT USAGE, SELECT ON SEQUENCE rf_envios_envio_id_seq                  TO anon;
GRANT USAGE, SELECT ON SEQUENCE rf_instituciones_institucion_id_seq     TO anon;

-- authenticated (admin dashboard)
GRANT ALL ON rf_isotopes         TO authenticated;
GRANT ALL ON rf_instituciones    TO authenticated;
GRANT ALL ON rf_envios           TO authenticated;
GRANT ALL ON SEQUENCE rf_envios_envio_id_seq                            TO authenticated;
GRANT ALL ON SEQUENCE rf_instituciones_institucion_id_seq               TO authenticated;
GRANT ALL ON SEQUENCE rf_isotopes_isotope_id_seq                        TO authenticated;
