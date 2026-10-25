from flask import Flask, render_template, request, redirect, url_for
import os
import conexion as db

from tkinter import *
from tkinter import messagebox as MessageBox


# Configurar la aplicación para ser ejecutado
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir,'src','templates')


# Declaramos la variable de ejecución de la aplicación
app= Flask(__name__,template_folder=template_dir)



#rutas de la aplicación
@app.route('/')
def home():
    cursor = db.conexion.cursor()
    cursor.execute("SELECT * FROM pais")
    datosDB = cursor.fetchall()
    # convertir los datos a diccionario
    insertObjeto = []
    columnName = [column[0] for column in cursor.description]
    for registro in datosDB:
        insertObjeto.append(dict(zip(columnName,registro)))
    cursor.close()
    return render_template('index.html',data = insertObjeto)



# crear la ruta para insertar los registros en la BD
@app.route('/insertPais', methods=['POST'])
def insertPais():
    nombre = request.form["PaisNombre"]
    sigla = request.form["PaisSigla"]

    if nombre and sigla:
        cursor = db.conexion.cursor()

        sql = """INSERT INTO Pais (PaisNombre, PaisSigla)
                 VALUES (%s, %s)"""

        datos = (nombre, sigla)

        cursor.execute(sql, datos)
        db.conexion.commit()
        cursor.close()

    return redirect(url_for('home'))



# Crear la ruta para ELIMINAR registros de la base de datos
@app.route('/eliminaPais/<int:id>')
def eliminaPais(id):
    cursor = db.conexion.cursor()

    sql = "DELETE FROM Pais WHERE idPais = %s"
    datos = (id,)

    cursor.execute(sql, datos)
    db.conexion.commit()
    cursor.close()

    return redirect(url_for('home'))



# Definimos el __name__ como plantilla principal a index.html y el puerto de ejecución

if __name__ == '__main__':
    app.run(debug=True, port=4000)