import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ACCESS_KEY = "Diosamor"

HTML_DISEÑO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOSOTROS RD - Sentinel</title>
    <style>
        body { background-color: #050505; color: #00ff41; font-family: 'Courier New', Courier, monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .panel { border: 2px solid #00ff41; padding: 40px; border-radius: 5px; box-shadow: 0 0 15px #00ff41; text-align: center; }
        h1 { font-size: 2em; letter-spacing: 5px; text-transform: uppercase; }
        .status { font-size: 1.2em; margin-top: 20px; border-top: 1px solid #00ff41; padding-top: 20px; }
        .blink { animation: b 1.5s infinite; }
        @keyframes b { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="panel">
        <h1>NOSOTROS RD</h1>
        <p>SISTEMA SENTINEL</p>
        <div class="status">ESTADO: <span class="blink">ONLINE</span></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_DISEÑO

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get("key") == ACCESS_KEY:
        return jsonify({"acceso": "CONFIRMADO", "mensaje": "Enlace Establecido"}), 200
    return jsonify({"acceso": "DENEGADO"}), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
