# src/model/mixFamiliari/agregado.py
from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship

ma = Marshmallow()
agregado = Blueprint('agregado', __name__)

class Agregado(db.Model):
    __tablename__ = 'agregados'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500))
    estado = db.Column(db.Boolean, default=True)
    idioma = db.Column(db.String(50))
    pais = db.Column(db.String(100))

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    entidad_id = db.Column(db.Integer, db.ForeignKey('entidadcontexto.id'))
    
    usuario = relationship("Usuario", back_populates="agregados")
    entidad = relationship("EntidadContexto", back_populates="agregados")

    analisis = relationship("AnalisisGranulometrico", back_populates="agregado", cascade="all, delete")
    composiciones = relationship("ComposicionAgregado", back_populates="agregado", cascade="all, delete")
    mallas = relationship("AgregadoMalla", back_populates="agregado", cascade="all, delete")
  
    @classmethod
    def crear_tabla(cls):
        insp = inspect(db.engine)
        if not insp.has_table(cls.__tablename__):
            db.create_all()

class AgregadoSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "nombre", "descripcion", "estado", "idioma",
            "usuario_id", "entidad_id", "pais"
            # "malla_id"  # Eliminado
        )


# 👇 Import necesario al final para evitar errores de relación
from src.model.entidad_contexto import EntidadContexto
from src.model.mixFamiliari.composicion_agregado import ComposicionAgregado
from src.model.mixFamiliari.agregado_malla import AgregadoMalla