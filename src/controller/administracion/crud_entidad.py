from flask import Blueprint, request, jsonify, render_template

from src.model.entidad_contexto import EntidadContexto, EntidadContextoSchema
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError

crud_entidad = Blueprint("crud_entidad", __name__)

entidad_schema = EntidadContextoSchema()
entidades_schema = EntidadContextoSchema(many=True)

# 👉 Ruta para mostrar la pantalla con entidades existentes
@crud_entidad.route('/administracion_crud_entidad_pantalla_entidades/', methods=['GET'])
def administracion_crud_entidad_pantalla_entidades():
    entidades = db.session.query(EntidadContexto).all()
    return render_template("pantalla_entidades/pantalla_entidades.html", entidades=entidades)

# 👉 Crear entidad (POST desde fetch)
@crud_entidad.route('/administracion_crud_entidad_crear_entidad/', methods=['POST'])
def crear_entidad():
    data = request.get_json()
    try:
        nueva = EntidadContexto(
            nombre=data.get('nombre'),
            tipo=data.get('tipo'),
            descripcion=data.get('descripcion'),
            estado=int(data.get('estado', 1))
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify(success=True, entidad={
            "id": nueva.id,
            "nombre": nueva.nombre,
            "tipo": nueva.tipo,
            "descripcion": nueva.descripcion,
            "estado": nueva.estado
        })
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 400

    
    
    
# ✏️ Editar (actualizar)
@crud_entidad.route('/administracion_crud_entidad_modifica_entidades/', methods=['POST'])
def administracion_crud_entidad_modifica_entidades():
    data = request.get_json()
    try:
        entidad = db.session.get(EntidadContexto, int(data["id"]))
        entidad.nombre = data["nombre"]
        entidad.tipo = data["tipo"]
        entidad.descripcion = data["descripcion"]
        entidad.estado = int(data["estado"])
        db.session.commit()
        return jsonify(success=True, entidad={
            "id": entidad.id,
            "nombre": entidad.nombre,
            "tipo": entidad.tipo,
            "descripcion": entidad.descripcion,
            "estado": entidad.estado
        })
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 400

    
    
    

@crud_entidad.route('/administracion_crud_entidad_eliminar_entidad/<int:id>', methods=['DELETE'])
def administracion_crud_entidad_eliminar_entidad(id):
    try:
        entidad = db.session.get(EntidadContexto, id)
        if not entidad:
            return jsonify({"status": "error", "message": "Entidad no encontrada"}), 404

        db.session.delete(entidad)
        db.session.commit()
        return jsonify({"status": "ok"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
