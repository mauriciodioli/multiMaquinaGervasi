from flask import Blueprint, request, jsonify, render_template
from src.model.maquina import Maquina
from src.model.usuario import Usuario
from src.utils.get_textos_menu  import get_textos_menu
from src.model.pannelli.inverter_panel import InverterPanel
from src.model.pannelli.historial_inverter import HistorialInverter

from src.utils.db_session import get_db_session
from datetime import datetime

pannelli_solar = Blueprint('pannelli_solar', __name__)



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
            # SQLAlchemy 2.x: Session.get(Model, pk)
            usuario = session.query(Usuario).get(int(user_id))
            
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404

           # Datos de prueba (mock) para el template
            columnas = ["Fecha", "Potencia (W)", "Energía (kWh)", "Tensión (V)", "Corriente (A)"]
            trabajos = [
                ["2025-10-16 09:05", 1850, 1.42, 310, 5.97],
                ["2025-10-16 09:10", 1920, 1.55, 311, 6.17],
                ["2025-10-16 09:15", 2010, 1.69, 312, 6.44],
            ]
            mensaje = ""

            # Si el usuario todavía no tiene paneles, inventamos 2 para mostrar algo
            paneles = list(usuario.pannelli) if getattr(usuario, "pannelli", None) else []
            if not paneles:
                class _MockPanel:
                    def __init__(self, marca, modelo, sn):
                        self.marca = marca
                        self.modelo = modelo
                        self.serial_number = sn
                paneles = [
                    _MockPanel("Danfoss", "VLT-2800", "SN-TEST-001"),
                    _MockPanel("IME", "Solar-Plus 5k", "SN-TEST-002"),
                ]

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
        # Log real recomendado
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
