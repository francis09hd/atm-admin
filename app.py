
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DB_PATH = 'database.db'

# Inicializa la base de datos y la tabla si no existen o migrar si faltan columnas
def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS dispositivos (
        hwid TEXT PRIMARY KEY,
        nombre_socio TEXT,
        status TEXT DEFAULT 'pendiente',
        plan TEXT,
        fecha_vencimiento TEXT
    )""")
    # Migración: agregar columnas si faltan
    columnas = [row[1] for row in c.execute("PRAGMA table_info(dispositivos)")]
    if 'plan' not in columnas:
        c.execute("ALTER TABLE dispositivos ADD COLUMN plan TEXT")
    if 'fecha_vencimiento' not in columnas:
        c.execute("ALTER TABLE dispositivos ADD COLUMN fecha_vencimiento TEXT")
    conn.commit()
    conn.close()

inicializar_db()

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
        .amarillo { color: #ffff00; font-weight: bold; }
        .rojo { color: #ff3131; font-weight: bold; }
    </style>
'''

PLANES = {
    '1 Mes': 30,
    '3 Meses': 90,
    '1 Año': 365
}

def calcular_vencimiento(plan):
    dias = PLANES.get(plan, 30)
    return (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')

def estado_visual(status, fecha_vencimiento):
    if not fecha_vencimiento:
        return status, '', ''
    hoy = datetime.now().date()
    try:
        vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
    except:
        return status, '', ''
    dias_restantes = (vencimiento - hoy).days
    if dias_restantes < 0:
        return 'Expirado', 'rojo', dias_restantes
    elif dias_restantes < 3:
        return status, 'amarillo', dias_restantes
    return status, '', dias_restantes

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db()
    c = conn.cursor()
    filtro_activos = request.args.get('activos') == '1'
    if request.method == 'POST':
        hwid = request.form.get('hwid')
        nombre = request.form.get('nombre_socio')
        plan = request.form.get('plan')
        if hwid:
            fecha_vencimiento = calcular_vencimiento(plan)
            c.execute('INSERT OR IGNORE INTO dispositivos (hwid, nombre_socio, status, plan, fecha_vencimiento) VALUES (?, ?, ?, ?, ?)',
                      (hwid, nombre, 'pendiente', plan, fecha_vencimiento))
            conn.commit()
        # Cambiar status si se envía
        for key in request.form:
            if key.startswith('aprobar_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('aprobado', key.split('_',1)[1]))
                conn.commit()
            if key.startswith('bloquear_'):
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('bloqueado', key.split('_',1)[1]))
                conn.commit()
    if filtro_activos:
        hoy = datetime.now().date()
        c.execute('SELECT * FROM dispositivos WHERE status="aprobado" AND fecha_vencimiento >= ?', (hoy.strftime('%Y-%m-%d'),))
    else:
        c.execute('SELECT * FROM dispositivos')
    dispositivos = c.fetchall()
    conn.close()
    html = CYBER_STYLE + '''
    <h2>ATM BOT - Centro de Socios</h2>
    <form method="post">
        <input name="hwid" placeholder="HWID" required>
        <input name="nombre_socio" placeholder="Nombre del socio">
        <select name="plan" required>
            <option value="1 Mes">1 Mes</option>
            <option value="3 Meses">3 Meses</option>
            <option value="1 Año">1 Año</option>
        </select>
        <button class="btn" type="submit">Registrar</button>
    </form>
    <form method="get" style="margin-top:10px;">
        <button class="btn" name="activos" value="1" type="submit">FILTRAR ACTIVOS</button>
        <a href="/" class="btn">Mostrar Todos</a>
    </form>
    <table>
        <tr>
            <th>HWID</th>
            <th>Nombre Socio</th>
            <th>Plan</th>
            <th>VENCIMIENTO</th>
            <th>Días Restantes</th>
            <th>Status</th>
            <th>Acciones</th>
        </tr>
        {% for d in dispositivos %}
        {% set status, color, dias_restantes = estado_visual(d['status'], d['fecha_vencimiento']) %}
        <tr>
            <td>{{ d['hwid'] }}</td>
            <td>{{ d['nombre_socio'] or '' }}</td>
            <td>{{ d['plan'] or '' }}</td>
            <td>{{ d['fecha_vencimiento'] or '' }}</td>
            <td>{{ dias_restantes }}</td>
            <td class="{{ color }}">{{ status }}</td>
            <td>
                <button class="btn" name="aprobar_{{ d['hwid'] }}" type="submit">APROBAR</button>
                <button class="btn" name="bloquear_{{ d['hwid'] }}" type="submit">BLOQUEAR</button>
            </td>
        </tr>
        {% endfor %}
    </table>
    <script>
    // JS para ocultar filas vencidas si se pulsa FILTRAR ACTIVOS
    document.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        if(urlParams.get('activos') === '1') {
            document.querySelectorAll('tr').forEach(function(row) {
                if(row.querySelector('.rojo')) row.style.display = 'none';
            });
        }
    });
    </script>
    '''
    return render_template_string(html, dispositivos=dispositivos, estado_visual=estado_visual)

@app.route('/validar/<hwid>')
def validar(hwid):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT status, fecha_vencimiento FROM dispositivos WHERE hwid=?', (hwid,))
    row = c.fetchone()
    if row and row['fecha_vencimiento']:
        try:
            vencimiento = datetime.strptime(row['fecha_vencimiento'], '%Y-%m-%d').date()
            hoy = datetime.now().date()
            if hoy > vencimiento:
                # Actualizar status a Expirado si ya venció
                c.execute('UPDATE dispositivos SET status=? WHERE hwid=?', ('Expirado', hwid))
                conn.commit()
                conn.close()
                return jsonify({"status": "Expirado", "vence": row['fecha_vencimiento']})
            if row['status'] == 'aprobado':
                conn.close()
                return jsonify({"status": "Aprobado", "vence": row['fecha_vencimiento']})
            else:
                conn.close()
                return jsonify({"status": row['status'], "vence": row['fecha_vencimiento']})
        except:
            conn.close()
            return jsonify({"status": "Error", "vence": None})
    conn.close()
    return jsonify({"status": "Pendiente", "vence": None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
