from flask import Flask
from flask_cors import CORS
from config.config import Config
from src.controller.trabajo_controller import trabajos_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(trabajos_bp)

    return app
