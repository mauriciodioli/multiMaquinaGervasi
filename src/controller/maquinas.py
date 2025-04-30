import pyodbc
from flask import Blueprint, render_template,request,jsonify
from src.model.maquina import Maquina
from utils.db import db
import json

maquinas = Blueprint('maquinas', __name__)

@maquinas.route('/maquinas_online/', methods=['POST'])
def maquinas_online():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        maquinas = db.session.query(Maquina).filter_by(user_id=int(user_id)).all()
  
        resultado = []
        for m in maquinas:
            if isinstance(m.setting, str):
                try:
                    setting = json.loads(m.setting)
                except:
                    setting = {}
            elif isinstance(m.setting, dict):
                setting = m.setting
            else:
                setting = {}

            resultado.append({
                "id": m.id,
                "user_id": m.user_id,
                "userCuenta": m.userCuenta,
                "estado": m.estado,
                "nombre": m.nombre,
                "ruta": m.ruta, 
                "nombreDb": m.nombreDb,
                "modulos": setting.get("modulos", [])
            })

        return jsonify({"success": True, "maquinas": resultado})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    finally:
        db.session.close()






# Ruta para ver los trabajos
@maquinas.route('/maquinas_sql')
def listar_maquina_sql():
    try:
        print("Conectando a la base de datos...")
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Lamiere_Tempi')  # O la tabla que tengas
        trabajos = cursor.fetchall()
        columnas = [column[0] for column in cursor.description]
        conn.close()
        print("Conexión exitosa.")
        return render_template('trabajos.html', trabajos=trabajos, columnas=columnas)
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return f"Error conectando a la base de datos: {e}"
#                 EjeZ_Origin,
#                 EjeX_Offset,
#                 EjeY_Offset,
#                 EjeZ_Offset,
#                 EjeX_Speed,
#                 EjeY_Speed,
#                 EjeZ_Speed,
#                 EjeX_Acceleration,
#                 EjeY_Acceleration,
#                 EjeZ_Acceleration,
#                 EjeX_Force,
#                 EjeY_Force,
#                 EjeZ_Force,
#                 EjeX_Force_Offset,
#                 EjeY_Force_Offset,    

