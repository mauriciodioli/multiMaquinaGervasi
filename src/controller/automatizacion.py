from flask import Blueprint, render_template, request, redirect, url_for,jsonify
import os
import shutil
import pyodbc
from dotenv import load_dotenv
from src.model.maquina import Maquina
from utils.db import db
from datetime import datetime
import json
import subprocess


# Cargar variables de entorno
load_dotenv()

automatizacion = Blueprint('automatizacion', __name__)


# Cargar rutas desde .env
origen_raw = os.getenv('ORIGEN_PATH')
destino_raw = os.getenv('DESTINO_PATH')

# Normalizar las rutas
origen = os.path.normpath(origen_raw)
destino = os.path.normpath(destino_raw)


# Copiar la carpeta del origen al destino con python desde el contenedor
# Correr el script.sh en la carpeta destino para crear la base de datos de access a sqlserver
# Conexión a la base de datos
# Actualizar a la base de datos con los nuevos datos
# Devolver un mensaje de éxito o error


@automatizacion.route('/copiar_origen_destino/', methods=['POST'])
def automatizacion_index():
    try:
        nombre_maquina = request.form.get('nombre_maquina')
        id_maquina = request.form.get('id')

        maquina = db.session.query(Maquina).filter_by(id=int(id_maquina)).first()

        if not maquina:
            mensaje = "❌ Error: Máquina no encontrada"
            return render_template('automatizacion/automatizacion.html', mensaje=mensaje)

        origen = os.path.join("/mnt/origen", maquina.nombreDb + '.mbd')
        destino = '/mnt/destino'

        print(f"Copiando desde: {origen}")
        print(f"Destino: {destino}")

      

        

        return render_template('automatizacion/automatizacion.html', mensaje=mensaje)

    except Exception as e:
        mensaje = f"❌ Error conectando o copiando: {e}"
        return render_template('automatizacion/automatizacion.html', mensaje=mensaje)




def copiar_carpeta(origen, destino):
    try:
        if not os.path.exists(origen):
            print(f"❌ Error: El origen '{origen}' no existe.")
            return

        if not os.path.exists(destino):
            os.makedirs(destino)

        nombre_archivo = os.path.basename(origen)
        destino_final = os.path.join(destino, nombre_archivo)

        # Si ya existe el archivo destino, lo sobrescribimos
        if os.path.exists(destino_final):
            os.remove(destino_final)

        shutil.copy2(origen, destino_final)  # copiar archivo individual (.mdb)

        print(f"✅ Archivo copiado correctamente a '{destino_final}'.")

    except Exception as e:
        print(f"❌ Error copiando la carpeta: {e}")



def tamaño_carpeta(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

def copiar_carpeta_segura(origen, destino, limite_maximo_gb=2):
    try:
        tamaño_origen = tamaño_carpeta(origen)
        tamaño_origen_gb = tamaño_origen / (1024 ** 3)

        print(f"Tamaño de la carpeta origen: {tamaño_origen_gb:.2f} GB")

        if tamaño_origen_gb > limite_maximo_gb:
            error_msg = f"❌ Error: La carpeta pesa {tamaño_origen_gb:.2f} GB, supera el límite de {limite_maximo_gb} GB."
            print(error_msg)
            return False, error_msg

        # Copia si pasa el control
        copiar_carpeta(origen, destino)

        success_msg = f"✅ Carpeta copiada exitosamente ({tamaño_origen_gb:.2f} GB)"
        print(success_msg)
        return True, success_msg

    except Exception as e:
        error_msg = f"❌ Error copiando la carpeta: {e}"
        print(error_msg)
        return False, error_msg


