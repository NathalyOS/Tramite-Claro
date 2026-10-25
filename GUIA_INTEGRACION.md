# 🚀 Guía de Integración - Trámite Claro

Esta guía explica cómo integrar toda la nueva funcionalidad creada (historias 2.2 y 3.1) con el proyecto existente.

## 📋 ¿Qué se agregó?

### 1. Nueva Estructura de Base de Datos

Se crearon 5 nuevas tablas para manejar documentos y checklists:

- **`documentos`**: Catálogo de documentos oficiales con descripciones detalladas
- **`pasos_tramite`**: Pasos ordenados de cada trámite
- **`documentos_por_paso`**: Relación de qué documentos se necesitan en cada paso
- **`checklist_usuario`**: Checklists personalizados para usuarios
- **`tramites`** (actualizada): Nuevos campos agregados

### 2. Carpeta `/info/tramites/`

11 archivos JSON con trámites complejos documentados a detalle nivel primaria:
1. visa-americana.json
2. cambio-propietario-vehiculo.json
3. pasaporte-primera-vez.json
4. apostilla-documentos.json
5. rfc-persona-fisica.json
6. licencia-conducir.json
7. escrituras-propiedad.json
8. testamento.json
9. residencia-temporal-mexico.json
10. acta-nacimiento.json
11. permiso-menor-viajar.json

### 3. Scripts SQL Listos

En `/workspace/sql/` tienes todos los scripts necesarios para crear la estructura.

---

## 🔧 Pasos para Integrar

### Paso 1: Ejecutar Scripts SQL

```bash
# Asegúrate de tener MySQL corriendo
# Conéctate a MySQL
mysql -u root -p

# Dentro de MySQL:
USE tramite_claro;

# Ejecuta los scripts EN ESTE ORDEN:
source /workspace/sql/actualizar_tramites.sql
source /workspace/sql/crear_documentos.sql
source /workspace/sql/crear_pasos_tramite.sql
source /workspace/sql/crear_documentos_por_paso.sql
source /workspace/sql/crear_checklist_usuario.sql

# Poblar catálogo de documentos:
source /workspace/sql/seed_documentos.sql

# Salir
exit;
```

O desde la terminal directamente:

```bash
cd /workspace
mysql -u root -p tramite_claro < sql/actualizar_tramites.sql
mysql -u root -p tramite_claro < sql/crear_documentos.sql
mysql -u root -p tramite_claro < sql/crear_pasos_tramite.sql
mysql -u root -p tramite_claro < sql/crear_documentos_por_paso.sql
mysql -u root -p tramite_claro < sql/crear_checklist_usuario.sql
mysql -u root -p tramite_claro < sql/seed_documentos.sql
```

### Paso 2: Configurar Conexión a MySQL

El archivo `/workspace/src/conexion.py` ya está actualizado. Solo necesitas:

1. **Configurar tu contraseña de MySQL**:
   - Edita `conexion.py` y pon tu contraseña en la línea:
     ```python
     password=os.getenv('DB_PASSWORD', 'TU_CONTRASEÑA_AQUI')
     ```
   - O mejor aún, usa variables de entorno:
     ```bash
     export DB_PASSWORD="tu_contraseña"
     export DB_USER="root"
     export DB_NAME="tramite_claro"
     ```

2. **Probar la conexión**:
   ```bash
   cd /workspace/src
   python conexion.py
   ```

### Paso 3: Usar los JSON en tu Aplicación

Los archivos JSON en `/workspace/info/tramites/` tienen toda la información detallada. Puedes:

**Opción A: Leerlos directamente desde Flask**

```python
import json
from flask import Flask, render_template

@app.route('/tramite/<tramite_id>')
def ver_tramite(tramite_id):
    # Leer el JSON del trámite
    with open(f'/workspace/info/tramites/{tramite_id}.json', 'r', encoding='utf-8') as f:
        tramite_data = json.load(f)
    
    return render_template('ver_tramite.html', tramite=tramite_data)
```

**Opción B: Poblar la base de datos desde los JSON**

Crea un script para importar los datos de los JSON a las tablas:

