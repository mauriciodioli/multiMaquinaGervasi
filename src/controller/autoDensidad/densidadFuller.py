import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify
from collections import defaultdict
import numpy as np
from flask import jsonify, request
from scipy.optimize import minimize




densidadFuller = Blueprint('densidadFuller', __name__)







@densidadFuller.route('/pantalla_densidad_fuller/')
def pantalla_densidad_fuller():
    return render_template('autoDensidad/densidadFuller.html')
    
@densidadFuller.route('/pantalla_densidad_fuller_multiple/')
def pantalla_densidad_fuller_multiple():
    return render_template('autoDensidad/densidadFullerMultiple.html')




def calcular_curva_fuller(tamices, d_max, n=0.5):
    return [(d / d_max) ** n * 100 for d in tamices]

def comparar_mezcla_real_vs_fuller(tamices, porcentajes_reales, d_max, n=0.5):
    curva_fuller = calcular_curva_fuller(tamices, d_max, n)
    diferencias = [real - ideal for real, ideal in zip(porcentajes_reales, curva_fuller)]

    # Preparar gráfico
    fig, ax = plt.subplots()
    ax.plot(tamices, porcentajes_reales, marker='o', label='Mezcla Real')
    ax.plot(tamices, curva_fuller, marker='x', label='Curva de Fuller')
    ax.invert_xaxis()  # invertir el eje x
    ax.set_xlabel("Tamaño de Tamiz (mm)")
    ax.set_ylabel("Porcentaje Acumulado que Pasa (%)")
    ax.set_title("Comparación Curva de Fuller vs Mezcla Real")
    ax.legend()
    ax.grid(True)

    # Guardar imagen en memoria
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return {
        "tamices": tamices,
        "real": porcentajes_reales,
        "fuller": curva_fuller,
        "diferencias": diferencias,
        "grafico": f"data:image/png;base64,{plot_url}"
    }

@densidadFuller.route('/densidadFuller/', methods=['POST'])
def densidad_fuller_route():
    data = request.get_json()
    tamices = data.get("tamices", [])
    reales = data.get("porcentajes_reales", [])
    d_max = float(data.get("d_max", max(tamices)))
    n = float(data.get("n", 0.5))

    resultado = comparar_mezcla_real_vs_fuller(tamices, reales, d_max, n)
    return jsonify(resultado)







@densidadFuller.route('/densidadFullerMultiple/', methods=['POST'])
def densidad_fuller_multiple():


    data = request.get_json()
    mezclas = data.get("mezclas", [])
    d_max = float(data.get("d_max", 25))
    n = float(data.get("n", 0.5))

    resultados = []

    def calcular_curva_fuller(tamices, d_max, n):
        return [(d / d_max) ** n * 100 for d in tamices]

    for mezcla in mezclas:
        nombre = mezcla.get("nombre", "Sin nombre")
        tamices = mezcla.get("tamices", [])
        reales = mezcla.get("porcentajes_reales", [])

        if not tamices or not reales or len(tamices) != len(reales):
            continue  # O agregar error al resultado

        curva_fuller = calcular_curva_fuller(tamices, d_max, n)
        diferencias = [r - f for r, f in zip(reales, curva_fuller)]

        # Generar gráfico
        fig, ax = plt.subplots()
        ax.plot(tamices, reales, marker='o', label='Real')
        ax.plot(tamices, curva_fuller, marker='x', label='Fuller Ideal')
        ax.invert_xaxis() # invertir el eje x
        ax.set_title(f"{nombre} - Curva de Fuller")
        ax.set_xlabel("Tamiz (mm)")
        ax.set_ylabel("% que pasa")
        ax.grid(True)
        ax.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        evaluacion, error_promedio = evaluar_mezcla(diferencias)
        ajustes = sugerir_ajustes(tamices, diferencias)

        resultados.append({
            "nombre": nombre,
            "curva_ideal": curva_fuller,
            "diferencias": diferencias,
            "grafico": f"data:image/png;base64,{img_base64}",
            "evaluacion": evaluacion,
            "error_promedio": error_promedio,
            "ajustes": ajustes
        })


          # 💥 Llamás a la nueva función acá
        curva_resultante = calcular_curva_resultante(mezclas, d_max, n)
        # Comparar la curva promedio con Fuller ideal
        tamices_res = curva_resultante["tamices"]
        promedios_res = curva_resultante["promedios"]
        curva_fuller_res = [(t / d_max) ** n * 100 for t in tamices_res]
        diferencias_res = [r - f for r, f in zip(promedios_res, curva_fuller_res)]

        # Evaluar y sugerir
        evaluacion_res, error_prom_res = evaluar_mezcla(diferencias_res)
        ajustes_res = sugerir_ajustes(tamices_res, diferencias_res)

        # Agregarlo al dict de la curva resultante
        curva_resultante["curva_ideal"] = curva_fuller_res
        curva_resultante["diferencias"] = diferencias_res
        curva_resultante["evaluacion"] = evaluacion_res
        curva_resultante["error_promedio"] = error_prom_res
        curva_resultante["ajustes"] = ajustes_res

        

    return jsonify({
        "resultados": resultados,
        "curva_resultante": curva_resultante
    })


