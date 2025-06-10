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
from controller.mixFamiliari.crud_agregado import crud_agregado
from src.controller.mixFamiliari.crud_mallas import crud_mallas
from src.controller.mixFamiliari.crud_componente_quimico import crud_componente_quimico
from src.controller.mixFamiliari.crud_tipo_mezcla import crud_tipo_mezcla

from src.controller.administracion.crud_usuario import crud_usuario
from src.controller.administracion.crud_entidad import crud_entidad

from src.utils.conexion_db_crud import conexion_db_crud





from utils.db import db

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)  # ✅ Primero la config
    db.init_app(app)                # ✅ Luego inicializás la DB con esa config
    CORS(app)
    app.register_blueprint(crud_usuario)
    app.register_blueprint(crud_entidad)

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
        
    
    app.register_blueprint(crud_agregado)
    app.register_blueprint(crud_mallas)
    
    app.register_blueprint(crud_componente_quimico)
    app.register_blueprint(crud_tipo_mezcla)
    
    

    return app

