from flask import Flask
from flask_cors import CORS
from config.config import Config
from src.controller.trabajo_controller import trabajos_bp
from src.controller.maquinas import maquinas
from src.controller.automatizacion import automatizacion
from src.controller.crud_maquinas import crud_maquinas
from src.controller.autoDensidad.densidadFuller import densidadFuller
from src.controller.autoDensidad.calcularMezclaOptima import calcularMezclaOptima
from src.controller.autoDensidad.optimizar_fuller import optimizar_fuller
from src.controller.autoDensidad.simuladorDosificacion.simulador_dosificacion import simulador_dosificacion
from src.controller.autoDensidad.analisis_densidad import analisis_densidad
from src.controller.mixFamiliari.mix_familiari import mix_familiari
from src.controller.mixFamiliari.categoria_bp import categoria_bp
from src.controller.mixFamiliari.componente_bp import componente_bp
from src.controller.mixFamiliari.tipo_bp import tipo_bp



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
    app.register_blueprint(optimizar_fuller)
    app.register_blueprint(simulador_dosificacion)
    app.register_blueprint(analisis_densidad)
    
    
    app.register_blueprint(mix_familiari)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(componente_bp)
    app.register_blueprint(tipo_bp)
    

    return app

