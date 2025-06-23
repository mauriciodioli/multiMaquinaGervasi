from utils.db import db
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

ma = Marshmallow()

class PesoZonaMezcla(db.Model):
    __tablename__ = 'pesoZonaMezcla'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)   
    nombre_mezcla = db.Column(db.String(500), nullable=True)
    zona = db.Column(db.String(100), nullable=False)  
    porcentaje = db.Column(db.Float, nullable=False)
   
    analisis_id = db.Column(db.Integer, ForeignKey('analisis_granulometrico.id'), nullable=False)
    analisis = relationship("AnalisisGranulometrico", back_populates="pesos_zona")

class PesoZonaMezclaSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "nombre_mezcla", "zona", "porcentaje", "analisis_id"
        )