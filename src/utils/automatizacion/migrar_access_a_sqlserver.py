import pyodbc
import pandas as pd


def conectar_a_sql_server(database, user, password, ip, port):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={ip},{port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def crear_base_si_no_existe(sql_database, sql_user, sql_password, ip, port):
    conn_master = conectar_a_sql_server("master", sql_user, sql_password, ip, port)
    conn_master.autocommit = True
    cursor = conn_master.cursor()
    cursor.execute(f"IF DB_ID('{sql_database}') IS NULL CREATE DATABASE [{sql_database}]")
    conn_master.commit()
    cursor.close()
    conn_master.close()
    print(f"[INFO] Verificación de base '{sql_database}' completada.")


def crear_tabla_si_no_existe(cursor, tabla_access, df):
    cols = ", ".join(f"[{col}] NVARCHAR(MAX)" for col in df.columns)
    create_sql = (
        f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{tabla_access}' AND xtype='U') "
        f"CREATE TABLE [{tabla_access}] ({cols})"
    )
    cursor.execute(create_sql)


def limpiar_tabla(cursor, tabla_access):
    cursor.execute(f"DELETE FROM [{tabla_access}]")
    print(f"[INFO] Tabla '{tabla_access}' limpiada antes de la migración.")

def tabla_existe_en_access(conn, nombre_tabla):
    cursor = conn.cursor()
    tablas = [r[2] for r in cursor.tables(tableType='TABLE')]
    return nombre_tabla in tablas


def migrar_tabla(access_db_path, tabla_access, sql_database, sql_user, sql_password, ip, port):
    access_conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"Dbq={access_db_path};"
    )
    access_conn = pyodbc.connect(access_conn_str)

    # 👇 Validar si la tabla existe en el archivo Access antes de continuar
    if not tabla_existe_en_access(access_conn, tabla_access):
        print(f"[WARN] Tabla '{tabla_access}' no encontrada en Access. Se omite esta migración.")
        access_conn.close()
        return

    df = pd.read_sql(f"SELECT * FROM [{tabla_access}]", access_conn)
    access_conn.close()

    print("[DEBUG] Cadena de conexión:", f"SERVER={ip},{port}; DATABASE={sql_database}; UID={sql_user}; ...")
    print("[DEBUG] Base a usar:", sql_database)

    crear_base_si_no_existe(sql_database, sql_user, sql_password, ip, port)

    sql_conn = conectar_a_sql_server(sql_database, sql_user, sql_password, ip, port)
    cursor = sql_conn.cursor()

    crear_tabla_si_no_existe(cursor, tabla_access, df)
    limpiar_tabla(cursor, tabla_access)
    sql_conn.commit()

    for _, row in df.iterrows():
        placeholders = ", ".join("?" * len(row))
        insert_sql = f"INSERT INTO [{tabla_access}] VALUES ({placeholders})"
        cursor.execute(insert_sql, tuple(row))

    sql_conn.commit()
    cursor.close()
    sql_conn.close()
    print(f"✅ Migración de la tabla '{tabla_access}' completada.")


