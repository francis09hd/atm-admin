import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Credenciales de Seguridad de Nosotros RD
USER_ID = "Edwinnes"
PASSWORD_MASTER = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - SISTEMA CENTRAL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #000000; --accent: #2ecc71; --bg: #ffffff; 
            --text: #1a1a1a; --border: #ececec; --danger: #ff4d4d;
        }

        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.6; }

        /* LOGIN SELLADO */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: var(--primary); position: fixed; width: 100%; z-index: 9999;
        }
        .login-card { background: white; padding: 45px; border-radius: 15px; width: 85%; max-width: 380px; text-align: center; }
        .login-card h1 { color: #000; font-weight: 900; margin-bottom: 5px; }

        /* SIDEBAR CON FOTO INTEGRADA */
        .sidebar { width: 280px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 1000; }
        .nav-header { padding: 40px 20px; text-align: center; background: #080808; border-bottom: 1px solid #222; }
        .profile-circle { width: 110px; height: 110px; border-radius: 50%; border: 4px solid var(--accent); object-fit: cover; margin-bottom: 15px; }
        
        .nav-link { padding: 18px 25px; text-decoration: none; color: #888; display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #111; }
        .nav-link:hover, .nav-link.active { background: #111; color: white; border-left: 6px solid var(--accent); }
        .nav-link i { margin-right: 15px; width: 25px; font-size: 1.2em; }

        /* CONTENIDO PRINCIPAL */
        .main-content { margin-left: 280px; padding: 35px; }
        .top-brand { border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 30px; }

        /* TABLA Y ACCIONES */
        .card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #f9f9f9; padding: 15px; text-align: left; font-size: 0.85em; text-transform: uppercase; border-bottom: 2px solid var(--border); }
        td { padding: 15px; border-bottom: 1px solid var(--border); font-size: 0.95em; }

        .btn { padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px; transition: 0.3s; }
        .btn-on { background: var(--accent); color: white; }
        .btn-off { background: var(--danger); color: white; }
        
        /* BANDEJA SOPORTE */
        .chat-container { height: 200px; background: #f1f1f1; border-radius: 8px; padding: 15px; margin-bottom: 15px; overflow-y: auto; border: 1px solid #ddd; }

        @media (max-width: 900px) {
            .sidebar { width: 70px; } .sidebar span, .nav-header h4, .nav-header button { display: none; }
            .main-content { margin-left: 70px; padding: 15px; }
            .profile-circle { width: 50px; height: 50px; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h1>NOSOTROS RD</h1>
            <p style="color: #777; margin-bottom: 30px;">SISTEMA CENTRAL</p>
            <input type="text" id="user" placeholder="OPERADOR" style="width:100%; padding:15px; margin-bottom:15px; border:1px solid #ddd; border-radius:8px;">
            <input type="password" id="pass" placeholder="PASSWORD" style="width:100%; padding:15px; margin-bottom:25px; border:1px solid #ddd; border-radius:8px;">
            <button onclick="access()" style="width:100%; padding:15px; background:var(--accent); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">INGRESAR</button>
            <p id="err" style="color:red; display:none; margin-top:15px;">DATOS INVÁLIDOS</p>
        </div>
    </div>

    <div id="dashboard" style="display:none;">
        <div class="sidebar">
            <div class="nav-header">
                <img src="https://via.placeholder.com/150/000/fff?text=EDWIN" id="userPhoto" class="profile-circle">
                <h4 style="margin:0;">Edwinnes</h4>
                <input type="file" id="file" hidden onchange="updatePhoto(event)">
                <button onclick="document.getElementById('file').click()" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:11px; margin-top:10px;">[ ACTUALIZAR LOGO ]</button>
            </div>
            <div class="nav-menu">
                <a onclick="openTab('m-users')" class="nav-link active" id="btn-m-users"><i class="fas fa-users"></i> <span>Gestión Usuarios</span></a>
                <a onclick="openTab('m-chat')" class="nav-link" id="btn-m-chat"><i class="fas fa-comment-alt"></i> <span>Soporte Bot</span></a>
                <a onclick="exit()" class="nav-link" style="color:var(--danger); border-top:1px solid #222; margin-top:20px;"><i class="fas fa-power-off"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="top-brand">
                <h1 style="margin:0; font-weight:900; letter-spacing:-1px;">NOSOTROS RD</h1>
                <span style="font-size:12px; color:var(--accent);">● SERVIDOR DE CONTROL ACTIVO</span>
            </div>

            <div id="m-users" class="tab-item">
                <div class="card">
                    <div style="margin-bottom:20px; display:flex; gap:10px;">
                        <button class="btn btn-on">ACTIVAR SELECCIÓN</button>
                        <button class="btn btn-off">DESACTIVAR SELECCIÓN</button>
                    </div>
                    <div style="overflow-x:auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th><input type="checkbox"></th>
                                    <th>Nombre / Teléfono / Correo</th>
                                    <th>ID Dispositivo</th>
                                    <th>Días Activo</th>
                                    <th>Habilitación</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><input type="checkbox"></td>
                                    <td>
                                        <strong>Usuario Indefinido</strong><br>
                                        <small>809-xxx-xxxx | mail@nosotros.rd</small>
                                    </td>
                                    <td><code style="background:#f4f4f4; padding:4px;">RD-BOT-2026</code></td>
                                    <td style="color:var(--danger); font-weight:bold;">15 Días</td>
                                    <td>
                                        <select style="padding:6px; border-radius:4px;">
                                            <option>Semana</option><option>Quincena</option><option selected>Mes</option>
                                        </select>
                                    </td>
                                    <td><button class="btn btn-off" style="padding:8px;">DESACTIVAR</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="m-chat" class="tab-item" style="display:none;">
                <div class="card">
                    <h3>Bandeja de Mensajes</h3>
                    <div class="chat-container">
                        <div style="background:white; padding:10px; border-radius:8px; margin-bottom:10px;">
                            <small>SISTEMA:</small> Esperando conexión del bot...
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <input type="text" placeholder="Instrucción técnica..." style="flex:1; padding:12px; border:1px solid #ddd; border-radius:8px;">
                        <button class="btn btn-on" style="width:120px;">ENVIAR</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function access() {
            if(document.getElementById('user').value === "Edwinnes" && document.getElementById('pass').value === "Diosamor") {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
            } else { document.getElementById('err').style.display = 'block'; }
        }
        function openTab(id) {
            document.querySelectorAll('.tab-item').forEach(t => t.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(id).style.display = 'block';
            document.getElementById('btn-' + id).classList.add('active');
        }
        function updatePhoto(e) { document.getElementById('userPhoto').src = URL.createObjectURL(e.target.files[0]); }
        function exit() { window.location.reload(); }
    </script>
</body>
</html>
