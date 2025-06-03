from flask import Blueprint, request, render_template, send_file, jsonify
import urllib.parse
import json
from utils.db import db
from src.model.mixFamiliari.mix_familiari import Mix_familiari
from src.model.mixFamiliari.mix_familiari import Mix_familiariSchema
from sqlalchemy import inspect




mix_familiari = Blueprint('mix_familiari', __name__)

schema = Mix_familiariSchema()
schema_many = Mix_familiariSchema(many=True)


@mix_familiari.route('/pantalla_mix_familiari/')
def pantalla_mix_familiari():
    try:
        if request.method == 'POST':
            data = request.get_json()
            user_id = data.get('user_id')
        else:
            user_id = request.args.get('user_id')

        if user_id:
            maquinas = db.session.query(Mix_familiari).filter_by(user_id=int(user_id)).all()
        else:
            maquinas = db.session.query(Mix_familiari).all()
        for m in maquinas:
            if isinstance(m.setting, str):
                try:
                    m.setting = json.loads(m.setting)
                except:
                    m.setting = {}
            return render_template('pantalla_mix_familiari/pantalla_mix_familiari.html', mix_familiari=mix_familiari)

    except Exception as e:
        db.session.rollback()
        return f"Error conectando a la base de datos: {e}"
    finally:
        db.session.close()
  

@mix_familiari.route('/mixfamiliari', methods=['POST'])
def crear_mix():
    data = request.get_json()
    nuevo = MixFamiliari(**data)
    db.session.add(nuevo)
    db.session.commit()
    return schema.jsonify(nuevo)

@mix_familiari.route('/mixfamiliari', methods=['GET'])
def listar_mix():
    todos = MixFamiliari.query.all()
    return schema_many.jsonify(todos)

@mix_familiari.route('/mixfamiliari/<int:id>', methods=['GET'])
def obtener_mix(id):
    mix = MixFamiliari.query.get_or_404(id)
    return schema.jsonify(mix)

@mix_familiari.route('/mixfamiliari/<int:id>', methods=['PUT'])
def actualizar_mix(id):
    mix = MixFamiliari.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(mix, key, value)
    db.session.commit()
    return schema.jsonify(mix)

@mix_familiari.route('/mixfamiliari/<int:id>', methods=['DELETE'])
def eliminar_mix(id):
    mix = MixFamiliari.query.get_or_404(id)
    db.session.delete(mix)
    db.session.commit()
    return jsonify({"mensaje": "Eliminado"})
