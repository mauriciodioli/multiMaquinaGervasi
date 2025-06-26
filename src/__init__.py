from flask import Flask, request, render_template, redirect, flash
from flask_mail import Mail
from flask_cors import CORS
from werkzeug.exceptions import ServiceUnavailable          # 503 HTTP
from sqlalchemy.exc import OperationalError
from config.config import Config
from utils.db import db
from src.model.usuario import Usuario

# ── Blueprints ─────────────────────────────────────────────
from src.controller.trabajo_controller import trabajos_bp
from src.controller.maquinas import maquinas
from src.controller.automatizacion import automatizacion
from src.controller.crud_maquinas import crud_maquinas
from src.controller.autoDensidad.densidadFuller import densidadFuller
from src.controller.autoDensidad.calcularMezclaOptima import calcularMezclaOptima
from src.controller.autoDensidad.optimizar_fuller import optimizar_fuller
from src.controller.autoDensidad.simuladorDosificacion.simulador_dosificacion \
import simulador_dosificacion
from src.controller.autoDensidad.analisis_densidad import analisis_densidad
from src.controller.autoDensidad.perfil_user_bp import perfil_user_bp
from src.controller.mixFamiliari.crud_agregado import crud_agregado
from src.controller.mixFamiliari.crud_mallas import crud_mallas
from src.controller.mixFamiliari.crud_componente_quimico import crud_componente_quimico
from src.controller.mixFamiliari.crud_tipo_mezcla import crud_tipo_mezcla
from src.controller.mixFamiliari.crud_materia_forma import crud_materia_forma
from src.controller.administracion.crud_usuario import crud_usuario
from src.controller.administracion.crud_entidad import crud_entidad
from src.controller.autenticacion.login import login
from src.utils.conexion_db_crud import conexion_db_crud

mail = Mail()

# ───────────────────────────────────────────────────────────
def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    # ── Mail ── (usa variables de entorno en prod)
    app.config.setdefault("MAIL_SERVER", "smtp.gmail.com")
    app.config.setdefault("MAIL_PORT", 587)
    app.config.setdefault("MAIL_USE_TLS", True)
    app.config.setdefault("MAIL_USERNAME", "mauriciodioli@gmail.com")
    app.config.setdefault("MAIL_PASSWORD", "tfgs apgz qini xcwv")
    app.config.setdefault("MAIL_DEFAULT_SENDER", "Gervasi <mauriciodioli@gmail.com>")

    # ── SQLAlchemy extra ──
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {
            "pool_pre_ping": True,   # verifica la conexión antes de usarla
            "pool_recycle": 1800,    # recicla cada 30 min
        },
    )

    # ── Extensiones ──
    db.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"*": {"origins": "*"}})

    # ── Blueprints ──
    for bp in (
        crud_usuario, 
        crud_entidad, 
        login,
        trabajos_bp, 
        maquinas, 
        automatizacion, 
        crud_maquinas, 
        perfil_user_bp,
        densidadFuller, 
        conexion_db_crud, 
        calcularMezclaOptima, 
        optimizar_fuller,
        simulador_dosificacion, 
        analisis_densidad,
        crud_agregado, 
        crud_mallas, 
        crud_componente_quimico, 
        crud_tipo_mezcla,
        crud_materia_forma,
    ):
        app.register_blueprint(bp)

    # ── Context processor (usuario en plantillas) ──
    @app.context_processor
    def inject_user():
        user_id = request.cookies.get("user_id")
        usuario = None
        if user_id:
            try:
                usuario = db.session.get(Usuario, int(user_id))
            except OperationalError:
                db.session.rollback()
        return dict(usuario=usuario)

    # ── Error 503 genérico ──
    @app.errorhandler(ServiceUnavailable)
    def maintenance_page(e):
        return render_template("503.html"), 503

    # ── Ruta raíz ──
    @app.route("/")
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

            if not user.entidades:
                return redirect("/administracion_crud_usuario_seleccionar_entidad/")

            return redirect("/pantalla_densidad_fuller_multiple/")

        except OperationalError as err:
            db.session.rollback()
            app.logger.error("DB down → %s", err)
            flash("Servidor de datos fuera de servicio. Intenta más tarde.", "error")
            raise ServiceUnavailable()

    return app
