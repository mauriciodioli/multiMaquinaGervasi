# src/model/mixFamiliari/entidad_contexto.py
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy.orm import relationship

ma = Marshmallow()

class EntidadContexto(db.Model):
    __tablename__ = 'entidadcontexto'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500))
    estado = db.Column(db.Integer, nullable=False, default=1)
    pais = db.Column(db.String(100), nullable=True)


    agregados = relationship("Agregado", back_populates="entidad")
    usuarios = relationship("UsuarioEntidad", back_populates="entidad", cascade="all, delete")  # ⚠️ esta línea necesita que UsuarioEntidad esté ya cargada



class EntidadContextoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "tipo", "descripcion", "estado", "pais")
        
from src.model.mixFamiliari.usuario_entidad import UsuarioEntidad
