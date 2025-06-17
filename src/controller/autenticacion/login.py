from flask import Blueprint, request, jsonify, make_response, redirect, render_template, url_for, current_app,has_app_context
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from src.model.usuario import Usuario
from src.model.sesionUsuario import SesionUsuario
from utils.db import db
import secrets
import re
from itsdangerous import URLSafeTimedSerializer
import os
from src.utils.extensions import mail
from src.utils.auth import current_user

from src.utils.get_textos_menu  import get_textos_menu,get_textos_login



login = Blueprint("login", __name__)




MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")



textos_login = {
    "es": {
        "no_encontrado": "Usuario no encontrado",
        "inactivo": "Usuario inactivo",
        "incorrecta": "Contraseña incorrecta",
        "error": "Error interno del servidor"
    },
    "en": {
        "no_encontrado": "User not found",
        "inactivo": "User is inactive",
        "incorrecta": "Incorrect password",
        "error": "Internal server error"
    },
    "it": {
        "no_encontrado": "Utente non trovato",
        "inactivo": "Utente inattivo",
        "incorrecta": "Password errata",
        "error": "Errore interno del server"
    }
}







# ========== LOGIN ==========
@login.route('/login_usuario/', methods=['POST'])
def login_usuario():
    data = request.get_json()
    correo = data.get("correo_electronico")
    password = data.get("password")
    lang = data.get("lang", "es")
    t = textos_login.get(lang, textos_login["es"])

    try:
        usuario = db.session.query(Usuario).filter_by(correo_electronico=correo).first()

        if not usuario:
            return jsonify(success=False, error=t["no_encontrado"]), 404

        if not usuario.activo:
            return jsonify(success=False, error=t["inactivo"]), 403

        if not check_password_hash(usuario.password, password):
            return jsonify(success=False, error=t["incorrecta"]), 401

        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(64)
        usuario.token = token
        usuario.refresh_token = refresh_token
        db.session.commit()
        # ⬇️ Registramos la sesión
        registrar_sesion(usuario, token, request)
       

        # 🔍 Verificar si tiene entidades asignadas
        if not usuario.entidades or len(usuario.entidades) == 0:
            response = make_response(jsonify(
                success=True,
                redireccion="/administracion_crud_usuario_seleccionar_entidad/"
            ))
            
            response.set_cookie("token", token, httponly=True, samesite="Strict", secure=False, max_age=3600)
            response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Strict", secure=False, max_age=3600 * 24 * 7)
            response.set_cookie("user_id", str(usuario.id), max_age=3600 * 24 * 7)
            response.set_cookie("lang", lang, max_age=3600 * 24 * 7)
            return response

        # ✅ Si tiene entidades, redirige según el rol
        response = make_response(jsonify(
            success=True,
            roll=usuario.roll,
            redireccion="/listar_maquinas/" if usuario.roll == "admin" else "/pantalla_densidad_fuller_multiple/"
        ))
        response.set_cookie("token", token, httponly=True, samesite="Strict", secure=False, max_age=3600)
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Strict", secure=False, max_age=3600 * 24 * 7)
        response.set_cookie("user_id", str(usuario.id), max_age=3600 * 24 * 7)
        response.set_cookie("lang", lang, max_age=3600 * 24 * 7)
        return response

    except Exception as e:
        return jsonify(success=False, error=t["error"]), 500
    finally:
        db.session.close()


@login.route("/logout/")
def logout():
    response = redirect("/")
    response.delete_cookie("token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("user_id")
    return response




def registrar_sesion(usuario, token, request):
    ip = request.remote_addr
    agente = request.headers.get("User-Agent")
    pais =  request.cookies.get("pais", "Desconocido")
    entidad_id = usuario.entidades[0].entidad_id if usuario.entidades else None

    sesion = SesionUsuario(
        usuario_id=usuario.id,
        token=token,
        ip_origen=ip,
        user_agent=agente,
        pais=pais,
        entidad_id=entidad_id
    )
    db.session.add(sesion)
    db.session.commit()































# ========== REESTABLECIEMIENTO  + CONFIRMACIÓN  DE PASSWORD==========
def get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)


