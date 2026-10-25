# 📂 Carpeta SQL - Trámite Claro

Esta carpeta contiene todos los scripts SQL necesarios para crear y poblar la base de datos del sistema Trámite Claro.

## 🗃️ Base de Datos

- **Nombre**: `tramite_claro`
- **Motor**: MySQL 8.0+
- **Charset**: utf8mb4
- **Collation**: utf8mb4_0900_ai_ci

## 📋 Orden de Ejecución

Es **MUY IMPORTANTE** ejecutar los scripts en este orden exacto:

### 1️⃣ Creación de Tablas Base

```bash
# 1. Primero crear la tabla principal de trámites (si no existe)
mysql -u root -p tramite_claro < crear_tramites.sql

# 2. Actualizar la tabla tramites con nuevos campos
mysql -u root -p tramite_claro < actualizar_tramites.sql

# 3. Crear tabla de documentos
mysql -u root -p tramite_claro < crear_documentos.sql

# 4. Crear tabla de pasos de trámite
mysql -u root -p tramite_claro < crear_pasos_tramite.sql

# 5. Crear tabla de relación documentos por paso
mysql -u root -p tramite_claro < crear_documentos_por_paso.sql

# 6. Crear tabla de checklist de usuario
mysql -u root -p tramite_claro < crear_checklist_usuario.sql
```

### 2️⃣ Inserción de Datos Iniciales (Seeds)

```bash
# 7. Poblar catálogo de documentos
mysql -u root -p tramite_claro < seed_documentos.sql

# 8. Poblar trámites completos con sus pasos (cuando esté listo)
# mysql -u root -p tramite_claro < seed_tramites_completos.sql
```

## 📊 Estructura de Tablas

### tramites (Tabla Principal)
- Información básica de cada trámite
- Campos: id, nombre, categoria, proceso, requerimientos, lugar, costos, duracion_estimada, dificultad, descripcion_simple

### documentos
- Catálogo de documentos oficiales
- Descripciones MUY detalladas en lenguaje simple
- Campos: id, nombre, descripcion, tipo, vigencia, ejemplos, categoria

### pasos_tramite
- Pasos ordenados de cada trámite
- Explicaciones paso a paso nivel primaria
- Campos: id, tramite_id, numero_paso, titulo, descripcion, tiempo_estimado, consejos, es_opcional

### documentos_por_paso
- Relación many-to-many
- Conecta qué documentos se necesitan en cada paso
- Campos: id, paso_id, documento_id, es_obligatorio, cantidad, notas_especiales

### checklist_usuario
- Checklists personalizados generados
- Seguimiento de progreso del usuario
- Campos: id, tramite_id, usuario_nombre, estado, items_json, porcentaje_completado

## 🔄 Relaciones entre Tablas

```
tramites (1) ──→ (N) pasos_tramite
pasos_tramite (N) ──→ (N) documentos (a través de documentos_por_paso)
tramites (1) ──→ (N) checklist_usuario
```

## 📝 Notas Importantes

1. **Idioma**: Todas las descripciones están en español con nivel de detalle "primaria"
2. **Charset**: utf8mb4 permite emojis y caracteres especiales
3. **Foreign Keys**: Configuradas con `ON DELETE CASCADE` para mantener integridad referencial
4. **Índices**: Agregados en campos que se consultan frecuentemente
5. **Timestamps**: Todas las tablas tienen fecha_creacion y fecha_actualizacion automáticas

## 🛠️ Comandos Útiles

### Crear la base de datos (si no existe)
```sql
CREATE DATABASE IF NOT EXISTS tramite_claro
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;
```

### Ver todas las tablas
```sql
USE tramite_claro;
SHOW TABLES;
```

### Ver estructura de una tabla
```sql
DESCRIBE tramites;
DESCRIBE documentos;
DESCRIBE pasos_tramite;
```

### Verificar relaciones
```sql
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'tramite_claro'
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

## 🔧 Troubleshooting

### Error: "Table already exists"
No hay problema, los scripts usan `IF NOT EXISTS` y `IF NOT EXISTS` en ALTER TABLE.

### Error: "Cannot add foreign key"
Asegúrate de ejecutar los scripts en el orden correcto. Las tablas referenciadas deben existir primero.

### Error: "Unknown database tramite_claro"
Crea la base de datos primero:
```bash
mysql -u root -p -e "CREATE DATABASE tramite_claro CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;"
```

## 📚 Recursos

- Archivos JSON con datos detallados: `/workspace/info/tramites/`
- Esquema de validación JSON: `/workspace/info/esquema.json`
- Documentación del proyecto: `/workspace/info/README.md`
