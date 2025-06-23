from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

ma = Marshmallow()

class RecomendacionMejora(db.Model):
    __tablename__ = 'recomendacionMejora'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tamiz = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    sugerencia = db.Column(db.String(500), nullable=True)

    analisis_id = db.Column(db.Integer, ForeignKey('analisis_granulometrico.id'), nullable=False)
    analisis = relationship("AnalisisGranulometrico")

class RecomendacionMejoraSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "tamiz", "valor", "sugerencia", "analisis_id"
        )