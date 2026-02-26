# src/model/pais_contexto.py
from flask_marshmallow import Marshmallow
from utils.db import db

ma = Marshmallow()


class PaisContexto(db.Model):
    __tablename__ = 'paiscontexto'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    codigo = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(500))
    estado = db.Column(db.Integer, nullable=False, default=1)


class PaisContextoSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "codigo", "descripcion", "estado")
