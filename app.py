from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Esto permite que tu APK se conecte sin bloqueos de seguridad

@app.route('/')
def home():
    # Esta es la respuesta que busca tu APK para ponerse en verde
    return jsonify({
        "status": "online",
        "message": "SENTINEL CORE v1.0 - STARK ACTIVE",
        "system_integrity": "100%"
    })

@app.route('/validate', methods=['POST'])
def validate_device():
    # Aquí es donde el bot enviará el ID del celular más adelante
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id", "unknown")
    return jsonify({"authorized": True, "user": "Edwin_Admin", "device_id": device_id})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
