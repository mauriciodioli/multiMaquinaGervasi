# migrar_access_sqlserver.py
import pyodbc
import pandas as pd

def migrar_tabla(access_db_path, tabla_access, sql_database, sql_user, sql_password,ip,port):
    access_conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"Dbq={access_db_path};"
    )
    access_conn = pyodbc.connect(access_conn_str)
    df = pd.read_sql(f"SELECT * FROM [{tabla_access}]", access_conn)
    access_conn.close()
   
    
    print("[DEBUG] Cadena de conexión:",f"SERVER={ip},{port}; DATABASE={sql_database}; UID={sql_user}; PASS={sql_password}; ...")
    print("[DEBUG] Base a usar:", sql_database)
    
    
    
    # Crear DB si no existe
    conn_master = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={ip},{port};"
        f"DATABASE=master;"
        f"UID={sql_user};"
        f"PWD={sql_password};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    conn_master.autocommit = True  # ✅ PRIMERO activás autocommit

    cursor_master = conn_master.cursor()
    cursor_master.execute(f"IF DB_ID('{sql_database}') IS NULL CREATE DATABASE [{sql_database}]")
    
    conn_master.commit()
    cursor_master.close()
    conn_master.close()
    print(f"[INFO] Verificación de base '{sql_database}' completada.")
    
   
    sqlserver_conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={ip},{port};"
        f"DATABASE={sql_database};"
        f"UID={sql_user};"
        f"PWD={sql_password};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    sql_conn = pyodbc.connect(sqlserver_conn_str)
    cursor = sql_conn.cursor()

    cols = ", ".join(f"[{col}] NVARCHAR(MAX)" for col in df.columns)
    create_sql = f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{tabla_access}' AND xtype='U') " \
                 f"CREATE TABLE [{tabla_access}] ({cols})"
    cursor.execute(create_sql)
    sql_conn.commit()

    for _, row in df.iterrows():
        placeholders = ", ".join("?" * len(row))
        insert_sql = f"INSERT INTO [{tabla_access}] VALUES ({placeholders})"
        cursor.execute(insert_sql, tuple(row))
    sql_conn.commit()

    cursor.close()
    sql_conn.close()

    print(f" Migración de la tabla '{tabla_access}' completada.")
