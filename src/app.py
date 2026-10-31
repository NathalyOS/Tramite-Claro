from datetime import datetime

from flask import Flask, jsonify, render_template, request, redirect, url_for
import json
import os

from tkinter import *
from tkinter import messagebox as MessageBox

from conexion import obtener_conexion, cerrar_conexion

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)
NIVELES_DIFICULTAD = {
    "baja": ("Baja", "success"),
    "media": ("Media", "warning"),
    "alta": ("Alta", "danger"),
}

COLORES_CATEGORIA = {
    "Internacional": "primary",
    "Nacional": "success",
    "Vehicular": "info",
    "Documentos Oficiales": "secondary",
    "Fiscal": "warning",
    "Notarial": "dark",
    "Inmobiliario": "success",
    "Bienestar Social": "danger",
}

# Configurar las carpetas de la aplicación
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

def preparar_datos_tramite(fila):
    categoria = fila.get("categoria") or "Trámite"
    fila["categoria"] = categoria
    fila["descripcion_simple"] = fila.get("descripcion_simple") or ""
    fila["color"] = COLORES_CATEGORIA.get(categoria, "secondary")

    fecha = fila.get("fecha_actualizacion")
    if hasattr(fecha, "day"):
        fila["fecha_iso"] = fecha.isoformat()
        fila["fecha_texto"] = f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"
    else:
        fila["fecha_iso"] = ""
        fila["fecha_texto"] = ""
    fila["fecha_actualizacion"] = fila["fecha_iso"]

    fila["mensaje_cambio"] = (fila.get("mensaje_cambio") or "").strip()
    estado = fila.get("estado_actualizacion") or ""
    fila["estado_actualizacion"] = estado if estado in ("actualizado", "desactualizado") else ""

    dificultad = (fila.get("dificultad") or "").strip().lower()
    texto, color = NIVELES_DIFICULTAD.get(dificultad, ("", ""))
    fila["dificultad"] = dificultad if texto else ""
    fila["dificultad_texto"] = texto
    fila["color_dificultad"] = color
    fila["duracion_estimada"] = (fila.get("duracion_estimada") or "").strip()
    return fila