@login.route("/recuperar-password/", methods=["GET", "POST"])
def recuperar_password():
    lang = request.cookies.get("lang", "es")
    t = get_textos_login(lang)

    try:
        if request.method == "POST":
            correo = request.form.get("correo")
            usuario = db.session.query(Usuario).filter_by(correo_electronico=correo).first()

            if usuario:
                token = get_serializer().dumps(correo, salt="recuperar-password")
                link = url_for("login.restablecer_password", token=token, _external=True)
                if usuario:
                    token = get_serializer().dumps(correo, salt="recuperar-password")
                    link = url_for("login.restablecer_password", token=token, _external=True)

                    mensaje = Message(t["recuperar_asunto"], recipients=[correo])
                    mensaje.html = f"""
                        <h3>{t['saludo']}</h3>
                        <p>{t['recuperacion']}</p>
                        <p><a href="{link}">{link}</a></p>
                        <p>{t['firma']} <a href="{url_for('index', _external=True)}">Gervasi</a>.</p>
                    """

                    mail.send(mensaje)

            return render_template("AutenticacionLogin/recuperar_enviado.html", t=t)

        return render_template("AutenticacionLogin/recuperar_form.html", t=t)

    finally:
        db.session.close()
        
        
        
        
        
@login.route("/restablecer-password/<token>", methods=["GET", "POST"])
def restablecer_password(token):
    lang = request.cookies.get("lang", "es")
    t = get_textos_login(lang)  # ✅ Carga textos por idioma

    serializer = get_serializer()  # ✅ Serializador activo con secret_key

    try:
        correo = serializer.loads(token, salt="recuperar-password", max_age=3600)
    except Exception:
        return render_template("AutenticacionLogin/token_invalido.html", t=t)

    try:
        if request.method == "POST":
            nueva = request.form.get("nueva")
            confirmar = request.form.get("confirmar")

            if nueva != confirmar or len(nueva) < 8:
                return render_template("AutenticacionLogin/restablecer_form.html", t=t, error=t["error_confirmacion"])

            usuario = db.session.query(Usuario).filter_by(correo_electronico=correo).first()
            if usuario:
                usuario.password = generate_password_hash(nueva)
                db.session.commit()
                return render_template("AutenticacionLogin/restablecer_ok.html", t=t)
            else:
                return render_template("AutenticacionLogin/token_invalido.html", t=t)

        # Formulario inicial de restablecimiento
        return render_template("AutenticacionLogin/restablecer_form.html", t=t, token=token)

    finally:
        db.session.close()























# ========== REGISTRO + CONFIRMACIÓN ==========
@login.route("/registrarse/")
def registrarse():
    return render_template('AutenticacionLogin/registrarse.html')

def generar_token_confirmacion(correo):
    try:
        secret_key = current_app.config['SECRET_KEY']
        s = URLSafeTimedSerializer(secret_key)
        return s.dumps(correo, salt='confirmacion-correo')
    except Exception as e:
        raise RuntimeError(f"No se pudo generar el token: {str(e)}")











@login.route("/api/registrar_usuario/", methods=["POST"])
def registrar_usuario():
        data = request.get_json()

        correo = data.get("correo_electronico", "").strip().lower()
        password = data.get("password")
        lang = data.get("lang", "es")  # 👈 si no viene, por defecto español

        if not correo or not password:
            return jsonify(success=False, error="Faltan datos")

        # 🛡️ Validación de la contraseña
        if len(password) < 8 \
        or not re.search(r"[A-Z]", password) \
        or not re.search(r"[0-9]", password) \
        or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return jsonify(success=False, error="La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un carácter especial.")

        
        
        # ✅ Validar formato de email
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_email, correo):
            return jsonify(success=False, error="El correo electrónico no tiene un formato válido.")
        
        
        if db.session.query(Usuario).filter_by(correo_electronico=correo).first():
            return jsonify(success=False, error="Ya existe un usuario con ese correo")

        try:
            token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(64)

            nuevo = Usuario(
                correo_electronico=correo,
                password=generate_password_hash(password),
                roll='regular',
                token=token,
                refresh_token=refresh_token,
                calendly_url='',
                activo=False
            )

            db.session.add(nuevo)
            db.session.commit()
            print("¿Tengo contexto de app?", has_app_context())
            # Enviar email de confirmación
            token_conf = generar_token_confirmacion(correo)
            link_confirmacion = url_for("login.confirmar_correo", token=token_conf, _external=True)
            
            
            
            t = obtener_textos_confirmacion(lang)

            print(f"Enviando correo de confirmación a: {correo}")


            mensaje = Message(t["asunto"], recipients=[correo])
            mensaje.html = f"""
                            <h3>{t['saludo']}</h3>
                            <p>{t['registro']}</p>
                            <p>{t['confirma']}</p>
                            <p><a href="{link_confirmacion}">{link_confirmacion}</a></p>
                            <p>{t['accion']} <a href="{url_for('index', _external=True)}">Gervasi</a>.</p>
                        """

            mail.send(mensaje)

            response = make_response(jsonify(success=True))

            response.set_cookie("token", token, httponly=True, max_age=3600)
            response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=3600 * 24 * 7)

            return response

        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=f"No se pudo completar el registro: {str(e)}"), 500

        finally:
            db.session.close()


