from flask import Flask, render_template, request, redirect, url_for
import os

from tkinter import *
from tkinter import messagebox as MessageBox

# Configurar las carpetas de la aplicación
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

#rutas de la aplicación
@app.route('/')
def home():
    return render_template('presentacion/index.html')

@app.route('/categorias')
def categorias():
    return render_template('presentacion/categorias.html')

@app.route('/crear-categoria')
def crear_categoria():
    return render_template('presentacion/crear-categoria.html')

@app.route('/guia-tramite')
def guia_tramite():
    return render_template('presentacion/guia-tramite.html')

# Definimos el __name__ como plantilla principal a index.html y el puerto de ejecución

if __name__ == '__main__':
    app.run(debug=True, port=4000)