from flask import Flask, request, render_template, redirect 
from flask_mail import Mail
from flask_cors import CORS
from config.config import Config
from utils.db import db
from src.model.usuario import Usuario

# Blueprints
from src.controller.trabajo_controller import trabajos_bp
from src.controller.maquinas import maquinas
from src.controller.automatizacion import automatizacion
from src.controller.crud_maquinas import crud_maquinas
from src.controller.autoDensidad.densidadFuller import densidadFuller
from src.controller.autoDensidad.calcularMezclaOptima import calcularMezclaOptima
from src.controller.autoDensidad.optimizar_fuller import optimizar_fuller
from src.controller.autoDensidad.simuladorDosificacion.simulador_dosificacion import simulador_dosificacion
from src.controller.autoDensidad.analisis_densidad import analisis_densidad
from src.controller.mixFamiliari.crud_agregado import crud_agregado
from src.controller.mixFamiliari.crud_mallas import crud_mallas
from src.controller.mixFamiliari.crud_componente_quimico import crud_componente_quimico
from src.controller.mixFamiliari.crud_tipo_mezcla import crud_tipo_mezcla
from src.controller.administracion.crud_usuario import crud_usuario
from src.controller.administracion.crud_entidad import crud_entidad
from src.controller.autenticacion.login import login
from src.utils.conexion_db_crud import conexion_db_crud
from src.utils.extensions import mail

# Instancias globales
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Config principal
    app.config.from_object(Config)

    # Config adicional para Mail si no lo tenés en config.py
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME='mauriciodioli@gmail.com',       # 👈 reemplazar
        MAIL_PASSWORD='tfgs apgz qini xcwv',    # 👈 reemplazar
        MAIL_DEFAULT_SENDER='Gervasi <mauriciodioli@gmail.com>'
    )

    # Inicializaciones
    db.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Registro de blueprints
    app.register_blueprint(crud_usuario)
    app.register_blueprint(crud_entidad)
    app.register_blueprint(login)
    
    
    app.register_blueprint(trabajos_bp)
    app.register_blueprint(maquinas)
    app.register_blueprint(automatizacion)
    app.register_blueprint(crud_maquinas)
    
    app.register_blueprint(densidadFuller)
    app.register_blueprint(conexion_db_crud)
    app.register_blueprint(calcularMezclaOptima)
    app.register_blueprint(optimizar_fuller)
    app.register_blueprint(simulador_dosificacion)
    app.register_blueprint(analisis_densidad)
    app.register_blueprint(crud_agregado)
    app.register_blueprint(crud_mallas)
    app.register_blueprint(crud_componente_quimico)
    app.register_blueprint(crud_tipo_mezcla)
    @app.context_processor
    def inject_user():
        try:
            user_id = request.cookies.get("user_id")
            usuario = db.session.get(Usuario, int(user_id)) if user_id else None
            return dict(usuario=usuario)
        finally:
            db.session.close()

    # Ruta raíz
    @app.route('/')
    def index():
        user_id = request.cookies.get("user_id")
        if not user_id:
            return render_template("AutenticacionLogin/login.html")

        try:
            user = db.session.get(Usuario, int(user_id))
            if not user:
                return render_template("AutenticacionLogin/login.html")
            
           
            if user.roll == "admin":
                return redirect("/listar_maquinas/")
            else:
                
                if not user.entidades or len(user.entidades) == 0:
                    return redirect("/administracion_crud_usuario_seleccionar_entidad/")

                return redirect("/pantalla_densidad_fuller_multiple/")
        except Exception:
            return render_template("login.html")

    return app
