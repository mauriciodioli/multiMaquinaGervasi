# src/model/mixFamiliari/agregado_malla.py

from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

class AgregadoMalla(db.Model):
    __tablename__ = 'agregado_malla'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    agregado_id = db.Column(db.Integer, ForeignKey('agregados.id'))
    malla_id = db.Column(db.Integer, ForeignKey('mallas.id'))
    porcentaje = db.Column(db.Float, nullable=False)

    agregado = relationship("Agregado", back_populates="mallas")
    malla = relationship("Malla", back_populates="agregados_asociados")

class AgregadoMallaSchema(ma.Schema):
    class Meta:
        fields = ("id", "agregado_id", "malla_id", "porcentaje")
from src.model.mixFamiliari.malla import Malla  # 🔁 IMPORT AL FINAL para evitar errores

