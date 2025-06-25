from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship  # <- necesario
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class MateriaForma(db.Model):
    __tablename__ = "materia_forma"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    origen = db.Column(db.String(200), nullable=False)
    forma = db.Column(db.String(500))
    descripcion = db.Column(db.String(500))
    estado = db.Column(db.Boolean, nullable=False, default=True)

    componentes = relationship("Componente_quimico", back_populates="materia_forma")


class Materia_formaSchema(ma.Schema):
    class Meta:
         fields = ("id", "origen", "forma", "descripcion", "estado")
