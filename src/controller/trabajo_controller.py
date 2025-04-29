import pyodbc
from flask import Blueprint, request, render_template
trabajos_bp = Blueprint('trabajos', __name__)

# Ruta para ver los trabajos
@trabajos_bp.route('/trabajos')
def listar_trabajos():
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Lamiere_Tempi')  # O la tabla que tengas
        trabajos = cursor.fetchall()
        columnas = [column[0] for column in cursor.description]
        conn.close()
        return render_template('trabajos.html', trabajos=trabajos, columnas=columnas)
    except Exception as e:
        return f"Error conectando a la base de datos: {e}"




     
            
@trabajos_bp.route('/')
def listar_maquinas():
    try:
        #conn = pyodbc.connect(  r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;')
        #cursor = conn.cursor()
        #cursor.execute('SELECT * FROM Lamiere_Tempi')  # O la tabla que tengas
        #trabajos = cursor.fetchall()
        #columnas = [column[0] for column in cursor.description]
        #conn.close()
        trabajos=''
        columnas=''
        return render_template('maquinas/maquinas.html', trabajos=trabajos, columnas=columnas)
    except Exception as e:
        return f"Error conectando a la base de datos: {e}"
    
@trabajos_bp.route('/trabajos/<int:id>')
def ver_trabajo(id):
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        
        # Consulta corregida
        query = '''
            SELECT 
                IdTrabajo, 
                NombreArchivo, 
                EjeX_Work, 
                EjeY_Work, 
                EjeZ_Work, 
                EjeX_Programmed, 
                EjeY_Programmed, 
                EjeZ_Programmed, 
                EjeX_Origin, 
                EjeY_Origin, 
                EjeZ_Origin, 
                FechaCreacion
            FROM 
                Processed
            WHERE 
                IdTrabajo = ?
        '''
        cursor.execute(query, id)
        trabajo = cursor.fetchone()
        conn.close()
        
        if trabajo:
            return render_template('trabajo.html', trabajo=trabajo)
        else:
            return f"No se encontró el trabajo con ID {id}."

    except Exception as e:
        return f"Error conectando a la base de datos: {e}"

@trabajos_bp.route('/trabajos/maquinas')
def listar_maquinas_trabajos():
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\Tecnico03\Documents\ProyectoMultiMaquina\si-cam.mdb;'
        )
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                NombrePieza,
                LargoTrabajo,
                AnchoTrabajo,
                PosicionOrigenX,
                PosicionOrigenY,
                EstadoTrabajo
            FROM 
                WorkSheets
            WHERE 
                EstadoTrabajo = 'Finalizado'
            ORDER BY 
                FechaUltimaActualizacion DESC
        '''
        
        cursor.execute(query)
        trabajos = cursor.fetchall()
        columnas = [column[0] for column in cursor.description]
        conn.close()
        
        return render_template('maquinas/maquinas.html', trabajos=trabajos, columnas=columnas)

    except Exception as e:
        return f"Error conectando a la base de datos: {e}"
