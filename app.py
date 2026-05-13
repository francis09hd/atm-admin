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
    <title>NOSOTROS RD - CONTROL MASTER</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #1a1c1e; --accent: #2ecc71; --bg: #ffffff; 
            --border: #e0e0e0; --text: #333; --danger: #e74c3c;
        }

        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.4; }

        /* LOGIN */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: var(--primary); position: fixed; width: 100%; z-index: 9999;
        }
        .login-card { background: white; padding: 40px; border-radius: 8px; width: 85%; max-width: 350px; text-align: center; }

        /* SIDEBAR CON FOTO INTEGRADA */
        .sidebar { width: 280px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 1000; }
        .admin-profile { padding: 30px 20px; text-align: center; border-bottom: 1px solid #333; }
        .admin-photo { width: 90px; height: 90px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 10px; }
        
        .nav-link { padding: 15px 25px; text-decoration: none; color: #bbb; display: flex; align-items: center; cursor: pointer; font-size: 14px; }
        .nav-link:hover, .nav-link.active { background: #2c2f33; color: white; border-left: 4px solid var(--accent); }
        .nav-link i { margin-right: 15px; width: 20px; text-align: center; }

        /* CONTENIDO */
        .main-content { margin-left: 280px; padding: 30px; }
        .brand-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid var(--bg); padding-bottom: 10px; }
        
        /* TABLA DE USUARIOS PROFESIONAL */
        .data-card { background: white; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; padding: 20px; margin-bottom: 25px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid var(--border); color: #666; }
        td { padding: 12px; border-bottom: 1px solid var(--border); }
        
        .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .btn-action { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        
        /* MENSAJERÍA */
        .chat-box { height: 200px; border: 1px solid var(--border); background: #fafafa; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        
        @media (max-width: 900px) {
            .sidebar { width: 70px; } .sidebar span, .admin-profile h4 { display: none; }
            .main-content { margin-left: 70px; padding: 15px; }
            .admin-photo { width: 45px; height: 45px; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h2 style="color: #1a1c1e;">NOSOTROS RD</h2>
            <input type="text" id="user" placeholder="Usuario" style="width:100%; padding:12px; margin:10px 0; border:1px solid #ddd;">
            <input type="password" id="pass" placeholder="Contraseña" style="width:100%; padding:12px; margin:10px 0; border:1px solid #ddd;">
            <button onclick="login()" style="width:100%; padding:12px; background:#2ecc71; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">ENTRAR</button>
        </div>
    </div>

    <div id="main-dashboard" style="display:none;">
        <div class="sidebar">
            <div class="admin-profile">
                <img src="https://via.placeholder.com/150/222/fff?text=EDWIN" id="navLogo" class="admin-photo">
                <h4 style="margin:0; font-size:16px;">Edwinnes</h4>
                <input type="file" id="up" hidden onchange="changePic(event)">
                <button onclick="document.getElementById('up').click()" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:10px;">CAMBIAR FOTO</button>
            </div>
            <div class="nav-menu">
                <a onclick="showTab('users')" class="nav-link active"><i class="fas fa-users"></i> <span>Gestión de Usuarios</span></a>
                <a onclick="showTab('support')" class="nav-link"><i class="fas fa-comments"></i> <span>Bandeja de Mensajes</span></a>
                <a onclick="logout()" class="nav-link" style="color:var(--danger);"><i class="fas fa-sign-out-alt"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="brand-header">
                <h1 style="margin:0; color:var(--primary);">NOSOTROS RD</h1>
                <div style="text-align:right">
                    <span style="font-size:12px; color:gray;">SISTEMA OPERATIVO V1.8</span>
                </div>
            </div>

            <div id="users" class="tab-content">
                <div class="data-card">
                    <div style="margin-bottom:15px; display:flex; gap:10px;">
                        <button class="btn-action" style="background:#2c3e50; color:white;">Activar Seleccionados</button>
                        <button class="btn-action" style="background:var(--danger); color:white;">Desactivar Seleccionados</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th><input type="checkbox"></th>
                                <th>Nombre</th>
                                <th>Correo / Teléfono</th>
                                <th>ID Dispositivo</th>
                                <th>Días Restantes</th>
                                <th>Habilitación</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><input type="checkbox"></td>
                                <td>Usuario Indefinido</td>
                                <td>edwin@ejemplo.com<br>809-000-0000</td>
                                <td>BOT-X892J</td>
                                <td style="font-weight:bold; color:var(--danger);">12 Días</td>
                                <td>
                                    <select style="font-size:11px;">
                                        <option>Semana</option>
                                        <option>Quincena</option>
                                        <option selected>Mes</option>
                                    </select>
                                </td>
                                <td>
                                    <button class="btn-action" style="background:#e74c3c; color:white;">OFF</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="support" class="tab-content" style="display:none;">
                <div class="data-card">
                    <h3>Bandeja de Soporte Técnico</h3>
                    <div class="chat-box" id="inbox">
                        <div style="margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                            <small><b>ID: BOT-X892J</b> - 10:45 AM</small>
                            <p style="margin:5px 0;">Solicitud de actualización de sistema recibida.</p>
                        </div>
                    </div>
                    <input type="text" placeholder="Escribir mensaje al bot..." style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ddd;">
                    <button class="btn-action" style="background:var(--primary); color:white; width:100%; padding:10px;">Enviar Mensaje</button>
                </div>
            </div>

        </div>
    </div>

    <script>
        function login() {
            if(document.getElementById('user').value === "Edwinnes" && document.getElementById('pass').value === "Diosamor") {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('main-dashboard').style.display = 'block';
            }
        }
        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
            document.getElementById(tab).style.display = 'block';
        }
        function changePic(e) {
            document.getElementById('navLogo').src = URL.createObjectURL(e.target.files[0]);
        }
        function logout() { window.location.reload(); }
    </script>
</body>
</html>
