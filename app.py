from datetime import datetime
import json
import os

from flask import Flask, jsonify, request, redirect, url_for, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "devices_registry.json"


def _load_db():
    if not os.path.exists(DB_FILE):
        return {"devices": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"devices": {}}
        if "devices" not in data or not isinstance(data["devices"], dict):
            data["devices"] = {}
        return data
    except Exception:
        return {"devices": {}}


def _save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _upsert_device(hwid, nombre=""):
    hwid = (hwid or "").strip()
    if not hwid:
        return None
    db = _load_db()
    devices = db["devices"]
    now = datetime.utcnow().isoformat()
    if hwid not in devices:
        devices[hwid] = {
            "hwid": hwid,
            "nombre": nombre.strip(),
            "status": "pendiente",
            "authorized": False,
            "created_at": now,
            "last_seen": now,
        }
    else:
        devices[hwid]["last_seen"] = now
        if nombre:
            devices[hwid]["nombre"] = nombre.strip()
    _save_db(db)
    return devices[hwid]


@app.route("/")
def home():
    return jsonify({"status": "online", "message": "SENTINEL STARK ACTIVE"})


@app.route("/validate", methods=["POST"])
def validate():
    payload = request.get_json(silent=True) or {}
    hwid = (payload.get("hardware_id") or payload.get("device_id") or "").strip()
    nombre = (payload.get("nombre") or "").strip()

    if not hwid:
        return jsonify({"authorized": False, "error": "hardware_id requerido"}), 400

    device = _upsert_device(hwid, nombre)
    authorized = bool(device.get("authorized", False))
    return jsonify(
        {
            "authorized": authorized,
            "status": device.get("status", "pendiente"),
            "hwid": hwid,
        }
    )


@app.route("/registro_cliente", methods=["POST"])
def registro_cliente():
    payload = request.get_json(silent=True) or {}
    hwid = (payload.get("hwid") or payload.get("hardware_id") or "").strip()
    nombre = (payload.get("nombre") or "").strip()
    email = (payload.get("email") or "").strip()

    if not hwid:
        return jsonify({"ok": False, "error": "hwid requerido"}), 400

    device = _upsert_device(hwid, nombre)
    if email:
        db = _load_db()
        db["devices"][hwid]["email"] = email
        _save_db(db)

    return jsonify(
        {
            "ok": True,
            "ya_registrado": device.get("created_at") != device.get("last_seen"),
            "status": device.get("status", "pendiente"),
            "authorized": bool(device.get("authorized", False)),
        }
    )


@app.route("/validar/<hwid>", methods=["GET"])
def validar_hwid(hwid):
    nombre = (request.args.get("nombre") or "").strip()
    device = _upsert_device(hwid, nombre)
    authorized = bool(device.get("authorized", False))
    return jsonify(
        {
            "access": "granted" if authorized else "denied",
            "status": "Aprobado" if authorized else "Pendiente",
            "authorized": authorized,
            "hwid": hwid,
        }
    )


@app.route("/protocol/v1/verify/<hwid>", methods=["GET"])
def protocol_verify(hwid):
    device = _upsert_device(hwid)
    return jsonify(
        {
            "authorized": bool(device.get("authorized", False)),
            "status": device.get("status", "pendiente"),
            "hwid": hwid,
        }
    )


@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    db = _load_db()
    devices = db["devices"]

    if request.method == "POST":
        hwid = (request.form.get("hwid") or "").strip()
        action = (request.form.get("action") or "").strip().lower()
        if hwid in devices:
            if action == "accept":
                devices[hwid]["authorized"] = True
                devices[hwid]["status"] = "aprobado"
            elif action == "reject":
                devices[hwid]["authorized"] = False
                devices[hwid]["status"] = "pendiente"
            devices[hwid]["updated_at"] = datetime.utcnow().isoformat()
            _save_db(db)
        return redirect(url_for("admin_panel"))

    rows = sorted(devices.values(), key=lambda x: x.get("last_seen", ""), reverse=True)
    html = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Sentinel Admin</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 24px; background: #0c111a; color: #d9f7ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #2f4d62; padding: 10px; font-size: 14px; }
        th { background: #153247; }
        .ok { color: #7CFFB2; }
        .wait { color: #FFD166; }
        button { padding: 6px 10px; margin-right: 6px; }
      </style>
    </head>
    <body>
      <h2>Sentinel Admin - Dispositivos</h2>
      <p>Usa Aceptar para activar el bot en el telefono.</p>
      <table>
        <tr>
          <th>HWID</th><th>Nombre</th><th>Estado</th><th>Autorizado</th><th>Ultima vez</th><th>Accion</th>
        </tr>
        {% for d in rows %}
        <tr>
          <td>{{ d.get('hwid','') }}</td>
          <td>{{ d.get('nombre','') }}</td>
          <td class="{{ 'ok' if d.get('status') == 'aprobado' else 'wait' }}">{{ d.get('status','pendiente') }}</td>
          <td>{{ d.get('authorized', False) }}</td>
          <td>{{ d.get('last_seen','') }}</td>
          <td>
            <form method="post" style="display:inline;">
              <input type="hidden" name="hwid" value="{{ d.get('hwid','') }}" />
              <input type="hidden" name="action" value="accept" />
              <button type="submit">Aceptar</button>
            </form>
            <form method="post" style="display:inline;">
              <input type="hidden" name="hwid" value="{{ d.get('hwid','') }}" />
              <input type="hidden" name="action" value="reject" />
              <button type="submit">Pendiente</button>
            </form>
          </td>
        </tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """
    return render_template_string(html, rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
