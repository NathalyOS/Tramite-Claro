from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

tramite = {
    "nombre": "Trámite Claro",
    "fuente": "",
    "requisitos": [
        "Identificación oficial (INE)",
        "Comprobante de domicilio (original y copia)",
        "Comprobante de pago de derechos",
        "Fotografía tamaño infantil"
    ],
    "publicado": False
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Trámite Claro - Sprint 2</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f4; color: #333; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h2 { color: #001F3F; }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Módulo de Bania - Trámite Claro</h1>
    
    <!-- HISTORIA 4.1: Validación de fuente oficial -->
    <div class="card">
        <h2>4.1 - Administración de Fuente Oficial</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/publicar">
            <label>Enlace o referencia de la fuente oficial:</label><br>
            <input type="text" name="fuente" value="{{ tramite.fuente }}" style="width: 80%; padding: 8px; margin: 10px 0;"><br>
            <button type="submit" style="padding: 10px 20px; background: #001F3F; color: white; border: none; border-radius: 4px; cursor: pointer;">Publicar Trámite</button>
        </form>
        <p><b>Fuente registrada:</b> {{ tramite.fuente if tramite.fuente else '[Pendiente de publicación]' }}</p>
    </div>

    <!-- HISTORIA 3.2: Checklist y porcentaje completado -->
    <div class="card">
        <h2>3.2 - Checklist de Requisitos y Progreso</h2>
        {% if not tramite.requisitos %}
            <p class="error">Checklist no disponible / Sin requisitos</p>
        {% else %}
            <h3 id="progreso-txt">Progreso: 0%</h3>
            <form id="checklist-form">
                {% for req in tramite.requisitos %}
                    <div style="margin-bottom: 8px;">
                        <input type="checkbox" class="chk-item" onchange="calcularProgreso()">
                        <label>{{ req }}</label>
                    </div>
                {% endfor %}
            </form>
        {% endif %}
    </div>

    <script>
        function calcularProgreso() {
            const checkboxes = document.querySelectorAll('.chk-item');
            const total = checkboxes.length;
            if (total === 0) return;
            let marcados = 0;
            checkboxes.forEach(chk => {
                if (chk.checked) marcados++;
            });
            const porcentaje = Math.round((marcados / total) * 100);
            document.getElementById('progreso-txt').innerText = "Progreso: " + porcentaje + "%";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, tramite=tramite, error=None)

@app.route('/publicar', methods=['POST'])
def publicar():
    fuente = request.form.get('fuente', '').strip()
    if not fuente:
        return render_template_string(HTML_TEMPLATE, tramite=tramite, error="Falta fuente oficial para publicar")
    tramite['fuente'] = fuente
    tramite['publicado'] = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)