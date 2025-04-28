import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = (
        r"access+pyodbc:///?Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ= C:\\Users\\Tecnico03\\Documents\\ProyectoMultiMaquina\\si-cam.mdb;"       
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

 