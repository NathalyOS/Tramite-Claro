-- Trámite Claro
-- Crea la tabla de pasos del trámite.
-- Cada trámite tiene varios pasos ordenados que el usuario debe seguir.
-- Cada paso tiene una descripción MUY detallada en lenguaje simple.

USE tramite_claro;

CREATE TABLE IF NOT EXISTS pasos_tramite (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tramite_id INT UNSIGNED NOT NULL COMMENT 'Relación con la tabla tramites',
    numero_paso INT NOT NULL COMMENT 'Orden del paso (1, 2, 3, etc)',
    titulo VARCHAR(200) NOT NULL COMMENT 'Título corto del paso (ej: Reunir documentos)',
    descripcion TEXT NOT NULL COMMENT 'Explicación MUY detallada del paso, en lenguaje simple como para un niño de primaria',
    tiempo_estimado VARCHAR(50) NULL COMMENT 'Tiempo aproximado para completar este paso (ej: 1-2 días, 30 minutos)',
    consejos TEXT NULL COMMENT 'Tips y advertencias útiles para este paso, separados por pipes (|)',
    es_opcional BOOLEAN DEFAULT FALSE COMMENT 'Indica si este paso puede omitirse en algunos casos',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (tramite_id) REFERENCES tramites(id) ON DELETE CASCADE,
    INDEX idx_tramite_numero (tramite_id, numero_paso),
    UNIQUE KEY unique_tramite_paso (tramite_id, numero_paso)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Pasos ordenados de cada trámite con descripciones muy detalladas';