```python
import json
import glob
from conexion import obtener_conexion

def importar_tramites_desde_json():
    conexion = obtener_conexion()
    if not conexion:
        return
    
    cursor = conexion.cursor()
    
    # Leer todos los JSON
    archivos_json = glob.glob('/workspace/info/tramites/*.json')
    
    for archivo in archivos_json:
        with open(archivo, 'r', encoding='utf-8') as f:
            tramite_data = json.load(f)
        
        # Insertar en tabla tramites
        cursor.execute("""
            INSERT INTO tramites 
            (nombre, categoria, duracion_estimada, dificultad, costos, descripcion_simple, tiene_pasos_detallados) 
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (
            tramite_data['nombre'],
            tramite_data['categoria'],
            tramite_data['duracion_estimada'],
            tramite_data['dificultad'],
            tramite_data['costo_aproximado'],
            tramite_data['descripcion_simple']
        ))
        
        tramite_id = cursor.lastrowid
        
        # Insertar pasos
        for paso in tramite_data['pasos']:
            cursor.execute("""
                INSERT INTO pasos_tramite 
                (tramite_id, numero_paso, titulo, descripcion, tiempo_estimado, consejos) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                tramite_id,
                paso['numero'],
                paso['titulo'],
                paso['descripcion'],
                paso.get('tiempo_estimado', ''),
                '|'.join(paso.get('consejos', []))
            ))
        
        conexion.commit()
    
    cursor.close()
    conexion.close()
    print(f"✓ Importados {len(archivos_json)} trámites a la base de datos")

if __name__ == '__main__':
    importar_tramites_desde_json()
```

---

## 🎨 Actualizar las Vistas

### Mostrar Documentos por Paso (Historia 2.2)

En tu template `guia-tramite.html` o similar:

```html
<div class="pasos-tramite">
    {% for paso in tramite.pasos %}
    <div class="paso">
        <h3>Paso {{ paso.numero }}: {{ paso.titulo }}</h3>
        <p>{{ paso.descripcion }}</p>
        
        <!-- DOCUMENTOS REQUERIDOS EN ESTE PASO -->
        {% if paso.documentos_requeridos %}
        <div class="documentos-paso">
            <h4>📄 Documentos para este paso:</h4>
            {% for doc in paso.documentos_requeridos %}
            <div class="documento">
                <label>
                    <input type="checkbox" name="doc_{{ paso.numero }}_{{ loop.index }}">
                    <strong>{{ doc.nombre }}</strong>
                    {% if doc.obligatorio %}
                    <span class="badge bg-danger">Obligatorio</span>
                    {% else %}
                    <span class="badge bg-secondary">Opcional</span>
                    {% endif %}
                </label>
                <p class="descripcion">{{ doc.descripcion }}</p>
                <small class="text-muted">
                    Tipo: {{ doc.tipo }} | Cantidad: {{ doc.cantidad }}
                </small>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="alert alert-info">Sin documentos en este paso</p>
        {% endif %}
    </div>
    {% endfor %}
</div>
```

### Generar Checklist (Historia 3.1)

Nueva ruta en Flask:

```python
@app.route('/tramite/<tramite_id>/checklist')
def generar_checklist(tramite_id):
    # Opción 1: Desde JSON
    with open(f'/workspace/info/tramites/{tramite_id}.json', 'r', encoding='utf-8') as f:
        tramite_data = json.load(f)
    
    # Opción 2: Desde BD
    # conexion = obtener_conexion()
    # cursor = conexion.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM tramites WHERE id = %s", (tramite_id,))
    # tramite = cursor.fetchone()
    
    checklist_items = tramite_data.get('checklist_completo', {})
    
    return render_template('checklist.html', 
                         tramite=tramite_data,
                         checklist=checklist_items)
```

Template `checklist.html`:

