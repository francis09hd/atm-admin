import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- LLAVE MAESTRA ---
ACCESS_KEY = "Diosamor"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - MASTER HUB</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #000; --accent: #2ecc71; --bg: #fff; 
            --border: #ddd; --danger: #ff4444; --warning: #f39c12; --support: #9b59b6;
        }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; overflow-x: hidden; }

        /* BLOQUEO */
        #lock { background: var(--primary); height: 100vh; display: flex; justify-content: center; align-items: center; position: fixed; width: 100%; z-index: 9999; }
        .lock-box { background: #fff; padding: 40px; border-radius: 20px; text-align: center; width: 320px; border-top: 5px solid var(--accent); }

        /* DASHBOARD */
        .sidebar { width: 260px; background: var(--primary); height: 100vh; position: fixed; color: #fff; z-index: 1000; }
        .nav-profile { padding: 30px 15px; text-align: center; border-bottom: 1px solid #222; }
        .profile-img { width: 90px; height: 90px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; }
        
        .nav-link { padding: 15px 20px; color: #888; display: flex; align-items: center; cursor: pointer; text-decoration: none; border-bottom: 1px solid #111; font-size: 14px; }
        .nav-link:hover, .nav-link.active { background: #111; color: #fff; border-left: 5px solid var(--accent); }
        .nav-link i { margin-right: 12px; width: 20px; text-align: center; }

        .main { margin-left: 260px; padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 25px; }

        /* CARDS */
        .card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .table-res { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; padding: 12px; background: #f8f9fa; border-bottom: 2px solid #eee; }
        td { padding: 12px; border-bottom: 1px solid #eee; }

        /* SOPORTE Y CHAT */
        .support-grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; }
        .ticket-list { height: 400px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; }
        .ticket-item { padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; transition: 0.2s; }
        .ticket-item:hover { background: #f9f9f9; }
        .ticket-item.active { border-left: 4px solid var(--support); background: #f4f0f7; }
        
        .chat-window { height: 350px; background: #fdfdfd; border: 1px solid #eee; border-radius: 8px; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; }
        .bubble { max-width: 80%; padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; font-size: 13px; }
        .b-in { background: #eee; align-self: flex-start; }
        .b-out { background: var(--primary); color: #fff; align-self: flex-end; }

        .badge { padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; text-transform: uppercase; }
        .b-urgent { background: var(--danger); color: white; }
        .b-tech { background: var(--info); color: white; }

        @media (max-width: 800px) {
            .sidebar { width: 70px; } .sidebar span, .nav-profile h4, .nav-profile button { display: none; }
            .main { margin-left: 70px; padding: 15px; }
            .support-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div id="lock">
        <div class="lock-box">
            <h2 style="margin:0">NOSOTROS RD</h2>
            <p style="font-size:12px; color:gray">CENTRAL DE MANDO</p>
            <input type="password" id="pass" placeholder="LLAVE DIOSAMOR" style="width:100%; padding:15px; margin:20px 0; border:1px solid #ddd; border-radius:10px; text-align:center; font-size:1.2em;">
            <button onclick="unlock()" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">AUTORIZAR ACCESO</button>
        </div>
    </div>

    <div id="panel" style="display:none">
        <div class="sidebar">
            <div class="nav-profile">
                <img src="https://via.placeholder.com/150/111/fff?text=ADMIN" id="admImg" class="profile-img">
                <h4 style="margin:10px 0 0 0">Edwin Master</h4>
                <button onclick="document.getElementById('f').click()" style="background:none; border:none; color:var(--accent); font-size:10px; cursor:pointer;">CONFIGURAR PERFIL</button>
                <input type="file" id="f" hidden onchange="document.getElementById('admImg').src=URL.createObjectURL(event.target.files[0])">
            </div>
            <a onclick="show('reg')" class="nav-link active" id="l-reg"><i class="fas fa-id-card"></i> <span>Solicitudes Registro</span></a>
            <a onclick="show('support')" class="nav-link" id="l-support"><i class="fas fa-headset"></i> <span>Central Soporte</span></a>
            <a onclick="show('list')" class="nav-link" id="l-list"><i class="fas fa-users"></i> <span>Socios Activos</span></a>
            <a onclick="logout()" class="nav-link" style="color:var(--danger); margin-top:50px;"><i class="fas fa-power-off"></i> <span>Cerrar Sistema</span></a>
        </div>

        <div class="main">
            <div class="header">
                <h1 style="margin:0; font-weight:900; letter-spacing:-1px;">NOSOTROS RD</h1>
                <div style="text-align:right">
                    <span style="color:var(--accent); font-size:11px; font-weight:bold">● CONTROL OPERATIVO</span>
                </div>
            </div>

            <div id="reg" class="tab">
                <div class="card">
                    <h3>Peticiones de Acceso Bot</h3>
                    <div class="table-res">
                        <table>
                            <thead>
                                <tr>
                                    <th>Dispositivo</th>
                                    <th>Usuario Detectado</th>
                                    <th>IMEI / ID</th>
                                    <th>Estado</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody id="reqBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="support" class="tab" style="display:none">
                <div class="support-grid">
                    <div class="card">
                        <h3>Tickets Abiertos</h3>
                        <div class="ticket-list" id="ticketArea">
                            </div>
                    </div>
                    <div class="card">
                        <h3 id="chatTitle">Seleccione un Ticket</h3>
                        <div class="chat-window" id="chatArea">
                            <div style="margin:auto; color:#ccc; text-align:center;">
                                <i class="fas fa-comments fa-3x"></i><br>Bandeja de mensajes técnica
                            </div>
                        </div>
                        <div style="display:flex; gap:10px; margin-top:15px;">
                            <input type="text" id="reply" placeholder="Escribir respuesta oficial..." style="flex:1; padding:12px; border:1px solid #ddd; border-radius:8px;">
                            <button onclick="sendReply()" class="btn" style="background:var(--primary); color:white; width:100px;">ENVIAR</button>
                        </div>
                    </div>
                </div>
            </div>

            <div id="list" class="tab" style="display:none">
                <div class="card">
                    <h3>Base de Datos de Socios</h3>
                    <div class="table-res">
                        <table id="activeTable">
                            <thead>
                                <tr><th>Nombre</th><th>Teléfono</th><th>ID Bot</th><th>Plan</th><th>Acciones</th></tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let requests = JSON.parse(localStorage.getItem('nr_req')) || [];
        let actives = JSON.parse(localStorage.getItem('nr_act')) || [];
        let tickets = JSON.parse(localStorage.getItem('nr_tix')) || [
            {id: 1, user: "Socio Fundador", msg: "Error al validar el token del banco", type: "URGENTE", chat: []}
        ];
        let currentTicket = null;

        function unlock() {
            if(document.getElementById('pass').value === "Diosamor") {
                localStorage.setItem('auth', '1');
                document.getElementById('lock').style.display = 'none';
                document.getElementById('panel').style.display = 'block';
                renderAll();
            }
        }

        function renderAll() {
            // Render Peticiones
            const rb = document.getElementById('reqBody');
            rb.innerHTML = requests.map((r, i) => `
                <tr>
                    <td><strong>${r.modelo}</strong></td>
                    <td>${r.user}<br><small>${r.tel}</small></td>
                    <td><code>${r.imei}</code></td>
                    <td><span class="badge" style="background:orange; color:white;">Pendiente</span></td>
                    <td><button onclick="approve(${i})" class="btn" style="background:var(--accent); color:white;">APROBAR</button></td>
                </tr>
            `).join('');

            // Render Tickets Soporte
            const ta = document.getElementById('ticketArea');
            ta.innerHTML = tickets.map((t, i) => `
                <div class="ticket-item ${currentTicket === i ? 'active' : ''}" onclick="openTicket(${i})">
                    <span class="badge ${t.type === 'URGENTE' ? 'b-urgent' : 'b-tech'}">${t.type}</span>
                    <div style="font-weight:bold; margin-top:5px;">${t.user}</div>
                    <div style="font-size:12px; color:#666;">${t.msg.substring(0,30)}...</div>
                </div>
            `).join('');

            // Render Tabla Activos
            const ab = document.querySelector('#activeTable tbody');
            ab.innerHTML = actives.map((a, i) => `
                <tr>
                    <td>${a.user}</td><td>${a.tel}</td><td><code>${a.imei}</code></td>
                    <td><span class="badge b-tech">MES</span></td>
                    <td><button class="btn" style="background:#eee;">Detalles</button></td>
                </tr>
            `).join('');
        }

        function openTicket(i) {
            currentTicket = i;
            const t = tickets[i];
            document.getElementById('chatTitle').innerText = "Chat con: " + t.user;
            const ca = document.getElementById('chatArea');
            ca.innerHTML = `
                <div class="bubble b-in"><b>REPORTE INICIAL:</b><br>${t.msg}</div>
                ${t.chat.map(m => `<div class="bubble ${m.role==='admin'?'b-out':'b-in'}">${m.txt}</div>`).join('')}
            `;
            renderAll();
        }

        function sendReply() {
            const val = document.getElementById('reply').value;
            if(currentTicket === null || !val) return;
            tickets[currentTicket].chat.push({role: 'admin', txt: val});
            document.getElementById('reply').value = '';
            save();
            openTicket(currentTicket);
        }

        function approve(i) {
            actives.push(requests[i]);
            requests.splice(i, 1);
            save(); renderAll();
        }

        function save() {
            localStorage.setItem('nr_req', JSON.stringify(requests));
            localStorage.setItem('nr_act', JSON.stringify(actives));
            localStorage.setItem('nr_tix', JSON.stringify(tickets));
        }

        function show(id) {
            document.querySelectorAll('.tab').forEach(t => t.style.display='none');
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById(id).style.display='block';
            document.getElementById('l-'+id).classList.add('active');
        }

        function logout() { localStorage.removeItem('auth'); window.location.reload(); }

        window.onload = () => {
            if(localStorage.getItem('auth')==='1') {
                document.getElementById('lock').style.display='none';
                document.getElementById('panel').style.display='block';
                renderAll();
            }
        }
    </script>
</body>
</html>