def listar_tramites():
    conexion = obtener_conexion()
    if not conexion:
        return []

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nombre, categoria, descripcion_simple, dificultad,
                   duracion_estimada, estado_actualizacion, mensaje_cambio,
                   fecha_actualizacion
            FROM tramites
            ORDER BY nombre
            """
        )
        filas = cursor.fetchall()
    except Exception as error:
        print(f"✗ Error al leer trámites: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    return [preparar_datos_tramite(fila) for fila in filas]


TIPOS_DOCUMENTO = {
    "original": "original",
    "copia": "copia",
    "copia_certificada": "copia certificada",
    "digital": "digital",
}


def listar_lugares():
    conexion = obtener_conexion()
    if not conexion:
        return []

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT tramite_id, nombre, direccion, horario, telefono, correo,
                   enlace, estado, municipio, referencia
            FROM lugares
            ORDER BY estado, municipio, nombre
            """
        )
        return cursor.fetchall()
    except Exception as error:
        print(f"✗ Error al leer lugares: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)


def listar_categorias_publicadas():
    conexion = obtener_conexion()
    if not conexion:
        return []

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT nombre, descripcion
            FROM categorias
            WHERE estado = 'publicado'
            ORDER BY nombre
            """
        )
        return cursor.fetchall()
    except Exception as error:
        print(f"✗ Error al leer categorías: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)


def guardar_categoria(nombre, descripcion, estado):
    nombre = (nombre or "").strip()
    descripcion = (descripcion or "").strip()
    estado = (estado or "").strip()
    if not nombre or not descripcion:
        return False, "Escribe el nombre y la descripción."
    if estado not in ("publicado", "desactivado"):
        return False, "El estado no es válido."

    conexion = obtener_conexion()
    if not conexion:
        return False, "No se pudo guardar la categoría."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM categorias WHERE nombre = %s", (nombre,))
        if cursor.fetchone():
            return False, "Ya existe una categoría con ese nombre."
        cursor.execute(
            """
            INSERT INTO categorias (nombre, descripcion, estado)
            VALUES (%s, %s, %s)
            """,
            (nombre, descripcion, estado),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar la categoría: {error}")
        conexion.rollback()
        return False, "No se pudo guardar la categoría."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    return True, None


def guardar_actualizacion(tramite_id, estado, mensaje, fecha, dificultad, duracion):
    estado = (estado or "").strip()
    mensaje = (mensaje or "").strip()
    fecha = (fecha or "").strip()
    dificultad = (dificultad or "").strip().lower()
    duracion = (duracion or "").strip()

    if estado and estado not in ("actualizado", "desactualizado"):
        return False, "Elige si está actualizado o desactualizado."
    if dificultad and dificultad not in NIVELES_DIFICULTAD:
        return False, "La dificultad solo puede ser Baja, Media o Alta."
    if len(mensaje) > 500:
        return False, "El mensaje es demasiado largo."
    if len(duracion) > 100:
        return False, "El tiempo estimado es demasiado largo."

    fecha_guardar = None
    if fecha:
        try:
            fecha_guardar = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return False, "La fecha no es válida."

    conexion = obtener_conexion()
    if not conexion:
        return False, "No se pudo guardar."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM tramites WHERE id = %s", (tramite_id,))
        if not cursor.fetchone():
            return False, "No se encontró el trámite."
        cursor.execute(
            """
            UPDATE tramites
            SET estado_actualizacion = %s,
                mensaje_cambio = %s,
                fecha_actualizacion = %s,
                dificultad = %s,
                duracion_estimada = %s
            WHERE id = %s
            """,
            (
                estado or None,
                mensaje or None,
                fecha_guardar,
                dificultad or None,
                duracion or None,
                tramite_id,
            ),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar la actualización: {error}")
        conexion.rollback()
        return False, "No se pudo guardar."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    return True, None


def leer_marcas_checklist(valor):
    if not valor:
        return {}
    if isinstance(valor, str):
        valor = json.loads(valor)
    if isinstance(valor, dict):
        return {nombre: bool(completo) for nombre, completo in valor.items()}
    if isinstance(valor, list):
        return {
            item.get("nombre"): bool(item.get("completado"))
            for item in valor
            if item.get("nombre")
        }
    return {}


def obtener_guia(tramite_id):
    conexion = obtener_conexion()
    if not conexion:
        return None, [], []

    cursor = None
    requisitos_nombres = []
    documentos_filas = []
    guardado = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, nombre, descripcion_simple, fuente_oficial, dificultad,
                   duracion_estimada, estado_actualizacion, mensaje_cambio,
                   fecha_actualizacion
            FROM tramites
            WHERE id = %s
            """,
            (tramite_id,),
        )
        tramite = cursor.fetchone()
        if not tramite:
            return None, [], []
        tramite["fuente_oficial"] = (tramite.get("fuente_oficial") or "").strip()
        preparar_datos_tramite(tramite)

        cursor.execute(
            """
            SELECT numero_paso, titulo, descripcion, tiempo_estimado, consejos
            FROM pasos_tramite
            WHERE tramite_id = %s
            ORDER BY numero_paso
            """,
            (tramite_id,),
        )
        pasos = cursor.fetchall()
        cursor.execute(
            """
            SELECT DISTINCT d.nombre
            FROM documentos d
            INNER JOIN documentos_por_paso pp ON pp.documento_id = d.id
            INNER JOIN pasos_tramite pt ON pt.id = pp.paso_id
            WHERE pt.tramite_id = %s AND pp.es_obligatorio = 1
            ORDER BY d.nombre
            """,
            (tramite_id,),
        )
        requisitos_nombres = [fila["nombre"] for fila in cursor.fetchall()]
        cursor.execute(
            """
            SELECT pt.numero_paso, d.nombre, d.tipo
            FROM documentos d
            INNER JOIN documentos_por_paso pp ON pp.documento_id = d.id
            INNER JOIN pasos_tramite pt ON pt.id = pp.paso_id
            WHERE pt.tramite_id = %s
            ORDER BY pt.numero_paso, d.nombre
            """,
            (tramite_id,),
        )
        documentos_filas = cursor.fetchall()
        cursor.execute(
            """
            SELECT items_json
            FROM checklist_usuario
            WHERE tramite_id = %s AND usuario_nombre = 'local'
            ORDER BY id DESC
            LIMIT 1
            """,
            (tramite_id,),
        )
        guardado = cursor.fetchone()
    except Exception as error:
        print(f"✗ Error al leer la guía: {error}")
        return None, [], []
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    documentos_por_paso = {}
    for fila in documentos_filas:
        documentos_por_paso.setdefault(fila["numero_paso"], []).append(
            {
                "nombre": fila["nombre"],
                "tipo": TIPOS_DOCUMENTO.get(fila.get("tipo") or "", fila.get("tipo") or ""),
            }
        )

    for paso in pasos:
        consejos = paso.get("consejos") or ""
        paso["consejos"] = [consejo for consejo in consejos.split("|") if consejo]
        paso["tiempo_estimado"] = paso.get("tiempo_estimado") or ""
        paso["documentos"] = documentos_por_paso.get(paso["numero_paso"], [])

    marcas = leer_marcas_checklist(guardado["items_json"]) if guardado else {}
    requisitos = [
        {"nombre": nombre, "completado": bool(marcas.get(nombre))}
        for nombre in requisitos_nombres
    ]
    return tramite, pasos, requisitos


