from flask import Blueprint, request, jsonify, render_template

from src.model.pais_contexto import PaisContexto, PaisContextoSchema
from sqlalchemy.exc import SQLAlchemyError
from src.utils.get_textos_menu import get_textos_menu
from src.utils.db_session import get_db_session

crud_pais = Blueprint("crud_pais", __name__)
pais_schema = PaisContextoSchema(many=True)
paises_schema = PaisContextoSchema(many=True)


# 👉 Ruta para mostrar la pantalla con países existentes
@crud_pais.route('/administracion_crud_pais_pantalla_paises/', methods=['GET'])
def administracion_crud_pais_pantalla_paises():
    with get_db_session() as session:
        paises = session.query(PaisContexto).all()
        lang = request.cookies.get("lang", "es")
        t_menu = get_textos_menu(lang)
        return render_template("pantalla_paises/pantalla_paises.html", paises=paises, t_menu=t_menu)


# 👉 Crear país (POST desde fetch)
@crud_pais.route('/administracion_crud_pais_crear_pais/', methods=['POST'])
def crear_pais():
    data = request.get_json()
    try:
        with get_db_session() as session:
            nuevo = PaisContexto(
                nombre=data.get('nombre'),
                codigo=data.get('codigo'),
                descripcion=data.get('descripcion'),
                estado=int(data.get('estado', 1))
            )
            session.add(nuevo)
            session.commit()
            return jsonify(success=True, pais={
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "codigo": nuevo.codigo,
                "descripcion": nuevo.descripcion,
                "estado": nuevo.estado
            })
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400


# ✏️ Editar (actualizar)
@crud_pais.route('/administracion_crud_pais_modifica_pais/', methods=['POST'])
def administracion_crud_pais_modifica_pais():
    data = request.get_json()
    try:
        with get_db_session() as session:
            pais = session.get(PaisContexto, int(data["id"]))
            pais.nombre = data["nombre"]
            pais.codigo = data["codigo"]
            pais.descripcion = data["descripcion"]
            pais.estado = int(data["estado"])
            session.commit()
            return jsonify(success=True, pais={
                "id": pais.id,
                "nombre": pais.nombre,
                "codigo": pais.codigo,
                "descripcion": pais.descripcion,
                "estado": pais.estado
            })
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400


@crud_pais.route('/administracion_crud_pais_eliminar_pais/<int:id>', methods=['DELETE'])
def administracion_crud_pais_eliminar_pais(id):
    try:
        with get_db_session() as session:
            pais = session.get(PaisContexto, id)
            if not pais:
                return jsonify({"status": "error", "message": "País no encontrado"}), 404

            session.delete(pais)
            session.commit()
            return jsonify({"status": "ok"})
    except SQLAlchemyError as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@crud_pais.route('/administracion_crud_pais_listar/', methods=['GET'])
def listar_paises():
    try:
        with get_db_session() as session:
            paises = session.query(PaisContexto).all()
            resultado = pais_schema.dump(paises)
            return jsonify({"success": True, "paises": resultado})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'error': str(e)})
