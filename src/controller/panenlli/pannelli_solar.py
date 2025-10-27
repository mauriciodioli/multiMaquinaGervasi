from flask import Blueprint, request, jsonify, render_template
from src.model.maquina import Maquina
from src.model.usuario import Usuario
from src.utils.get_textos_menu  import get_textos_menu
from src.model.pannelli.inverter_panel import InverterPanel
from src.model.pannelli.historial_inverter import HistorialInverter

from src.utils.db_session import get_db_session
from datetime import datetime,timedelta

from src.controller.panenlli.modbus_sma import read_all, IPS

import time
from flask import jsonify, request

pannelli_solar = Blueprint('pannelli_solar', __name__)











def _simplify(inv: dict):
    """Compacta el dict para frontend."""
    txt = (inv.get("status_text") or "").lower()
    if "falla" in txt:
        device_status = "Error"
    elif "standby" in txt or "espera" in txt:
        device_status = "Standby"
    elif "ok" in txt or "operando" in txt or "marcha" in txt:
        device_status = "Ok"
    else:
        device_status = "Unknown"

    return {
        "ip": inv.get("ip"),
        "manufacturer": inv.get("manufacturer"),
        "model": inv.get("model"),
        "serial": inv.get("serial"),
        "device_status": device_status,              # <- para el “Device status” de la UI
        "status_text": inv.get("status_text"),
        "power_W": inv.get("P_AC_W"),
        "power_kW": inv.get("P_AC_kW"),
        "voltage_V": inv.get("V_AC"),
        "frequency_Hz": inv.get("freq_Hz"),
    }

@pannelli_solar.get("/api/pannelli/status")
def pannelli_status():
    """
    Devuelve estado de todos los inversores para AJAX.
    Opcional: ?ips=192.168.1.101,192.168.1.102
    """
    ips_param = request.args.get("ips")
    ips = [s.strip() for s in ips_param.split(",")] if ips_param else IPS

    data = read_all(ips)                # reutiliza tu lógica sin tocar nada
    items = [_simplify(d) for d in data]

    total_power_w = sum(
        i["power_W"] for i in items if isinstance(i.get("power_W"), (int, float))
    )

    return jsonify({
        "ts": int(time.time()),
        "total_power_W": round(total_power_w, 1),
        "inverters": items
    })







