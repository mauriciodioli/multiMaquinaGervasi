from flask import Blueprint, request, jsonify, render_template,make_response, redirect

from src.model.entidad_contexto import EntidadContexto, EntidadContextoSchema
from src.model.mixFamiliari.usuario_entidad import UsuarioEntidad
from src.model.sesionUsuario import SesionUsuario

from src.model.mixFamiliari.agregado import Agregado
from src.model.mixFamiliari.analisis_granulometrico import AnalisisGranulometrico
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError
from src.model.usuario import Usuario  # ajustá si tenés otro path

import secrets  # para token seguro
from datetime import timedelta
from src.utils.get_textos_menu  import get_textos_menu

crud_usuario = Blueprint("crud_usuario", __name__)



# 👉 Ruta para mostrar la pantalla con usuarios existentes
@crud_usuario.route('/administracion_crud_usuario_pantalla_usuario/', methods=['GET'])
def administracion_crud_usuario_pantalla_usuario():
    try:
        resultados = (
            db.session.query(Usuario, UsuarioEntidad, EntidadContexto)
            .outerjoin(UsuarioEntidad, Usuario.id == UsuarioEntidad.usuario_id)
            .outerjoin(EntidadContexto, EntidadContexto.id == UsuarioEntidad.entidad_id)
            .all()
        )

        usuarios_dict = {}
        for usuario, relacion, entidad in resultados:
            if usuario.id not in usuarios_dict:
                usuarios_dict[usuario.id] = {
                    "id": usuario.id,
                    "correo_electronico": usuario.correo_electronico,
                    "roll": usuario.roll,
                    "activo": usuario.activo,
                    "entidades": []
                }

            if entidad:
                usuarios_dict[usuario.id]["entidades"].append({
                    "id": entidad.id,
                    "nombre": entidad.nombre,
                    "tipo": entidad.tipo,
                    "roll": relacion.roll if relacion else None
                })
        lang = request.cookies.get("lang", "es")
        t_menu = get_textos_menu(lang)
        return render_template("pantalla_usuarios/pantalla_crud_usuarios.html", usuarios=list(usuarios_dict.values()), t_menu=t_menu)
    except Exception as e:
        return f"Error al cargar usuarios: {str(e)}", 500
    finally:
        db.session.close()


@crud_usuario.route('/administracion_crud_usuario_crear_usuario/', methods=['POST'])
def administracion_crud_usuario_crear_usuario():
    data = request.get_json()
    try:
        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(64)

        nuevo = Usuario(
            correo_electronico=data.get('correo_electronico'),
            password=data.get('password').encode('utf-8'),
            roll=data.get('roll', 'regular'),
            token=token,
            refresh_token=refresh_token,
            calendly_url='',
            activo=bool(int(data.get('activo', 1)))
        )

        db.session.add(nuevo)
        db.session.commit()

        response = make_response(jsonify(success=True, usuario={
            "id": nuevo.id,
            "correo_electronico": nuevo.correo_electronico,
            "roll": nuevo.roll,
            "activo": nuevo.activo
        }))
        response.set_cookie("token", token, httponly=True, max_age=3600)
        response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=3600 * 24 * 7)

        return response
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 400
    finally:
        db.session.close()


@crud_usuario.route('/asignar_entidad_usuario/', methods=['POST'])
def asignar_entidad_usuario():
    try:
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        entidad_id = data.get('entidad_id')

        if not usuario_id or not entidad_id:
            return jsonify(success=False, error="Faltan datos")

        existe = db.session.query(UsuarioEntidad).filter_by(
            usuario_id=usuario_id,
            entidad_id=entidad_id
        ).first()

        if existe:
            return jsonify(success=False, error="Ya existe esa asignación")

        nueva_relacion = UsuarioEntidad(
            usuario_id=usuario_id,
            entidad_id=entidad_id,
            roll='visualizador'
        )

        db.session.add(nueva_relacion)
        db.session.commit()

        entidad = db.session.query(EntidadContexto).get(entidad_id)
        return jsonify(success=True, entidad={"nombre": entidad.nombre, "tipo": entidad.tipo})
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    finally:
        db.session.close()


