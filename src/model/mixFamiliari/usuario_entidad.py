# src/model/mixFamiliari/usuario_entidad.py

from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship

ma = Marshmallow()

class UsuarioEntidad(db.Model):
    __tablename__ = 'usuario_entidad'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    entidad_id = db.Column(db.Integer, db.ForeignKey('entidadcontexto.id'), nullable=False)
    roll = db.Column(db.String(20), nullable=True)  
    
    usuario = relationship("Usuario", back_populates="entidades")
    entidad = relationship("EntidadContexto", back_populates="usuarios")


class UsuarioEntidadSchema(ma.Schema):
    class Meta:
        fields = ("id", "usuario_id", "entidad_id", "roll") 
