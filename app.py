import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- PANEL MAESTRO NOSOTROS RD ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NOSOTROS RD - CONTROL CENTRAL</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --p: #000; --a: #2ecc71; --bg: #fff; --b: #ddd; --d: #ff4444; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; }
        
        #lock { background: var(--p); height: 100vh; display: flex; justify-content: center; align-items: center; position: fixed; width: 100%; z-index: 9999; }
        .l-box { background: #fff; padding: 30px; border-radius: 15px; text-align: center; width: 280px; }

        .side { width: 250px; background: var(--p); height: 100vh; position: fixed; color: #fff; }
        .main { margin-left: 250px; padding: 25px; }
        
        .nav-l { padding: 15px; color: #888; display: flex; align-items: center; cursor: pointer; border-bottom: 1px solid #111; font-size: 14px; }
        .nav-l.act { color: #fff; border-left: 4px solid var(--a); background: #111; }

        .card { background: #fff; border: 1px solid var(--b); border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th { text-align: left; padding: 10px; background: #f8f9fa; border-bottom: 1px solid #eee; }
        td { padding: 10px; border-bottom: 1px solid #eee; }

        .chat-h { height: 250px; background: #f9f9f9; border: 1px solid #eee; border-radius: 5px; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; }
        .bub { padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; font-size: 12px; max-width: 80%; }
        .b-in { background: #e1f5fe; align-self: flex-start; }
        .b-out { background: var(--p); color: #fff; align-self: flex-end; }

        @media (max-width: 800px) { .side { width: 60px; } .side span { display: none; } .main { margin-left: 60px; } }
    </style>
</head>
<body>
    <div id="lock">
        <div class="l-box">
            <h2 style="margin:0">NOSOTROS RD</h2>
            <input type="password" id="pk" placeholder="Diosamor" style="width:100%; padding:10px; margin:15px 0; border:1px solid #ddd; border-radius:5px; text-align:center;">
            <button onclick="login()" style="width:100%; padding:10px; background:#000; color:#fff; border:none; border-radius:5px; cursor:pointer;">ACCEDER</button>
        </div>
    </div>

    <div id="app" style="display:none">
        <div class="side">
            <div style="padding:20px; text-align:center;"><img src="https://via.placeholder.com/80" id="p-img" style="border-radius:50%; border:2px solid var(--a); width:80px;"></div>
            <div onclick="tab('reg')" class="nav-l act" id="t-reg"><i class="fas fa-id-card"></i> <span>&nbsp; Registros</span></div>
            <div onclick="tab('sop')" class="nav-l" id="t-sop"><i class="fas fa-headset"></i> <span>&nbsp; Soporte</span></div>
            <div onclick="tab('usr')" class="nav-l" id="t-usr"><i class="fas fa-users"></i> <span>&nbsp; Socios</span></div>
            <div onclick="exit()" class="nav-l" style="color:var(--d)"><i class="fas fa-power-off"></i> <span>&nbsp; Salir</span></div>
        </div>

        <div class="main">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #000; margin-bottom:20px;">
                <h2 style="margin:0">NOSOTROS RD</h2>
                <small style="color:var(--a)">● MASTER</small>
            </div>

            <div id="reg" class="view">
                <div class="card">
                    <h3>Solicitudes del Bot</h3>
                    <table>
                        <thead><tr><th>Usuario</th><th>Detalles Técnicos</th><th>Acción</th></tr></thead>
                        <tbody id="r-body"></tbody>
                    </table>
                </div>
            </div>

            <div id="sop" class="view" style="display:none">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <div class="card">
                        <h3>Tickets</h3>
                        <div id="t-list"></div>
                    </div>
                    <div class="card">
                        <h3 id="c-title">Chat</h3>
                        <div class="chat-h" id="c-area"></div>
                        <input type="text" id="ans" placeholder="Responder..." style="width:100%; padding:10px; margin-top:10px; box-sizing:border-box;">
                        <button onclick="send()" style="width:100%; margin-top:5px; padding:8px; background:var(--p); color:#fff; border:none; border-radius:5px;">ENVIAR</button>
                    </div>
                </div>
            </div>

            <div id="usr" class="view" style="display:none">
                <div class="card"><h3>Lista de Socios</h3><table id="u-table"><thead><tr><th>Nombre</th><th>ID</th><th>Estado</th></tr></thead><tbody></tbody></table></div>
            </div>
        </div>
    </div>

    <script>
        let reqs = JSON.parse(localStorage.getItem('n_req')) || [];
        let usrs = JSON.parse(localStorage.getItem('n_usr')) || [];
        let tix = JSON.parse(localStorage.getItem('n_tix')) || [{u:"Socio 1", m:"Error banco", c:[]}];
        let curr = null;

        function login() {
            if(document.getElementById('pk').value === "Diosamor") {
                localStorage.setItem('n_auth', '1');
                document.getElementById('lock').style.display = 'none';
                document.getElementById('app').style.display = 'block';
                render();
            }
        }

        function render() {
            document.getElementById('r-body').innerHTML = reqs.map((r,i) => `
                <tr>
                    <td><b>${r.name}</b><br>${r.tel}</td>
                    <td>Mod: ${r.mod}<br>IMEI: ${r.imei}</td>
                    <td><button onclick="ok(${i})" style="background:var(--a); color:#fff; border:none; padding:5px; border-radius:3px; cursor:pointer;">OK</button></td>
                </tr>
            `).join('');

            document.getElementById('t-list').innerHTML = tix.map((t,i) => `
                <div onclick="openT(${i})" style="padding:10px; border-bottom:1px solid #eee; cursor:pointer; ${curr==i?'background:#f0f0f0':''}">
                    <b>${t.u}</b><br><small>${t.m}</small>
                </div>
            `).join('');
        }

        function openT(i) {
            curr = i; render();
            document.getElementById('c-area').innerHTML = `<div class="bub b-in"><b>REPORTE:</b> ${tix[i].m}</div>` + 
                tix[i].c.map(m => `<div class="bub ${m.r=='a'?'b-out':'b-in'}">${m.t}</div>`).join('');
        }

        function send() {
            let v = document.getElementById('ans').value;
            if(curr==null || !v) return;
            tix[curr].c.push({r:'a', t:v});
            document.getElementById('ans').value = '';
            localStorage.setItem('n_tix', JSON.stringify(tix));
            openT(curr);
        }

        function ok(i) {
            usrs.push(reqs[i]);
            reqs.splice(i,1);
            localStorage.setItem('n_req', JSON.stringify(reqs));
            localStorage.setItem('n_usr', JSON.stringify(usrs));
            render();
        }

        function tab(id) {
            document.querySelectorAll('.view').forEach(v => v.style.display='none');
            document.querySelectorAll('.nav-l').forEach(l => l.classList.remove('act'));
            document.getElementById(id).style.display='block';
            document.getElementById('t-'+id).classList.add('act');
        }

        function exit() { localStorage.removeItem('n_auth'); window.location.reload(); }

        window.onload = () => { if(localStorage.getItem('n_auth')=='1') login(); }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
