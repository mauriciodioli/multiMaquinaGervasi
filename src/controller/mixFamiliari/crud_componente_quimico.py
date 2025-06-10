from flask import Blueprint, request, jsonify, render_template
from src.model.mixFamiliari.componente_quimico import Componente_quimico, Componente_quimicoSchema
from src.model.mixFamiliari.tipo_mezcla import Tipo_mezcla, Tipo_mezclaSchema
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError

crud_componente_quimico = Blueprint("crud_componente_quimico", __name__)

componente_quimicoSchema = Componente_quimicoSchema()
componente_quimicoSchema = Componente_quimicoSchema(many=True)

tipo_mezcla_schema = Tipo_mezclaSchema()
tipo_mezcla_schema_many = Tipo_mezclaSchema(many=True)

# Vista HTML
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_listar/")
def mixFamiliari_crud_componente_quimico_pantalla_listar():
    try:
        
        componentes = db.session.query(Componente_quimico).all()
        return render_template("pantalla_componente_quimico/pantalla_componente_quimico.html", componentes=componentes)
    finally:
        db.session.close()


# Agregar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_agregar/", methods=["POST"])
def mixFamiliari_crud_componente_quimico_pantalla_agregar():
    try:
        data = request.get_json()

        nuevo = Componente_quimico(
            nombre=data.get("nombre"),
            pais=data.get("pais"),
            descripcion=data.get("descripcion"),
            tipo_mezcla_id=data.get("tipo_mezcla_id")
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify(success=True, componente_quimico={
            "id": nuevo.id,
            "nombre": nuevo.nombre,
            "pais": nuevo.pais,
            "descripcion": nuevo.descripcion,
            "tipo_mezcla_id": nuevo.tipo_mezcla_id
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()


# Modificar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_modificar/<int:id>", methods=["PUT"])
def mixFamiliari_crud_componente_quimico_pantalla_modificar(id):
    try:
        data = request.get_json()
        componente = db.session.get(Componente_quimico, id)
        if not componente:
            return jsonify(success=False, error="Componente químico no encontrado")

        componente.nombre = data.get("nombre")
        componente.pais = data.get("pais")
        componente.descripcion = data.get("descripcion")
        componente.tipo_mezcla_id = data.get("tipo_mezcla_id")
        tipo_mezcla_nome = data.get("tipo_mezcla_nome")

        db.session.commit()

        return jsonify(success=True, componente_quimico={
            "id": componente.id,
            "nombre": componente.nombre,
            "pais": componente.pais,
            "descripcion": componente.descripcion,
            "tipo_mezcla_id": componente.tipo_mezcla_id,
            "tipo_mezcla_nome":tipo_mezcla_nome
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()

# Modificar tipo_Mezcla
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_modificar_tipo_Mezcla/<int:id>", methods=["PUT"])
def mixFamiliari_crud_componente_quimico_pantalla_modificar_tipo_Mezcla(id):
    try:
        data = request.get_json()
        componente = db.session.get(Componente_quimico, id)
        if not componente:
            return jsonify(success=False, error="Componente químico no encontrado")

        # Asegúrate de convertir a int si es necesario
        componente.tipo_mezcla_id = int(data.get("tipo_mezcla_id"))

        db.session.commit()

        return jsonify(success=True, componente_quimico={
            "id": componente.id,
            "nombre": componente.nombre,
            "pais": componente.pais,
            "descripcion": componente.descripcion,
            "tipo_mezcla_id": componente.tipo_mezcla_id
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()
        
        
        
        
# Eliminar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_eliminar/<int:id>", methods=["DELETE"])
def mixFamiliari_crud_componente_quimico_pantalla_eliminar(id):
    try:
        componente = db.session.get(Componente_quimico, id)
        if not componente:
            return jsonify(success=False, error="Componente químico no encontrado")

        db.session.delete(componente)
        db.session.commit()
        return jsonify(success=True)

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

    finally:
        db.session.close()
