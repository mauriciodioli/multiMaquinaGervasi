import pyodbc
import os

def exportar_mdb_a_sql(mdb_path, output_sql):
    # Conexión
    conn_str = (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={mdb_path};'
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Obtener todas las tablas
    tablas = [tabla.table_name for tabla in cursor.tables(tableType='TABLE')]

    with open(output_sql, 'w', encoding='utf-8') as f:
        for tabla in tablas:
            cursor.execute(f"SELECT * FROM [{tabla}]")
            columnas = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                valores = []
                for valor in row:
                    if valor is None:
                        valores.append('NULL')
                    elif isinstance(valor, str):
                        valores.append(f"'{valor.replace('\'', '\'\'')}'")
                    elif isinstance(valor, (int, float)):
                        valores.append(str(valor))
                    else:
                        valores.append(f"'{valor}'")

                insert = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({', '.join(valores)});"
                f.write(insert + '\n')

    conn.close()
    print(f"✅ Archivo SQL generado correctamente en {output_sql}")

if __name__ == "__main__":
    mdb_path = os.environ.get('MDB_PATH', 'si-cam.mdb')
    output_sql = os.environ.get('OUTPUT_SQL', 'export_si_cam.sql')

    exportar_mdb_a_sql(mdb_path, output_sql)
