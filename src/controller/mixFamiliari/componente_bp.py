
# componente_quimico.py
from flask import Blueprint, request, jsonify
from utils.db import db
from src.model.mixFamiliari.componente_quimico import Componente_quimico 
from src.model.mixFamiliari.componente_quimico import Componente_quimicoSchema

componente_bp = Blueprint('componente_bp', __name__)
schema = Componente_quimicoSchema()
schema_many = Componente_quimicoSchema(many=True)

@componente_bp.route('/componentes', methods=['POST'])
def crear_componente():
    data = request.get_json()
    nuevo = Componente_quimico(**data)
    db.session.add(nuevo)
    db.session.commit()
    return schema.jsonify(nuevo)

@componente_bp.route('/componentes', methods=['GET'])
def listar_componentes():
    todos = Componente_quimico.query.all()
    return schema_many.jsonify(todos)

@componente_bp.route('/componentes/<int:id>', methods=['PUT'])
def actualizar_componente(id):
    comp = Componente_quimico.query.get_or_404(id)
    data = request.get_json()
    for k, v in data.items():
        setattr(comp, k, v)
    db.session.commit()
    return schema.jsonify(comp)

@componente_bp.route('/componentes/<int:id>', methods=['DELETE'])
def eliminar_componente(id):
    comp = Componente_quimico.query.get_or_404(id)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"mensaje": "Eliminado"})
