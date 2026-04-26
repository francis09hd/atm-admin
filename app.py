"""
SENTINEL CORE - Servidor Render Minimalista
============================================
Servidor Flask ligero para conectar el APK Sentinel Core en Render.
Objeto principal: app (para gunicorn app:app)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# ============== CONFIG ==============
app = Flask(__name__)
CORS(app)

DEVICES_FILE = 'devices.json'
DEBUG_MODE = os.environ.get('DEBUG', 'False') == 'True'

# ============== UTILIDADES ==============

def load_devices():
    """Carga dispositivos desde JSON"""
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Cargando devices.json: {e}")
            return {}
    return {}

def save_devices(devices):
    """Guarda dispositivos en JSON"""
    try:
        with open(DEVICES_FILE, 'w') as f:
            json.dump(devices, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Guardando devices.json: {e}")
        return False

# ============== ENDPOINTS ==============

@app.route('/', methods=['GET'])
def status():
    """
    Endpoint de verificación - Responde al ping del bot
    Returns: {"status": "online", "message": "...", "timestamp": "..."}
    """
    return jsonify({
        "status": "online",
        "message": "🛡️ Sentinel Core Activo",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/device/register', methods=['POST'])
def register_device():
    """
    Registra un dispositivo nuevo
    Body: {"hwid": "DEVICE_HWID"}
    Returns: {"status": "registered", "hwid": "...", "message": "..."}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body requerido"}), 400
        
        hwid = data.get('hwid', '').strip()
        if not hwid:
            return jsonify({"error": "HWID requerido"}), 400
        
        devices = load_devices()
        now = datetime.now().isoformat()
        
        if hwid not in devices:
            devices[hwid] = {
                "hwid": hwid,
                "registered_at": now,
                "status": "active",
                "last_ping": now
            }
            save_devices(devices)
        
        return jsonify({
            "status": "registered",
            "hwid": hwid,
            "message": "Dispositivo registrado",
            "timestamp": now
        }), 200
    
    except Exception as e:
        print(f"[ERROR] register_device: {e}")
        return jsonify({"error": f"Error en registro: {str(e)}"}), 500

@app.route('/api/device/<hwid>', methods=['GET'])
def get_device(hwid):
    """
    Obtiene información del dispositivo
    Returns: {"hwid": "...", "status": "...", "last_ping": "..."}
    """
    try:
        devices = load_devices()
        
        if hwid in devices:
            return jsonify(devices[hwid]), 200
        else:
            return jsonify({
                "error": "Dispositivo no encontrado",
                "hwid": hwid,
                "total_devices": len(devices)
            }), 404
    
    except Exception as e:
        print(f"[ERROR] get_device: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ping', methods=['POST'])
def ping():
    """
    Heartbeat del bot - mantiene vivo el registro del dispositivo
    Body: {"hwid": "DEVICE_HWID"} (opcional)
    Returns: {"status": "pong", "server_time": "..."}
    """
    try:
        data = request.get_json() or {}
        hwid = data.get('hwid', '').strip()
        
        if hwid:
            devices = load_devices()
            if hwid in devices:
                devices[hwid]['last_ping'] = datetime.now().isoformat()
                save_devices(devices)
        
        return jsonify({
            "status": "pong",
            "server_time": datetime.now().isoformat(),
            "message": "Heartbeat recibido"
        }), 200
    
    except Exception as e:
        print(f"[ERROR] ping: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check para monitoreo de Render
    Returns: {"healthy": true, "devices": count}
    """
    try:
        devices = load_devices()
        
        return jsonify({
            "healthy": True,
            "devices_registered": len(devices),
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        print(f"[ERROR] health: {e}")
        return jsonify({
            "healthy": False,
            "error": str(e)
        }), 500

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(e):
    """Maneja rutas no encontradas"""
    return jsonify({
        "error": "Endpoint no encontrado",
        "path": request.path,
        "method": request.method
    }), 404

@app.errorhandler(500)
def server_error(e):
    """Maneja errores internos"""
    return jsonify({
        "error": "Error interno del servidor",
        "message": str(e)
    }), 500

@app.errorhandler(405)
def method_not_allowed(e):
    """Maneja métodos HTTP no permitidos"""
    return jsonify({
        "error": "Método no permitido",
        "method": request.method,
        "path": request.path
    }), 405

# ============== MAIN ==============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=DEBUG_MODE,
        threaded=True
    )
