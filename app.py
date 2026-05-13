import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from datetime import datetime

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
    <title>NOSOTROS RD - NÚCLEO DE REGISTRO</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #000; --accent: #2ecc71; --bg: #fff; 
            --border: #ddd; --danger: #ff4444; --info: #3498db;
        }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; overflow-x: hidden; }

        /* LOGIN */
        #lock { background: var(--primary); height: 100vh; display: flex; justify-content: center; align-items: center; position: fixed; width: 100%; z-index: 9999; }
        .lock-box { background: #fff; padding: 40px; border-radius: 20px; text-align: center; width: 320px; }

        /* DASHBOARD */
        .sidebar { width: 260px; background: var(--primary); height: 100vh; position: fixed; color: #fff; z-index: 1000; }
        .nav-profile { padding: 30px 15px; text-align: center; border-bottom: 1px solid #222; }
        .profile-img { width: 90px; height: 90px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; }
        
        .nav-link { padding: 15px 20px; color: #888; display: flex; align-items: center; cursor: pointer; text-decoration: none; border-bottom: 1px solid #111; font-size: 14px; }
        .nav-link:hover, .nav-link.active { background: #111; color: #fff; border-left: 5px solid var(--accent); }
        .nav-link i { margin-right: 12px; width: 20px; text-align: center; }

        .main { margin-left: 260px; padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 25px; }

        /* LISTAS DE REGISTRO */
        .card { background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        
        .table-res { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; padding: 12px; background: #f8f9fa; border-bottom: 2px solid #eee; color: #666; }
        td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: middle; }

        /* ETIQUETAS DETALLADAS */
        .detail-list { list-style: none; padding: 0; margin: 5px 0; font-size: 11px; color: #555; }
        .detail-list li { margin-bottom: 3px; display: flex; justify-content: space-between; }
        .badge { background: #eee; padding: 2px 6px; border-radius: 4px; font-weight: bold; }

        .btn { border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 11px; }
        .btn-ok { background: var(--accent); color: #fff; }
        .btn-no { background: var(--danger); color: #fff; }

        @media (max-width: 800px) {
            .sidebar { width: 70px; } .sidebar span, .nav-profile h4, .nav-profile button { display: none; }
            .main { margin-left: 70px; padding: 15px; }
        }
    </style>
</head>
<body>

    <div id="lock">
        <div class="lock-box">
            <h2 style="margin:0">NOSOTROS RD</h2>
            <p style="font-size:12px; color:gray">ACCESO SENTINEL</p>
            <input type="password" id="pass" placeholder="LLAVE DIOSAMOR" style="width:100%; padding:12px; margin:20px 0; border:1px solid #ddd; border-radius:8px; text-align:center;">
            <button onclick="unlock()" style="width:100%; padding:12px; background:#000; color:#fff; border:none; border-radius:8px; cursor:pointer;">ENTRAR</button>
        </div>
    </div>

    <div id="panel" style="display:none">
        <div class="sidebar">
            <div class="nav-profile">
                <img src="https://via.placeholder.com/150/111/fff?text=EDWIN" id="admImg" class="profile-img">
                <h4 style="margin:10px 0 0 0">Edwin Master</h4>
                <button onclick="document.getElementById('f').click()" style="background:none; border:none; color:var(--accent); font-size:10px; cursor:pointer;">CAMBIAR LOGO</button>
                <input type="file" id="f" hidden onchange="document.getElementById('admImg').src=URL.createObjectURL(event.target.files[0])">
            </div>
            <a onclick="show('reg')" class="nav-link active" id="l-reg"><i class="fas fa-mobile-alt"></i> <span>Nuevas Solicitudes</span></a>
            <a onclick="show('list')" class="nav-link" id="l-list"><i class="fas fa-users"></i> <span>Usuarios Activos</span></a>
            <a onclick="logout()" class="nav-link" style="color:var(--danger); margin-top:50px;"><i class="fas fa-power-off"></i> <span>Salir</span></a>
        </div>

        <div class="main">
            <div class="header">
                <h1 style="margin:0; font-weight:900">NOSOTROS RD</h1>
                <div style="text-align:right">
                    <span id="sync-status" style="color:var(--accent); font-size:11px; font-weight:bold">● ESCUCHANDO PETICIONES</span>
                </div>
            </div>

            <div id="reg" class="tab">
                <div class="card">
                    <h3>Solicitudes de Registro del Bot</h3>
                    <p style="font-size:12px; color:gray;">Aquí aparecerá automáticamente cualquier teléfono que intente conectarse.</p>
                    <div class="table-res">
                        <table>
                            <thead>
                                <tr>
                                    <th>Fecha/Hora</th>
                                    <th>Información del Usuario</th>
                                    <th>Detalles Técnicos (Bot)</th>
                                    <th>Estado</th>
                                    <th>Acción</th>
                                </tr>
                            </thead>
                            <tbody id="requestTable">
                                </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="list" class="tab" style="display:none">
                <div class="card">
                    <h3>Base de Datos: Usuarios Autorizados</h3>
                    <div id="activeUsers"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Memoria para no perder datos al reiniciar
        let requests = JSON.parse(localStorage.getItem('nr_req')) || [];
        let actives = JSON.parse(localStorage.getItem('nr_act')) || [];

        function unlock() {
            if(document.getElementById('pass').value === "Diosamor") {
                localStorage.setItem('auth', '1');
                document.getElementById('lock').style.display = 'none';
                document.getElementById('panel').style.display = 'block';
                render();
            }
        }

        // Esta función simula la llegada de datos del bot (Lo que pides: Lista completa)
        function receiveNewDevice(data) {
            requests.unshift({
                time: new Date().toLocaleString(),
                user: data.nombre || "Desconocido",
                tel: data.telefono || "Sin número",
                mail: data.correo || "N/A",
                imei: data.imei || "Desconocido",
                modelo: data.modelo || "Genérico",
                ip: data.ip || "0.0.0.0",
                os: data.version_os || "Android",
                storage: data.espacio || "2GB"
            });
            save();
            render();
        }

        function render() {
            const rt = document.getElementById('requestTable');
            rt.innerHTML = requests.map((r, i) => `
                <tr>
                    <td><small>${r.time}</small></td>
                    <td>
                        <strong>${r.user}</strong><br>
                        <i class="fas fa-phone"></i> ${r.tel}<br>
                        <i class="fas fa-envelope"></i> ${r.mail}
                    </td>
                    <td>
                        <ul class="detail-list">
                            <li><span>Modelo:</span> <span class="badge">${r.modelo}</span></li>
                            <li><span>ID/IMEI:</span> <span class="badge">${r.imei}</span></li>
                            <li><span>IP:</span> <span class="badge">${r.ip}</span></li>
                            <li><span>Storage:</span> <span class="badge">${r.storage}</span></li>
                        </ul>
                    </td>
                    <td><span class="status-dot" style="background:orange"></span> Pendiente</td>
                    <td>
                        <button class="btn btn-ok" onclick="approve(${i})">AUTORIZAR</button>
                        <button class="btn btn-no" onclick="remove(${i})">RECHAZAR</button>
                    </td>
                </tr>
            `).join('');
            if(requests.length === 0) rt.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:30px; color:#999;">No hay peticiones nuevas en este momento.</td></tr>';
        }

        function approve(i) {
            actives.push(requests[i]);
            requests.splice(i, 1);
            save(); render();
            alert("Usuario Autorizado en Nosotros RD");
        }

        function remove(i) {
            if(confirm("¿Bloquear esta solicitud?")) {
                requests.splice(i, 1);
                save(); render();
            }
        }

        function save() {
            localStorage.setItem('nr_req', JSON.stringify(requests));
            localStorage.setItem('nr_act', JSON.stringify(actives));
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
                render();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

# ESTA ES LA RUTA QUE USARÁ TU APP/BOT PARA MANDAR LA INFO
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    # Aquí es donde el servidor recibe la lista: Nombre, Tel, IMEI, Modelo, etc.
    return jsonify({"status": "received", "message": "Datos enviados al Panel Master"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
