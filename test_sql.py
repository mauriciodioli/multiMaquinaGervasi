import pyodbc
import urllib.parse

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.1.250,1433;"
    "DATABASE=multiMaquinaDB;"
    "UID=multimaquinaadmin;"
    "PWD=Dpia1234!;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=192.168.1.250,1433;DATABASE=multiMaquinaDB;UID=multimaquinaadmin;PWD=Dpia1234!;Encrypt=no;TrustServerCertificate=yes;")

print("✔️ Conexión exitosa")
conn.close()




