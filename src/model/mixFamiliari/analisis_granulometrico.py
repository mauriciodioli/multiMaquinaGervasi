from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

ma = Marshmallow()

class AnalisisGranulometrico(db.Model):
    __tablename__ = 'analisis_granulometrico'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(500))
    d_max = db.Column(db.Float, nullable=True)
    n = db.Column(db.Float, nullable=True)

    agregado_id = db.Column(db.Integer, ForeignKey('agregados.id'), nullable=False)
    usuario_id = db.Column(db.Integer, ForeignKey('usuarios.id'), nullable=False)

    agregado = relationship("Agregado", back_populates="analisis")
    usuario = relationship("Usuario", back_populates="analisis")
    resultados = relationship("ResultadoTamiz", back_populates="analisis", cascade="all, delete")
    recomendaciones = relationship("RecomendacionMejora", back_populates="analisis", cascade="all, delete")  # <-- Agrega esta línea
    diagnosticos = relationship("DiagnosticoAnalisis", back_populates="analisis", cascade="all, delete")
    pesos_zona = relationship("PesoZonaMezcla", back_populates="analisis", cascade="all, delete")
    proporciones_optimas = relationship("ProporcionOptima", back_populates="analisis", cascade="all, delete")

class AnalisisGranulometricoSchema(ma.Schema):
    class Meta:
        fields = ("id", "fecha", "descripcion", "d_max", "n", "agregado_id", "usuario_id")

from src.model.mixFamiliari.resultado_tamiz import ResultadoTamiz
from src.model.mixFamiliari.recomendacionMejora import RecomendacionMejora  # <-- Importa el modelo
from src.model.mixFamiliari.diagnosticoAnalisis import DiagnosticoAnalisis
from src.model.mixFamiliari.pesoZonaMezcla import PesoZonaMezcla
from src.model.mixFamiliari.proporcionOptima import ProporcionOptima
