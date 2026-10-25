-- Trámite Claro
-- Crea la tabla de documentos oficiales que se pueden requerir en los trámites.
-- Esta tabla contiene un catálogo de documentos con descripciones muy detalladas
-- escritas en lenguaje simple (nivel primaria).

USE tramite_claro;

CREATE TABLE IF NOT EXISTS documentos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL COMMENT 'Nombre del documento (ej: Identificación oficial vigente)',
    descripcion TEXT NOT NULL COMMENT 'Explicación muy detallada en lenguaje simple, como para un niño de primaria',
    tipo ENUM('original', 'copia', 'copia_certificada', 'digital') NOT NULL DEFAULT 'original' COMMENT 'Tipo de documento requerido',
    vigencia VARCHAR(100) NULL COMMENT 'Requisitos de vigencia (ej: No mayor a 3 meses)',
    ejemplos TEXT NULL COMMENT 'Ejemplos concretos separados por comas (ej: INE, pasaporte, cédula profesional)',
    categoria VARCHAR(50) NULL COMMENT 'Categoría del documento (identificacion, comprobante, acta, fiscal, etc)',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_categoria (categoria),
    INDEX idx_tipo (tipo)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Catálogo de documentos oficiales con descripciones detalladas en lenguaje simple';
