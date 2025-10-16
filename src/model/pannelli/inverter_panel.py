# src/models/historial_inverter.py

# src/models/inverter_panel.py
from flask_marshmallow import Marshmallow
from utils.db import db
from sqlalchemy import inspect

ma = Marshmallow()

class InverterPanel(db.Model):
    __tablename__ = 'inverter_panel'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # nombre descriptivo
    marca = db.Column(db.String(50), nullable=False)     # IME, Danfoss, etc.
    modelo = db.Column(db.String(100), nullable=True)    # modelo del equipo
    ubicacion = db.Column(db.String(200), nullable=True) # ubicación física o zona
    serial_number = db.Column(db.String(100), unique=True, nullable=False)

    # Relación con historial
    historial = db.relationship('HistorialInverter', backref='inverter', lazy=True)

    def __repr__(self):
        return f'<InverterPanel {self.marca} - {self.serial_number}>'
    @classmethod
    def crear_tabla(cls):
        insp = inspect(db.engine)
        if not insp.has_table(cls.__tablename__):
            db.create_all()

class InverterPanelSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "nombre", "marca", "modelo", "ubicacion",
            "serial_number"
        )
