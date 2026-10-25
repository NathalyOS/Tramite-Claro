-- Trámite Claro
-- Crea la tabla tramites en la base que ya existe.
-- Columnas del diagrama: ID, NOMBRE, PROCESO, REQUERIMIENTOS, LUGAR, COSTOS.
--
-- El esquema en MySQL se llama tramite_claro (la conexión de Workbench es "Tramite Claro").
USE tramite_claro;

CREATE TABLE IF NOT EXISTS tramites (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    proceso TEXT NOT NULL,
    requerimientos TEXT NOT NULL,
    lugar VARCHAR(255) NOT NULL,
    costos VARCHAR(150) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;
