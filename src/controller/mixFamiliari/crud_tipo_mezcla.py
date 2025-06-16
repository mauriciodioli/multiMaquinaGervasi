from flask import Blueprint, request, jsonify, render_template, redirect
from utils.db import db
from src.model.mixFamiliari.tipo_mezcla import Tipo_mezcla, Tipo_mezclaSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from src.utils.auth import current_user
from src.utils.get_textos_menu import get_textos_menu

crud_tipo_mezcla = Blueprint('crud_tipo_mezcla', __name__)
tipo_mezcla_schema = Tipo_mezclaSchema()
tipo_mezcla_schema_many = Tipo_mezclaSchema(many=True)

# Vista HTML
@crud_tipo_mezcla.route("/mixFamiliari_crud_tipo_mezcla_pantalla_listar/")
def mixFamiliari_crud_tipo_mezcla_pantalla_listar():
    try:
        usuario = current_user()
        if not usuario:
            return redirect("/login")

        lang = request.cookies.get("lang", "es")
        t_menu = get_textos_menu(lang)

        tipos = db.session.query(Tipo_mezcla).all()
        return render_template("pantalla_tipo_mezcla/pantalla_tipo_mezcla.html", tipos=tipos, t_menu=t_menu)
    finally:
        db.session.close()


@crud_tipo_mezcla.route("/mixFamiliari_crud_tipo_mezcla_pantalla_listar_json/")
def mixFamiliari_crud_tipo_mezcla_pantalla_listar_json():
    try:
        tipos = db.session.query(Tipo_mezcla).all()
        tipos_json = [
            {"id": t.id, "nombre": t.nombre, "descripcion": t.descripcion}
            for t in tipos
        ]
        return jsonify(success=True, tipos_mezcla=tipos_json)
    finally:
        db.session.close()


# Agregar
@crud_tipo_mezcla.route("/mixFamiliari_crud_tipo_mezcla_pantalla_agregar/", methods=["POST"])
def mixFamiliari_crud_tipo_mezcla_pantalla_agregar():
    try:
        data = request.get_json()

        nuevo = Tipo_mezcla(
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion")
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify(success=True, tipo_mezcla={
            "id": nuevo.id,
            "nombre": nuevo.nombre,
            "descripcion": nuevo.descripcion
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()

# Modificar
@crud_tipo_mezcla.route("/mixFamiliari_crud_tipo_mezcla_pantalla_modificar/<int:id>", methods=["PUT"])
def mixFamiliari_crud_tipo_mezcla_pantalla_modificar(id):
    try:
        data = request.get_json()
        tipo = db.session.get(Tipo_mezcla, id)
        if not tipo:
            return jsonify(success=False, error="Tipo de mezcla no encontrado")

        tipo.nombre = data.get("nombre")
        tipo.descripcion = data.get("descripcion")

        db.session.commit()

        return jsonify(success=True, tipo_mezcla={
            "id": tipo.id,
            "nombre": tipo.nombre,
            "descripcion": tipo.descripcion
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()

# Eliminar
@crud_tipo_mezcla.route("/mixFamiliari_crud_tipo_mezcla_pantalla_eliminar/<int:id>", methods=["DELETE"])
def mixFamiliari_crud_tipo_mezcla_pantalla_eliminar(id):
    try:
        tipo = db.session.get(Tipo_mezcla, id)
        if not tipo:
            return jsonify(success=False, error="Tipo de mezcla no encontrado")

        db.session.delete(tipo)
        db.session.commit()
        return jsonify(success=True)

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()
