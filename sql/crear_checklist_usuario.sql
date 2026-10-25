-- Trámite Claro
-- Crea la tabla de checklist generados para usuarios.
-- Cuando un usuario selecciona un trámite, se genera un checklist personalizado
-- que puede ir marcando mientras reúne los documentos.

USE tramite_claro;

CREATE TABLE IF NOT EXISTS checklist_usuario (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tramite_id INT UNSIGNED NOT NULL COMMENT 'Trámite para el cual se generó este checklist',
    usuario_nombre VARCHAR(200) NULL COMMENT 'Nombre del usuario (opcional, por si queremos identificar al usuario)',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Cuándo se generó el checklist',
    fecha_ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Última vez que se marcó un item',
    estado ENUM('en_progreso', 'completado', 'abandonado') DEFAULT 'en_progreso' COMMENT 'Estado actual del checklist',
    items_json JSON NOT NULL COMMENT 'Lista de items del checklist con su estado (marcado/no marcado)',
    notas_usuario TEXT NULL COMMENT 'Notas personales del usuario sobre el trámite',
    porcentaje_completado DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Porcentaje de items completados (0.00 a 100.00)',
    PRIMARY KEY (id),
    FOREIGN KEY (tramite_id) REFERENCES tramites(id) ON DELETE CASCADE,
    INDEX idx_tramite (tramite_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_creacion (fecha_creacion)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci
  COMMENT='Checklists personalizados generados para usuarios con seguimiento de progreso';

-- Ejemplo de estructura JSON para items_json:
-- {
--   "items": [
--     {
--       "id": 1,
--       "nombre": "Identificación oficial vigente",
--       "completado": true,
--       "fecha_marcado": "2026-10-25T12:30:00"
--     },
--     {
--       "id": 2,
--       "nombre": "Comprobante de domicilio",
--       "completado": false,
--       "fecha_marcado": null
--     }
--   ]
-- }
