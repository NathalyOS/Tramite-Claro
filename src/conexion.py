import mysql.connector
from mysql.connector import Error
import os

def obtener_conexion():
 
    try:
        # Configuración de la conexión
        # IMPORTANTE: Actualiza estos valores según tu configuración local
        conexion = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '12345678'),
            database=os.getenv('DB_NAME', 'tramite_claro'),
            charset='utf8mb4',
            collation='utf8mb4_0900_ai_ci'
        )
        
        if conexion.is_connected():
            print("✓ Conexión exitosa a la base de datos MySQL")
            return conexion
            
    except Error as e:
        print(f"✗ Error al conectar a MySQL: {e}")
        print("\nSugerencias:")
        print("1. Verifica que MySQL esté corriendo")
        print("2. Verifica usuario y contraseña")
        print("3. Verifica que la base de datos 'tramite_claro' exista")
        return None

def cerrar_conexion(conexion):
    if conexion and conexion.is_connected():
        conexion.close()
        print("✓ Conexión cerrada correctamente")

# Ejemplo de uso si ejecutas este archivo directamente
if __name__ == '__main__':
    print("=== Probando conexión a MySQL ===\n")
    conn = obtener_conexion()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Prueba 1: Verificar tablas existentes
            cursor.execute("SHOW TABLES")
            tablas = cursor.fetchall()
            print(f"\n✓ Tablas encontradas: {len(tablas)}")
            for tabla in tablas:
                print(f"  - {tabla[0]}")
            
            # Prueba 2: Contar trámites
            cursor.execute("SELECT COUNT(*) FROM tramites")
            cantidad = cursor.fetchone()[0]
            print(f"\n✓ Trámites en la base de datos: {cantidad}")
            
            cursor.close()
            
        except Error as e:
            print(f"\n✗ Error al ejecutar consultas: {e}")
        
        finally:
            cerrar_conexion(conn)
    else:
        print("\n✗ No se pudo establecer la conexión")
