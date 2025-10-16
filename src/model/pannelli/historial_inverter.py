# src/models/historial_inverter.py

from utils.db import db
from datetime import datetime

class HistorialInverter(db.Model):
    __tablename__ = 'historial_inverter'

    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea al panel físico
    inverter_id = db.Column(db.Integer, db.ForeignKey('inverter_panel.id'), nullable=False)

    # Fecha y hora de la lectura
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Datos eléctricos
    voltaje = db.Column(db.Float, nullable=True)
    corriente = db.Column(db.Float, nullable=True)
    potencia = db.Column(db.Float, nullable=True)
    energia = db.Column(db.Float, nullable=True)
    frecuencia = db.Column(db.Float, nullable=True)

    # Estado del equipo
    estado = db.Column(db.String(100), nullable=True)
    codigo_alarma = db.Column(db.String(100), nullable=True)

    # Payload original por si se necesitan más datos
    datos_raw = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<HistorialInverter panel_id={self.inverter_id} @ {self.timestamp}>'
