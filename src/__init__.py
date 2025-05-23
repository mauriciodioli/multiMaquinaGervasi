from flask import Flask
from flask_cors import CORS
from config.config import Config
from src.controller.trabajo_controller import trabajos_bp
from src.controller.maquinas import maquinas
from src.controller.automatizacion import automatizacion
from src.controller.crud_maquinas import crud_maquinas
from src.controller.autoDensidad.densidadFuller import densidadFuller
from src.controller.autoDensidad.calcularMezclaOptima import calcularMezclaOptima
from src.utils.conexion_db_crud import conexion_db_crud



 # from src.controller.crud_usuarios import crud_usuarios
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
    app.register_blueprint(crud_maquinas)
    app.register_blueprint(densidadFuller)
    app.register_blueprint(conexion_db_crud)  # Puedes ajustar la URL base
    app.register_blueprint(calcularMezclaOptima)

    return app

