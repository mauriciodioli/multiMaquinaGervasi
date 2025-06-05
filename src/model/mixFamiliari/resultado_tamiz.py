# src/model/mixFamiliari/resultado_tamiz.py

from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

ma = Marshmallow()

class ResultadoTamiz(db.Model):
    __tablename__ = 'resultado_tamiz'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tamiz = db.Column(db.String(100), nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)

    analisis_id = db.Column(db.Integer, ForeignKey('analisis_granulometrico.id'), nullable=False)
    analisis = relationship("AnalisisGranulometrico", back_populates="resultados")


class ResultadoTamizSchema(ma.Schema):
    class Meta:
        fields = ("id", "tamiz", "porcentaje", "analisis_id")