@pannelli_solar.route("/pannelli_crud_consulta/", methods=["GET"])
def pannelli_crud_consulta():
    try:
        user_id = request.cookies.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "user_id inválido"}), 400

        with get_db_session() as session:
            # Mantengo tu estilo
            usuario = session.query(Usuario).get(int(user_id))
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404

            # === Paneles del usuario ===
            paneles = list(usuario.pannelli) if getattr(usuario, "pannelli", None) else []

            # --- MOCK de paneles si no hay (3 paneles) ---
            if not paneles:
                class _MockPanel:
                    def __init__(self, _id, marca, modelo, sn):
                        self.id = _id
                        self.marca = marca
                        self.modelo = modelo
                        self.serial_number = sn
                paneles = [
                    _MockPanel(-1, "Danfoss", "VLT-2800", "SN-TEST-001"),
                    _MockPanel(-2, "IME",     "Solar-Plus 5k", "SN-TEST-002"),
                    _MockPanel(-3, "Fronius", "Symo 10.0",     "SN-TEST-003"),
                ]

            panel_ids = [p.id for p in paneles if getattr(p, "id", None)]

            # === Tabla ===
            columnas = [
                "Fecha","Potencia (W)","Energía (kWh)","Tensión (V)",
                "Corriente (A)","Frecuencia (Hz)","Estado","Alarma","Panel"
            ]
            trabajos = []

            lecturas = []
            # Solo consulta real si los IDs son reales (>0)
            if panel_ids and all(i > 0 for i in panel_ids):
                lecturas = (
                    session.query(HistorialInverter)
                    .filter(HistorialInverter.inverter_id.in_(panel_ids))
                    .order_by(HistorialInverter.timestamp.desc())
                    .limit(100).all()
                )

            panel_map = {p.id: p for p in paneles if getattr(p, "id", None)}

            if lecturas:
                for h in lecturas:
                    p = panel_map.get(h.inverter_id)
                    etiqueta_panel = f"{p.marca} {p.modelo or ''} (SN {p.serial_number})" if p else f"ID {h.inverter_id}"
                    trabajos.append({
                        "Fecha":          h.timestamp.strftime('%Y-%m-%d %H:%M') if h.timestamp else '',
                        "Potencia (W)":   h.potencia or 0,
                        "Energía (kWh)":  h.energia or 0,
                        "Tensión (V)":    h.voltaje or 0,
                        "Corriente (A)":  h.corriente or 0,
                        "Frecuencia (Hz)":h.frecuencia or 0,
                        "Estado":         h.estado or '-',
                        "Alarma":         h.codigo_alarma or '-',
                        "Panel":          etiqueta_panel,
                        "_panel_id":      h.inverter_id
                    })
                mensaje = ""
            else:
                # --- MOCK de lecturas: 3 filas para CADA panel ---
                base = datetime.utcnow().replace(second=0, microsecond=0)

                for idx, p in enumerate(paneles, start=0):
                    etiqueta = f"{p.marca} {p.modelo or ''} (SN {p.serial_number})"
                    # desplazamos los minutos por panel para que no queden iguales
                    filas = [
                        (base + timedelta(minutes=idx*3 + 0), 1850 + idx*30, 1.42 + idx*0.05, 310 + idx, 5.97 + idx*0.1, 50.0, "OK",     "-"),
                        (base + timedelta(minutes=idx*3 + 5), 1920 + idx*30, 1.55 + idx*0.05, 311 + idx, 6.17 + idx*0.1, 50.0, "OK",     "-"),
                        (base + timedelta(minutes=idx*3 +10), 2010 + idx*30, 1.69 + idx*0.05, 312 + idx, 6.44 + idx*0.1, 50.0, "NORMAL", "-"),
                    ]
                    for ts, pot, ene, v, a, hz, est, alarm in filas:
                        trabajos.append({
                            "Fecha": ts.strftime('%Y-%m-%d %H:%M'),
                            "Potencia (W)": pot,
                            "Energía (kWh)": ene,
                            "Tensión (V)": v,
                            "Corriente (A)": a,
                            "Frecuencia (Hz)": hz,
                            "Estado": est,
                            "Alarma": alarm,
                            "Panel": etiqueta,
                            "_panel_id": p.id  # <-- importantísimo para que el filtro funcione
                        })

                mensaje = ""

            lang = request.cookies.get("lang", "es")
            t_menu = get_textos_menu(lang)

            return render_template(
                "pannelli/pannelli.html",
                user=usuario,
                paneles=paneles,
                columnas=columnas,
                trabajos=trabajos,
                mensaje=mensaje,
                t_menu=t_menu,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Crear nuevo panel
@pannelli_solar.route('/pannelli_crud_crear_panel', methods=['POST'])
def pannelli_crud_crear_panel():
    data = request.json
    try:
        with get_db_session() as session:
            nuevo = InverterPanel(
                nombre=data['nombre'],
                marca=data['marca'],
                modelo=data.get('modelo'),
                ubicacion=data.get('ubicacion'),
                serial_number=data['serial_number']
            )
            session.add(nuevo)
            session.flush()
            return panel_schema.jsonify(nuevo), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Cargar nueva lectura (historial)
@pannelli_solar.route('/pannelli_crud_crear_lectura/<int:panel_id>', methods=['POST'])
def pannelli_crud_crear_lectura(panel_id):
    data = request.json
    try:
        with get_db_session() as session:
            lectura = HistorialInverter(
                inverter_id=panel_id,
                timestamp=datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S'),
                voltaje=data.get('voltaje'),
                corriente=data.get('corriente'),
                potencia=data.get('potencia'),
                energia=data.get('energia'),
                frecuencia=data.get('frecuencia'),
                estado=data.get('estado'),
                codigo_alarma=data.get('codigo_alarma'),
                datos_raw=data
            )
            session.add(lectura)
            session.flush()
            return historial_schema.jsonify(lectura), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Ver historial por panel
@pannelli_solar.route('/pannelli_crud_historial/<int:panel_id>', methods=['GET'])
def pannelli_crud_historial(panel_id):
    try:
        with get_db_session() as session:
            lecturas = session.query(HistorialInverter) \
                .filter_by(inverter_id=panel_id) \
                .order_by(HistorialInverter.timestamp.desc()) \
                .limit(100).all()
            return historials_schema.jsonify(lecturas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
