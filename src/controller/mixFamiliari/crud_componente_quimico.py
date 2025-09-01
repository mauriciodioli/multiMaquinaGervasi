from flask import Blueprint, request, jsonify, render_template, redirect
from src.model.mixFamiliari.componente_quimico import Componente_quimico, Componente_quimicoSchema
from src.model.mixFamiliari.tipo_mezcla import Tipo_mezcla, Tipo_mezclaSchema
from src.model.mixFamiliari.materia_forma import  MateriaForma
from utils.db import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from src.utils.auth import current_user
from src.utils.get_textos_menu import get_textos_menu
from src.utils.db_session import get_db_session

crud_componente_quimico = Blueprint("crud_componente_quimico", __name__)

componente_quimicoSchema = Componente_quimicoSchema()
componente_quimicoSchema = Componente_quimicoSchema(many=True)

tipo_mezcla_schema = Tipo_mezclaSchema()
tipo_mezcla_schema_many = Tipo_mezclaSchema(many=True)

@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_listar/")
def mixFamiliari_crud_componente_quimico_pantalla_listar():
    try:
        with get_db_session() as session:
            # 1) Traer componentes (dejo joinedload del tipo_mezcla si lo usás)
            componentes = (
                session.query(Componente_quimico)
                .options(joinedload(Componente_quimico.tipo_mezcla))
                .all()
            )

            # 2) Traer MateriaForma activas
            materia_formas = (
                session.query(MateriaForma)
                .filter(MateriaForma.estado == True)
                .all()
            )

            # 3) Armar un diccionario id -> forma (clarito, sin comprensiones)
            mf_by_id = {}
            for mf in materia_formas:
                mf_by_id[mf.id] = mf.forma

            # 4) Construir una lista “lista para la vista” con la forma ya resuelta
            componentes_vista = []
            for c in componentes:
                item = {
                    "id": c.id,
                    "nombre": getattr(c, "nombre", ""),
                    "pais": getattr(c, "pais", ""),
                    "descripcion": getattr(c, "descripcion", ""),
                    "tipo_mezcla": c.tipo_mezcla.nombre if getattr(c, "tipo_mezcla", None) else "-",
                    "materia_forma_id": getattr(c, "materia_forma_id", None),
                    # Si el componente no tiene materia_forma_id o no existe en el diccionario: "-"
                    "materia_forma_forma": mf_by_id.get(getattr(c, "materia_forma_id", None), "-"),
                }
                componentes_vista.append(item)

            # 5) Usuario / menú
            usuario = current_user()
            if not usuario:
                return redirect("/login")

            lang = request.cookies.get("lang", "es")
            t_menu = get_textos_menu(lang)

            return render_template(
                "pantalla_componente_quimico/pantalla_componente_quimico.html",
                componentes=componentes_vista,   # ← usamos la lista ya “matcheada”
                materia_formas=materia_formas,   # catálogo por si tenés selects
                usuario=usuario,
                t_menu=t_menu,
                lang=lang,
            )

    except Exception as e:
        return f"Error al cargar componentes químicos: {e}"


# Agregar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_agregar/", methods=["POST"])
def mixFamiliari_crud_componente_quimico_pantalla_agregar():
    try:
        data = request.get_json()
        with get_db_session() as session:
            nuevo = Componente_quimico(
                nombre=data.get("nombre"),
                pais=data.get("pais"),
                descripcion=data.get("descripcion"),
                tipo_mezcla_id=data.get("tipo_mezcla_id")
            )

            session.add(nuevo)
            session.commit()

            return jsonify(success=True, componente_quimico={
                "id": nuevo.id,
                "nombre": nuevo.nombre,
                "pais": nuevo.pais,
                "descripcion": nuevo.descripcion,
                "tipo_mezcla_id": nuevo.tipo_mezcla_id
            })
    except SQLAlchemyError as e:        
        return jsonify(success=False, error=str(e))

    
    