```html
<div class="checklist-container">
    <h2>✅ Checklist: {{ tramite.nombre }}</h2>
    
    <div class="seccion-checklist">
        <h3>Documentos Obligatorios</h3>
        {% if checklist.documentos_obligatorios %}
        {% for item in checklist.documentos_obligatorios %}
        <div class="checklist-item">
            <label>
                <input type="checkbox" class="form-check-input" 
                       onchange="actualizarProgreso()">
                {{ item }}
            </label>
        </div>
        {% endfor %}
        {% else %}
        <p class="alert alert-warning">Checklist no disponible para este trámite</p>
        {% endif %}
    </div>
    
    <div class="seccion-checklist">
        <h3>Documentos Opcionales</h3>
        {% for item in checklist.documentos_opcionales %}
        <div class="checklist-item opcional">
            <label>
                <input type="checkbox" class="form-check-input">
                {{ item }}
            </label>
        </div>
        {% endfor %}
    </div>
    
    <!-- Progreso -->
    <div class="progress mt-4">
        <div id="barra-progreso" class="progress-bar" 
             role="progressbar" style="width: 0%">0%</div>
    </div>
</div>

<script>
function actualizarProgreso() {
    const total = document.querySelectorAll('.checklist-item input[type="checkbox"]').length;
    const completados = document.querySelectorAll('.checklist-item input[type="checkbox"]:checked').length;
    const porcentaje = Math.round((completados / total) * 100);
    
    document.getElementById('barra-progreso').style.width = porcentaje + '%';
    document.getElementById('barra-progreso').textContent = porcentaje + '%';
}
</script>
```

---

## 📊 Guardar Progreso del Checklist

Para guardar el progreso del usuario en la tabla `checklist_usuario`:

```python
@app.route('/api/guardar_checklist', methods=['POST'])
def guardar_checklist():
    datos = request.json
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    items_json = json.dumps({
        'items': datos['items'],
        'completados': datos['completados']
    })
    
    porcentaje = (len(datos['completados']) / len(datos['items'])) * 100
    
    cursor.execute("""
        INSERT INTO checklist_usuario 
        (tramite_id, items_json, porcentaje_completado, estado)
        VALUES (%s, %s, %s, 'en_progreso')
    """, (datos['tramite_id'], items_json, porcentaje))
    
    conexion.commit()
    cursor.close()
    conexion.close()
    
    return {'success': True}
```

---

## 🧪 Probar la Integración

1. **Verifica la conexión a MySQL**:
   ```bash
   python src/conexion.py
   ```

2. **Verifica que las tablas existan**:
   ```sql
   USE tramite_claro;
   SHOW TABLES;
   DESCRIBE documentos;
   DESCRIBE pasos_tramite;
   SELECT COUNT(*) FROM documentos;
   ```

3. **Prueba leer un JSON**:
   ```python
   import json
   with open('/workspace/info/tramites/visa-americana.json', 'r') as f:
       data = json.load(f)
       print(f"Trámite: {data['nombre']}")
       print(f"Pasos: {len(data['pasos'])}")
   ```

4. **Inicia la aplicación Flask**:
   ```bash
   cd /workspace/src
   python app.py
   ```

---

## 📚 Recursos Adicionales

- **Documentación de tablas**: `/workspace/sql/README.md`
- **Esquema JSON**: `/workspace/info/esquema.json`
- **Ejemplo de conexión**: `/workspace/example/python-flask-mysql/`

## ✅ Checklist de Integración

- [ ] Scripts SQL ejecutados correctamente
- [ ] Conexión a MySQL funcionando
- [ ] Archivos JSON accesibles desde la aplicación
- [ ] Vistas actualizadas para mostrar documentos por paso
- [ ] Generación de checklist implementada
- [ ] Función para guardar progreso del checklist
- [ ] Pruebas realizadas con éxito

---

## 🆘 Problemas Comunes

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté corriendo: `sudo systemctl status mysql`
- Inicia MySQL: `sudo systemctl start mysql`

### Error: "Access denied for user 'root'"
- Verifica tu contraseña en `conexion.py`
- O configura variable de entorno: `export DB_PASSWORD="tu_contraseña"`

### Error: "Unknown database 'tramite_claro'"
- Crea la base de datos: `mysql -u root -p -e "CREATE DATABASE tramite_claro;"`

### Los JSON no se encuentran
- Verifica la ruta: `/workspace/info/tramites/`
- Usa rutas absolutas en tu código

---

¡Listo! Ahora tienes todo integrado para las historias 2.2 y 3.1. 🎉
