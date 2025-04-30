from flask import Flask
from flask_cors import CORS
from config.config import Config
from src.controller.trabajo_controller import trabajos_bp
from src.controller.maquinas import maquinas
from src.controller.automatizacion import automatizacion
from src.model import Usuario, Maquina
from utils.db import db

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)  # ✅ Primero la config
    db.init_app(app)                # ✅ Luego inicializás la DB con esa config
    CORS(app)

    app.register_blueprint(trabajos_bp)
    app.register_blueprint(maquinas)
    app.register_blueprint(automatizacion)

    return app

