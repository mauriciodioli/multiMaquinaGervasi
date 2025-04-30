import pyodbc
from flask import Blueprint, render_template

maquinas = Blueprint('maquinas', __name__)

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

