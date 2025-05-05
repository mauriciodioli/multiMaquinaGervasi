# model/maquina.py

from flask import Blueprint
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy.orm import relationship
from src.model.usuario import Usuario  # Ojo la ruta: src.model.usuario

ma = Marshmallow()
maquina = Blueprint('maquina', __name__)

class Maquina(db.Model):
    __tablename__ = 'maquinas'
    __table_args__ = {'extend_existing': True}  

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    userCuenta = db.Column(db.String(120), nullable=False)
    passwordCuenta = db.Column(db.LargeBinary(128), nullable=False)
    accountCuenta = db.Column(db.String(500), nullable=True)

    nombre = db.Column(db.String(255))
    ruta = db.Column(db.String(255))
    port = db.Column(db.String(255))
    nombreDb = db.Column(db.String(255))
    selector = db.Column(db.String(255))
    sector = db.Column(db.String(255))
    fecha = db.Column(db.DateTime)
    estado = db.Column(db.String(100))
    setting = db.Column(db.JSON)
    potencia = db.Column(db.Float)

    usuario = relationship('Usuario', back_populates='maquinas')

    def __init__(self, user_id, userCuenta, passwordCuenta, accountCuenta=None,
                 nombre=None, ruta=None,port=None, nombreDb=None, selector=None, sector=None, fecha=None, estado=None, setting=None, potencia=None):
        self.potencia = potencia
        self.user_id = user_id
        self.userCuenta = userCuenta
        self.passwordCuenta = passwordCuenta
        self.accountCuenta = accountCuenta
        self.nombre = nombre
        self.ruta = ruta
        self.port = port
        self.nombreDb = nombreDb
        self.selector = selector
        self.sector = sector
        self.fecha = fecha
        self.estado = estado
        self.setting = setting

    def __repr__(self):
        return f"<Maquina id={self.id} userCuenta={self.userCuenta}>"

# Schema para serializar
# Schema de serialización
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "user_id","nombreDb","ruta","port","nombreDb")
mer_schema = MerShema()
mer_shema = MerShema(many=True)
