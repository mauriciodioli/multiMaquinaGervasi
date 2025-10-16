# pannelli/inverter_schemas.py
from flask_marshmallow import Marshmallow
from model.pannelli.inverter_panel import InverterPanel
from model.pannelli.historial_inverter import HistorialInverter

ma = Marshmallow()

class InverterPanelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InverterPanel
        load_instance = True

class HistorialInverterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialInverter
        load_instance = True
