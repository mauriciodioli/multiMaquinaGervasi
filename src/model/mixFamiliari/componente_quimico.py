### Archivo: componente_quimico.py
from utils.db import db
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow

from sqlalchemy.orm import relationship

ma = Marshmallow()

class Componente_quimico(db.Model):
    __tablename__ = 'componente_quimico'
    __table_args__ = {'extend_existing': True}  

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    pais = db.Column(db.String(100))
    descripcion = db.Column(db.String(500))

    agregado_id = db.Column(db.Integer, db.ForeignKey('agregados.id'))
    tipo_mezcla_id = db.Column(db.Integer, db.ForeignKey('tipo_mezcla.id'))

    agregado = relationship("Agregado", back_populates="componentes")
    tipo_mezcla = relationship("Tipo_mezcla", back_populates="componentes")

class Componente_quimicoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "porcentaje", "tipo_mezcla_id")