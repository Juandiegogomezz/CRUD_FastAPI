-- Consultas de verificacion (Integrante 2): equivalentes SQL de los endpoints C, D y G.

-- C: GET /personas/estadisticas/dominios
SELECT SUBSTRING_INDEX(email, '@', -1) AS dominio, COUNT(*) AS total
FROM personas
GROUP BY dominio
ORDER BY total DESC;

-- D: GET /personas/estadisticas/edad
SELECT ROUND(AVG(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())), 1) AS edad_promedio,
       MIN(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS edad_minima,
       MAX(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS edad_maxima
FROM personas
WHERE birth_date IS NOT NULL;