# Este archivo define los endpoints CRUD para la entidad Agregado y su combinación con Componentes

from flask import Blueprint, request, jsonify, render_template,redirect, url_for
from utils.db import db
from src.model.mixFamiliari.agregado import Agregado, AgregadoSchema
from src.model.mixFamiliari.componente_quimico import Componente_quimico, Componente_quimicoSchema
from src.model.mixFamiliari.malla import Malla
from src.model.mixFamiliari.agregado_malla import AgregadoMalla
from src.model.mixFamiliari.composicion_agregado import ComposicionAgregado
from src.model.mixFamiliari.analisis_granulometrico import AnalisisGranulometrico
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from src.utils.auth import current_user

from src.utils.get_textos_menu  import get_textos_menu



from sqlalchemy.exc import SQLAlchemyError
import json

perfil_user_bp = Blueprint('perfil_user_bp', __name__)

agregado_schema = AgregadoSchema()
agregados_schema = AgregadoSchema(many=True)
componente_schema = Componente_quimicoSchema()
componentes_schema = Componente_quimicoSchema(many=True)



@perfil_user_bp.route("/api/autoDensidad/perfil_usuario/analisis_granulometrico/", methods=["GET"])
def analisis_granulometrico():
    try:
        usuario = current_user()
        if not usuario:
            return jsonify({"error": "Usuario no autenticado"}), 401

        analisis = (
            db.session.query(AnalisisGranulometrico)
            .filter_by(usuario_id=usuario.id)
            .order_by(AnalisisGranulometrico.fecha.desc())
            .limit(5)
            .all()
        )

        resultado = []
        for a in analisis:
            resultado.append({
                "id": a.id,
                "nombre": a.nombre,
                "fecha": a.fecha.isoformat(),
                "resultado": a.resultado,  # Asegurate que sea JSON serializable
                "diagnostico": a.diagnostico  # idem
            })

        return jsonify(resultado)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.session.close()
