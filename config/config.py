import os
from dotenv import load_dotenv
import urllib

load_dotenv()

class Config:
    SQLSERVER_DRIVER = os.getenv("SQLSERVER_DRIVER")
    SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
    SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE")
    SQLSERVER_PORT = os.getenv("SQLSERVER_PORT", "1433")
    SQLSERVER_TRUSTED_CONNECTION = os.getenv("SQLSERVER_TRUSTED_CONNECTION", "yes")

    params = urllib.parse.quote_plus(
        f"DRIVER={SQLSERVER_DRIVER};"
        f"SERVER={SQLSERVER_HOST};"
        f"DATABASE={SQLSERVER_DATABASE};"
        f"Trusted_Connection={SQLSERVER_TRUSTED_CONNECTION};"
    )

    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

