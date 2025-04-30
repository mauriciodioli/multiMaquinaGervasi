import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()  # Cargar variables del .env

class Config:
    SQLSERVER_DRIVER = os.getenv("SQLSERVER_DRIVER")
    SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
    SQLSERVER_PORT = os.getenv("SQLSERVER_PORT")
    SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE")
    SQLSERVER_USER = os.getenv("SQLSERVER_USER")
    SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
    SQLSERVER_ENCRYPT = os.getenv("SQLSERVER_ENCRYPT", "no")
    SQLSERVER_TRUST_CERTIFICATE = os.getenv("SQLSERVER_TRUST_CERTIFICATE", "yes")

    params = urllib.parse.quote_plus(
        f"DRIVER={SQLSERVER_DRIVER};"
        f"SERVER={SQLSERVER_HOST},{SQLSERVER_PORT};"
        f"DATABASE={SQLSERVER_DATABASE};"
        f"UID={SQLSERVER_USER};"
        f"PWD={SQLSERVER_PASSWORD};"
        f"Encrypt={SQLSERVER_ENCRYPT};"
        f"TrustServerCertificate={SQLSERVER_TRUST_CERTIFICATE};"
    )

    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False



