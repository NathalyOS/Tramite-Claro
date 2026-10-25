-- Trámite Claro
-- Crea la tabla de relación entre pasos y documentos.
-- Esta tabla conecta qué documentos se necesitan en cada paso del trámite.
-- Un paso puede requerir varios documentos, y un documento puede usarse en varios pasos.

USE tramite_claro;

CREATE TABLE IF NOT EXISTS documentos_por_paso (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    paso_id INT UNSIGNED NOT NULL COMMENT 'Relación con la tabla pasos_tramite',
    documento_id INT UNSIGNED NOT NULL COMMENT 'Relación con la tabla documentos',
    es_obligatorio BOOLEAN DEFAULT TRUE COMMENT 'Si el documento es obligatorio u opcional en este paso',
    cantidad INT DEFAULT 1 COMMENT 'Cuántas copias se necesitan (1, 2, 3, etc)',
    notas_especiales TEXT NULL COMMENT 'Aclaraciones específicas del documento en este paso particular',
    orden_presentacion INT DEFAULT 0 COMMENT 'Orden en que se debe presentar el documento dentro del paso',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (paso_id) REFERENCES pasos_tramite(id) ON DELETE CASCADE,
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    INDEX idx_paso (paso_id),
    INDEX idx_documento (documento_id),
    INDEX idx_obligatorio (es_obligatorio),
    UNIQUE KEY unique_paso_documento (paso_id, documento_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Relación many-to-many entre pasos de trámites y documentos requeridos';
