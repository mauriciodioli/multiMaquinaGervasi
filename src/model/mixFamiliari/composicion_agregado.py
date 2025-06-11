# src/model/mixFamiliari/composicion_agregado.py

from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

ma = Marshmallow()

class ComposicionAgregado(db.Model):
    __tablename__ = 'composicion_agregado'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    componente_id = db.Column(db.Integer, ForeignKey('componente_quimico.id'))
    agregado_id = db.Column(db.Integer, ForeignKey('agregados.id'))
    porcentaje = db.Column(db.Float, nullable=False)
    orden = db.Column(db.Integer) 

    componente = relationship("Componente_quimico", backref="composiciones")
    agregado = relationship("Agregado", back_populates="composiciones")


class ComposicionAgregadoSchema(ma.Schema):
    class Meta:
        fields = ("id", "componente_id", "agregado_id", "porcentaje", "orden")
