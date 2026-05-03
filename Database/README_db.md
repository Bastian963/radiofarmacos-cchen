# Base de Datos — Radiofarmacos CCHEN

## Aplicar en Supabase

1. Ir a **Supabase Dashboard → SQL Editor**
2. Ejecutar en orden:
   - `schema_radiofarmacia.sql` — crea las 3 tablas `rf_*` y políticas RLS
   - `seed_isotopes.sql` — carga isótopos iniciales
   - `seed_instituciones.sql` — carga CCHEN + hospitales principales

## Tablas

| Tabla | Descripción | RLS INSERT | RLS SELECT |
|-------|-------------|-----------|-----------|
| `rf_isotopes` | Catálogo de isótopos | solo auth | público |
| `rf_instituciones` | Hospitales y clínicas | público (conductores proponen) | público (solo aprobadas) |
| `rf_envios` | Entregas registradas | público (formulario) | solo auth (admin) |

## Columna `aprobada` en `rf_instituciones`

Las instituciones nuevas que agregan los conductores llegan con `aprobada=FALSE` y no aparecen en el dropdown hasta que un admin las apruebe desde el panel de administración.

## Agregar isótopos o instituciones

Desde la interfaz admin de la app (`?view=admin`) o directamente en Supabase SQL Editor con:

```sql
INSERT INTO rf_isotopes (symbol, nombre_completo, vida_media_h, unidad_actividad, color_hex)
VALUES ('Ho-166', 'DOTMP de Holmio-166', 26.8, 'MBq', '#8B4513');

INSERT INTO rf_instituciones (nombre, tipo, region, ciudad, lat, lon, aprobada)
VALUES ('Hospital Regional Rancagua', 'hospital', "O'Higgins", 'Rancagua', -34.1703, -70.7406, TRUE);
```
