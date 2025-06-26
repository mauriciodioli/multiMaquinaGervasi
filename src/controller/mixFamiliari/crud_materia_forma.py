from flask import Blueprint, request, jsonify, render_template, redirect
from utils.db import db
from src.model.mixFamiliari.materia_forma import MateriaForma, Materia_formaSchema
from sqlalchemy.exc import SQLAlchemyError
from src.utils.auth import current_user
from src.utils.get_textos_menu import get_textos_menu

crud_materia_forma = Blueprint('crud_materia_forma', __name__)
schema      = Materia_formaSchema()
schema_many = Materia_formaSchema(many=True)

@crud_materia_forma.route("/mixFamiliari_crud_materia_forma_pantalla_listar/")
def mixFamiliari_crud_materia_forma_pantalla_listar():
    usuario = current_user()
    if not usuario:
        return redirect("/login")
    tipos = MateriaForma.query.all()
    return render_template(
        "pantalla_materia_forma/pantalla_materia_forma.html",
        tipos=tipos,
        t_menu=get_textos_menu(request.cookies.get("lang", "es"))
    )

@crud_materia_forma.route("/mixFamiliari_crud_materia_forma_listar_json/")
def listar_json():
    tipos = MateriaForma.query.all()
    return jsonify(
        success=True,
        tipos=schema_many.dump(tipos)
    )

@crud_materia_forma.route("/mixFamiliari_crud_materia_forma_pantalla_agregar/", methods=["POST"])
def mixFamiliari_crud_materia_forma_pantalla_agregar():
    data = request.get_json()
    nuevo = MateriaForma(
        origen     = data["origen"],
        forma      = data.get("forma"),
        descripcion= data.get("descripcion"),
        estado     = data.get("estado", True)   # <-- ahora incluimos estado
    )
    try:
        db.session.add(nuevo)
        db.session.commit()
        return jsonify(success=True, tipo=schema.dump(nuevo))
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    finally:
        db.session.close()

@crud_materia_forma.route("/mixFamiliari_crud_materia_forma_pantalla_modificar/<int:id>", methods=["PUT"])
def mixFamiliari_crud_materia_forma_pantalla_modificar(id):
    data = request.get_json()
    tipo = db.session.get(MateriaForma, id)
    if not tipo:
        return jsonify(success=False, error="No existe el registro"), 404

    tipo.origen      = data.get("origen", tipo.origen)
    tipo.forma       = data.get("forma", tipo.forma)
    tipo.descripcion = data.get("descripcion", tipo.descripcion)
    tipo.estado      = data.get("estado", tipo.estado)  # <-- y aquí también

    try:
        db.session.commit()
        return jsonify(success=True, tipo=schema.dump(tipo))
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    finally:
        db.session.close()

@crud_materia_forma.route("/mixFamiliari_crud_materia_forma_pantalla_eliminar/<int:id>", methods=["DELETE"])
def mixFamiliari_crud_materia_forma_pantalla_eliminar(id):
    tipo = db.session.get(MateriaForma, id)
    if not tipo:
        return jsonify(success=False, error="No existe el registro"), 404
    try:
        db.session.delete(tipo)
        db.session.commit()
        return jsonify(success=True)
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    finally:
        db.session.close()
