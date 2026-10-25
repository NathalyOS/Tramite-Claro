-- Trámite Claro
-- Actualiza la tabla tramites existente para agregar nuevos campos
-- que complementan la información básica del trámite.

USE tramite_claro;

-- Agregar columna de categoría si no existe
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS categoria VARCHAR(100) NULL COMMENT 'Categoría del trámite (Internacional, Nacional, Vehicular, etc)'
AFTER nombre;

-- Agregar columna de duración estimada si no existe
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS duracion_estimada VARCHAR(100) NULL COMMENT 'Tiempo aproximado para completar el trámite (ej: 2-3 semanas)'
AFTER requerimientos;

-- Agregar columna de dificultad si no existe
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS dificultad ENUM('baja', 'media', 'alta') DEFAULT 'media' COMMENT 'Nivel de complejidad del trámite'
AFTER duracion_estimada;

-- Agregar columna de descripción simple si no existe
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS descripcion_simple TEXT NULL COMMENT 'Descripción breve y clara en lenguaje simple'
AFTER dificultad;

-- Agregar columna de documentación disponible si no existe
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS tiene_pasos_detallados BOOLEAN DEFAULT FALSE COMMENT 'Indica si el trámite tiene pasos detallados en la tabla pasos_tramite'
AFTER descripcion_simple;

-- Agregar índices para mejorar las consultas
CREATE INDEX IF NOT EXISTS idx_categoria ON tramites(categoria);
CREATE INDEX IF NOT EXISTS idx_dificultad ON tramites(dificultad);

-- Agregar columnas de auditoría si no existen
ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del registro'
AFTER tiene_pasos_detallados;

ALTER TABLE tramites 
ADD COLUMN IF NOT EXISTS fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Última actualización del registro'
AFTER fecha_creacion;
