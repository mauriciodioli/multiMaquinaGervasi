# Este archivo define los endpoints CRUD para la entidad Agregado y su combinación con Componentes

from flask import Blueprint, request, jsonify, render_template
from utils.db import db
from src.model.mixFamiliari.agregado import Agregado, AgregadoSchema
from src.model.mixFamiliari.componente_quimico import Componente_quimico, Componente_quimicoSchema
from sqlalchemy.exc import SQLAlchemyError
import json

crud_agregado = Blueprint('crud_agregado', __name__)

agregado_schema = AgregadoSchema()
agregados_schema = AgregadoSchema(many=True)
componente_schema = Componente_quimicoSchema()
componentes_schema = Componente_quimicoSchema(many=True)


@crud_agregado.route('/pantalla_agregado/', methods=['GET', 'POST'])
def pantalla_agregado():
    try:
        if request.method == 'POST':
            data = request.get_json()
            user_id = data.get('user_id')
        else:
            user_id = request.args.get('user_id')

        if user_id:
            mezclas = db.session.query(Agregado).filter_by(usuario_id=int(user_id)).all()
        else:
            mezclas = db.session.query(Agregado).all()

        # Parsear JSON en campo setting si existe
        for m in mezclas:
            if hasattr(m, "setting") and isinstance(m.setting, str):
                try:
                    m.setting = json.loads(m.setting)
                except Exception:
                    m.setting = {}

        return render_template(
            'pantalla_agregados/pantalla_agregados.html',
            mezclas=mezclas
        )

    except Exception as e:
        db.session.rollback()
        return f"Error conectando a la base de datos: {e}"

    finally:
        db.session.close()
  


@crud_agregado.route('/agregados/', methods=['GET'])
def listar_agregados():
    try:
        agregados = Agregado.query.all()
        return jsonify(agregados_schema.dump(agregados))
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@crud_agregado.route('/mixFamiliari_crear_agregado_agregados/', methods=['POST'])
def crear_agregado():
    try:
        data = request.get_json()
        nuevo = Agregado(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            idioma=data.get('idioma'),
            estado=data.get('estado', True),
            usuario_id=data['usuario_id'],
            malla_id=data.get('malla_id')
        )
        db.session.add(nuevo)
        db.session.commit()
        return agregado_schema.jsonify(nuevo)
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@crud_agregado.route('/agregados/<int:id>', methods=['PUT'])
def actualizar_agregado(id):
    try:
        data = request.get_json()
        agregado = Agregado.query.get_or_404(id)

        for field in ['nombre', 'descripcion', 'idioma', 'estado', 'malla_id']:
            if field in data:
                setattr(agregado, field, data[field])

        db.session.commit()
        return agregado_schema.jsonify(agregado)
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@crud_agregado.route('/agregados/<int:id>', methods=['DELETE'])
def eliminar_agregado(id):
    try:
        agregado = Agregado.query.get_or_404(id)
        db.session.delete(agregado)
        db.session.commit()
        return jsonify({'mensaje': 'Agregado eliminado'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@crud_agregado.route('/agregados/<int:agregado_id>/componentes', methods=['GET'])
def obtener_componentes(agregado_id):
    try:
        componentes = Componente_quimico.query.filter_by(agregado_id=agregado_id).all()
        return jsonify(componentes_schema.dump(componentes))
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


