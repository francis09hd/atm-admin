from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "SENTINEL CORE v1.0 - STARK ACTIVE",
        "system_integrity": "100%"
    })


@app.route('/validate', methods=['POST'])
def validate_device():
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id", "unknown")
    return jsonify({
        "authorized": True,
        "user": "Edwin_Admin",
        "device_id": device_id
    })
