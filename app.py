import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CREDENCIALES MAESTRAS ---
USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

# --- INTERFAZ PROFESIONAL DIMENSIONADA ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - ADMIN PANEL</title>
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

        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--text-main); margin: 0; }

        /* PANTALLA DE LOGIN CON TAMAÑO NORMALIZADO */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: #1a1c1e;
        }
        .login-card {
            background: var(--white); padding: 40px; border-radius: 12px; 
            width: 90%; max-width: 400px; box-sizing: border-box; text-align: center;
        }
        .login-card h2 { margin-bottom: 30px; letter-spacing: 2px; color: var(--primary); }

        /* DASHBOARD PRINCIPAL */
        #main-dashboard { display: none; }
        
        .sidebar {
            width: 260px; background: var(--primary); height: 100vh; position: fixed;
            color: white; padding-top: 30px; transition: 0.3s; z-index: 100;
        }
        .logo-section { text-align: center; padding: 0 20px 40px 20px; border-bottom: 1px solid #333; }
        .logo-img { width: 110px; height: 110px; border-radius: 50%; border: 4px solid var(--accent); object-fit: cover; margin-bottom: 15px; }

        .nav-menu { padding-top: 20px; }
        .nav-item {
            padding: 18px 25px; text-decoration: none; color: #aeb9c1; display: flex;
            align-items: center; font-size: 16px; transition: 0.2s;
        }
        .nav-item:hover { background: #2c2f33; color: white; border-left: 4px solid var(--accent); }
        .nav-item i { margin-right: 15px; width: 25px; font-size: 20px; }

        .main-content { margin-left: 260px; padding: 40px; min-height: 100vh; }
        
        /* TARJETAS DE CONTENIDO */
        .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .card { 
            background: var(--white); padding: 30px; border-radius: 10px; 
            border: 1px solid var(--border); box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 25px;
        }

        /* ELEMENTOS DE FORMULARIO */
        input[type="text"], input[type="password"], select {
            width: 100%; padding: 15px; margin: 12px 0; border: 1px solid var(--border);
            border-radius: 8px; font-size: 16px; background: #fafafa;
        }
        .btn-main {
            background: var(--accent); color: white; border: none; padding: 16px;
            width: 100%; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer;
            text-transform: uppercase; letter-spacing: 1px; transition: 0.3s;
        }
        .btn-main:hover { background: #27ae60; transform: translateY(-1px); }

        /* RESPONSIVO PARA IPHONE */
        @media (max-width: 900px) {
            .sidebar { width: 80px; }
            .sidebar span, .logo-section h4 { display: none; }
            .main-content { margin-left: 80px; padding: 20px; }
            .logo-img { width: 50px; height: 50px; }
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
                <img src="https://via.placeholder.com/150/222/fff?text=ADMIN" id="navLogo" class="logo-img">
                <h4 style="margin: 0; font-size: 18px;">Edwinnes</h4>
            </div>
            <div class="nav-menu">
                <a href="#" class="nav-item"><i class="fas fa-home"></i> <span>Inicio</span></a>
                <a href="#" class="nav-item"><i class="fas fa-user-plus"></i> <span>Nuevo Socio</span></a>
                <a href="#" class="nav-item"><i class="fas fa-shield-halved"></i> <span>KYC & Seguridad</span></a>
                <a href="#" class="nav-item"><i class="fas fa-gear"></i> <span>Configuración</span></a>
                <a href="/" class="nav-item" style="color: #ff7675; margin-top: 50px;"><i class="fas fa-power-off"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="header-bar">
                <h1>Panel de Control</h1>
                <span style="color: var(--text-muted);">Estado: <strong style="color: var(--accent);">● En Línea</strong></span>
            </div>

            <div class="card">
                <h3>Identidad Visual</h3>
                <p style="color: var(--text-muted);">Sube tu foto para personalizar el logotipo del menú.</p>
                <input type="file" accept="image/*" onchange="uploadLogo(event)">
            </div>

            <div class="card">
                <h3>Registro de Socios Fundadores</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <input type="text" placeholder="Nombre Completo">
                    <input type="text" placeholder="Cédula / ID">
                </div>
                <select>
                    <option>Categoría: Clásico</option>
                    <option>Categoría: Estándar</option>
                    <option>Categoría: Premium</option>
                    <option>Categoría: Elite</option>
                </select>
                <button class="btn-main">Guardar en Base de Datos</button>
            </div>
        </div>
    </div>

    <script>
        function validate() {
            const u = document.getElementById('user').value;
            const p = document.getElementById('pass').value;
            if(u === "Edwinnes" && p === "Diosamor") {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('main-dashboard').style.display = 'block';
            } else {
                document.getElementById('err').style.display = 'block';
            }
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
