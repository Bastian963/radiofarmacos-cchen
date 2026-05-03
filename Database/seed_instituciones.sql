-- Seed: Instituciones iniciales (CCHEN + hospitales principales Chile)
-- Las nuevas se agregan progresivamente desde el formulario de conductores
-- aprobada=TRUE para que aparezcan en el dropdown; es_origen=TRUE solo para CCHEN

INSERT INTO rf_instituciones (nombre, nombre_corto, tipo, region, ciudad, lat, lon, aprobada, es_origen)
VALUES
    -- Origen
    ('CCHEN - La Reina',                         'CCHEN',           'CCHEN',     'Metropolitana', 'La Reina',     -33.4443, -70.5657, TRUE, TRUE),

    -- Región Metropolitana
    ('Hospital San Juan de Dios',                'H. San Juan',     'hospital',  'Metropolitana', 'Santiago',     -33.4453, -70.6718, TRUE, FALSE),
    ('Hospital del Salvador',                    'H. Salvador',     'hospital',  'Metropolitana', 'Providencia',  -33.4354, -70.6057, TRUE, FALSE),
    ('Hospital Clínico U. de Chile',             'HCUChile',        'hospital',  'Metropolitana', 'Santiago',     -33.4585, -70.6639, TRUE, FALSE),
    ('Hospital Base Luis Calvo Mackenna',        'H. Calvo Mack.',  'hospital',  'Metropolitana', 'Ñuñoa',        -33.4540, -70.6103, TRUE, FALSE),
    ('Hospital Barros Luco-Trudeau',             'H. Barros Luco',  'hospital',  'Metropolitana', 'San Miguel',   -33.4982, -70.6570, TRUE, FALSE),
    ('Hospital El Pino',                         'H. El Pino',      'hospital',  'Metropolitana', 'El Bosque',    -33.5490, -70.6700, TRUE, FALSE),
    ('Clínica Las Condes',                       'Clínica LC',      'clinica',   'Metropolitana', 'Las Condes',   -33.4060, -70.5780, TRUE, FALSE),
    ('Clínica Santa María',                      'Clínica SM',      'clinica',   'Metropolitana', 'Providencia',  -33.4252, -70.6103, TRUE, FALSE),
    ('Hospital DIPRECA',                         'H. DIPRECA',      'hospital',  'Metropolitana', 'Las Condes',   -33.4008, -70.5783, TRUE, FALSE),

    -- Región de Valparaíso
    ('Hospital Carlos Van Buren',                'H. Van Buren',    'hospital',  'Valparaíso',    'Valparaíso',   -33.0433, -71.6163, TRUE, FALSE),
    ('Hospital Dr. Eduardo Pereira',             'H. Pereira',      'hospital',  'Valparaíso',    'Valparaíso',   -33.0358, -71.6218, TRUE, FALSE),

    -- Región del Biobío
    ('Hospital Guillermo Grant Benavente',       'H. Concepción',   'hospital',  'Biobío',        'Concepción',   -36.8213, -73.0527, TRUE, FALSE),

    -- Región de la Araucanía
    ('Hospital Regional de Temuco',              'H. Temuco',       'hospital',  'Araucanía',     'Temuco',       -38.7304, -72.5909, TRUE, FALSE),

    -- Región de Los Ríos
    ('Hospital Base Valdivia',                   'H. Valdivia',     'hospital',  'Los Ríos',      'Valdivia',     -39.8135, -73.2418, TRUE, FALSE),

    -- Región de Los Lagos
    ('Hospital Puerto Montt',                    'H. Pto. Montt',   'hospital',  'Los Lagos',     'Puerto Montt', -41.4695, -72.9435, TRUE, FALSE),

    -- Región de Antofagasta
    ('Hospital Regional de Antofagasta',         'H. Antofagasta',  'hospital',  'Antofagasta',   'Antofagasta',  -23.6457, -70.3973, TRUE, FALSE),

    -- Región de Tarapacá
    ('Hospital Regional Dr. Juan Noé Crevani',   'H. Arica',        'hospital',  'Arica y Parinacota', 'Arica',  -18.4783, -70.3126, TRUE, FALSE)

ON CONFLICT DO NOTHING;
