import pyodbc
from flask import Blueprint, render_template

trabajos_bp = Blueprint('trabajos', __name__)

# Ruta para ver los trabajos
@trabajos_bp.route('/trabajos')
def listar_trabajos():
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Lamiere_Tempi')  # O la tabla que tengas
        trabajos = cursor.fetchall()
        columnas = [column[0] for column in cursor.description]
        conn.close()
        return render_template('trabajos.html', trabajos=trabajos, columnas=columnas)
    except Exception as e:
        return f"Error conectando a la base de datos: {e}"

@trabajos_bp.route('/')
def listar_maquinas():
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Lamiere_Tempi')  # O la tabla que tengas
        trabajos = cursor.fetchall()
        columnas = [column[0] for column in cursor.description]
        conn.close()
        return render_template('maquinas/maquinas.html', trabajos=trabajos, columnas=columnas)
    except Exception as e:
        return f"Error conectando a la base de datos: {e}"
    