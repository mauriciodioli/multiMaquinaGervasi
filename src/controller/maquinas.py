import pyodbc
from flask import Blueprint, render_template,request,jsonify
from src.model.maquina import Maquina
from src.model.usuario import Usuario
from utils.db import db
from src.utils.db_session import get_db_session
import json

maquinas = Blueprint('maquinas', __name__)









@maquinas.route('/maquinas_online/', methods=['POST'])
def maquinas_online():
    try:
        data = request.get_json()
        user_id = request.cookies.get("user_id")
        with get_db_session() as session:
            usuario = session.query(Usuario).get(int(user_id))
            if not usuario:
                return jsonify({"success": False, "message": "Usuario no encontrado"})

            if usuario.roll == "admin":
                maquinas = session.query(Maquina).all()
            else:
                maquinas = session.query(Maquina).filter_by(user_id=int(user_id)).all()

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
                    "user_id": user_id,
                    "userCuenta": m.userCuenta,
                    "estado": m.estado,
                    "potencia": m.potencia,
                    "nombre": m.nombre,
                    "ruta": m.ruta,
                    "nombreDb": m.nombreDb,
                    "nombreTabla": m.nombreTabla,
                    "modulos": setting.get("modulos", [])
                })

            return jsonify({"success": True, "maquinas": resultado})

    except Exception as e:        
        return jsonify({"success": False, "message": str(e)})
    
















# Ruta para ver todos los trabajos (sin límite, ordenados por fecha)
@maquinas.route('/maquinas_sql_histoy/', methods=['POST'])
def listar_maquina_sql_filtrado_history():
    try:
        data = request.get_json()
        filtro_clfile = data.get("clfile", "")  # puede venir vacío
        nombre = data.get("nombre_maquina", "").strip()
        ip = data.get("ip", "")
        port = data.get("port", "")
        user = data.get("user", "")
        password = data.get("password", "")
         
         # Imprimir detalles antes de conectar
         # print(f"Intentando conectar a la base de datos...")
         # print(f"Base de datos: {database}")
         # print(f"IP: {ip}")
         # print(f"Puerto: {port}")
         # print(f"Usuario: {user}")
         # print(f"Contraseña: {password}")  # Ojo con la contraseña, para evitar logueo no deseado
        with get_db_session() as session:
            maquinas = session.query(Maquina).filter_by(nombre=nombre).all()
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={ip},{port};"
                f"DATABASE=CNC_DATA;"
                f"UID={user};"
                f"PWD={password};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
            cursor = conn.cursor()

            campos = "*"
            
            try:
                nombre_tabla_dict = json.loads(maquinas[0].nombreTabla)
                tablas = nombre_tabla_dict.get("tablas", [])
                if not tablas:
                    return jsonify(success=False, error="No hay tablas configuradas en nombreTabla.")
            
        
                if filtro_clfile != "":
                    cursor.execute(f"SELECT TOP 50 {campos} FROM {tablas[0]} WHERE CLFileName LIKE ? ORDER BY DataOraReg DESC", f"%{filtro_clfile}%")
                else:
                    cursor.execute(f"SELECT TOP 50 {campos} FROM {tablas[0]} ORDER BY DataOraReg DESC")
                
                
            except Exception as e:
                return jsonify(success=False, error=f"Error al procesar nombreTabla: {str(e)}")
        
                
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













