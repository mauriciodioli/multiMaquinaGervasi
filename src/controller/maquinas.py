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
                "potencia": m.potencia,
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















# Ruta para ver todos los trabajos (sin límite, ordenados por fecha)
@maquinas.route('/maquinas_sql_histoy/', methods=['POST'])
def listar_maquina_sql_filtrado_history():
    try:
        data = request.get_json()
        filtro_clfile = data.get("clfile", "")  # puede venir vacío

        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.1.250,1433;"
            "DATABASE=si_cam_db;"
            "UID=usuario_si_cam;"
            "PWD=Dpia1234!;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
        cursor = conn.cursor()

        campos = "*"

        if filtro_clfile != "":
            cursor.execute(f"SELECT TOP 50 {campos} FROM Lamiere_Tempi WHERE CLFileName LIKE ? ORDER BY DataOraReg DESC", f"%{filtro_clfile}%")
        else:
            cursor.execute(f"SELECT TOP 50 {campos} FROM Lamiere_Tempi ORDER BY DataOraReg DESC")
        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()

        trabajos = [dict(zip(columnas, fila)) for fila in filas]

        conn.close()
        return jsonify({
            "success": True,
            "columnas": columnas,
            "trabajos": trabajos
        })

    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return jsonify({"success": False, "error": str(e)})














@maquinas.route('/resumen_trabajos/', methods=['GET'])
def resumen_trabajos():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.1.250,1433;"
            "DATABASE=si_cam_db;"
            "UID=usuario_si_cam;"
            "PWD=Dpia1234!;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
        cursor = conn.cursor()

        query = """
            SELECT 
                TOP 50 
                CLFileName,
                CodMacchina,
                COUNT(*) AS numero_di_record,
                SUM(TRY_CAST(TempTotale AS FLOAT)) AS tempo_totale_secondi,
                AVG(TRY_CAST(Spessore AS FLOAT)) AS spessore_medio,
                SUM(TRY_CAST(PesoLamiera AS FLOAT)) AS peso_totale,
                MAX(DataOraReg) AS ultima_data
            FROM 
                Lamiere_Tempi
            GROUP BY 
                CLFileName, CodMacchina
            ORDER BY 
                MAX(DataOraReg) DESC

        """

        cursor.execute(query)
        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        resumen = [dict(zip(columnas, fila)) for fila in filas]

        conn.close()
        return jsonify({"success": True, "resumen": resumen})

    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return jsonify({"success": False, "error": str(e)})














# Ruta para ver los trabajos
@maquinas.route('/maquinas_sql_cost/', methods=['POST'])
def listar_maquina_sql_filtrado_cost():
    try:
        data = request.get_json()
        filtro_clfile = data.get("clfile", "")  # puede venir vacío
        precioKwh = data.get("precioKwh")  # Precio por kWh, por defecto 0.20
        potencia = data.get("potencia")  # Potencia de la máquina, por defecto 8kW
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.1.250,1433;"
            "DATABASE=si_cam_db;"
            "UID=usuario_si_cam;"
            "PWD=Dpia1234!;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
        cursor = conn.cursor()

        campos = "ID_CLF,CLFileName, CodMacchina, DataOraReg, TempTotale"

        if filtro_clfile != "":
            cursor.execute(f"SELECT TOP 500 {campos} FROM Lamiere_Tempi WHERE CLFileName LIKE ? ORDER BY DataOraReg DESC", f"%{filtro_clfile}%")
        else:
            cursor.execute(f"SELECT TOP 500 {campos} FROM Lamiere_Tempi ORDER BY DataOraReg DESC")

        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        trabajos = []

        # Solo estos campos queremos devolver
        columnas_finales = ["ID_CLF","CLFileName", "CodMacchina", "DataOraReg", "TempTotale", "Consumo_kWh", "Costo_Euro"]
        trabajos = []

        for fila in filas:
            fila_dict = dict(zip(columnas, fila))
            fila_dict = calculo_consumo_por_trabajo(fila_dict, precioKwh,potencia)
            # Convertir a float si es necesario    
            resultado = {k: fila_dict.get(k) for k in columnas_finales}
           # print("[✅ Fila procesada]", resultado)

            trabajos.append(resultado)

        conn.close()
        return jsonify({"success": True, "columnas": columnas_finales, "trabajos": trabajos})
    except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return jsonify({"success": False, "error": str(e)})
    
def calculo_consumo_por_trabajo(fila, precioKwh,potencia):
    try:
        temp_total = fila.get("TempTotale", 0) or 0
        if isinstance(temp_total, str):
            temp_total = float(temp_total.replace(",", "."))  # soporte coma como decimal
        consumo_kw = (float(temp_total) / 3600) * potencia  # Suponiendo 8kW de potencia
        costo_euro = round(consumo_kw * float(precioKwh), 2)  # Supongamos 0.20 €/kWh
        fila["Consumo_kWh"] = round(consumo_kw, 2)
        fila["Costo_Euro"] = costo_euro
    except Exception as e:
        fila["Consumo_kWh"] = 0
        fila["Costo_Euro"] = 0
        print(f"[ERROR cálculo consumo] {e}")
    return fila

  

