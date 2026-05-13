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
    <title>NOSOTROS RD - MASTER PANEL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #1a1c1e; --accent: #2ecc71; --bg: #f8f9fa; --white: #ffffff;
            --border: #e0e0e0; --text: #2c3e50; --danger: #e74c3c;
        }

        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.5; }

        /* LOGIN SCREEN */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: #1a1c1e; position: fixed; width: 100%; z-index: 2000;
        }
        .login-card { background: white; padding: 30px; border-radius: 12px; width: 90%; max-width: 380px; text-align: center; }

        /* DASHBOARD LAYOUT */
        #main-dashboard { display: none; }
        .sidebar { width: 260px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 100; transition: 0.3s; }
        .logo-section { text-align: center; padding: 20px; border-bottom: 1px solid #333; }
        .logo-img { width: 80px; height: 80px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; }
        
        .nav-menu { padding-top: 10px; }
        .nav-item { padding: 15px 20px; text-decoration: none; color: #aeb9c1; display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #222; }
        .nav-item:hover, .nav-item.active { background: #2c2f33; color: white; border-left: 4px solid var(--accent); }
        .nav-item i { margin-right: 12px; font-size: 18px; width: 20px; }

        .main-content { margin-left: 260px; padding: 20px; }

        /* HEADER DETAILS BOX */
        .header-stats { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; 
            margin-bottom: 20px; background: white; padding: 15px; border-radius: 8px; border: 1px solid var(--border);
        }
        .stat-box { text-align: center; border-right: 1px solid var(--border); }
        .stat-box:last-child { border-right: none; }
        .stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; display: block; }
        .stat-value { font-size: 16px; font-weight: bold; color: var(--accent); }

        /* CARDS & TABLES */
        .card { background: white; padding: 20px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px; display: none; }
        .card.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: #fafafa; }

        .btn-pro { background: var(--accent); color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; background: #eee; }

        @media (max-width: 900px) {
            .sidebar { width: 60px; } .sidebar span, .logo-section h4 { display: none; }
            .main-content { margin-left: 60px; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h2 style="margin: 0 0 20px 0;">NOSOTROS RD</h2>
            <input type="text" id="user" placeholder="Usuario" style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px;">
            <input type="password" id="pass" placeholder="Contraseña" style="width:100%; padding:10px; margin-bottom:20px; border:1px solid #ccc; border-radius:5px;">
            <button class="btn-pro" onclick="validate()">ACCEDER</button>
            <p id="err" style="color:red; display:none; margin-top:10px;">Credenciales Erróneas</p>
        </div>
    </div>

    <div id="main-dashboard">
        <div class="sidebar">
            <div class="logo-section">
                <img src="https://via.placeholder.com/150/000/fff?text=EDWIN" id="navLogo" class="logo-img">
                <h4 style="margin: 10px 0 0 0; font-size: 14px;">Edwinnes</h4>
            </div>
            <div class="nav-menu">
                <a onclick="showTab('inicio')" class="nav-item active" id="btn-inicio"><i class="fas fa-desktop"></i> <span>Dashboard</span></a>
                <a onclick="showTab('usuarios')" class="nav-item" id="btn-usuarios"><i class="fas fa-users"></i> <span>Usuarios Registrados</span></a>
                <a onclick="showTab('soporte')" class="nav-item" id="btn-soporte"><i class="fas fa-envelope"></i> <span>Soporte (Inbox)</span></a>
                <a onclick="showTab('identidad')" class="nav-item" id="btn-identidad"><i class="fas fa-camera"></i> <span>Identidad Visual</span></a>
                <a onclick="logout()" class="nav-item" style="color: var(--danger);"><i class="fas fa-power-off"></i> <span>Salir</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="header-stats">
                <div class="stat-box"><span class="stat-label">Socios Activos</span><span class="stat-value">142 / 150</span></div>
                <div class="stat-box"><span class="stat-label">Soporte Pendiente</span><span class="stat-value">3</span></div>
                <div class="stat-box"><span class="stat-label">Licencia Sistema</span><span class="stat-value">VIGENTE</span></div>
            </div>

            <div id="inicio" class="card active">
                <h3>Resumen de Actividad</h3>
                <p>Bienvenido al núcleo de Nosotros RD. Aquí puedes gestionar los accesos y notificaciones del sistema.</p>
                <button class="btn-pro" onclick="sendPush()">ENVIAR NOTIFICACIÓN PUSH A TODOS</button>
            </div>

            <div id="usuarios" class="card">
                <h3>Gestión de Usuarios</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Categoría</th>
                            <th>Habilitado Por</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Juan Pérez</td>
                            <td>Elite</td>
                            <td>
                                <select style="padding:5px;">
                                    <option>1 Semana</option>
                                    <option>1 Quincena</option>
                                    <option selected>1 Mes</option>
                                </select>
                            </td>
                            <td><span class="badge" style="background:#d4edda; color:#155724;">Activo</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div id="soporte" class="card">
                <h3>Bandeja de Soporte</h3>
                <div style="display:flex; border-bottom:1px solid #ddd; margin-bottom:15px;">
                    <button style="flex:1; padding:10px; background:none; border:none; border-bottom:2px solid var(--accent);">Entrada</button>
                    <button style="flex:1; padding:10px; background:none; border:none;">Salida</button>
                </div>
                <div style="padding:10px; border:1px solid #eee; margin-bottom:10px;">
                    <strong>Socio #023:</strong> Problema con el GPS de la app.
                    <span style="font-size:10px; float:right;">12:45 PM</span>
                </div>
                <input type="text" placeholder="Escribir respuesta rápida...">
                <button class="btn-pro" style="background:#333;">Responder</button>
            </div>

            <div id="identidad" class="card">
                <h3>Identidad Visual</h3>
                <p>Sube tu foto de administrador aquí:</p>
                <input type="file" accept="image/*" onchange="uploadLogo(event)">
            </div>
        </div>
    </div>

    <script>
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

        function sendPush() {
            alert("Notificación Push enviada a todos los socios de Nosotros RD");
        }

        function logout() {
            localStorage.removeItem('logged');
            window.location.reload();
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
