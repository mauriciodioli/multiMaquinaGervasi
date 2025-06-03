
# tipo_mezcla.py
from flask import Blueprint, request, jsonify
from utils.db import db
from src.model.mixFamiliari.tipo_mezcla import Tipo_mezcla
from src.model.mixFamiliari.tipo_mezcla import Tipo_mezclaSchema


tipo_bp = Blueprint('tipo_bp', __name__)
schema = Tipo_mezclaSchema()
schema_many = Tipo_mezclaSchema(many=True)

@tipo_bp.route('/tipos', methods=['POST'])
def crear_tipo():
    data = request.get_json()
    nuevo = Tipo_mezcla(**data)
    db.session.add(nuevo)
    db.session.commit()
    return schema.jsonify(nuevo)

@tipo_bp.route('/tipos', methods=['GET'])
def listar_tipos():
    todos = Tipo_mezcla.query.all()
    return schema_many.jsonify(todos)