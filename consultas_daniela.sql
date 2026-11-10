USE fastapi_demo;

-- E. Buscador (comparar con GET /personas/buscar/lopez)
SELECT * FROM personas
WHERE first_name LIKE '%lopez%' OR last_name LIKE '%lopez%' OR email LIKE '%lopez%';

-- F. Activos (comparar con GET /personas/reporte/activos)
SELECT id, email, phone, is_active FROM personas WHERE is_active = 1;
SELECT COUNT(*) FROM personas WHERE is_active = 1;

-- H. Estado de los IDs enviados al PATCH bulk (cambiar por los IDs usados)
SELECT id, is_active FROM personas WHERE id IN (1, 2, 99999);