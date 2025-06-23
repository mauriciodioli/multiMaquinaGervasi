from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

ma = Marshmallow()

class DiagnosticoAnalisis(db.Model):
    __tablename__ = 'diagnosticoAnalisis'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    error_promedio = db.Column(db.Float, nullable=False)
    evalucion = db.Column(db.String(500), nullable=True)
    mensaje = db.Column(db.Text, nullable=True)
   
    analisis_id = db.Column(db.Integer, ForeignKey('analisis_granulometrico.id'), nullable=False)
    analisis = relationship("AnalisisGranulometrico", back_populates="diagnosticos")

class DiagnosticoAnalisisSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "error_promedio", "evalucion", "mensaje", "analisis_id"
        )