from flask import Flask, request, jsonify
import os
import sys
import shutil
import atexit
import datetime

from migrar_access_a_sqlserver import migrar_tabla


# === REDIRECCIÓN DE LOGS DESDE PYTHONW.EXE (SIN CONSOLA) ===
BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
ESTADO_DIR = os.path.join(BASE_DIR, "estado")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ESTADO_DIR, exist_ok=True)

fecha = datetime.date.today().isoformat()
log_path = os.path.join(LOG_DIR, f"flask_log_{fecha}.txt")

sys.stdout = open(log_path, "a", encoding="utf-8")
sys.stderr = sys.stdout
# === FIN DE CONFIGURACIÓN DE LOG ===

app = Flask(__name__)

# Parámetros para migrar
tabla = "Lamiere_Tempi"  # o la que corresponda
# sql_database = "si_cam_db"


ESTADO_PATH = os.path.join(os.path.dirname(__file__), "estado", "estado.txt")

def marcar_estado_apagado():
    try:
        with open(ESTADO_PATH, "w") as f:
            f.write("apagado")
        print("[OFF] Estado: apagado")
    except Exception as e:
        print(f"[ERROR] No se pudo escribir estado apagado: {e}")

# Se ejecuta al cerrar el servidor
atexit.register(marcar_estado_apagado)

@app.route('/copiar_origen_destino/', methods=['POST'])
def copiar_archivo():
    try:
        nombre_archivo = request.form.get('nombre_archivo')
        origen_base = request.form.get('origen')
        destino_base = request.form.get('destino')
        estado = request.form.get('estado')
        ip = request.form.get('ip')
        port = request.form.get('port')
        userSqlServer = request.form.get('userSqlServer')
        passwordSqlServer = request.form.get('passwordSqlServer') 
        sql_database = request.form.get('nombreMaquina')

        print(f"[INFO] Datos recibidos - nombre_archivo: {nombre_archivo}, origen: {origen_base}, destino: {destino_base}, estado: {estado}")
        
        if not estado or estado.strip().lower() != 'activo':
            print("[ERROR] Maquina inactiva")
            return jsonify({"error": "Maquina inactiva"}), 400

        if not all([nombre_archivo, origen_base, destino_base]):
            print("[ERROR] Faltan datos en la solicitud")
            return jsonify({"error": "Faltan datos"}), 400

        origen = os.path.normpath(os.path.join(origen_base, f"{nombre_archivo}.mdb"))
        destino_dir = os.path.normpath(destino_base)
        destino = os.path.normpath(os.path.join(destino_dir, f"{nombre_archivo}.mdb"))

        print(f"[CHECK] Verificando existencia de archivo en: {origen}")
        print("-> Existe:", os.path.exists(origen))
        print("-> Es archivo:", os.path.isfile(origen))

        if not os.path.isfile(origen):
            print(f"[WARN] No se encontró el archivo origen. Puede que la máquina esté apagada: {origen}")
            return jsonify({"mensaje": " La máquina origen podría estar apagada. No se realizó la copia."}), 200


        print(f"[COPY] Copiando desde: {origen}")
        print(f"[COPY] Hacia: {destino}")

        os.makedirs(destino_dir, exist_ok=True)
        shutil.copy(origen, destino)

        print(f"[OK] Archivo copiado correctamente a: {destino}")
        
        
        
        try:
           migrar_tabla(destino, tabla, sql_database, userSqlServer, passwordSqlServer,ip,port)
           print(f"[CLEANUP] Eliminando archivo temporal: {destino}")
           os.remove(destino)  # ✅ Eliminar solo si migración fue exitosa
        except Exception as e:
            print(f"[ERROR MIGRACIÓN] {str(e)}")
        return jsonify({"mensaje": f"Archivo copiado a {destino}"}), 200

    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")
        marcar_estado_apagado()
        return jsonify({"error": f"Excepción: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=False)
