from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = 'database.db'

# Inicializa la base de datos y la tabla si no existen
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE dispositivos (
        hwid TEXT PRIMARY KEY,
        nombre_socio TEXT,
        status TEXT DEFAULT 'pendiente'
    )''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

CYBER_STYLE = '''
    <style>
        body { background: #000; color: #00FFFF; font-family: 'Segoe UI', Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; margin-top: 30px; }
        th, td { border: 1px solid #00FFFF; padding: 10px; text-align: center; }
        th { background: #111; }
        tr:nth-child(even) { background: #111; }
        .btn { background: #00FFFF; color: #000; border: none; padding: 6px 16px; margin: 2px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #00bfbf; }
        input, select { background: #111; color: #00FFFF; border: 1px solid #00FFFF; padding: 6px; border-radius: 4px; }
    </style>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        hwid = request.form.get('hwid')
        nombre = request.form.get('nombre_socio')
        if hwid:
            c.execute('INSERT OR IGNORE INTO dispositivos (hwid, nombre_socio, status) VALUES (?, ?, ?)', (hwid, nombre, 'pendiente'))
            conn.commit()
        # Cambiar status si se envía
        for key in request.form:
            if key.startswith('aprobar_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('aprobado', key.split('_',1)[1]))
                conn.commit()
            if key.startswith('bloquear_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('bloqueado', key.split('_',1)[1]))
                conn.commit()
    c.execute('SELECT * FROM dispositivos')
    dispositivos = c.fetchall()
    conn.close()
    html = CYBER_STYLE + '''
    <h2>ATM BOT - Centro de Socios</h2>
    <form method="post">
        <input name="hwid" placeholder="HWID" required>
        <input name="nombre_socio" placeholder="Nombre del socio">
        <button class="btn" type="submit">Registrar</button>
    </form>
    <table>
        <tr>
            <th>HWID</th>
            <th>Nombre Socio</th>
            <th>Status</th>
            <th>Acciones</th>
        </tr>
        {% for d in dispositivos %}
        <tr>
            <td>{{ d['hwid'] }}</td>
            <td>{{ d['nombre_socio'] or '' }}</td>
            <td>{{ d['status'] }}</td>
            <td>
                <button class="btn" name="aprobar_{{ d['hwid'] }}" type="submit">APROBAR</button>
                <button class="btn" name="bloquear_{{ d['hwid'] }}" type="submit">BLOQUEAR</button>
            </td>
        </tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, dispositivos=dispositivos)

@app.route('/check/<hwid>')
def check(hwid):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT status FROM dispositivos WHERE hwid=?', (hwid,))
    row = c.fetchone()
    conn.close()
    if row and row['status'] == 'aprobado':
        return jsonify({"access": "granted"})
    else:
        return jsonify({"access": "denied"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
