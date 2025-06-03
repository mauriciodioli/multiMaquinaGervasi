# categoria_mezcla.py
from flask import Blueprint, request, jsonify
from utils.db import db
from src.model.mixFamiliari.categoria_mezcla import Categoria_mezcla

from src.model.mixFamiliari.categoria_mezcla import Categoria_mezclaSchema

categoria_bp = Blueprint('categoria_bp', __name__)
schema = Categoria_mezclaSchema()
schema_many = Categoria_mezclaSchema(many=True)

@categoria_bp.route('/categorias', methods=['POST'])
def crear_categoria():
    data = request.get_json()
    nueva = Categoria_mezcla(**data)
    db.session.add(nueva)
    db.session.commit()
    return schema.jsonify(nueva)

@categoria_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    todas = Categoria_mezcla.query.all()
    return schema_many.jsonify(todas)

@categoria_bp.route('/categorias/<int:id>', methods=['PUT'])
def actualizar_categoria(id):
    cat = Categoria_mezcla.query.get_or_404(id)
    data = request.get_json()
    for k, v in data.items():
        setattr(cat, k, v)
    db.session.commit()
    return schema.jsonify(cat)

@categoria_bp.route('/categorias/<int:id>', methods=['DELETE'])
def eliminar_categoria(id):
    cat = Categoria_mezcla.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"mensaje": "Eliminada"})