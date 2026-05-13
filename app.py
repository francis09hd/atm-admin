import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - CONTROL PANEL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #1a1c1e;
            --accent: #2ecc71;
            --bg: #f8f9fa;
            --white: #ffffff;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --border: #e0e0e0;
        }

        body { 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background: var(--bg); 
            color: var(--text-main); 
            margin: 0; 
            line-height: 1.6; /* Evita que las letras se encimen */
        }

        /* LOGIN */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: #1a1c1e; position: fixed; width: 100%; z-index: 1000;
        }
        .login-card {
            background: var(--white); padding: 40px; border-radius: 12px; 
            width: 90%; max-width: 400px; text-align: center;
        }

        /* DASHBOARD */
        #main-dashboard { display: none; }
        
        .sidebar {
            width: 260px; background: var(--primary); height: 100vh; position: fixed;
            color: white; padding-top: 30px; z-index: 100;
        }
        .logo-section { text-align: center; padding: 0 20px 30px 20px; border-bottom: 1px solid #333; }
        .logo-img { width: 90px; height: 90px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 10px; }

        .nav-menu { padding-top: 15px; }
        .nav-item {
            padding: 15px 25px; text-decoration: none; color: #aeb9c1; display: flex;
            align-items: center; font-size: 15px; transition: 0.2s; cursor: pointer;
        }
        .nav-item:hover, .nav-item.active { background: #2c2f33; color: white; border-left: 4px solid var(--accent); }
        .nav-item i { margin-right: 12px; width: 20px; font-size: 18px; }

        .main-content { margin-left: 260px; padding: 30px; min-height: 100vh; }
        
        .card { 
            background: var(--white); padding: 25px; border-radius: 10px; 
            border: 1px solid var(--border); margin-bottom: 20px; display: none;
        }
        .card.active { display: block; }

        h1, h3 { margin-bottom: 20px; line-height: 1.2; }
        p { margin-bottom: 15px; }

        input, select {
            width: 100%; padding: 12px; margin: 10px 0; border: 1px solid var(--border);
            border-radius: 6px; font-size: 15px; display: block;
        }
        .btn-main {
            background: var(--accent); color: white; border: none; padding: 14px;
            width: 100%; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer;
        }

        @media (max-width: 900px) {
            .sidebar { width: 70px; }
            .sidebar span, .logo-section h4 { display: none; }
            .main-content { margin-left: 70px; padding: 15px; }
            .logo-img { width: 45px; height: 45px; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h2>NOSOTROS RD</h2>
            <input type="text" id="user" placeholder="Usuario">
            <input type="password" id="pass" placeholder="Contraseña">
            <button class="btn-main" onclick="validate()">INGRESAR</button>
            <p id="err" style="color: #e74c3c; margin-top: 15px; display: none;">Acceso Denegado</p>
        </div>
    </div>

    <div id="main-dashboard">
        <div class="sidebar">
            <div class="logo-section">
                <img src="https://via.placeholder.com/150/222/fff?text=EDWIN" id="navLogo" class="logo-img">
                <h4 style="margin: 0;">Edwinnes</h4>
            </div>
            <div class="nav-menu">
                <a onclick="showTab('inicio')" class="nav-item active" id="btn-inicio"><i class="fas fa-home"></i> <span>Inicio</span></a>
                <a onclick="showTab('registro')" class="nav-item" id="btn-registro"><i class="fas fa-user-plus"></i> <span>Registro de Usuario</span></a>
                <a onclick="showTab('identidad')" class="nav-item" id="btn-identidad"><i class="fas fa-image"></i> <span>Identidad Visual</span></a>
                <a onclick="showTab('seguridad')" class="nav-item" id="btn-seguridad"><i class="fas fa-shield-halved"></i> <span>Seguridad</span></a>
                <a onclick="logout()" class="nav-item" style="color: #ff7675; margin-top: 30px;"><i class="fas fa-power-off"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div id="inicio" class="card active">
                <h1>Panel Principal</h1>
                <p>Bienvenido al sistema de gestión de <strong>Nosotros RD</strong>. Seleccione una opción del menú lateral.</p>
            </div>

            <div id="registro" class="card">
                <h3>Registro de Socios Fundadores</h3>
                <input type="text" placeholder="Nombre del Socio">
                <input type="text" placeholder="Cédula / ID">
                <select>
                    <option>Categoría: Clásico</option>
                    <option>Categoría: Estándar</option>
                    <option>Categoría: Premium</option>
                    <option>Categoría: Elite</option>
                </select>
                <button class="btn-main">Guardar Socio</button>
            </div>

            <div id="identidad" class="card">
                <h3>Identidad Visual</h3>
                <p>Actualice su logotipo o foto de perfil del sistema:</p>
                <input type="file" accept="image/*" onchange="uploadLogo(event)">
            </div>

            <div id="seguridad" class="card">
                <h3>Protocolos de Seguridad</h3>
                <p>Estado del Sistema: <strong style="color: var(--accent);">Protegido</strong></p>
                <button class="btn-main" style="background:#333;">Cambiar Llave Diosamor</button>
            </div>
        </div>
    </div>

    <script>
        // Comprobar si ya estaba logueado
        window.onload = function() {
            if(localStorage.getItem('logged') === 'true') {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('main-dashboard').style.display = 'block';
            }
        }

        function validate() {
            const u = document.getElementById('user').value;
            const p = document.getElementById('pass').value;
            if(u === "Edwinnes" && p === "Diosamor") {
                localStorage.setItem('logged', 'true');
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('main-dashboard').style.display = 'block';
            } else {
                document.getElementById('err').style.display = 'block';
            }
        }

        function logout() {
            localStorage.removeItem('logged');
            window.location.reload();
        }

        function showTab(id) {
            document.querySelectorAll('.card').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            document.getElementById('btn-' + id).classList.add('active');
        }

        function uploadLogo(event) {
            const logo = document.getElementById('navLogo');
            logo.src = URL.createObjectURL(event.target.files[0]);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
