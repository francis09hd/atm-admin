from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Base de datos en memoria (RAM)
db = {}

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "SENTINEL ACTIVE"})

@app.route('/validate', methods=['POST', 'GET'])
@app.route('/validar/<hwid>', methods=['GET', 'POST'])
def validate(hwid=None):
    # Detecta el ID si viene por URL o por JSON (POST)
    device_id = hwid or (request.json.get('hardware_id') if (request.is_json and request.json) else None)
    
    if not device_id:
        return jsonify({"error": "No HWID"}), 400

    if device_id not in db:
        db[device_id] = {"status": "pending", "name": "Dispositivo Nuevo"}
    
    return jsonify({
        "authorized": db[device_id]['status'] == 'authorized',
        "status": db[device_id]['status'],
        "online": True
    })

@app.route('/admin')
def admin_panel():
    # --- AQUÍ ESTÁ EL DISEÑO DE LA INTERFAZ ---
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SENTINEL ADMIN</title>
        <style>
            body { background-color: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
            h1 { color: #00ff41; text-shadow: 0 0 10px #00ff41; font-size: 1.5rem; text-align: center; }
            .container { max-width: 600px; margin: auto; border: 1px solid #00ff41; padding: 15px; box-shadow: 0 0 15px rgba(0, 255, 65, 0.2); }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #00ff41; padding: 10px; text-align: center; font-size: 0.8rem; }
            th { background: #003300; }
            .btn { display: inline-block; padding: 5px 10px; background: #00ff41; color: #000; text-decoration: none; font-weight: bold; border-radius: 3px; }
            .status-pending { color: #ff3e3e; }
            .status-ok { color: #00ff41; font-weight: bold; }
            .footer { margin-top: 20px; font-size: 0.7rem; text-align: center; opacity: 0.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SENTINEL CORE v1.0</h1>
            <p style="text-align:center; font-size: 0.8rem;">[ SISTEMA ONLINE - BIENVENIDO EDWIN ]</p>
            
            <table>
                <thead>
                    <tr>
                        <th>ID DISPOSITIVO</th>
                        <th>ESTADO</th>
                        <th>ACCIÓN</th>
                    </tr>
                </thead>
                <tbody>
                    {% for id, info in devices.items() %}
                    <tr>
                        <td>{{ id }}</td>
                        <td class="{{ 'status-ok' if info.status == 'authorized' else 'status-pending' }}">
                            {{ info.status.upper() }}
                        </td>
                        <td>
                            {% if info.status != 'authorized' %}
                                <a href="/approve/{{ id }}" class="btn">AUTORIZAR</a>
                            {% else %}
                                [ ACCESO OK ]
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            {% if not devices %}
            <p style="text-align:center; padding: 20px; color: #888;">Esperando conexión del bot...</p>
            {% endif %}

            <div class="footer">PROPIEDAD DE NOSOTROS RD - DOMINICANA</div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, devices=db)

@app.route('/approve/<id>')
def approve(id):
    if id in db:
        db[id]['status'] = 'authorized'
    return f'<script>alert("Dispositivo {id} Autorizado"); window.location.href="/admin";</script>'

if __name__ == '__main__':
    app.run()
