from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def health():
    return jsonify({"status": "online"})


@app.route('/validate', methods=['POST'])
def validate_hardware():
    payload = request.get_json(silent=True) or {}
    hardware_id = payload.get("hardware_id")
    return jsonify({
        "authorized": True,
        "hardware_id": hardware_id
    })
