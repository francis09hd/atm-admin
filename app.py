import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Credenciales Maestras
USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - CONTROL MASTER</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #0a0a0a; --accent: #2ecc71; --bg: #ffffff; 
            --border: #eeeeee; --text-dark: #111111; --danger: #ff3333;
        }

        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: var(--bg); color: var(--text-dark); margin: 0; line-height: 1.6; 
        }

        /* ACCESO */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: var(--primary); position: fixed; width: 100%; z-index: 9999;
        }
        .login-card { background: white; padding: 40px; border-radius: 16px; width: 85%; max-width: 360px; text-align: center; }

        /* SIDEBAR SELLADO */
        .sidebar { width: 280px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 1000; transition: 0.3s; }
        .nav-profile { padding: 40px 20px; text-align: center; border-bottom: 1px solid #222; }
        .profile-img { 
            width: 100px; height: 100px; border-radius: 50%; border: 3px solid var(--accent); 
            object-fit: cover; margin-bottom: 15px; background: #222;
        }
        
        .nav-link { padding: 18px 25px; text-decoration: none; color: #999; display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #111; }
        .nav-link:hover, .nav-link.active { background: #1a1a1a; color: white; border-left: 6px solid var(--accent); }
        .nav-link i { margin-right: 15px; width: 20px; text-align: center; font-size: 1.1em; }

        /* CONTENIDO */
        .main-content { margin-left: 280px; padding: 40px; min-height: 100vh; }
        .brand-bar { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 3px solid var(--primary); padding-bottom: 15px; }

        /* TABLA DE USUARIOS */
        .card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .table-container { overflow-x: auto; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { background: #fafafa; padding: 15px; text-align: left; color: #666; border-bottom: 2px solid var(--border); }
        td { padding: 15px; border-bottom: 1px solid var(--border); }
        
        .btn { border: none; border-radius: 8px; padding: 10px 16px; font-weight: bold; cursor: pointer; transition: 0.2s; font-size: 12px; }
        .btn-on { background: var(--accent); color: white; }
        .btn-off { background: var(--danger); color: white; }

        @media (max-width: 900px) {
            .sidebar { width: 75px; } .sidebar span, .nav-profile h4, .nav-profile button { display: none; }
            .main-content { margin-left: 75px; padding: 20px; }
            .profile-img { width: 45px; height: 45px; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h1 style="margin:0 0 10px 0; letter-spacing: -1px;">NOSOTROS RD</h1>
            <p style="color: #666; margin-bottom: 30px; font-size: 14px;">Panel de Administración Central</p>
            <input type="text" id="user" placeholder="Usuario de Acceso" style="width:100%; padding:14px; margin-bottom:15px; border:1px solid #ddd; border-radius:8px; box-sizing: border-box;">
            <input type="password" id="pass" placeholder="Contraseña Segura" style="width:100%; padding:14px; margin-bottom:25px; border:1px solid #ddd; border-radius:8px; box-sizing: border-box;">
            <button onclick="login()" style="width:100%; padding:14px; background:var(--accent); color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">INGRESAR AL NÚCLEO</button>
            <p id="err" style="color:var(--danger); display:none; margin-top:15px; font-size:14px;">Credenciales no válidas</p>
        </div>
    </div>

    <div id="app-shell" style="display:none;">
        <div class="sidebar">
            <div class="nav-profile">
                <img src="https://via.placeholder.com/150/111/fff?text=ADMIN" id="adminPic" class="profile-img">
                <h4 style="margin:0; font-size:16px;">Edwinnes</h4>
                <input type="file" id="upload" hidden onchange="updatePhoto(event)">
                <button onclick="document.getElementById('upload').click()" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:11px; margin-top:10px;">[ ACTUALIZAR LOGO ]</button>
            </div>
            <div class="nav-menu">
                <a onclick="showTab('users')" class="nav-link active" id="l-users"><i class="fas fa-robot"></i> <span>Gestión del Bot</span></a>
                <a onclick="showTab('chat')" class="nav-link" id="l-chat"><i class="fas fa-terminal"></i> <span>Consola Soporte</span></a>
                <a onclick="logout()" class="nav-link" style="color:var(--danger); margin-top:30px;"><i class="fas fa-power-off"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="brand-bar">
                <h1 style="margin:0; font-weight: 900; color: var(--primary);">NOSOTROS RD</h1>
                <div style="text-align:right">
                    <span style="font-size:12px; color:var(--accent); font-weight:bold;">● SISTEMA EN LÍNEA</span>
                </div>
            </div>

            <div id="users" class="tab-view">
                <div class="card">
                    <div style="margin-bottom:25px; display:flex; gap:12px;">
                        <button class="btn btn-on">ACTIVAR SELECCIONADOS</button>
                        <button class="btn btn-off">DESACTIVAR SELECCIONADOS</button>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th><input type="checkbox"></th>
                                    <th>Usuario / Contacto</th>
                                    <th>ID Dispositivo</th>
                                    <th>Vencimiento</th>
                                    <th>Plan de Tiempo</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><input type="checkbox"></td>
                                    <td>
                                        <strong>Usuario Indefinido</strong><br>
                                        <small style="color:#777;">809-xxx-xxxx | bot@nosotros.rd</small>
                                    </td>
                                    <td><code style="background:#f0f0f0; padding:4px; border-radius:4px;">ID-BOT-RD-01</code></td>
                                    <td style="color:var(--danger); font-weight:bold;">15 Días</td>
                                    <td>
                                        <select style="padding:6px; border-radius:4px; border:1px solid #ccc;">
                                            <option>Semana</option>
                                            <option>Quincena</option>
                                            <option selected>Mes</option>
                                        </select>
                                    </td>
                                    <td><button class="btn btn-off">DESACTIVAR</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="chat" class="tab-view" style="display:none;">
                <div class="card">
                    <h3>Mensajería Técnica de Soporte</h3>
                    <div style="height:250px; background:#f8f9fa; border:1px solid #ddd; border-radius:8px; padding:15px; margin-bottom:15px; overflow-y:auto;">
                        <div style="background:white; padding:10px; border-radius:8px; margin-bottom:10px; border-left:4px solid var(--accent);">
                            <strong>SISTEMA:</strong> Consola lista para recibir comandos.
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <input type="text" placeholder="Escribir comando o respuesta..." style="flex:1; padding:12px; border:1px solid #ddd; border-radius:8px;">
                        <button class="btn btn-on" style="width:120px;">ENVIAR</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function login() {
            const u = document.getElementById('user').value;
            const p = document.getElementById('pass').value;
            if(u === "Edwinnes" && p === "Diosamor") {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app-shell').style.display = 'block';
            } else { document.getElementById('err').style.display = 'block'; }
        }
        function showTab(id) {
            document.querySelectorAll('.tab-view').forEach(t => t.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(id).style.display = 'block';
            document.getElementById('l-' + id).classList.add('active');
        }
        function updatePhoto(e) { document.getElementById('adminPic').src = URL.createObjectURL(e.target.files[0]); }
        function logout() { window.location.reload(); }
    </script>
</body>
</html>
"""

@app.route('/')
def main_view():
    return render_template_string(HTML_INTERFACE)

if __name__ == "__main__":
    # Configuración para que Render use el puerto correcto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
