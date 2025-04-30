# src/model/usuario.py

from flask import Blueprint
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy.orm import relationship

ma = Marshmallow()
usuario = Blueprint('usuario', __name__)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True}  

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activo = db.Column(db.Boolean, nullable=False, default=False)
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    token = db.Column(db.String(1000), nullable=True)
    roll = db.Column(db.String(20), nullable=False, default='regular')
    refresh_token = db.Column(db.String(1000), nullable=True)
    calendly_url = db.Column(db.String(255), nullable=True)
    
    maquinas = relationship('Maquina', back_populates='usuario')

    def __init__(self, correo_electronico, password, roll='regular', activo=False,
                 token=None, refresh_token=None, calendly_url=None):
        self.correo_electronico = correo_electronico
        self.password = password
        self.roll = roll
        self.activo = activo
        self.token = token
        self.refresh_token = refresh_token
        self.calendly_url = calendly_url

    def __repr__(self):
        return f"<Usuario {self.id} - {self.correo_electronico}>"

# Schema de serialización
class MerShema(ma.Schema):
    class Meta:
        fields = ("id",  "correo_electronico","token","refresh_token","activo","password","roll")
mer_schema = MerShema()
mer_shema = MerShema(many=True)
