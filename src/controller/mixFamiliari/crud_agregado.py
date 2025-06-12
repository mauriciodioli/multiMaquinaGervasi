# Este archivo define los endpoints CRUD para la entidad Agregado y su combinación con Componentes

from flask import Blueprint, request, jsonify, render_template,redirect, url_for
from utils.db import db
from src.model.mixFamiliari.agregado import Agregado, AgregadoSchema
from src.model.mixFamiliari.componente_quimico import Componente_quimico, Componente_quimicoSchema
from src.model.mixFamiliari.malla import Malla
from src.model.mixFamiliari.agregado_malla import AgregadoMalla
from src.model.mixFamiliari.composicion_agregado import ComposicionAgregado
from sqlalchemy.exc import SQLAlchemyError




from sqlalchemy.exc import SQLAlchemyError
import json

crud_agregado = Blueprint('crud_agregado', __name__)

agregado_schema = AgregadoSchema()
agregados_schema = AgregadoSchema(many=True)
componente_schema = Componente_quimicoSchema()
componentes_schema = Componente_quimicoSchema(many=True)





@crud_agregado.route('/mixFamiliari_crud_agregado_agregados_listar/', methods=['GET', 'POST'])
def mixFamiliari_crud_agregado_agregados_listar():
    try:
        if request.method == 'POST':
            data = request.get_json()
            user_id = data.get('user_id')
        else:
            user_id = request.args.get('user_id')
            entidad_id = request.args.get('entidad_id')

        query = db.session.query(Agregado)
        if user_id:
            query = query.filter_by(usuario_id=int(user_id))
        if entidad_id:
            query = query.filter_by(entidad_id=int(entidad_id))
               
        mezclas = query.all()
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
  