def guardar_progreso_checklist(tramite_id, items):
    tramite, pasos, requisitos = obtener_guia(tramite_id)
    if not tramite:
        return None

    nombres = [requisito["nombre"] for requisito in requisitos]
    recibidos = {
        item.get("nombre"): bool(item.get("completado"))
        for item in items
        if isinstance(item, dict)
    }
    marcas = {nombre: bool(recibidos.get(nombre)) for nombre in nombres}
    total = len(nombres)
    completados = sum(1 for completo in marcas.values() if completo)
    porcentaje = round((completados / total) * 100, 2) if total else 0
    estado = "completado" if total and porcentaje == 100 else "en_progreso"
    payload = json.dumps(marcas, ensure_ascii=False)

    conexion = obtener_conexion()
    if not conexion:
        return None

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT id
            FROM checklist_usuario
            WHERE tramite_id = %s AND usuario_nombre = 'local'
            ORDER BY id DESC
            LIMIT 1
            """,
            (tramite_id,),
        )
        existente = cursor.fetchone()
        if existente:
            cursor.execute(
                """
                UPDATE checklist_usuario
                SET items_json = CAST(%s AS JSON),
                    porcentaje_completado = %s,
                    estado = %s
                WHERE id = %s
                """,
                (payload, porcentaje, estado, existente[0]),
            )
        else:
            cursor.execute(
                """
                INSERT INTO checklist_usuario
                    (tramite_id, usuario_nombre, estado, items_json, porcentaje_completado)
                VALUES (%s, 'local', %s, CAST(%s AS JSON), %s)
                """,
                (tramite_id, estado, payload, porcentaje),
            )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar el checklist: {error}")
        conexion.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    return {"porcentaje": porcentaje, "estado": estado}


#rutas de la aplicación
@app.route('/')
def home():
    return render_template('presentacion/index.html')

@app.route('/categorias')
def categorias():
    return render_template(
        'presentacion/categorias.html',
        tramites=listar_tramites(),
        lugares=listar_lugares(),
        categorias=listar_categorias_publicadas(),
    )

@app.route('/crear-categoria', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        datos = request.get_json(silent=True) or {}
        guardada, error = guardar_categoria(
            datos.get("nombre"),
            datos.get("descripcion"),
            datos.get("estado"),
        )
        if not guardada:
            return jsonify({"error": error}), 400
        return jsonify({"ok": True, "estado": datos.get("estado")})
    return render_template('presentacion/crear-categoria.html')

@app.route('/actualizar-tramite', methods=['GET', 'POST'])
def actualizar_tramite():
    if request.method == 'POST':
        datos = request.get_json(silent=True) or {}
        try:
            tramite_id = int(datos.get("tramite_id"))
        except (TypeError, ValueError):
            return jsonify({"error": "Elige un trámite."}), 400
        guardada, error = guardar_actualizacion(
            tramite_id,
            datos.get("estado"),
            datos.get("mensaje"),
            datos.get("fecha"),
            datos.get("dificultad"),
            datos.get("duracion"),
        )
        if not guardada:
            return jsonify({"error": error}), 400
        return jsonify({"ok": True})
    return render_template(
        'presentacion/actualizar-tramite.html',
        tramites=listar_tramites(),
    )

@app.route('/guia-tramite')
@app.route('/guia-tramite/<int:tramite_id>')
def guia_tramite(tramite_id=None):
    tramite = None
    pasos = []
    requisitos = []
    if tramite_id is not None:
        tramite, pasos, requisitos = obtener_guia(tramite_id)
    return render_template(
        'presentacion/guia-tramite.html',
        tramite=tramite,
        pasos=pasos,
        requisitos=requisitos,
    )


@app.route('/guia-tramite/<int:tramite_id>/checklist', methods=['POST'])
def guardar_checklist(tramite_id):
    datos = request.get_json(silent=True) or {}
    resultado = guardar_progreso_checklist(tramite_id, datos.get("items") or [])
    if resultado is None:
        return jsonify({"error": "No se pudo guardar el checklist"}), 400
    return jsonify(resultado)

# Definimos el __name__ como plantilla principal a index.html y el puerto de ejecución

if __name__ == '__main__':
    app.run(debug=True, port=4000)