@maquinas.route('/resumen_trabajos/', methods=['POST'])
def resumen_trabajos():
    try:
        data = request.get_json()
        filtro_clfile = data.get("clfile", "")
        database = data.get("nombre_maquina", "")
        ip = data.get("ip", "")
        port = data.get("port", "")
        user = data.get("user", "")
        password = data.get("password", "")
        with get_db_session() as session:
            # ✅ Obtener tabla desde modelo
            maquinas = session.query(Maquina).filter_by(nombre=database).all()
            if not maquinas:
                return jsonify(success=False, error="Máquina no encontrada")

            try:
                nombre_tabla_dict = json.loads(maquinas[0].nombreTabla)
                tablas = nombre_tabla_dict.get("tablas", [])
                if not tablas:
                    return jsonify(success=False, error="No hay tablas configuradas.")
                tabla_tempi = tablas[0]
            except Exception as e:
                return jsonify(success=False, error=f"Error al procesar nombreTabla: {str(e)}")

            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={ip},{port};"
                f"DATABASE=CNC_DATA;"
                f"UID={user};"
                f"PWD={password};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
            cursor = conn.cursor()

            # ✅ Query con nombre de tabla dinámico
            query = f"""
                SELECT 
                    T.ID_CLF,
                    T.CLFileName,
                    T.STZFileName,
                    T.CodMacchina,
                    T.DataOraReg,
                    TRY_CAST(T.TempTotale AS FLOAT) AS TempTotale
                FROM 
                    (
                        SELECT DISTINCT STZFileName 
                        FROM {tabla_tempi}
                    ) AS STZ
                OUTER APPLY (
                    SELECT TOP 1 *
                    FROM {tabla_tempi}
                    WHERE {tabla_tempi}.STZFileName = STZ.STZFileName
                    ORDER BY DataOraReg DESC
                ) AS T
                ORDER BY T.DataOraReg DESC;
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












@maquinas.route('/resumen_lamiere/', methods=['POST'])
def resumen_lamiere():
    try:
        data = request.get_json()
        database = data.get("nombre_maquina", "")
        ip = data.get("ip", "")
        port = data.get("port", "")
        user = data.get("user", "")
        password = data.get("password", "")
        precio_kwh = data.get("precioKwh")
        potencia_kw = data.get("potencia")
        with get_db_session() as session:
            # ✅ Obtener nombreTabla desde la base
            maquinas = session.query(Maquina).filter_by(nombre=database).all()
            if not maquinas:
                return jsonify(success=False, error="Máquina no encontrada")

            try:
                nombre_tabla_dict = json.loads(maquinas[0].nombreTabla)
                tablas = nombre_tabla_dict.get("tablas", [])
                if len(tablas) < 2:
                    return jsonify(success=False, error="Faltan tablas en nombreTabla")
                tabla_tempi = tablas[0]
                tabla_icone = tablas[1]
            except Exception as e:
                return jsonify(success=False, error=f"Error al procesar nombreTabla: {str(e)}")

            # ✅ Conexión
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={ip},{port};"
                f"DATABASE=CNC_DATA;"
                f"UID={user};"
                f"PWD={password};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
            cursor = conn.cursor()

            # ✅ Consulta usando tablas dinámicas
            query = f"""
                SELECT TOP 50
                    t.ID_CLF,                    
                    t.STZFileName,
                    t.TempTotale,
                    i.FileIcona,
                    i.NumIconCLF,
                    i.TIconTaglio,
                    t.DataOraReg
                FROM 
                    {tabla_tempi} t
                LEFT JOIN 
                    {tabla_icone} i ON t.ID_CLF = i.ID_CLF
                ORDER BY 
                    t.DataOraReg DESC;
            """

            cursor.execute(query)
            columnas = [col[0] for col in cursor.description]
            filas = cursor.fetchall()

            resumen = []
            for fila in filas:
                fila_dict = dict(zip(columnas, fila))
                fila_dict = agregar_costos(fila_dict, potencia_kw, precio_kwh)
                resumen.append(fila_dict)

            conn.close()
            return jsonify({"success": True, "resumen": resumen})

    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return jsonify({"success": False, "error": str(e)})



def agregar_costos(fila, potencia, precio_kwh):
    try:
        tiempo_est = fila.get("TIconTaglio", 0) or 0
        if isinstance(tiempo_est, str):
            tiempo_est = float(tiempo_est.replace(",", "."))  # Soporta coma decimal
        consumo_kwh = (tiempo_est / 3600) * float(potencia)
        costo = consumo_kwh * float(precio_kwh)
        fila["Consumo_kWh"] = round(consumo_kwh, 2)
        fila["Costo_Euro"] = round(costo, 2)
    except Exception as e:
        print(f"[ERROR cálculo consumo] {e}")
        fila["Consumo_kWh"] = 0
        fila["Costo_Euro"] = 0
    return fila














# Ruta para ver los trabajos con coste calculado
# Esta ruta recibe un JSON con los filtros y devuelve los trabajos con coste calculado
# Ejemplo de JSON esperado:
# {
#     "clfile": "nombre_clfile",
#     "precioKwh": 0.20,  # Precio por kWh, por defecto 0.20
#     "potencia": 8,  # Potencia de la máquina, por defecto 8kW
#     "nombre_maquina": "nombre     de la máquina",
#     "ip": "           
@maquinas.route('/maquinas_sql_cost/', methods=['POST'])
def listar_maquina_sql_filtrado_cost():
    try:
        data = request.get_json()
        filtro_clfile = data.get("clfile", "")
        precioKwh = data.get("precioKwh")
        potencia = data.get("potencia")
        database = data.get("nombre_maquina", "")
        ip = data.get("ip", "")
        port = data.get("port", "")
        user = data.get("user", "")
        password = data.get("password", "")
        with get_db_session() as session:
            # ✅ Buscar máquina y obtener tabla desde nombreTabla
            maquinas = session.query(Maquina).filter_by(nombre=database).all()
            if not maquinas:
                return jsonify(success=False, error="Máquina no encontrada")

            try:
                nombre_tabla_dict = json.loads(maquinas[0].nombreTabla)
                tablas = nombre_tabla_dict.get("tablas", [])
                if not tablas:
                    return jsonify(success=False, error="No hay tablas configuradas.")
                tabla_tempi = tablas[0]
            except Exception as e:
                return jsonify(success=False, error=f"Error al procesar nombreTabla: {str(e)}")

            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={ip},{port};"
                f"DATABASE=CNC_DATA;"
                f"UID={user};"
                f"PWD={password};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )
            cursor = conn.cursor()

            campos = "ID_CLF, CLFileName, CodMacchina, DataOraReg, TempTotale"

            # ✅ Ejecutar consulta sobre tabla dinámica
            if filtro_clfile != "":
                cursor.execute(
                    f"SELECT TOP 500 {campos} FROM {tabla_tempi} WHERE CLFileName LIKE ? ORDER BY DataOraReg DESC",
                    f"%{filtro_clfile}%"
                )
            else:
                cursor.execute(
                    f"SELECT TOP 500 {campos} FROM {tabla_tempi} ORDER BY DataOraReg DESC"
                )

            columnas = [col[0] for col in cursor.description]
            filas = cursor.fetchall()

            columnas_finales = ["ID_CLF", "CLFileName", "CodMacchina", "DataOraReg", "TempTotale", "Consumo_kWh", "Costo_Euro"]
            trabajos = []

            for fila in filas:
                fila_dict = dict(zip(columnas, fila))
                fila_dict = calculo_consumo_por_trabajo(fila_dict, precioKwh, potencia)
                resultado = {k: fila_dict.get(k) for k in columnas_finales}
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

  

