import os
from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de Marca y Seguridad
BRAND = "NOSOTROS RD"
ACCESS_KEY = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - CONTROL TOTAL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #000000; --accent: #2ecc71; --bg: #ffffff; 
            --border: #eeeeee; --text: #1a1a1a; --danger: #ff3333; --gray: #888888;
        }

        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; }

        /* LOGIN */
        #login-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: var(--primary); position: fixed; width: 100%; z-index: 9999;
        }
        .login-card { background: white; padding: 40px; border-radius: 15px; width: 85%; max-width: 360px; text-align: center; }

        /* ESTRUCTURA SIDEBAR */
        .sidebar { width: 280px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 1000; transition: 0.3s; }
        .nav-profile { padding: 40px 20px; text-align: center; border-bottom: 1px solid #222; }
        .profile-img { width: 100px; height: 100px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; background: #222; }
        
        .nav-link { padding: 18px 25px; text-decoration: none; color: var(--gray); display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #111; font-size: 14px; }
        .nav-link:hover, .nav-link.active { background: #111; color: white; border-left: 6px solid var(--accent); }
        .nav-link i { margin-right: 15px; width: 20px; text-align: center; }

        /* CONTENIDO */
        .main-content { margin-left: 280px; padding: 40px; }
        .brand-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 30px; }

        /* TABLAS Y CARTAS */
        .card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 25px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #f9f9f9; padding: 15px; text-align: left; border-bottom: 2px solid var(--border); }
        td { padding: 15px; border-bottom: 1px solid var(--border); }

        /* BANDEJAS DE MENSAJERÍA */
        .inbox-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .msg-list { height: 300px; border: 1px solid var(--border); border-radius: 8px; overflow-y: auto; background: #fdfdfd; padding: 10px; }
        .msg-item { padding: 10px; border-bottom: 1px solid #eee; font-size: 12px; margin-bottom: 5px; border-radius: 4px; }
        .msg-in { background: #e8f5e9; border-left: 4px solid var(--accent); }
        .msg-out { background: #f1f1f1; border-left: 4px solid var(--primary); }
        .msg-notif { background: #fff3e0; border-left: 4px solid #ff9800; }

        .btn { border: none; border-radius: 6px; padding: 10px 15px; font-weight: bold; cursor: pointer; font-size: 12px; }
        .btn-on { background: var(--accent); color: white; }
        .btn-off { background: var(--danger); color: white; }

        @media (max-width: 900px) {
            .sidebar { width: 75px; } .sidebar span, .nav-profile h4, .nav-profile button { display: none; }
            .main-content { margin-left: 75px; padding: 20px; }
            .profile-img { width: 45px; height: 45px; }
            .inbox-container { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div id="login-screen">
        <div class="login-card">
            <h1 style="margin:0; font-weight:900;">NOSOTROS RD</h1>
            <p style="color:var(--gray); margin-bottom:30px;">SISTEMA DE CONTROL</p>
            <input type="password" id="pass" placeholder="Clave de Acceso" style="width:100%; padding:15px; margin-bottom:20px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box; text-align:center;">
            <button onclick="checkAccess()" style="width:100%; padding:15px; background:var(--accent); color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">INGRESAR</button>
        </div>
    </div>

    <div id="app" style="display:none;">
        <div class="sidebar">
            <div class="nav-profile">
                <img src="https://via.placeholder.com/150/111/fff?text=ADMIN" id="adminPic" class="profile-img">
                <h4 style="margin:10px 0 0 0;">Edwinnes</h4>
                <input type="file" id="up" hidden onchange="changePic(event)">
                <button onclick="document.getElementById('up').click()" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:10px;">[ CAMBIAR FOTO ]</button>
            </div>
            <div class="nav-menu">
                <a onclick="setTab('m-users')" class="nav-link active" id="l-m-users"><i class="fas fa-users"></i> <span>Gestión Usuarios</span></a>
                <a onclick="setTab('m-messages')" class="nav-link" id="l-m-messages"><i class="fas fa-exchange-alt"></i> <span>Entrada / Salida</span></a>
                <a onclick="setTab('m-notif')" class="nav-link" id="l-m-notif"><i class="fas fa-bell"></i> <span>Notificaciones</span></a>
                <a onclick="exit()" class="nav-link" style="color:var(--danger); margin-top:30px;"><i class="fas fa-power-off"></i> <span>Cerrar</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="brand-header">
                <h1 style="margin:0; font-weight:900;">NOSOTROS RD</h1>
                <span style="font-size:12px; color:var(--accent); font-weight:bold;">● MODO PERSISTENTE ACTIVO</span>
            </div>

            <div id="m-users" class="tab">
                <div class="card">
                    <div style="margin-bottom:15px; display:flex; gap:10px;">
                        <button class="btn btn-on" onclick="bulk(true)">Activar Selección</button>
                        <button class="btn btn-off" onclick="bulk(false)">Desactivar Selección</button>
                    </div>
                    <div style="overflow-x:auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th><input type="checkbox" id="selectAll"></th>
                                    <th>Usuario / Contacto</th>
                                    <th>ID Bot</th>
                                    <th>Días Restantes</th>
                                    <th>Habilitación</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody id="userTable">
                                </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="m-messages" class="tab" style="display:none;">
                <div class="inbox-container">
                    <div class="card">
                        <h3><i class="fas fa-arrow-down" style="color:var(--accent);"></i> Entrada (Soporte)</h3>
                        <div class="msg-list" id="inbox"></div>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-arrow-up"></i> Salida (Comandos)</h3>
                        <div class="msg-list" id="outbox"></div>
                        <hr>
                        <input type="text" id="msgInput" placeholder="Enviar comando al usuario..." style="width:100%; padding:10px; border:1px solid #ddd; border-radius:5px; box-sizing:border-box;">
                        <button class="btn btn-on" style="width:100%; margin-top:10px;" onclick="sendMsg()">ENVIAR AHORA</button>
                    </div>
                </div>
            </div>

            <div id="m-notif" class="tab" style="display:none;">
                <div class="card">
                    <h3>Historial de Notificaciones Push</h3>
                    <div class="msg-list" id="notifBox" style="height:400px;"></div>
                    <hr>
                    <button class="btn btn-on" onclick="pushAlert()">EMITIR NOTIFICACIÓN GLOBAL</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- LÓGICA DE PERSISTENCIA (LOCALSTORAGE) ---
        let users = JSON.parse(localStorage.getItem('users')) || [
            {id: 'BOT-01', name: 'Usuario Indefinido', contact: '809-xxx-xxxx', days: 15, active: true}
        ];
        let inbox = JSON.parse(localStorage.getItem('inbox')) || [{txt: "Sistema Nosotros RD iniciado", time: "12:00 PM"}];
        let outbox = JSON.parse(localStorage.getItem('outbox')) || [];
        let notifs = JSON.parse(localStorage.getItem('notifs')) || [];

        function save() {
            localStorage.setItem('users', JSON.stringify(users));
            localStorage.setItem('inbox', JSON.stringify(inbox));
            localStorage.setItem('outbox', JSON.stringify(outbox));
            localStorage.setItem('notifs', JSON.stringify(notifs));
        }

        function checkAccess() {
            if(document.getElementById('pass').value === "Diosamor") {
                localStorage.setItem('logged', 'true');
                renderAll();
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app').style.display = 'block';
            }
        }

        function renderAll() {
            // Render Usuarios
            const ut = document.getElementById('userTable');
            ut.innerHTML = users.map((u, i) => `
                <tr>
                    <td><input type="checkbox" class="u-check" data-index="${i}"></td>
                    <td><strong>${u.name}</strong><br><small>${u.contact}</small></td>
                    <td><code>${u.id}</code></td>
                    <td style="color:${u.days < 5 ? 'red' : 'green'}; font-weight:bold;">${u.days} Días</td>
                    <td>
                        <select onchange="updateDays(${i}, this.value)">
                            <option value="7">Semana</option>
                            <option value="15">Quincena</option>
                            <option value="30" selected>Mes</option>
                        </select>
                    </td>
                    <td><button class="btn ${u.active ? 'btn-off' : 'btn-on'}" onclick="toggleUser(${i})">${u.active ? 'Bloquear' : 'Activar'}</button></td>
                </tr>
            `).join('');

            // Render Mensajes
            document.getElementById('inbox').innerHTML = inbox.map(m => `<div class="msg-item msg-in"><b>Soporte:</b> ${m.txt} <br><small>${m.time}</small></div>`).join('');
            document.getElementById('outbox').innerHTML = outbox.map(m => `<div class="msg-item msg-out"><b>Tú:</b> ${m.txt} <br><small>${m.time}</small></div>`).join('');
            document.getElementById('notifBox').innerHTML = notifs.map(m => `<div class="msg-item msg-notif"><b>PUSH:</b> ${m.txt} <br><small>${m.time}</small></div>`).join('');
        }

        function sendMsg() {
            const val = document.getElementById('msgInput').value;
            if(!val) return;
            outbox.unshift({txt: val, time: new Date().toLocaleTimeString()});
            document.getElementById('msgInput').value = '';
            save(); renderAll();
        }

        function pushAlert() {
            const msg = prompt("Mensaje de la Notificación Push:");
            if(msg) {
                notifs.unshift({txt: msg, time: new Date().toLocaleTimeString()});
                save(); renderAll();
            }
        }

        function toggleUser(i) {
            users[i].active = !users[i].active;
            save(); renderAll();
        }

        function setTab(id) {
            document.querySelectorAll('.tab').forEach(t => t.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(id).style.display = 'block';
            document.getElementById('l-' + id).classList.add('active');
        }

        function exit() { localStorage.removeItem('logged'); window.location.reload(); }

        window.onload = () => {
            if(localStorage.getItem('logged') === 'true') {
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app').style.display = 'block';
                renderAll();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def main():
    return render_template_string(HTML_INTERFACE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
