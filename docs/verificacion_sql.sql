-- Consultas de verificacion (Integrante 2): equivalentes SQL de los endpoints C, D y G.

-- C: GET /personas/estadisticas/dominios
SELECT SUBSTRING_INDEX(email, '@', -1) AS dominio, COUNT(*) AS total
FROM personas
GROUP BY dominio
ORDER BY total DESC;
