# app.py
from src import create_app
from utils.db import db
import pyodbc

# Función para crear la base de datos si no existe
def crear_base_si_no_existe():
    try:
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=host.docker.internal\SQLEXPRESS;'
            r'DATABASE=master;'
            r'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()

        nombre_bd = "multiMaquinas"

        # Verificar si existe
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{nombre_bd}'")
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(f"CREATE DATABASE {nombre_bd}")
            conn.commit()
            print(f"✅ Base de datos '{nombre_bd}' creada exitosamente.")
        else:
            print(f"ℹ️ La base de datos '{nombre_bd}' ya existe.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error creando/verificando la base de datos: {e}")

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    crear_base_si_no_existe()  # Primero crea/verifica la base
    app = create_app()         # Luego crea la app
    app.run(host="0.0.0.0", port=5000, debug=True)  # Finalmente levanta el servidor
