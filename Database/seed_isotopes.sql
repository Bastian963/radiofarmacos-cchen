-- Seed: Catálogo inicial de isótopos/radiofarmacos
-- Ejecutar DESPUÉS de schema_radiofarmacia.sql
-- Agregar más desde la interfaz admin de la aplicación

INSERT INTO rf_isotopes (symbol, nombre_completo, vida_media_h, unidad_actividad, color_hex, activo)
VALUES
    ('I-131',   'Yoduro de sodio I-131',           192.0,  'MBq', '#C8102E', TRUE),
    ('Tc-99m',  'Pertecnetato de sodio Tc-99m',    6.02,   'MBq', '#003B6F', TRUE),
    ('Lu-177',  'Cloruro de Lutecio-177',           161.4,  'MBq', '#00A896', TRUE),
    ('Ga-68',   'Cloruro de Galio-68',              1.13,   'MBq', '#F4A60D', TRUE),
    ('F-18',    'Fluorodeoxiglucosa F-18 (FDG)',    1.83,   'MBq', '#7B2D8B', TRUE),
    ('Sm-153',  'EDTMP de Samario-153',             46.3,   'MBq', '#E76F51', TRUE),
    ('Y-90',    'Cloruro de Itrio-90',              64.1,   'MBq', '#52B788', TRUE),
    ('Ra-223',  'Dicloruro de Radio-223',           276.0,  'MBq', '#264653', TRUE),
    ('In-111',  'Cloruro de Indio-111',             67.3,   'MBq', '#6B4226', TRUE),
    ('P-32',    'Fosfato de Fósforo-32 (crónico)',  342.0,  'MBq', '#8B0000', TRUE),
    ('Otro',    'Otro (especificar en observaciones)', NULL, 'MBq', '#94A3B8', TRUE)
ON CONFLICT (symbol) DO NOTHING;
