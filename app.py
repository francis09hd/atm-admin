import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CREDENCIALES MAESTRAS ---
USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

# --- INTERFAZ PROFESIONAL (HTML/CSS) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOSOTROS RD - PRO PANEL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #2c3e50;
            --accent: #27ae60;
            --bg: #f4f7f6;
            --white: #ffffff;
            --text: #333;
        }

        /* TEMA BLANCO PROFESIONAL */
        body.light-theme {
            --bg: #f4f7f6;
            --white: #ffffff;
            --text: #333;
            --primary: #2c3e50;
        }

        /* TEMA OSCURO (Opcional) */
        body.dark-theme {
            --bg: #1a1a1a;
            --white: #2d2d2d;
            --text: #eee;
            --primary: #0f0;
        }

        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; transition: 0.3s; }
        
        /* PANTALLA DE LOGIN */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        }
        .login-card {
            background: var(--white); padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            text-align: center; width: 100%; max-width: 350px;
        }

        /* DASHBOARD PRINCIPAL */
        #main-dashboard { display: none; }
        .sidebar {
            width: 250px; background: var(--primary); height: 100vh; position: fixed; color: white;
            display: flex; flex-direction: column; align-items: center; padding-top: 20px;
        }
        .logo-container { text-align: center; margin-bottom: 30px; }
        .logo-img { width: 100px; height: 100px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; background: #eee; }
        
        .menu-item {
            width: 100%; padding: 15px 25px; text-decoration: none; color: #bdc3c7; display: flex; align-items: center; transition: 0.2s;
        }
        .menu-item:hover { background: rgba(255,255,255,0.1); color: white; }
        .menu-item i { margin-right: 15px; width: 20px; }

        .content { margin-left: 250px; padding: 40px; }
        .card { background: var(--white); padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
        
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .btn-pro { background: var(--accent); color: white; border: none; padding: 12px; width: 100%; border-radius: 5px; cursor: pointer; font-weight: bold; }
        
        @media (max-width: 768px) {
            .sidebar { width: 70px; }
            .sidebar span, .logo-container h4 { display: none; }
            .content { margin-left: 70px; }
        }
    </style>
</head>
<body class="light-theme">

    <div id="login-screen">
        <div class="login-card">
            <h2 style="color: #333;">NOSOTROS RD</h2>
            <p style="color: #666; font-size: 0.9em;">INGRESO AL NÚCLEO</p>
            <input type="text" id="user" placeholder="Usuario">
            <input type="password" id="pass" placeholder="Contraseña">
            <button class="btn-pro" onclick="checkAuth()">ACCEDER</button>
            <p id="error" style="color: red; font-size: 0.8em; margin-top: 10px; display: none;">Credenciales Incorrectas</p>
        </div>
    </div>

    <div id="main-dashboard">
        <div class="sidebar">
            <div class="logo-container">
                <img src="https://via.placeholder.com/150/000?text=EDWIN" id="profilePic" class="logo-img">
                <h4 style="margin-top: 10px;">Edwinnes</h4>
            </div>
            <a href="#" class="menu-item"><i class="fas fa-chart-line"></i> <span>Dashboard</span></a>
            <a href="#" class="menu-item"><i class="fas fa-users"></i> <span>Socios</span></a>
            <a href="#" class="menu-item"><i class="fas fa-file-shield"></i> <span>KYC</span></a>
            <a href="#" class="menu-item" onclick="toggleTheme()"><i class="fas fa-adjust"></i> <span>Cambiar Tema</span></a>
            <a href="/" class="menu-item" style="margin-top: auto; color: #e74c3c;"><i class="fas fa-sign-out-alt"></i> <span>Salir</span></a>
        </div>

        <div class="content">
            <h1>Bienvenido, Edwinnes</h1>
            <div class="card">
                <h3>Configuración de Perfil</h3>
                <p>Sube tu logotipo o foto para el menú:</p>
                <input type="file" accept="image/*" onchange="updatePhoto(event)">
            </div>

            <div class="card">
                <h3>Registro de Socios Fundadores</h3>
                <input type="text" placeholder="Nombre del Socio">
                <select>
                    <option>Categoría: Clásico</option>
                    <option>Categoría: Estándar</option>
                    <option>Categoría: Premium</option>
                    <option>Categoría: Elite</option>
                </select>
                <button class="btn-pro">Guardar Registro</button>
            </div>
        </div>
    </div>

    <script>
        function checkAuth() {
            const u = document.getElementById('user').value;
            const p = document.getElementById('pass').value;
            if(u === "Edwinnes" && p === "Diosamor") {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('main-dashboard').style.display = 'block';
            } else {
                document.getElementById('error').style.display = 'block';
            }
        }

        function updatePhoto(event) {
            const pic = document.getElementById('profilePic');
            pic.src = URL.createObjectURL(event.target.files[0]);
        }

        function toggleTheme() {
            document.body.classList.toggle('dark-theme');
            document.body.classList.toggle('light-theme');
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
