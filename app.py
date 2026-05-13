import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CREDENCIALES MAESTRAS ---
USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

# --- INTERFAZ CON SELECTOR DE TEMAS ---
HTML_ADMIN = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENTINEL MASTER - NOSOTROS RD</title>
    <style>
        :root { --main-color: #0f0; --bg-color: #000; --panel-bg: rgba(0,20,0,0.8); }
        
        /* TEMAS CONFIGURABLES */
        .theme-red { --main-color: #f00; --panel-bg: rgba(20,0,0,0.8); }
        .theme-blue { --main-color: #0cf; --panel-bg: rgba(0,10,20,0.8); }
        .theme-gold { --main-color: #d4af37; --panel-bg: rgba(20,20,0,0.8); }

        body { background: var(--bg-color); color: var(--main-color); font-family: 'Courier New', monospace; margin: 0; padding: 10px; transition: 0.5s; }
        .master-panel { border: 2px solid var(--main-color); padding: 20px; box-shadow: 0 0 25px var(--main-color); max-width: 500px; margin: auto; background: var(--panel-bg); }
        
        h1 { text-align: center; letter-spacing: 5px; font-size: 1.5em; border-bottom: 2px solid var(--main-color); padding-bottom: 10px; }
        
        .profile-container { text-align: center; margin: 20px 0; }
        .avatar { width: 130px; height: 130px; border: 3px solid var(--main-color); border-radius: 50%; object-fit: cover; background: #111; }
        
        .info-box { border: 1px solid var(--main-color); padding: 15px; margin-bottom: 15px; }
        
        input, select { width: 100%; background: #000; border: 1px solid var(--main-color); color: var(--main-color); padding: 10px; margin: 10px 0; box-sizing: border-box; }
        
        .action-btn { width: 100%; background: var(--main-color); color: #000; border: none; padding: 15px; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 10px; }
        
        .theme-selector { display: flex; justify-content: space-between; margin-bottom: 20px; }
        .dot { height: 30px; width: 30px; border-radius: 50%; cursor: pointer; border: 2px solid #fff; }
    </style>
</head>
<body id="body-theme">
    <div class="master-panel">
        <h1>SENTINEL CORE</h1>

        <div class="theme-selector">
            <div class="dot" style="background: #0f0;" onclick="setTheme('')"></div>
            <div class="dot" style="background: #f00;" onclick="setTheme('theme-red')"></div>
            <div class="dot" style="background: #0cf;" onclick="setTheme('theme-blue')"></div>
            <div class="dot" style="background: #d4af37;" onclick="setTheme('theme-gold')"></div>
        </div>
        
        <div class="profile-container">
            <img src="https://via.placeholder.com/150/000000/00FF00?text=EDWINNES" class="avatar" id="output">
            <p style="font-size: 1.2em;">OPERADOR: <strong>Edwinnes</strong></p>
            <input type="file" accept="image/*" onchange="loadFile(event)" id="fileInput" style="display:none;">
            <button class="action-btn" style="padding: 5px; font-size: 0.7em;" onclick="document.getElementById('fileInput').click()">CAMBIAR FOTO</button>
        </div>

        <div class="info-box">
            <h3>REGISTRO RÁPIDO</h3>
            <input type="text" placeholder="NOMBRE SOCIO">
            <select>
                <option>CATEGORÍA: CLÁSICO</option>
                <option>CATEGORÍA: ESTÁNDAR</option>
                <option>CATEGORÍA: PREMIUM</option>
                <option>CATEGORÍA: ELITE</option>
            </select>
            <button class="action-btn">REGISTRAR</button>
        </div>

        <div class="info-box">
            <h3 style="color: var(--main-color);">SEGURIDAD: Diosamor</h3>
            <button class="action-btn" style="background: #333; color: #fff;">LOGOUT</button>
        </div>
    </div>

    <script>
        function setTheme(themeName) {
            document.getElementById('body-theme').className = themeName;
        }
        var loadFile = function(event) {
            var output = document.getElementById('output');
            output.src = URL.createObjectURL(event.target.files[0]);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_ADMIN)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get("key") == PASSWORD_MASTER:
        return jsonify({"auth": "OK"}), 200
    return jsonify({"auth": "FAIL"}), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
