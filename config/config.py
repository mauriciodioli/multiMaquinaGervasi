import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('/app/.env'))
#load_dotenv()
#load_dotenv(Path(__file__).resolve().parent / ".env")  # carga /config/.env


class Config:
    
    SECRET_KEY = os.getenv("SECRET_KEY", "2462128990")  # <<🔐 necesario
    
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
    
    
    
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    host = os.environ["MYSQL_HOST"]
    database = os.environ["MYSQL_DATABASE"]
    port = os.environ["MYSQL_PORT"]  # Asegúrate de tener la variable de entorno MYSQL_PORT configurada
     # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    BOCHU_APP_ID =  os.environ["BOCHU_APP_ID"]        # ej: "op18fae905315
    BOCHU_APP_SECRET =  os.environ["BOCHU_APP_SECRET"] # ej: "1e02e5f10c2f4bcd..."
    BOCHU_ORG_CODE = os.environ.get("BOCHU_ORG_CODE")
    BOCHU_BASE_URL = os.environ.get("BOCHU_BASE_URL")
    