def calcular_curva_resultante(mezclas, d_max, n):
    """Calcula la curva promedio de todas las mezclas y devuelve la imagen en base64 + datos"""
    
    tamiz_data = defaultdict(list)

    for mezcla in mezclas:
        for t, p in zip(mezcla["tamices"], mezcla["porcentajes_reales"]):
            tamiz_data[t].append(p)

    # Ordenar y calcular promedio por tamiz
    tamices_ordenados = sorted(tamiz_data.keys(), reverse=True)
    promedio_reales = [np.mean(tamiz_data[t]) for t in tamices_ordenados]
    curva_fuller_resultante = [(t / d_max) ** n * 100 for t in tamices_ordenados]

    # Generar gráfico
    fig, ax = plt.subplots()
    ax.plot(tamices_ordenados, promedio_reales, marker='o', label='Promedio Real')
    ax.plot(tamices_ordenados, curva_fuller_resultante, marker='x', label='Fuller Ideal')
    ax.invert_xaxis()  # invertir el eje x
    ax.set_title("Curva Promedio de Todas las Mezclas")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.grid(True)
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    curva_global_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    return {
        "tamices": tamices_ordenados,
        "promedios": promedio_reales,
        "grafico": f"data:image/png;base64,{curva_global_base64}"
    }
    
    
    
def evaluar_mezcla(diferencias):
    error_promedio = np.mean([abs(d) for d in diferencias])
    
    if error_promedio <= 10:
        return ("Excelente", error_promedio)
    elif error_promedio <= 25:
        return ("Aceptable", error_promedio)
    else:
        return ("Desviada", error_promedio)
    

def sugerir_ajustes(tamices, diferencias):
    zonas = {
        "finos": [],
        "medios": [],
        "gruesos": []
    }

    for t, d in zip(tamices, diferencias):
        if t < 0.3:
            zonas["finos"].append(d)
        elif t <= 4.75:
            zonas["medios"].append(d)
        else:
            zonas["gruesos"].append(d)

    ajustes = []

    for zona, valores in zonas.items():
        if not valores:
            continue
        promedio = np.mean(valores)

        if promedio > 5:
            ajustes.append(f"Reducir material {zona} (exceso de {promedio:.1f}%)")
        elif promedio < -5:
            ajustes.append(f"Aumentar material {zona} (déficit de {abs(promedio):.1f}%)")

    if not ajustes:
        return ["Mezcla equilibrada. No requiere ajustes."]
    
    return ajustes













@densidadFuller.route('/densidadFullerOptimo/', methods=['POST'])
def densidad_fuller_optimo():
    data = request.get_json()
    mezclas = data.get("mezclas", [])
    d_max = float(data.get("d_max", 25))
    n = float(data.get("n", 0.5))

    # Eje común: tamices de la curva promedio (supuesto)
    tamices_comunes = sorted(set(t for m in mezclas for t in m["tamices"]), reverse=True)

    # Interpolar cada curva a los tamices comunes
    curvas_interp = []
    for mezcla in mezclas:
        x = mezcla["tamices"]
        y = mezcla["porcentajes_reales"]
        curva_interp = np.interp(tamices_comunes, x[::-1], y[::-1])
        curvas_interp.append(curva_interp)

    materiales = np.array(curvas_interp)  # cada fila es una mezcla

    curva_fuller = np.array([(d / d_max)**n * 100 for d in tamices_comunes])

    def error_total(pesos):
        curva = np.dot(pesos, materiales)
        return np.mean(np.abs(curva - curva_fuller))

    n_mezclas = len(mezclas)
    bounds = [(0, 1)] * n_mezclas
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    initial = [1/n_mezclas] * n_mezclas

    result = minimize(error_total, initial, bounds=bounds, constraints=constraints)

    pesos = result.x
    curva_optima = np.dot(pesos, materiales)

    return jsonify({
        "pesos": [round(p * 100, 2) for p in pesos],  # como porcentaje
        "tamices": tamices_comunes,
        "curva_optima": list(curva_optima),
        "curva_ideal": list(curva_fuller),
        "error_promedio": round(error_total(pesos), 2)
    })






