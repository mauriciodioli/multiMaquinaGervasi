### Archivo: componente_quimico.py
from utils.db import db
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class Componente_quimico(db.Model):
    __tablename__ = 'componente_quimico'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_mezcla.id'))  # relación correcta

    tipo = db.relationship("Tipo_mezcla", back_populates="componentes")
class Componente_quimicoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "porcentaje", "tipo_mezcla_id")