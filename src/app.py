# app.py
from src import create_app
from utils.db import db
import os

print("📌 Inicio app.py")

app = create_app()
print("✅ app creada")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print("🧠 Contexto activo, creando tablas...")
        with app.app_context():
            db.create_all()
        print("✅ Tablas listas")

    print("🚀 Ejecutando app...")
    app.run(host="0.0.0.0", port=5000, debug=True)

