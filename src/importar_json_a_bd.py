"""
Script para importar los trámites desde archivos JSON a la base de datos MySQL.
Este script lee todos los JSON de la carpeta /workspace/info/tramites/ y los inserta
en las tablas de la base de datos.

Uso:
    python importar_json_a_bd.py
"""

import json
import glob
import sys
import os

# Agregar el directorio src al path para importar conexion
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conexion import obtener_conexion, cerrar_conexion

def importar_tramites_desde_json():
    """
    Importa todos los trámites desde los archivos JSON a la base de datos.
    """
    print("=" * 60)
    print("IMPORTACIÓN DE TRÁMITES DESDE JSON A BASE DE DATOS")
    print("=" * 60)
    
    conexion = obtener_conexion()
    if not conexion:
        print("\n✗ No se pudo conectar a la base de datos")
        return False
    
    cursor = conexion.cursor()
    
    # Buscar todos los archivos JSON en la carpeta de trámites
    ruta_tramites = '/workspace/info/tramites/*.json'
    archivos_json = glob.glob(ruta_tramites)
    
    if not archivos_json:
        print(f"\n✗ No se encontraron archivos JSON en {ruta_tramites}")
        cerrar_conexion(conexion)
        return False
    
    print(f"\n✓ Se encontraron {len(archivos_json)} archivos JSON\n")
    
    tramites_importados = 0
    pasos_importados = 0
    documentos_relacionados = 0
    
    try:
        for archivo in archivos_json:
            print(f"Procesando: {os.path.basename(archivo)}")
            
            with open(archivo, 'r', encoding='utf-8') as f:
                tramite_data = json.load(f)
            
            # Verificar si el trámite ya existe
            cursor.execute("SELECT id FROM tramites WHERE nombre = %s", (tramite_data['nombre'],))
            tramite_existente = cursor.fetchone()
            
            if tramite_existente:
                print(f"  ⚠ Ya existe en la BD, omitiendo...")
                continue
            
            # Insertar en tabla tramites
            cursor.execute("""
                INSERT INTO tramites 
                (nombre, categoria, proceso, requerimientos, lugar, costos, 
                 duracion_estimada, dificultad, descripcion_simple, tiene_pasos_detallados) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """, (
                tramite_data['nombre'],
                tramite_data['categoria'],
                'Ver pasos detallados',  # El proceso ahora está en pasos_tramite
                'Ver documentos por paso',  # Los requerimientos ahora están estructurados
                'Varía según ubicación',
                tramite_data['costo_aproximado'],
                tramite_data['duracion_estimada'],
                tramite_data['dificultad'],
                tramite_data['descripcion_simple']
            ))
            
            tramite_id = cursor.lastrowid
            tramites_importados += 1
            print(f"  ✓ Trámite insertado (ID: {tramite_id})")
            
            # Insertar pasos del trámite
            for paso in tramite_data['pasos']:
                # Concatenar consejos con pipe separator
                consejos_str = '|'.join(paso.get('consejos', []))
                
                cursor.execute("""
                    INSERT INTO pasos_tramite 
                    (tramite_id, numero_paso, titulo, descripcion, tiempo_estimado, consejos, es_opcional) 
                    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                """, (
                    tramite_id,
                    paso['numero'],
                    paso['titulo'],
                    paso['descripcion'],
                    paso.get('tiempo_estimado', ''),
                    consejos_str
                ))
                
                paso_id = cursor.lastrowid
                pasos_importados += 1
                
                # Insertar documentos requeridos en este paso
                if 'documentos_requeridos' in paso:
                    for doc in paso['documentos_requeridos']:
                        # Primero buscar o crear el documento en el catálogo
                        cursor.execute("""
                            SELECT id FROM documentos WHERE nombre = %s
                        """, (doc['nombre'],))
                        
                        documento_row = cursor.fetchone()
                        
                        if documento_row:
                            documento_id = documento_row[0]
                        else:
                            # Insertar el documento en el catálogo si no existe
                            cursor.execute("""
                                INSERT INTO documentos 
                                (nombre, descripcion, tipo, vigencia, ejemplos, categoria) 
                                VALUES (%s, %s, %s, %s, %s, 'general')
                            """, (
                                doc['nombre'],
                                doc['descripcion'],
                                doc['tipo'],
                                doc.get('vigencia', ''),
                                ', '.join(doc.get('ejemplos', []))
                            ))
                            documento_id = cursor.lastrowid
                        
                        # Relacionar documento con paso
                        cursor.execute("""
                            INSERT INTO documentos_por_paso 
                            (paso_id, documento_id, es_obligatorio, cantidad, notas_especiales) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            paso_id,
                            documento_id,
                            doc['obligatorio'],
                            doc.get('cantidad', 1),
                            f"Tipo: {doc['tipo']}"
                        ))
                        documentos_relacionados += 1
            
            print(f"  ✓ {len(tramite_data['pasos'])} pasos insertados\n")
        
        # Commit de todas las transacciones
        conexion.commit()
        
        print("=" * 60)
        print("RESUMEN DE IMPORTACIÓN")
        print("=" * 60)
        print(f"✓ Trámites importados: {tramites_importados}")
        print(f"✓ Pasos insertados: {pasos_importados}")
        print(f"✓ Documentos relacionados: {documentos_relacionados}")
        print("\n¡Importación completada exitosamente! 🎉\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error durante la importación: {e}")
        conexion.rollback()
        return False
        
    finally:
        cursor.close()
        cerrar_conexion(conexion)

if __name__ == '__main__':
    print("\n🚀 Iniciando importación de trámites...\n")
    
    # Preguntar confirmación
    respuesta = input("¿Deseas importar los trámites a la base de datos? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        exito = importar_tramites_desde_json()
        
        if exito:
            print("✓ Puedes verificar los datos con:")
            print("  mysql -u root -p tramite_claro")
            print("  SELECT nombre, categoria FROM tramites;")
        else:
            print("✗ La importación falló. Revisa los errores anteriores.")
            sys.exit(1)
    else:
        print("\nImportación cancelada por el usuario.")
