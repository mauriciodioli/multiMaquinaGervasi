from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship  # <- necesario
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class Malla(db.Model):
    __tablename__ = 'mallas'
    __table_args__ = {'extend_existing': True}  

    id = db.Column(db.Integer, primary_key=True)
    nombre_comercial = db.Column(db.String(50))
    diametro_mm = db.Column(db.Float)

  
    agregados_asociados = relationship("AgregadoMalla", back_populates="malla", cascade="all, delete")



class Tipo_mallasSchema(ma.Schema):
    class Meta:
         fields = ("id", "nombre_comercial", "diametro_mm", "porcentaje_pasa")
         