from flask import Blueprint, render_template, request, redirect, url_for,jsonify,abort,make_response
from src.model.maquina import Maquina
from src.model.usuario import Usuario
from utils.db import db
from datetime import datetime
import json
from src.utils.get_textos_menu  import get_textos_menu

crud_maquinas = Blueprint('crud_maquinas', __name__)



@crud_maquinas.route('/maquinas_crud_consulta/', methods=['GET', 'POST'])
def maquinas_crud():
    try:
        if request.method == 'POST':
            data = request.get_json()
            user_id = request.cookies.get("user_id")
        else:
            user_id = request.cookies.get("user_id")

        if user_id:
            usuario = db.session.query(Usuario).get(int(user_id))
            maquinas = db.session.query(Maquina).filter_by(user_id=int(user_id)).all()
        else:
            usuario = None
            maquinas = db.session.query(Maquina).all()

        for m in maquinas:
            if isinstance(m.setting, str):
                try:
                    m.setting = json.loads(m.setting)
                except:
                    m.setting = {}

        lang = request.cookies.get("lang", "es")
        t_menu = get_textos_menu(lang)

        response = make_response(render_template('maquinas/CRUD_maquinas.html', maquinas=maquinas, t_menu=t_menu))

        # ✅ Agregamos la cookie del correo si el usuario existe
        if usuario:
            response.set_cookie("correo_electronico", usuario.correo_electronico, max_age=60*60*24*30)  # 30 días

        return response

    except Exception as e:
        db.session.rollback()
        return f"Error conectando a la base de datos: {e}"

    finally:
        db.session.close()







#ALTA
@crud_maquinas.route('/maquinas_crud/agregar/', methods=['POST'])
def agregar_maquina():
    try:
        data = request.get_json()

        try:
            settings_dict = json.loads(data.get("setting", "{}"))
        except:
            settings_dict = {}

        settings_dict["modulos"] = data.get("modulos", [])
        passwordCuenta = "123456789"
        nueva = Maquina(
            user_id=int(data["user_id"]),
            userCuenta=data["userCuenta"],
            passwordCuenta=passwordCuenta.encode('utf-8'),
            accountCuenta=data.get("accountCuenta"),
            nombre=data.get("nombre"),
            ruta=data.get("ruta"),
            nombreDb=data.get("nombreDb"),
            nombreTabla=data.get("nombreTabla"),  # Nuevo campo
            selector=data.get("selector"),
            sector=data.get("sector"),
            estado=data.get("estado"),
            potencia=data.get("potenza"),
            fecha=datetime.now(),
            setting=settings_dict
        )

        db.session.add(nueva)
        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error al agregar máquina: {e}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

    finally:
        db.session.close()


# BAJA
@crud_maquinas.route('/maquinas_crud/eliminar/<int:id>', methods=['DELETE'])
def eliminar_maquina(id):
    try:
        maquina = db.session.get(Maquina, id)  # 👈 acceso directo con SQLAlchemy 1.4+
        if not maquina:
            abort(404, description="Máquina no encontrada")

        db.session.delete(maquina)
        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

    finally:
        db.session.close()



# MODIFICACIÓN
@crud_maquinas.route('/maquinas_crud/modificar/<int:id>', methods=['PUT'])
def modificar_maquina(id):
    try:
        data = request.get_json()
        print(f"[DEBUG] Payload recibido: {data}")  # 🐞 Imprime todo el JSON recibido

        maquina = db.session.get(Maquina, id)
        if not maquina:
            return jsonify({"success": False, "message": "Máquina no encontrada"})

        # Actualizar campos básicos
        maquina.userCuenta = data.get("userCuenta", maquina.userCuenta)
        if data.get("passwordCuenta"):
            maquina.passwordCuenta = data["passwordCuenta"].encode('utf-8')
        maquina.accountCuenta = data.get("accountCuenta")
        maquina.nombre = data.get("nombre")
        maquina.ruta = data.get("ruta")
       
        maquina.nombreDb = data.get("nombreDb")
        maquina.nombreTabla = data.get("nombreTabla")  
        maquina.selector = data.get("selector")
        maquina.sector = data.get("sector")
        maquina.estado = data.get("estado")
        maquina.potencia = float(data.get("potencia"))

        # Procesar setting con JSON
        setting_raw = data.get("setting")
        print(f"[DEBUG] Setting recibido: {setting_raw}")  # 🐞 Imprime el setting tal como llegó

        if isinstance(setting_raw, str):
            try:
                setting_dict = json.loads(setting_raw)
            except Exception as e:
                print(f"[ERROR] Fallo al parsear setting: {e}")  # 🐞 Log del error
                return jsonify({"success": False, "message": f"JSON inválido en setting: {e}"})
        else:
            setting_dict = setting_raw

        maquina.setting = json.dumps(setting_dict)  # ✅ Guarda como JSON string

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Excepción general: {e}")  # 🐞 Log de error general
        return jsonify({"success": False, "message": str(e)})

    finally:
        db.session.close()



