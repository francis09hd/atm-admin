import os
from flask import Flask, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE NÚCLEO ---
ACCESS_KEY = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - MASTER CONSOLE</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #000000; --accent: #2ecc71; --bg: #ffffff; 
            --border: #e0e0e0; --text: #1a1a1a; --danger: #ff3333; --warning: #f1c40f;
        }

        body { font-family: 'Inter', 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; }

        /* PANTALLA ACCESO DIOSAMOR */
        #lock-screen {
            display: flex; justify-content: center; align-items: center; height: 100vh;
            background: var(--primary); position: fixed; width: 100%; z-index: 9999;
        }
        .lock-card { background: white; padding: 40px; border-radius: 20px; width: 85%; max-width: 380px; text-align: center; }

        /* SIDEBAR MAESTRA */
        .sidebar { width: 280px; background: var(--primary); height: 100vh; position: fixed; color: white; z-index: 1000; overflow-y: auto; }
        .nav-profile { padding: 40px 20px; text-align: center; border-bottom: 1px solid #1a1a1a; background: #050505; }
        .profile-img { width: 110px; height: 110px; border-radius: 50%; border: 4px solid var(--accent); object-fit: cover; margin-bottom: 15px; }
        
        .nav-link { padding: 18px 25px; text-decoration: none; color: #777; display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #0a0a0a; font-size: 14px; transition: 0.3s; }
        .nav-link:hover, .nav-link.active { background: #111; color: white; border-left: 6px solid var(--accent); }
        .nav-link i { margin-right: 15px; width: 25px; font-size: 1.2em; text-align: center; }

        /* CUERPO CENTRAL */
        .main-content { margin-left: 280px; padding: 40px; min-height: 100vh; }
        .top-banner { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--primary); padding-bottom: 20px; margin-bottom: 35px; }

        /* CARDS Y TABLAS */
        .card { background: white; border: 1px solid var(--border); border-radius: 15px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.04); margin-bottom: 30px; }
        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #f8f9fa; padding: 15px; text-align: left; border-bottom: 2px solid var(--border); text-transform: uppercase; letter-spacing: 1px; color: #666; }
        td { padding: 15px; border-bottom: 1px solid var(--border); vertical-align: middle; }

        /* BANDEJAS TRIPLE */
        .grid-inbox { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }
        .monitor-box { height: 350px; border: 1px solid var(--border); border-radius: 10px; overflow-y: auto; background: #fafafa; padding: 15px; display: flex; flex-direction: column; }
        .msg { padding: 12px; margin-bottom: 10px; border-radius: 8px; font-size: 12px; line-height: 1.4; animation: fadeIn 0.3s; }
        .msg-in { background: #e8f5e9; border-left: 4px solid var(--accent); align-self: flex-start; }
        .msg-out { background: #eeeeee; border-left: 4px solid var(--primary); align-self: flex-end; width: 80%; }
        .msg-notif { background: #fff3e0; border-left: 4px solid var(--warning); text-align: center; font-weight: bold; }

        /* CONTROLES */
        .btn { border: none; border-radius: 8px; padding: 12px 20px; font-weight: bold; cursor: pointer; transition: 0.2s; font-size: 12px; }
        .btn-on { background: var(--accent); color: white; }
        .btn-off { background: var(--danger); color: white; }
        input[type="text"], select { padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 900px) {
            .sidebar { width: 80px; } .sidebar span, .nav-profile h4, .nav-profile button { display: none; }
            .main-content { margin-left: 80px; padding: 20px; }
            .profile-img { width: 50px; height: 50px; }
            .grid-inbox { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div id="lock-screen">
        <div class="lock-card">
            <h1 style="margin:0; font-weight:900;">NOSOTROS RD</h1>
            <p style="color:gray; margin-bottom:35px;">CONTROL DE SEGURIDAD</p>
            <input type="password" id="key" placeholder="ACCESO DIOSAMOR" style="width:100%; text-align:center; padding:15px; margin-bottom:20px; border:1px solid #ddd; border-radius:10px;">
            <button onclick="unlock()" style="width:100%; padding:15px; background:var(--accent); color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">VERIFICAR</button>
        </div>
    </div>

    <div id="master-panel" style="display:none;">
        <div class="sidebar">
            <div class="nav-profile">
                <img src="https://via.placeholder.com/150/111/fff?text=ADMIN" id="masterPic" class="profile-img">
                <h4 style="margin:10px 0 0 0; letter-spacing:1px;">EDWIN MASTER</h4>
                <input type="file" id="up" hidden onchange="changeMasterPic(event)">
                <button onclick="document.getElementById('up').click()" style="background:none; border:none; color:var(--accent); cursor:pointer; font-size:10px; margin-top:8px;">[ EDITAR FOTO ]</button>
            </div>
            <div class="nav-menu">
                <a onclick="tab('m-users')" class="nav-link active" id="l-m-users"><i class="fas fa-users-cog"></i> <span>Gestión de Usuarios</span></a>
                <a onclick="tab('m-comms')" class="nav-link" id="l-m-comms"><i class="fas fa-satellite-dish"></i> <span>Terminal de Datos</span></a>
                <a onclick="tab('m-push')" class="nav-link" id="l-m-push"><i class="fas fa-bullhorn"></i> <span>Notificaciones Globales</span></a>
                <a onclick="lockOut()" class="nav-link" style="color:var(--danger); margin-top:40px;"><i class="fas fa-power-off"></i> <span>Cerrar Sesión</span></a>
            </div>
        </div>

        <div class="main-content">
            <div class="top-banner">
                <h1 style="margin:0; font-weight:900; font-size:2em;">NOSOTROS RD</h1>
                <div style="text-align:right">
                    <span style="font-size:11px; color:var(--accent); font-weight:bold;">● SISTEMA CENTRALIZADO v3.0</span><br>
                    <small id="clock" style="color:#999;"></small>
                </div>
            </div>

            <div id="m-users" class="tab-view">
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h3 style="margin:0;">Registro de Usuarios</h3>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-on" onclick="bulkAction(true)">ACTIVAR TODO</button>
                            <button class="btn btn-off" onclick="bulkAction(false)">BLOQUEO TOTAL</button>
                        </div>
                    </div>
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th><input type="checkbox" id="masterCheck"></th>
                                    <th>Nombre y Contacto</th>
                                    <th>ID Dispositivo</th>
                                    <th>Vencimiento</th>
                                    <th>Plan</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody id="userBody"></tbody>
                        </table>
                        <button class="btn" style="background:#eee; width:100%; margin-top:15px; border:1px dashed #ccc;" onclick="addUser()">+ AGREGAR USUARIO NUEVO</button>
                    </div>
                </div>
            </div>

            <div id="m-comms" class="tab-view" style="display:none;">
                <div class="grid-inbox">
                    <div class="card">
                        <h3><i class="fas fa-level-down-alt" style="color:var(--accent);"></i> Entrada (Reportes)</h3>
                        <div class="monitor-box" id="inBox"></div>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-paper-plane"></i> Salida (Comandos)</h3>
                        <div class="monitor-box" id="outBox"></div>
                        <div style="display:flex; gap:10px; margin-top:15px;">
                            <input type="text" id="cmdInput" placeholder="Escribir comando directo..." style="flex:1;">
                            <button class="btn btn-on" onclick="sendCmd()">EJECUTAR</button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="m-push" class="tab-view" style="display:none;">
                <div class="card" style="max-width:600px; margin:auto;">
                    <h3>Historial de Notificaciones Push</h3>
                    <div class="monitor-box" id="pushBox" style="height:300px;"></div>
                    <hr style="border:0; border-top:1px solid #eee; margin:20px 0;">
                    <button class="btn btn-on" style="width:100%; padding:20px;" onclick="emitPush()">ENVIAR NOTIFICACIÓN GLOBAL A LA APP</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- MEMORIA PERSISTENTE (LOCALSTORAGE) ---
        let users = JSON.parse(localStorage.getItem('nr_users')) || [];
        let inData = JSON.parse(localStorage.getItem('nr_in')) || [{txt: "Conexión establecida con Nosotros RD", time: "SISTEMA"}];
        let outData = JSON.parse(localStorage.getItem('nr_out')) || [];
        let pushData = JSON.parse(localStorage.getItem('nr_push')) || [];

        function sync() {
            localStorage.setItem('nr_users', JSON.stringify(users));
            localStorage.setItem('nr_in', JSON.stringify(inData));
            localStorage.setItem('nr_out', JSON.stringify(outData));
            localStorage.setItem('nr_push', JSON.stringify(pushData));
            render();
        }

        function unlock() {
            if(document.getElementById('key').value === "Diosamor") {
                localStorage.setItem('nr_auth', 'true');
                document.getElementById('lock-screen').style.display = 'none';
                document.getElementById('master-panel').style.display = 'block';
                render();
            }
        }

        function render() {
            // Render Usuarios
            const ub = document.getElementById('userBody');
            ub.innerHTML = users.length ? users.map((u, i) => `
                <tr>
                    <td><input type="checkbox" class="row-check" data-index="${i}"></td>
                    <td><strong>${u.name}</strong><br><small>${u.tel} | ${u.mail}</small></td>
                    <td><code>${u.id}</code></td>
                    <td style="color:${u.days < 3 ? 'red' : 'green'}; font-weight:bold;">${u.days} DÍAS</td>
                    <td>
                        <select onchange="changePlan(${i}, this.value)">
                            <option value="7" ${u.plan=='7'?'selected':''}>Semana</option>
                            <option value="15" ${u.plan=='15'?'selected':''}>Quincena</option>
                            <option value="30" ${u.plan=='30'?'selected':''}>Mes</option>
                        </select>
                    </td>
                    <td><button class="btn ${u.active ? 'btn-off' : 'btn-on'}" onclick="toggleUser(${i})">${u.active ? 'BLOQUEAR' : 'ACTIVAR'}</button></td>
                </tr>
            `).join('') : '<tr><td colspan="6" style="text-align:center; padding:40px;">No hay usuarios registrados.</td></tr>';

            // Render Bandejas
            document.getElementById('inBox').innerHTML = inData.map(m => `<div class="msg msg-in"><b>${m.time}</b><br>${m.txt}</div>`).join('');
            document.getElementById('outBox').innerHTML = outData.map(m => `<div class="msg msg-out"><b>TÚ:</b><br>${m.txt}</div>`).join('');
            document.getElementById('pushBox').innerHTML = pushData.map(m => `<div class="msg msg-notif">${m.txt} <br><small>${m.time}</small></div>`).join('');
        }

        function addUser() {
            const name = prompt("Nombre del Usuario:");
            if(!name) return;
            const tel = prompt("Teléfono:");
            const mail = prompt("Correo:");
            const id = "RD-BOT-" + Math.floor(Math.random()*9999);
            users.push({name, tel, mail, id, days: 30, plan: '30', active: true});
            sync();
        }

        function sendCmd() {
            const val = document.getElementById('cmdInput').value;
            if(!val) return;
            outData.unshift({txt: val});
            document.getElementById('cmdInput').value = '';
            sync();
        }

        function emitPush() {
            const val = prompt("Escriba el mensaje para la notificación global:");
            if(val) {
                pushData.unshift({txt: val, time: new Date().toLocaleTimeString()});
                sync();
            }
        }

        function toggleUser(i) { users[i].active = !users[i].active; sync(); }
        
        function changePlan(i, val) { users[i].plan = val; users[i].days = parseInt(val); sync(); }

        function tab(id) {
            document.querySelectorAll('.tab-view').forEach(v => v.style.display = 'none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(id).style.display = 'block';
            document.getElementById('l-' + id).classList.add('active');
        }

        function changeMasterPic(e) {
            document.getElementById('masterPic').src = URL.createObjectURL(e.target.files[0]);
        }

        function lockOut() { localStorage.removeItem('nr_auth'); window.location.reload(); }

        window.onload = () => {
            if(localStorage.getItem('nr_auth') === 'true') {
                document.getElementById('lock-screen').style.display = 'none';
                document.getElementById('master-panel').style.display = 'block';
                render();
            }
            setInterval(() => { document.getElementById('clock').innerText = new Date().toLocaleString(); }, 1000);
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
