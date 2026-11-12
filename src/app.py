from datetime import date, datetime
import base64
import json
import os
import random
import re
import urllib.error
import urllib.request

from flask import Flask, jsonify, render_template, request, redirect, url_for

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


def asegurar_tabla_quejas():
    conexion = obtener_conexion()
    if not conexion:
        return False
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quejas (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                tramite_id INT UNSIGNED NOT NULL,
                numero_paso INT UNSIGNED NULL,
                tipo ENUM('queja', 'sugerencia', 'duda') NOT NULL,
                mensaje TEXT NOT NULL,
                estado ENUM('pendiente', 'atendida') NOT NULL DEFAULT 'pendiente',
                respuesta TEXT NULL,
                fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                fecha_respuesta DATETIME NULL,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al preparar quejas: {error}")
        conexion.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    return True


TIPOS_QUEJA = {
    "queja": "Queja",
    "sugerencia": "Sugerencia",
    "duda": "Duda",
}


def preparar_queja(fila):
    tipo = fila.get("tipo") or ""
    fila["tipo_texto"] = TIPOS_QUEJA.get(tipo, tipo)
    fecha = fila.get("fecha_creacion")
    if hasattr(fecha, "day"):
        fila["fecha_texto"] = f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"
    else:
        fila["fecha_texto"] = ""
    fila["respuesta"] = (fila.get("respuesta") or "").strip()
    fila["mensaje"] = (fila.get("mensaje") or "").strip()
    return fila


def guardar_queja(tramite_id, numero_paso, tipo, mensaje):
    tipo = (tipo or "").strip().lower()
    mensaje = (mensaje or "").strip()
    if tipo not in TIPOS_QUEJA:
        return False, "Elige si es queja, sugerencia o duda."
    if not mensaje:
        return False, "Escribe el mensaje."
    if len(mensaje) > 1000:
        return False, "El mensaje es demasiado largo."

    paso = None
    if numero_paso not in (None, ""):
        try:
            paso = int(numero_paso)
        except (TypeError, ValueError):
            return False, "El paso no es válido."
        if paso < 1:
            return False, "El paso no es válido."

    if not asegurar_tabla_quejas():
        return False, "No se pudo guardar la queja."

    conexion = obtener_conexion()
    if not conexion:
        return False, "No se pudo guardar la queja."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM tramites WHERE id = %s", (tramite_id,))
        if not cursor.fetchone():
            return False, "No se encontró el trámite."
        cursor.execute(
            """
            INSERT INTO quejas (tramite_id, numero_paso, tipo, mensaje)
            VALUES (%s, %s, %s, %s)
            """,
            (tramite_id, paso, tipo, mensaje),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar la queja: {error}")
        conexion.rollback()
        return False, "No se pudo guardar la queja."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    return True, None


def listar_quejas(tramite_id=None, estado=""):
    if not asegurar_tabla_quejas():
        return []

    conexion = obtener_conexion()
    if not conexion:
        return []

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        consulta = """
            SELECT q.id, q.tramite_id, q.numero_paso, q.tipo, q.mensaje,
                   q.estado, q.respuesta, q.fecha_creacion, t.nombre AS tramite_nombre
            FROM quejas q
            JOIN tramites t ON t.id = q.tramite_id
            WHERE 1 = 1
        """
        valores = []
        if tramite_id is not None:
            consulta += " AND q.tramite_id = %s"
            valores.append(tramite_id)
        if estado in ("pendiente", "atendida"):
            consulta += " AND q.estado = %s"
            valores.append(estado)
        consulta += " ORDER BY q.fecha_creacion DESC"
        cursor.execute(consulta, valores)
        filas = cursor.fetchall()
    except Exception as error:
        print(f"✗ Error al leer quejas: {error}")
        return []
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)

    return [preparar_queja(fila) for fila in filas]


def responder_queja(queja_id, respuesta, resolver):
    respuesta = (respuesta or "").strip()
    if not respuesta:
        return False, "Escribe una respuesta."
    if len(respuesta) > 1000:
        return False, "La respuesta es demasiado larga."
    if not asegurar_tabla_quejas():
        return False, "No se pudo guardar la respuesta."

    conexion = obtener_conexion()
    if not conexion:
        return False, "No se pudo guardar la respuesta."

    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM quejas WHERE id = %s", (queja_id,))
        if not cursor.fetchone():
            return False, "No se encontró la queja."
        cursor.execute(
            """
            UPDATE quejas
            SET respuesta = %s,
                estado = %s,
                fecha_respuesta = NOW()
            WHERE id = %s
            """,
            (respuesta, "atendida" if resolver else "pendiente", queja_id),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al responder la queja: {error}")
        conexion.rollback()
        return False, "No se pudo guardar la respuesta."
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


CORREO_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def correo_limpio(valor):
    correo = (valor or "").strip().lower()
    if not CORREO_VALIDO.match(correo) or len(correo) > 180:
        return ""
    return correo


def asegurar_tablas_correo():
    conexion = obtener_conexion()
    if not conexion:
        return False
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS correo_verificacion (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                correo VARCHAR(180) NOT NULL,
                codigo CHAR(6) NOT NULL,
                verificado TINYINT(1) NOT NULL DEFAULT 0,
                PRIMARY KEY (id),
                UNIQUE KEY correo_unico (correo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS avance_correo (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                correo VARCHAR(180) NOT NULL,
                tramite_id INT UNSIGNED NOT NULL,
                numero_paso INT NOT NULL DEFAULT 1,
                items_json JSON NULL,
                porcentaje_completado DECIMAL(5,2) NOT NULL DEFAULT 0,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                UNIQUE KEY avance_unico (correo, tramite_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recordatorios (
                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                correo VARCHAR(180) NOT NULL,
                tramite_id INT UNSIGNED NOT NULL,
                descripcion VARCHAR(200) NOT NULL,
                fecha_limite DATE NOT NULL,
                aviso_enviado SMALLINT NOT NULL DEFAULT 0,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """
        )
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = 'recordatorios' AND column_name = 'aviso_enviado'
            """
        )
        if not cursor.fetchone()[0]:
            cursor.execute(
                "ALTER TABLE recordatorios ADD COLUMN aviso_enviado SMALLINT NOT NULL DEFAULT 0"
            )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al preparar el avance por correo: {error}")
        return False
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    return True


def correo_esta_verificado(cursor, correo):
    cursor.execute(
        "SELECT verificado FROM correo_verificacion WHERE correo = %s",
        (correo,),
    )
    fila = cursor.fetchone()
    if not fila:
        return False
    valor = fila["verificado"] if isinstance(fila, dict) else fila[0]
    return bool(valor)


def dia_de_fecha(fecha_limite):
    if hasattr(fecha_limite, "year") and not hasattr(fecha_limite, "hour"):
        return fecha_limite
    if hasattr(fecha_limite, "date") and hasattr(fecha_limite, "hour"):
        return fecha_limite.date()
    return datetime.strptime(str(fecha_limite)[:10], "%Y-%m-%d").date()


def texto_vencimiento(fecha_limite):
    dia = dia_de_fecha(fecha_limite)
    dias = (dia - date.today()).days
    if dias < 0:
        return ""
    if dias == 0:
        return "Vence hoy."
    if dias == 1:
        return "Vence en 1 día."
    if dias <= 5:
        return f"Vence en {dias} días."
    return ""


def clave_brevo():
    clave = os.getenv("BREVO_API_KEY", "").strip()
    if clave.startswith("xkeysib-") or not clave:
        return clave
    try:
        datos = json.loads(base64.b64decode(clave).decode("utf-8"))
        if isinstance(datos, dict) and str(datos.get("api_key", "")).startswith("xkeysib-"):
            return datos["api_key"]
    except Exception:
        pass
    return clave


def enviar_mensaje_brevo(correo, asunto, texto):
    clave = clave_brevo()
    desde = os.getenv("CORREO_DESDE", "").strip()
    if not clave or not desde:
        return "local"
    nombre = "Trámite Claro"
    email_desde = desde
    coincidencia = re.fullmatch(r"(.*?)<([^>]+)>", desde)
    if coincidencia:
        nombre = coincidencia.group(1).strip() or nombre
        email_desde = coincidencia.group(2).strip()
    cuerpo = {
        "sender": {"name": nombre, "email": email_desde},
        "to": [{"email": correo}],
        "subject": asunto,
        "textContent": texto,
    }
    peticion = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": clave,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            if respuesta.status >= 400:
                return None
    except urllib.error.HTTPError as error:
        detalle = error.read().decode("utf-8", "replace")
        print(f"✗ Error al enviar el correo: {error.code} {detalle}")
        return None
    except Exception as error:
        print(f"✗ Error al enviar el correo: {error}")
        return None
    return "enviado"


def enviar_codigo_correo(correo, codigo):
    return enviar_mensaje_brevo(
        correo,
        "Tu código de Trámite Claro",
        (
            f"Tu código es {codigo}.\n\n"
            "Escríbelo en Trámite Claro para confirmar tu correo y guardar tu avance.\n"
            "Si no pediste este código, ignora este mensaje."
        ),
    )


def pedir_codigo_correo(correo):
    correo = correo_limpio(correo)
    if not correo:
        return None, "Escribe un correo válido."
    if not asegurar_tablas_correo():
        return None, "No se pudo preparar el correo."
    codigo = f"{random.randint(0, 999999):06d}"
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo guardar el código."
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO correo_verificacion (correo, codigo, verificado)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE codigo = VALUES(codigo), verificado = 0
            """,
            (correo, codigo),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al crear el código: {error}")
        conexion.rollback()
        return None, "No se pudo crear el código."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    envio = enviar_codigo_correo(correo, codigo)
    if envio is None:
        return None, "No se pudo enviar el código. Intenta de nuevo."
    if envio == "local":
        return {"codigo": codigo, "correo": correo}, None
    return {"correo": correo, "enviado": True}, None


def listar_avances_correo(cursor, correo):
    cursor.execute(
        """
        SELECT a.tramite_id, a.numero_paso, a.items_json, a.porcentaje_completado, t.nombre
        FROM avance_correo a
        INNER JOIN tramites t ON t.id = a.tramite_id
        WHERE a.correo = %s
        ORDER BY a.actualizado_en DESC
        """,
        (correo,),
    )
    avances = []
    for fila in cursor.fetchall():
        avances.append({
            "tramite_id": fila["tramite_id"],
            "nombre": fila["nombre"],
            "numero_paso": fila["numero_paso"],
            "porcentaje": float(fila["porcentaje_completado"] or 0),
            "items": leer_marcas_checklist(fila["items_json"]),
        })
    return avances


def listar_recordatorios_correo(cursor, correo, tramite_id=None):
    if tramite_id:
        cursor.execute(
            """
            SELECT id, tramite_id, descripcion, fecha_limite
            FROM recordatorios
            WHERE correo = %s AND tramite_id = %s
            ORDER BY fecha_limite, id
            """,
            (correo, tramite_id),
        )
    else:
        cursor.execute(
            """
            SELECT id, tramite_id, descripcion, fecha_limite
            FROM recordatorios
            WHERE correo = %s
            ORDER BY fecha_limite, id
            """,
            (correo,),
        )
    lista = []
    for fila in cursor.fetchall():
        fecha = fila["fecha_limite"]
        lista.append({
            "id": fila["id"],
            "tramite_id": fila["tramite_id"],
            "descripcion": fila["descripcion"],
            "fecha": fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha)[:10],
            "aviso": texto_vencimiento(fecha),
        })
    return lista


def fecha_en_palabras(fecha_limite):
    dia = dia_de_fecha(fecha_limite)
    return f"{dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def avisar_recordatorios_pendientes(correo):
    correo = correo_limpio(correo)
    if not correo or not asegurar_tablas_correo():
        return
    conexion = obtener_conexion()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not correo_esta_verificado(cursor, correo):
            return
        cursor.execute(
            """
            SELECT r.id, r.descripcion, r.fecha_limite, t.nombre
            FROM recordatorios r
            INNER JOIN tramites t ON t.id = r.tramite_id
            WHERE r.correo = %s AND r.aviso_enviado = 0
            ORDER BY r.fecha_limite, r.id
            """,
            (correo,),
        )
        pendientes = cursor.fetchall()
        for fila in pendientes:
            aviso = texto_vencimiento(fila["fecha_limite"])
            if not aviso:
                continue
            envio = enviar_mensaje_brevo(
                correo,
                "Recordatorio de Trámite Claro",
                (
                    f"Tu trámite {fila['nombre']}.\n"
                    f"{fila['descripcion']}\n"
                    f"Fecha límite: {fecha_en_palabras(fila['fecha_limite'])}.\n"
                    f"{aviso}"
                ),
            )
            if envio != "enviado":
                continue
            cursor.execute(
                "UPDATE recordatorios SET aviso_enviado = 1 WHERE id = %s AND correo = %s",
                (fila["id"], correo),
            )
            conexion.commit()
    except Exception as error:
        print(f"✗ Error al avisar recordatorios: {error}")
        conexion.rollback()
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)


def confirmar_codigo_correo(correo, codigo):
    correo = correo_limpio(correo)
    codigo = (codigo or "").strip()
    if not correo:
        return None, "Escribe un correo válido."
    if not re.fullmatch(r"\d{6}", codigo):
        return None, "El código debe tener 6 números."
    if not asegurar_tablas_correo():
        return None, "No se pudo preparar el correo."
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo confirmar el correo."
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT codigo FROM correo_verificacion WHERE correo = %s",
            (correo,),
        )
        fila = cursor.fetchone()
        if not fila or (fila["codigo"] or "").strip() != codigo:
            return None, "El código no coincide."
        cursor.execute(
            "UPDATE correo_verificacion SET verificado = 1 WHERE correo = %s",
            (correo,),
        )
        avances = listar_avances_correo(cursor, correo)
        recordatorios = listar_recordatorios_correo(cursor, correo)
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al confirmar el correo: {error}")
        conexion.rollback()
        return None, "No se pudo confirmar el correo."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    avisar_recordatorios_pendientes(correo)
    ultimo = avances[0]["tramite_id"] if avances else None
    return {
        "correo": correo,
        "avances": avances,
        "ultimo": ultimo,
        "recordatorios": recordatorios,
    }, None


def leer_avance_correo(correo, tramite_id):
    correo = correo_limpio(correo)
    if not correo:
        return None, "Escribe un correo válido."
    if not asegurar_tablas_correo():
        return None, "No se pudo leer el avance."
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo leer el avance."
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not correo_esta_verificado(cursor, correo):
            return None, "Confirma tu correo para ver el avance."
        avances = [
            avance for avance in listar_avances_correo(cursor, correo)
            if avance["tramite_id"] == tramite_id
        ]
        recordatorios = listar_recordatorios_correo(cursor, correo, tramite_id)
    except Exception as error:
        print(f"✗ Error al leer el avance: {error}")
        return None, "No se pudo leer el avance."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    avisar_recordatorios_pendientes(correo)
    return {
        "avance": avances[0] if avances else None,
        "recordatorios": recordatorios,
    }, None


def guardar_avance_correo(tramite_id, correo, numero_paso, items, solo_registrar=False):
    correo = correo_limpio(correo)
    if not correo:
        return None, "Escribe un correo válido."
    tramite, pasos, requisitos = obtener_guia(tramite_id)
    if not tramite or not pasos:
        return None, "No hay guía para guardar."
    try:
        numero_paso = int(numero_paso)
    except (TypeError, ValueError):
        numero_paso = 1
    if numero_paso < 1 or numero_paso > len(pasos):
        numero_paso = 1
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
    payload = json.dumps(marcas, ensure_ascii=False)
    if not asegurar_tablas_correo():
        return None, "No se pudo guardar el avance."
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo guardar el avance."
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not correo_esta_verificado(cursor, correo):
            return None, "Confirma tu correo para guardar el avance."
        cursor.execute(
            "SELECT id FROM avance_correo WHERE correo = %s AND tramite_id = %s",
            (correo, tramite_id),
        )
        ya_existe = cursor.fetchone()
        if ya_existe and solo_registrar:
            return {"mensaje": "Tu avance se guardó.", "porcentaje": porcentaje}, None
        cursor.execute(
            """
            INSERT INTO avance_correo (correo, tramite_id, numero_paso, items_json, porcentaje_completado)
            VALUES (%s, %s, %s, CAST(%s AS JSON), %s)
            ON DUPLICATE KEY UPDATE
                numero_paso = VALUES(numero_paso),
                items_json = VALUES(items_json),
                porcentaje_completado = VALUES(porcentaje_completado)
            """,
            (correo, tramite_id, numero_paso, payload, porcentaje),
        )
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar el avance: {error}")
        conexion.rollback()
        return None, "No se pudo guardar el avance."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    return {"mensaje": "Tu avance se guardó.", "porcentaje": porcentaje}, None


def fecha_recordatorio(valor):
    texto = (valor or "").strip()
    try:
        dia = datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return None
    if dia < date.today():
        return None
    return dia


def guardar_recordatorio(tramite_id, correo, descripcion, fecha, recordatorio_id=None):
    correo = correo_limpio(correo)
    descripcion = (descripcion or "").strip()
    dia = fecha_recordatorio(fecha)
    if not correo:
        return None, "Escribe un correo válido."
    if not descripcion or len(descripcion) > 200:
        return None, "Escribe para qué es el recordatorio."
    if not dia:
        return None, "La fecha no puede ser de un día pasado."
    if not asegurar_tablas_correo():
        return None, "No se pudo guardar el recordatorio."
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo guardar el recordatorio."
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if not correo_esta_verificado(cursor, correo):
            return None, "Confirma tu correo para guardar el recordatorio."
        if recordatorio_id:
            cursor.execute(
                """
                SELECT fecha_limite FROM recordatorios
                WHERE id = %s AND correo = %s AND tramite_id = %s
                """,
                (recordatorio_id, correo, tramite_id),
            )
            anterior = cursor.fetchone()
            if not anterior:
                return None, "No se encontró el recordatorio."
            cambio_fecha = dia_de_fecha(anterior["fecha_limite"]) != dia
            if cambio_fecha:
                cursor.execute(
                    """
                    UPDATE recordatorios
                    SET descripcion = %s, fecha_limite = %s, aviso_enviado = 0
                    WHERE id = %s AND correo = %s AND tramite_id = %s
                    """,
                    (descripcion, dia, recordatorio_id, correo, tramite_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE recordatorios
                    SET descripcion = %s, fecha_limite = %s
                    WHERE id = %s AND correo = %s AND tramite_id = %s
                    """,
                    (descripcion, dia, recordatorio_id, correo, tramite_id),
                )
        else:
            cursor.execute(
                """
                INSERT INTO recordatorios (correo, tramite_id, descripcion, fecha_limite)
                VALUES (%s, %s, %s, %s)
                """,
                (correo, tramite_id, descripcion, dia),
            )
        recordatorios = listar_recordatorios_correo(cursor, correo, tramite_id)
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al guardar el recordatorio: {error}")
        conexion.rollback()
        return None, "No se pudo guardar el recordatorio."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    avisar_recordatorios_pendientes(correo)
    return {"recordatorios": recordatorios, "mensaje": "Recordatorio guardado."}, None


def eliminar_recordatorio(tramite_id, recordatorio_id, correo):
    correo = correo_limpio(correo)
    if not correo:
        return None, "Escribe un correo válido."
    if not asegurar_tablas_correo():
        return None, "No se pudo eliminar el recordatorio."
    conexion = obtener_conexion()
    if not conexion:
        return None, "No se pudo eliminar el recordatorio."
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "DELETE FROM recordatorios WHERE id = %s AND correo = %s AND tramite_id = %s",
            (recordatorio_id, correo, tramite_id),
        )
        if cursor.rowcount == 0:
            return None, "No se encontró el recordatorio."
        recordatorios = listar_recordatorios_correo(cursor, correo, tramite_id)
        conexion.commit()
    except Exception as error:
        print(f"✗ Error al eliminar el recordatorio: {error}")
        conexion.rollback()
        return None, "No se pudo eliminar el recordatorio."
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(conexion)
    return {"recordatorios": recordatorios}, None


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
    respuestas = []
    if tramite_id is not None:
        tramite, pasos, requisitos = obtener_guia(tramite_id)
        if tramite:
            respuestas = [
                queja for queja in listar_quejas(tramite_id, "atendida")
                if queja.get("respuesta")
            ]
    return render_template(
        'presentacion/guia-tramite.html',
        tramite=tramite,
        pasos=pasos,
        requisitos=requisitos,
        respuestas=respuestas,
    )


@app.route('/guia-tramite/<int:tramite_id>/queja', methods=['POST'])
def guardar_queja_guia(tramite_id):
    datos = request.get_json(silent=True) or {}
    guardada, error = guardar_queja(
        tramite_id,
        datos.get("numero_paso"),
        datos.get("tipo"),
        datos.get("mensaje"),
    )
    if not guardada:
        return jsonify({"error": error}), 400
    return jsonify({"ok": True})


@app.route('/quejas')
def quejas():
    estado = (request.args.get("estado") or "").strip()
    if estado not in ("pendiente", "atendida"):
        estado = ""
    return render_template(
        'presentacion/quejas.html',
        quejas=listar_quejas(estado=estado),
        filtro=estado,
    )


@app.route('/quejas/<int:queja_id>', methods=['POST'])
def atender_queja(queja_id):
    datos = request.get_json(silent=True) or {}
    guardada, error = responder_queja(
        queja_id,
        datos.get("respuesta"),
        bool(datos.get("resolver")),
    )
    if not guardada:
        return jsonify({"error": error}), 400
    return jsonify({"ok": True, "estado": "atendida" if datos.get("resolver") else "pendiente"})


@app.route('/correo/codigo', methods=['POST'])
def correo_codigo():
    datos = request.get_json(silent=True) or {}
    resultado, error = pedir_codigo_correo(datos.get("correo"))
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


@app.route('/correo/confirmar', methods=['POST'])
def correo_confirmar():
    datos = request.get_json(silent=True) or {}
    resultado, error = confirmar_codigo_correo(datos.get("correo"), datos.get("codigo"))
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


@app.route('/correo/recordatorios/avisar', methods=['POST'])
def correo_avisar_recordatorios():
    datos = request.get_json(silent=True) or {}
    avisar_recordatorios_pendientes(datos.get("correo"))
    return jsonify({"ok": True})


@app.route('/correo/avance', methods=['POST'])
def correo_avance():
    datos = request.get_json(silent=True) or {}
    try:
        tramite_id = int(datos.get("tramite_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Elige un trámite."}), 400
    resultado, error = leer_avance_correo(datos.get("correo"), tramite_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


@app.route('/guia-tramite/<int:tramite_id>/avance', methods=['POST'])
def guardar_avance_guia(tramite_id):
    datos = request.get_json(silent=True) or {}
    resultado, error = guardar_avance_correo(
        tramite_id,
        datos.get("correo"),
        datos.get("numero_paso"),
        datos.get("items") or [],
        bool(datos.get("registrar")),
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


@app.route('/guia-tramite/<int:tramite_id>/recordatorios', methods=['POST'])
def guardar_recordatorio_guia(tramite_id):
    datos = request.get_json(silent=True) or {}
    resultado, error = guardar_recordatorio(
        tramite_id,
        datos.get("correo"),
        datos.get("descripcion"),
        datos.get("fecha"),
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


@app.route('/guia-tramite/<int:tramite_id>/recordatorios/<int:recordatorio_id>', methods=['POST'])
def editar_recordatorio_guia(tramite_id, recordatorio_id):
    datos = request.get_json(silent=True) or {}
    if datos.get("eliminar"):
        resultado, error = eliminar_recordatorio(tramite_id, recordatorio_id, datos.get("correo"))
    else:
        resultado, error = guardar_recordatorio(
            tramite_id,
            datos.get("correo"),
            datos.get("descripcion"),
            datos.get("fecha"),
            recordatorio_id,
        )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(resultado)


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