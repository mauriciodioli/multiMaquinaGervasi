from flask import Blueprint
from datetime import datetime, timedelta
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from utils.db import db

ma = Marshmallow()
sesionUsuario = Blueprint('sesionUsuario', __name__)

class SesionUsuario(db.Model):
    __tablename__ = 'sesiones_usuario'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, ForeignKey('usuarios.id'), nullable=False)
    entidad_id = db.Column(db.Integer, ForeignKey('entidadcontexto.id'), nullable=True)

    token = db.Column(db.String(512), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    expira_en = db.Column(db.DateTime, nullable=False)
    ip_origen = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)

    pais = db.Column(db.String(100))

    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
    entidad = relationship("EntidadContexto", back_populates="sesiones_usuario")

    def __init__(self, usuario_id, token, expira_en=None, ip_origen=None, user_agent=None, pais=None, entidad_id=None):
        self.usuario_id = usuario_id
        self.token = token
        self.creado_en = datetime.utcnow()
        self.expira_en = expira_en or (self.creado_en + timedelta(hours=24))
        self.ip_origen = ip_origen
        self.user_agent = user_agent
        self.pais = pais
        self.entidad_id = entidad_id
        self.activo = True

    def __repr__(self):
        return f"<SesionUsuario {self.id} | Usuario {self.usuario_id} | Activo: {self.activo}>"

class SesionUsuarioSchema(ma.SQLAlchemySchema):
    class Meta:
        fields = ("id", 
                  "usuario_id", 
                  "entidad_id", 
                  "token", 
                  "creado_en", 
                  "expira_en",
                  "ip_origen",
                  "user_agent",
                  "pais",
                  "activo"
                  )

  
   