# Modificar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_modificar_agrega_materia_forma/<int:id>", methods=["PUT"])
def mixFamiliari_crud_componente_quimico_pantalla_modificar_agrega_materia_forma(id):
    try:
        data = request.get_json()
        with get_db_session() as session:
            componente = session.get(Componente_quimico, id)
            if not componente:
                return jsonify(success=False, error="Componente químico no encontrado")

            componente.nombre = data.get("nombre")
            componente.pais = data.get("pais")
            componente.descripcion = data.get("descripcion")
            tipo_mezcla_id = data.get("tipo_mezcla_id")
            materia_forma_id = data.get("materia_forma_id")
            componente.materia_forma_id = int(materia_forma_id)
            tipo_mezcla_nome = data.get("tipo_mezcla_nome")

            session.commit()

            materiaForma = session.get(MateriaForma,componente.materia_forma_id)
            return jsonify(success=True, componente_quimico={
                "id": componente.id,
                "nombre": componente.nombre,
                "pais": componente.pais,
                "descripcion": componente.descripcion,
                "tipo_mezcla_id": componente.tipo_mezcla_id,
                "materia_forma_forma": materiaForma.forma,
                "tipo_mezcla_nome":tipo_mezcla_nome
            })

    except SQLAlchemyError as e:      
        return jsonify(success=False, error=str(e))

       
    
    

# Modificar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_modificar/<int:id>", methods=["PUT"])
def mixFamiliari_crud_componente_quimico_pantalla_modificar(id):
    try:
        data = request.get_json()
        with get_db_session() as session:
            componente = session.get(Componente_quimico, id)
            if not componente:
                return jsonify(success=False, error="Componente químico no encontrado")

            componente.nombre = data.get("nombre")
            componente.pais = data.get("pais")
            componente.descripcion = data.get("descripcion")
            tipo_mezcla_id = data.get("tipo_mezcla_id")
            if tipo_mezcla_id in [None, '', 'null']:
                componente.tipo_mezcla_id = None
            else:
                componente.tipo_mezcla_id = int(tipo_mezcla_id)
            tipo_mezcla_nome = data.get("tipo_mezcla_nome")

            session.commit()

            return jsonify(success=True, componente_quimico={
                "id": componente.id,
                "nombre": componente.nombre,
                "pais": componente.pais,
                "descripcion": componente.descripcion,
                "tipo_mezcla_id": componente.tipo_mezcla_id,
                "tipo_mezcla_nome":tipo_mezcla_nome
            })

    except SQLAlchemyError as e:      
        return jsonify(success=False, error=str(e))

   


# Modificar tipo_Mezcla
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_modificar_tipo_Mezcla/<int:id>", methods=["PUT"])
def mixFamiliari_crud_componente_quimico_pantalla_modificar_tipo_Mezcla(id):
    try:
        data = request.get_json()
        with get_db_session() as session:
            componente = session.get(Componente_quimico, id)
            if not componente:
                return jsonify(success=False, error="Componente químico no encontrado")

            # Asegúrate de convertir a int si es necesario
            componente.tipo_mezcla_id = int(data.get("tipo_mezcla_id"))

            session.commit()
        # Obtener el nombre del tipo de mezcla actualizado
            tipo_mezcla_nome = componente.tipo_mezcla.nombre if componente.tipo_mezcla else ""

            return jsonify(success=True, componente_quimico={
                "id": componente.id,
                "nombre": componente.nombre,
                "pais": componente.pais,
                "descripcion": componente.descripcion,
                "tipo_mezcla_id": componente.tipo_mezcla_id,
                "tipo_mezcla_nome": tipo_mezcla_nome
            })

    except SQLAlchemyError as e:       
        return jsonify(success=False, error=str(e))

  
        
        
        
# Eliminar
@crud_componente_quimico.route("/mixFamiliari_crud_componente_quimico_pantalla_eliminar/<int:id>", methods=["DELETE"])
def mixFamiliari_crud_componente_quimico_pantalla_eliminar(id):
    try:
         with get_db_session() as session:
            componente = session.get(Componente_quimico, id)
            if not componente:
                return jsonify(success=False, error="Componente químico no encontrado")

            session.delete(componente)
            session.commit()
            return jsonify(success=True)

    except SQLAlchemyError as e:    
        return jsonify(success=False, error=str(e))

        
