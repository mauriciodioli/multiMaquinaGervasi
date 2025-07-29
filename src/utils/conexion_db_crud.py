from flask import Blueprint, request, jsonify
from utils.db import db
from src.model.conexion_db import Conexion_db, mer_schema, mer_schemas
from src.utils.db_session import get_db_session

# Crear Blueprint
conexion_db_crud = Blueprint('conexion_db_crud', __name__)

# 1. Crear una nueva conexión
@conexion_db_crud.route('/conexion_db/', methods=['POST'])
def crear_conexion_db():
    try:
        data = request.get_json()

        # Obtener los datos del JSON
        user_id = data.get('user_id')
        driver = data.get('driver')
        ipSqlServer = data.get('ipSqlServer')
        portSqlServer = data.get('portSqlServer', '1433')  # Valor por defecto
        database = data.get('database')
        userSqlServer = data.get('userSqlServer')
        pasSqlServer = data.get('pasSqlServer')
        encrypt = data.get('encrypt')
        trustServerCertificate = data.get('trustServerCertificate')
        sector = data.get('sector')
        fecha = data.get('fecha')
        estado = data.get('estado')
        with get_db_session() as session:
            # Crear la instancia de Conexion_db
            nueva_conexion = Conexion_db(
                user_id=user_id,
                driver=driver,
                ipSqlServer=ipSqlServer,
                portSqlServer=portSqlServer,
                database=database,
                userSqlServer=userSqlServer,
                pasSqlServer=pasSqlServer,
                encrypt=encrypt,
                trustServerCertificate=trustServerCertificate,
                sector=sector,
                fecha=fecha,
                estado=estado
            )

            # Agregar a la sesión y confirmar
            session.add(nueva_conexion)
            session.commit()

            return jsonify(mer_schema.dump(nueva_conexion)), 201  # Devuelve la conexión creada
    except Exception as e:        
        return jsonify({"error": str(e)}), 500  # Manejo de errores en caso de excepción
    


# 2. Obtener todas las conexiones
@conexion_db_crud.route('/conexion_db', methods=['GET'])
def obtener_conexiones_db():
    conexiones = Conexion_db.query.all()
    return jsonify(mer_schemas.dump(conexiones)), 200


# 3. Obtener una conexión por ID
@conexion_db_crud.route('/conexion_db/<int:id>', methods=['GET'])
def obtener_conexion_db(id):
    with get_db_session() as session:
        conexion = session.query(Conexion_db).filter_by(id=id).first()

        
        if conexion:
            return jsonify(mer_schema.dump(conexion)), 200
    return jsonify({"error": "Conexión no encontrada"}), 404


# 4. Actualizar una conexión por ID
@conexion_db_crud.route('/conexion_db/<int:id>', methods=['PUT'])
def actualizar_conexion_db(id):
    try:
        with get_db_session() as session:
            conexion = session.query(Conexion_db).filter_by(id=id).first()
            if not conexion:
                return jsonify({"error": "Conexión no encontrada"}), 404

            data = request.get_json()

            # Actualizar los campos
            conexion.user_id = data.get('user_id', conexion.user_id)
            conexion.driver = data.get('driver', conexion.driver)
            conexion.ipSqlServer = data.get('ipSqlServer', conexion.ipSqlServer)
            conexion.portSqlServer = data.get('portSqlServer', conexion.portSqlServer)
            conexion.database = data.get('database', conexion.database)
            conexion.userSqlServer = data.get('userSqlServer', conexion.userSqlServer)
            conexion.pasSqlServer = data.get('pasSqlServer', conexion.pasSqlServer)
            conexion.encrypt = data.get('encrypt', conexion.encrypt)
            conexion.trustServerCertificate = data.get('trustServerCertificate', conexion.trustServerCertificate)
            conexion.sector = data.get('sector', conexion.sector)
            conexion.fecha = data.get('fecha', conexion.fecha)
            conexion.estado = data.get('estado', conexion.estado)

            # Guardar cambios
            session.commit()

            return jsonify(mer_schema.dump(conexion)), 200
    except Exception as e:        
        return jsonify({"error": f"Error actualizando conexión: {str(e)}"}), 500

@conexion_db_crud.route('/conexion_db/<int:id>', methods=['DELETE'])
def eliminar_conexion_db(id):
    try:
        with get_db_session() as session:
            conexion = session.get(Conexion_db, id)
            if not conexion:
                return jsonify({"error": "Conexión no encontrada"}), 404

            session.delete(conexion)
            session.commit()

            return jsonify({"message": "Conexión eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error eliminando conexión: {str(e)}"}), 500
