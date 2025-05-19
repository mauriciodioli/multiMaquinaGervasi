# model/conexion_db.py

from flask import Blueprint
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy.orm import relationship
from src.model.usuario import Usuario  # Ojo la ruta: src.model.usuario

ma = Marshmallow()
conexion_db = Blueprint('conexion_db', __name__)

class Conexion_db(db.Model):
    __tablename__ = 'conexion_db'
    __table_args__ = {'extend_existing': True}  

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    driver = db.Column(db.String(255))
    ipSqlServer = db.Column(db.String(120), nullable=False)
    portSqlServer = db.Column(db.String(120), nullable=False)
    database = db.Column(db.String(255))   
    userSqlServer = db.Column(db.String(120), nullable=False)
    pasSqlServer = db.Column(db.String(500), nullable=True)    
    encrypt = db.Column(db.String(255))
    trustServerCertificate = db.Column(db.String(255))    
    sector = db.Column(db.String(255))
    fecha = db.Column(db.DateTime)
    estado = db.Column(db.String(100))
   

    usuario = relationship('Usuario', back_populates='conexion_db')

    def __init__(self, user_id, driver, ipSqlServer, portSqlServer=None,
             database=None, userSqlServer=None, pasSqlServer=None, 
             encrypt=None, trustServerCertificate=None, sector=None, fecha=None, estado=None):
        self.user_id = user_id
        self.driver = driver
        self.ipSqlServer = ipSqlServer
        self.portSqlServer = portSqlServer or "1433"  # Valor predeterminado si no se pasa
        self.database = database
        self.userSqlServer = userSqlServer
        self.pasSqlServer = pasSqlServer
        self.encrypt = encrypt
        self.trustServerCertificate = trustServerCertificate
        self.sector = sector
        self.fecha = fecha
        self.estado = estado

 

    def __repr__(self):
        return f"<Conexion_db id={self.id} database={self.database}>"

# Schema para serializar
class MerShema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "database", "portSqlServer", "ipSqlServer", "driver")

# Crear las instancias del esquema
mer_schema = MerShema()  # Para un solo objeto
mer_schemas = MerShema(many=True)  # Para múltiples objetos
