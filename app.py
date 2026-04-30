from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- BASE DE DATOS TEMPORAL ---
# Aquí se guardan los HWID, nombres y estados
devices = {}

# --- INTERFAZ HTML (ADMIN PANEL) ---
ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENTINEL CORE - NOSOTROS RD</title>
    <meta name="mobile-web-app-capable" content="yes">
    <style>
        body { background: #050505; color: #00ff41; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 10px; }
        .header { border-bottom: 2px solid #00ff41; padding-bottom: 10px; text-align: center; margin-bottom: 20px; }
        .card { background: #111; border: 1px solid #00ff41; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 0 10px rgba(0,255,65,0.1); }
        .btn { display: inline-block; background: #00ff41; color: #000; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 14px; }
        .btn-revocar { background: #ff3e3e; color: white; }
        .status { font-weight: bold; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .status-pending { background: #554400; color: #ffcc00; }
        .status-authorized { background: #004400; color: #00ff41; }
        .id-text { font-family: monospace; color: #aaa; display: block; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">NOSOTROS RD</h2>
        <small>CONTROL DE ACCESO SENTINEL</small>
    </div>

    {% for id, info in lista_dispositivos.items() %}
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span><strong>Dispositivo:</strong></span>
            <span class="status {{ 'status-authorized' if info.status == 'authorized' else 'status-pending' }}">
                {{ info.status.upper() }}
            </span>
        </div>
        <span class="id-text">HWID: {{ id }}</span>
        <hr style="border:0; border-top:1px solid #222; margin:10px 0;">
        <div style="text-align:right;">
            {% if info.status == 'pending' %}
                <a href="/approve/{{ id }}" class="btn">AUTORIZAR ACCESO</a>
            {% else %}
                <a href="/revoke/{{ id }}" class="btn btn-revocar">REVOCAR</a>
            {% endif %}
        </div>
    </div>
    {% else %}
    <div style="text-align:center; padding:50px; color:#555;">
        <p>No hay solicitudes pendientes.</p>
    </div>
    {% endfor %}

    <div style="text-align:center; margin-top:20px;">
        <button onclick="location.reload()" style="background:none; border:1px solid #333; color:#555; padding:5px 10px; border-radius:5px;">Actualizar Lista</button>
    </div>
</body>
</html>
'''

# --- RUTAS DE LÓGICA ---

@app.route('/')
def index():
    return jsonify({"server": "SENTINEL CORE", "status": "running"})

# Esta es la ruta que llama el Bot
@app.route('/validate', methods=['POST', 'GET'])
def validate():
    # Soporta tanto JSON (POST) como parámetros de URL (GET) para pruebas rápidas
    hwid = request.args.get('hwid') or (request.json.get('hardware_id') if request.is_json else None)
    
    if not hwid:
        return jsonify({"authorized": False, "error": "Missing HWID"}), 400

    # Si es nuevo, lo registra como pendiente
    if hwid not in devices:
        devices[hwid] = {"status": "pending"}
    
    return jsonify({
        "authorized": devices[hwid]['status'] == "authorized",
        "status": devices[hwid]['status']
    })

# Panel de administración
@app.route('/admin')
def admin():
    return render_template_string(ADMIN_HTML, lista_dispositivos=devices)

# Ruta para autorizar
@app.route('/approve/<hwid>')
def approve(hwid):
    if hwid in devices:
        devices[hwid]['status'] = 'authorized'
    return redirect(url_for('admin'))

# Ruta para revocar (por si te roban el código o el socio se porta mal)
@app.route('/revoke/<hwid>')
def revoke(hwid):
    if hwid in devices:
        devices[hwid]['status'] = 'pending'
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
