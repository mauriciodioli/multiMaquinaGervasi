from flask_marshmallow import Marshmallow
from flask import Blueprint
from utils.db import db
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
# ❌ NO importes CategoriaMezcla aquí para evitar import circular
# from .categoria_mezcla import CategoriaMezcla

ma = Marshmallow()

mix_familiari = Blueprint('mix_familiari', __name__)

class Mix_familiari(db.Model):
    __tablename__ = 'mix_familiari'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(500), unique=True, nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    idioma = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.String(500), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    estado = db.Column(db.String(500), nullable=True)

    categorias = db.relationship("Categoria_mezcla", backref="familia", cascade="all, delete")  # 👈 string OK

    def __init__(self, nombre, descripcion, color, idioma=None, valor=None, estado=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.idioma = idioma
        self.valor = valor
        self.color = color
        self.estado = estado

    @classmethod
    def crear_tabla(cls):
        insp = inspect(db.engine)
        if not insp.has_table(cls.__tablename__):
            db.create_all()

class Mix_familiariSchema(ma.Schema):
    class Meta:
        fields = ("id", "nombre", "descripcion", "idioma", "color", "valor", "estado")
