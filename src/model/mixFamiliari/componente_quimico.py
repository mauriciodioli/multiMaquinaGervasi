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
    materia_forma_id = db.Column(db.Integer, ForeignKey('materia_forma.id'))


    tipo_mezcla_id = db.Column(db.Integer, db.ForeignKey('tipo_mezcla.id'))
    tipo_mezcla = relationship("Tipo_mezcla", back_populates="componentes")
    materia_forma = relationship("MateriaForma", back_populates="componentes")
class Componente_quimicoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "porcentaje", "tipo_mezcla_id")
        
from src.model.mixFamiliari.materia_forma import MateriaForma  # noqa: E402
