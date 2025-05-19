# app.py
from src import create_app
from utils.db import db
import os
import logging
from sqlalchemy import text  # Importar text de SQLAlchemy

# Configuración de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("📌 Inicio app.py")

app = create_app()
def verificar_conexion_db():
    try:
        # Intentar realizar una consulta de prueba para verificar la conexión
        with app.app_context():
              db.session.execute(text('SELECT 1'))  # Consulta con text() para SQLAlchemy
        logger.info("✅ Conexión a la base de datos exitosa.")
    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {str(e)}")
        # Si hay un error, detiene el arranque de la aplicación
        raise SystemExit("⚠️ No se pudo conectar a la base de datos. El servidor no se iniciará.")

# Verificar la conexión a la base de datos
verificar_conexion_db()
print("✅ app creada")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print("🧠 Contexto activo, creando tablas...")
        with app.app_context():
            db.create_all()
        print("✅ Tablas listas")

    print("🚀 Ejecutando app...")
    app.run(host="0.0.0.0", port=5000, debug=True)