@crud_usuario.route('/administracion_crud_usuario_eliminar_usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = db.session.get(Usuario, id)
        if not usuario:
            return jsonify(success=False, error="Usuario no encontrado"), 404

        # Borrar sesiones asociadas
        db.session.query(SesionUsuario).filter_by(usuario_id=usuario.id).delete()

        # Ahora sí, eliminar usuario
        db.session.delete(usuario)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500
    finally:
        db.session.close()



@crud_usuario.route('/administracion_crud_usuario_modificar_usuario/<int:id>', methods=['PUT'])
def modificar_usuario(id):
    try:
        data = request.get_json()
        usuario = db.session.get(Usuario, id)

        if not usuario:
            return jsonify(success=False, error="Usuario no encontrado")

        usuario.correo_electronico = data.get('correo_electronico', usuario.correo_electronico)
        usuario.roll = data.get('roll', usuario.roll)
        usuario.activo = bool(int(data.get('activo', usuario.activo)))

        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    finally:
        db.session.close()



@crud_usuario.route("/administracion_crud_usuario_seleccionar_entidad/", methods=["GET", "POST"])
def seleccionar_entidad():
    usuario_id = request.cookies.get("user_id")
    if not usuario_id:
        return redirect("/login")

    try:
        usuario = db.session.query(Usuario).filter_by(id=int(usuario_id)).first()
    except (ValueError, TypeError):
        return redirect("/login")

    if not usuario:
        return redirect("/login")

    if request.method == "POST":
        entidad_id = request.form.get("entidad_id")
        entidad = db.session.query(EntidadContexto).filter_by(id=entidad_id).first()

        if not entidad:
            return "Entidad no encontrada", 404

        relacion_existente = db.session.query(UsuarioEntidad).filter_by(
            usuario_id=usuario.id,
            entidad_id=entidad.id
        ).first()

        if not relacion_existente:
            nueva_relacion = UsuarioEntidad(
                usuario_id=usuario.id,
                entidad_id=entidad.id,
                roll='visualizador'
            )
            db.session.add(nueva_relacion)
            db.session.commit()

        return redirect("/pantalla_densidad_fuller_multiple/")

    pais_cookie = request.cookies.get("pais")
    entidades_disponibles = db.session.query(EntidadContexto).filter_by(pais=pais_cookie).all()
    language = request.cookies.get("language", "es")  # 'es' por defecto

    return render_template(
            "AutenticacionLogin/seleccionar_entidad.html",
            usuario=usuario,
            entidades=entidades_disponibles,
            language=language
        )





@crud_usuario.route('/perfil_usuario/')
def perfil_usuario():
    lang = request.cookies.get("lang", "es")
    t_menu = get_textos_menu(lang)
    
    user_id = request.cookies.get("user_id")
    pais = request.cookies.get("pais", "—")  # 👈 Por defecto guion si no viene
    
    usuario = db.session.query(Usuario).filter_by(id=user_id).first()

    entidades = (
        db.session.query(EntidadContexto, UsuarioEntidad)
        .join(UsuarioEntidad, EntidadContexto.id == UsuarioEntidad.entidad_id)
        .filter(UsuarioEntidad.usuario_id == user_id)
        .all()
    )

    agregados = Agregado.query.filter_by(usuario_id=user_id).all()
    
    analisis = (
        AnalisisGranulometrico.query
        .filter_by(usuario_id=user_id)
        .order_by(AnalisisGranulometrico.fecha.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'pantalla_usuarios/perfil_usuario.html',
        usuario=usuario,
        entidades=entidades,
        agregados=agregados,
        analisis=analisis,
        t_menu=t_menu,
        pais=pais,  # 👈 lo pasás al HTML
        lang=lang  # 👈 lo pasás al HTML
    )


