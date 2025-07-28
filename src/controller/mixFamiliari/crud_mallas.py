from flask import Blueprint, request, jsonify, render_template,redirect
from src.model.mixFamiliari.malla import Malla, Tipo_mallasSchema
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError
from src.utils.auth import current_user
from src.utils.get_textos_menu import get_textos_menu
from src.utils.db_session import get_db_session

crud_mallas = Blueprint("crud_mallas", __name__)

malla_schema = Tipo_mallasSchema()
mallas_schema = Tipo_mallasSchema(many=True)

# Vista HTML
@crud_mallas.route("/mixFamiliari_crud_mallas_pantalla_mallas_listar/")
def mixFamiliari_crud_mallas_pantalla_mallas_listar():
    try:
        with get_db_session() as session:
            mallas = session.query(Malla).all()
            
            usuario = current_user()
            if not usuario:
                return redirect("/login")

            lang = request.cookies.get("lang", "es")
            t_menu = get_textos_menu(lang)

            return render_template(
                "pantalla_mallas/pantalla_mallas.html",
                mallas=mallas,
                usuario=usuario,
                t_menu=t_menu
            )

    except Exception as e:        
        return f"Error al cargar mallas: {e}"

  


# Agregar
@crud_mallas.route("/mixFamiliari_crud_mallas_pantalla_mallas_agregar/", methods=["POST"])
def mixFamiliari_crud_mallas_pantalla_mallas_agregar():
    try:
        data = request.get_json()
        with get_db_session() as session:
            nueva = Malla(
                nombre_comercial=data.get("nombre_comercial"),
                diametro_mm=data.get("diametro_mm")
            )

            session.add(nueva)
            session.commit()

            malla_dict = {
                "id": nueva.id,
                "nombre_comercial": nueva.nombre_comercial,
                "diametro_mm": nueva.diametro_mm
            }

            return jsonify(success=True, malla=malla_dict)

    except SQLAlchemyError as e:      
        return jsonify(success=False, error=str(e))

  


@crud_mallas.route("/mixFamiliari_crud_mallas_pantalla_mallas_modificar/<int:id>", methods=["PUT"])
def mixFamiliari_crud_mallas_pantalla_mallas_modificar(id):
    try:
        data = request.get_json()
        with get_db_session() as session:
            malla = session.get(Malla, id)
            if not malla:
                return jsonify(success=False, error="Malla no encontrada")

            malla.nombre_comercial = data.get("nombre_comercial")
            malla.diametro_mm = data.get("diametro_mm")
            session.commit()

            # Devolver la malla actualizada
            return jsonify(success=True, malla={
                "id": malla.id,
                "nombre_comercial": malla.nombre_comercial,
                "diametro_mm": malla.diametro_mm
            })

    except SQLAlchemyError as e:       
        return jsonify(success=False, error=str(e))

   

# Eliminar
@crud_mallas.route("/mixFamiliari_crud_mallas_pantalla_mallas_eliminar/<int:id>", methods=["DELETE"])
def mixFamiliari_crud_mallas_pantalla_mallas_eliminar(id):
    try:
        with get_db_session() as session:
            malla = session.get(Malla, id)
            if not malla:
                return jsonify(success=False, error="Malla no encontrada")
            session.delete(malla)
            session.commit()
            return jsonify(success=True)
    except SQLAlchemyError as e:       
        return jsonify(success=False, error=str(e))
  
