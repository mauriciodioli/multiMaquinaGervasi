### Archivo: tipo_mezcla.py
from utils.db import db
from sqlalchemy import ForeignKey
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class Tipo_mezcla(db.Model):
    __tablename__ = 'tipo_mezcla'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    categoria_id = db.Column(db.Integer, ForeignKey('categoria_mezcla.id'))

    componentes = db.relationship("ComponenteQuimico", backref="mezcla", cascade="all, delete")

class Tipo_mezclaSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "categoria_id")