@login.route("/confirmar/<token>")
def confirmar_correo(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        correo = s.loads(token, salt='confirmacion-correo', max_age=3600)

        usuario = db.session.query(Usuario).filter_by(correo_electronico=correo).first()
        if not usuario:
            return "Usuario no encontrado", 404

        if not usuario.activo:
            usuario.activo = True
            db.session.commit()
            
        # ✅ Generar nueva sesión activa
        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(64)
        usuario.token = token
        usuario.refresh_token = refresh_token
        db.session.commit()

        registrar_sesion(usuario, token, request)
        lang = request.cookies.get("lang", "es")
        textos = get_textos_confirmacion(lang)

        response = make_response(render_template("AutenticacionLogin/confirmado.html", t=textos))
        response.set_cookie("token", token, httponly=True, samesite="Strict", secure=False, max_age=3600)
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Strict", secure=False, max_age=3600 * 24 * 7)
        response.set_cookie("user_id", str(usuario.id), max_age=3600 * 24 * 7)
        response.set_cookie("lang", lang, max_age=3600 * 24 * 7)

        return response

    except Exception:
        return "Token inválido o expirado", 400

    finally:
        db.session.close()












@login.route("/reenviar_confirmacion/", methods=["POST"])
def reenviar_confirmacion():
    data = request.get_json()
    correo = data.get("correo_electronico")

    usuario = db.session.query(Usuario).filter_by(correo_electronico=correo).first()

    if not usuario:
        return jsonify(success=False, error="Correo no registrado")

    if usuario.activo:
        return jsonify(success=False, error="La cuenta ya está activada")

    try:
        token_conf = generar_token_confirmacion(correo)
        link_confirmacion = url_for("login.confirmar_correo", token=token_conf, _external=True)

        mensaje = Message("📩 Reenvío de confirmación", recipients=[correo])
        mensaje.body = f"Hola, te reenviamos el enlace de confirmación:\n{link_confirmacion}"
        mail.send(mensaje)

        return jsonify(success=True, mensaje="Correo reenviado correctamente")
    except Exception as e:
        return jsonify(success=False, error=f"Error al reenviar correo: {str(e)}")







@login.route("/verifica_email/")
def verifica_email():
    return render_template("AutenticacionLogin/verifica_email.html")








def obtener_textos_confirmacion(lang):
    textos = {
        "es": {
            "asunto": "Confirma tu cuenta",
            "saludo": "Hola 👋",
            "registro": "Gracias por registrarte en Gervasi.",
            "confirma": "Confirmá tu cuenta haciendo clic en el siguiente enlace:",
            "accion": "Una vez confirmada, podés iniciar sesión en"
        },
        "en": {
            "asunto": "Confirm your account",
            "saludo": "Hi 👋",
            "registro": "Thanks for signing up with Gervasi.",
            "confirma": "Please confirm your account by clicking the link below:",
            "accion": "Once confirmed, you can log in at"
        },
        "it": {
            "asunto": "Conferma il tuo account",
            "saludo": "Ciao 👋",
            "registro": "Grazie per esserti registrato su Gervasi.",
            "confirma": "Conferma il tuo account cliccando sul seguente link:",
            "accion": "Una volta confermato, puoi accedere da"
        }
    }
    return textos.get(lang, textos["es"])







def get_textos_confirmacion(lang):
    textos = {
            "es": {
                "titulo": "Cuenta confirmada",
                "mensaje": "Tu cuenta ha sido activada con éxito.",
                "boton": "Ir al inicio",
                "redireccion": "Serás redirigido en"
            },
            "en": {
                "titulo": "Account confirmed",
                "mensaje": "Your account has been successfully activated.",
                "boton": "Go to homepage",
                "redireccion": "You will be redirected in"
            },
            "it": {
                "titulo": "Account confermato",
                "mensaje": "Il tuo account è stato attivato con successo.",
                "boton": "Vai alla home",
                "redireccion": "Verrai reindirizzato tra"
            }
        }
    return textos.get(lang, textos["es"])



