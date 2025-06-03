### Archivo: categoria_mezcla.py
from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class Categoria_mezcla(db.Model):
    __tablename__ = 'categoria_mezcla'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    familia_id = db.Column(db.Integer, ForeignKey('mix_familiari.id'))

    tipos = db.relationship("Tipo_mezcla", backref="categoria", cascade="all, delete")

class Categoria_mezclaSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "familia_id")

