from flask import Blueprint, request, jsonify, render_template,make_response

from src.model.entidad_contexto import EntidadContexto, EntidadContextoSchema
from src.model.mixFamiliari.usuario_entidad import UsuarioEntidad
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError
from src.model.usuario import Usuario  # ajustá si tenés otro path
import secrets  # para token seguro
from datetime import timedelta

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

            if entidad:  # Si hay entidad relacionada
                usuarios_dict[usuario.id]["entidades"].append({
                    "id": entidad.id,
                    "nombre": entidad.nombre,
                    "tipo": entidad.tipo,
                    "rol": relacion.rol if relacion else None
                })

        usuarios_con_entidades = list(usuarios_dict.values())

        return render_template(
            "pantalla_usuarios/pantalla_crud_usuarios.html",
            usuarios=usuarios_con_entidades
        )

    except Exception as e:
        return f"Error al cargar usuarios: {str(e)}", 500



@crud_usuario.route('/administracion_crud_usuario_crear_usuario/', methods=['POST'])
def administracion_crud_usuario_crear_usuario():
    data = request.get_json()

    try:
        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(64)

        nuevo = Usuario(
            correo_electronico=data.get('correo_electronico'),
            password=data.get('password').encode('utf-8'),  # guardar en binario
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
       
        # Guardar tokens en cookies HTTPOnly
        response.set_cookie("token", token, httponly=True, max_age=3600)  # 1 hora
        response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=3600 * 24 * 7)  # 1 semana

        return response

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 400
    finally:
        db.session.close()