@crud_agregado.route('/mixFamiliari_crear_agregado_agregados/', methods=['POST'])
def crear_agregado():
    try:
        data = request.get_json()
        estado_raw = data.get('estado')
        estado = True if estado_raw == "Attivo" else False

        nuevo = Agregado(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),                  
            estado=estado,
            usuario_id=int(data.get('usuario_id')),
            entidad_id=int(data.get('entidad_id')),                  
            pais=data.get('pais')
        )

        db.session.add(nuevo)
        db.session.commit()

        # Obtener el nombre de la entidad relacionada
        entidad_nombre = nuevo.entidad.nombre if nuevo.entidad else None

        return jsonify({
            'id': nuevo.id,
            'nombre': nuevo.nombre,
            'descripcion': nuevo.descripcion,
            'estado': "Attivo" if nuevo.estado else "Inattivo",
            'idioma': nuevo.idioma or "—",
            'entidad_id': nuevo.entidad_id,
            'entidad_nombre': entidad_nombre
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.session.close()





@crud_agregado.route('/mixFamiliari_eliminar_agregado/<int:id>', methods=['DELETE'])
def mixFamiliari_eliminar_agregado(id):
    try:
        agregado = Agregado.query.get(id)
        if not agregado:
            return jsonify({'error': 'No encontrado'}), 404
        db.session.delete(agregado)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.session.close()










@crud_agregado.route('/mixFamiliari_modificar_agregado/<int:id>', methods=['PUT'])
def mixFamiliari_modificar_agregado(id):
    try:
        data = request.get_json()
        agregado = Agregado.query.get(id)
        if not agregado:
            return jsonify({'error': 'No encontrado'}), 404

        agregado.nombre = data.get('nombre')
        agregado.descripcion = data.get('descripcion')
        estado_raw = data.get('estado')
        agregado.estado = True if estado_raw == "Attivo" else False

        db.session.commit()

        entidad_nombre = agregado.entidad.nombre if agregado.entidad else None

        return jsonify({
            'id': agregado.id,
            'nombre': agregado.nombre,
            'descripcion': agregado.descripcion,
            'entidad_nombre': entidad_nombre,
            'estado': "True" if agregado.estado else "False"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.session.close()





@crud_agregado.route('/mixFamiliari_crud_agregado_agregados/<int:agregado_id>/detalle')
def mixFamiliari_crud_agregado_agregados(agregado_id):
    try:
        agregado = db.session.query(Agregado).get(agregado_id)
        if not agregado:
            return "Agregado no encontrado", 404

        agregado_mallas = (
            db.session.query(AgregadoMalla)
            .filter_by(agregado_id=agregado_id)
            .join(Malla)
            .all()
        )

        composicion = (
            db.session.query(ComposicionAgregado)
            .filter_by(agregado_id=agregado_id)
            .join(Componente_quimico)
            .order_by(ComposicionAgregado.orden.asc())
            .all()
        )

        mallas_disponibles = db.session.query(Malla).all()
        componentes_disponibles = db.session.query(Componente_quimico).all()

        return render_template(
            'pantalla_agregados/agregado_detalle.html',
            agregado=agregado,
            entidad=agregado.entidad,
            agregado_mallas=agregado_mallas,
            composicion=composicion,
            mallas_disponibles=mallas_disponibles,
            componentes_disponibles=componentes_disponibles
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Error al cargar el detalle del agregado: {str(e)}", 500

    finally:
        db.session.close()



@crud_agregado.route('/mixFamiliari_crud_agregado_agregados_mallas/<int:agregado_id>/agregar_malla', methods=['POST'])
def mixFamiliari_crud_agregado_agregados_mallas(agregado_id):
    try:
        malla_id = request.form.get("malla_id")

        if not malla_id:
            return jsonify({"error": "Falta seleccionar la malla"}), 400

        # Uso correcto de db.session para obtener la malla
        malla = db.session.query(Malla).get(int(malla_id))
        if not malla:
            return jsonify({"error": "Malla no encontrada"}), 404

        nueva = AgregadoMalla(
            agregado_id=agregado_id,
            malla_id=malla.id,
            porcentaje=0
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify({
            "success": True,
            "id": nueva.id,
            "nombre_comercial": malla.nombre_comercial,
            "diametro_mm": malla.diametro_mm
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.session.close()






@crud_agregado.route('/mixFamiliari_crud_agregado_agregados_mallas/<int:malla_agregada_id>/eliminar', methods=['DELETE'])
def eliminar_malla_de_agregado(malla_agregada_id):
    try:
        relacion = db.session.query(AgregadoMalla).get(malla_agregada_id)
        if not relacion:
            return jsonify({"error": "Relación malla-agregado no encontrada"}), 404

        db.session.delete(relacion)
        db.session.commit()
        return jsonify({"success": True})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        db.session.close()



















@crud_agregado.route('/mixFamiliari_crud_agregado_composicion/<int:agregado_id>/agregar', methods=['POST'])
def agregar_componente_agregado(agregado_id):
    try:
        componente_id = request.form.get("componente_id")
        porcentaje = request.form.get("porcentaje")
        orden = request.form.get("orden")

        if not all([componente_id, porcentaje, orden]):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        nuevo = ComposicionAgregado(
            agregado_id=agregado_id,
            componente_id=int(componente_id),
            porcentaje=float(porcentaje),
            orden=int(orden)
        )

        db.session.add(nuevo)
        db.session.commit()

        componente = db.session.query(Componente_quimico).get(int(componente_id))

        return jsonify({
            "success": True,
            "id": nuevo.id,
            "nombre": componente.nombre,
            "porcentaje": nuevo.porcentaje,
            "orden": nuevo.orden
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.session.close()





@crud_agregado.route('/mixFamiliari_crud_agregado_agregados_componente/<int:componente_agregada_id>/modificar', methods=['PUT'])
def modificar_componente_de_agregado(componente_agregada_id):
    try:
        data = request.get_json()  # Solo get_json, ya no request.form
        relacion = db.session.query(ComposicionAgregado).get(componente_agregada_id)
        if not relacion:
            return jsonify({"error": "Componente no encontrado"}), 404

        relacion.porcentaje = data.get('porcentaje')
        relacion.orden = data.get('orden')
        # Si permites cambiar el componente:
        # relacion.componente_id = data.get('componente_id')

        db.session.commit()

        return jsonify({
            "success": True,
            "id": relacion.id,
            "nombre": relacion.componente.nombre,
            "porcentaje": relacion.porcentaje,
            "orden": relacion.orden
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()









@crud_agregado.route('/mixFamiliari_crud_agregado_agregados_componente/<int:componente_agregada_id>/eliminar', methods=['DELETE'])
def eliminar_componente_de_agregado(componente_agregada_id):
    try:
        relacion = db.session.query(ComposicionAgregado).get(componente_agregada_id)
        if not relacion:
            return jsonify({"error": "Relación componente-agregado no encontrada"}), 404

        db.session.delete(relacion)
        db.session.commit()
        return jsonify({"success": True})
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        db.session.close()