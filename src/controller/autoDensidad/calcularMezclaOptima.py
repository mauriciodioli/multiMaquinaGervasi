import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify
from collections import defaultdict
import numpy as np
from flask import jsonify, request
from scipy.optimize import minimize
import pandas as pd





calcularMezclaOptima = Blueprint('calcularMezclaOptima', __name__)

def calcular_curva_fuller(tamices, d_max=25, n=0.5):
    return [(t / d_max) ** n * 100 for t in tamices]


def mezclar_ponderado(mezclas, pesos):
    """
    Recibe una lista de curvas de mezclas y un vector de pesos (en %).
    Devuelve la curva combinada.
    """
    mezcla_final = np.zeros(len(mezclas[0]))
    for i, mezcla in enumerate(mezclas):
        mezcla_final += np.array(mezcla) * pesos[i]
    return mezcla_final.tolist()


def calcular_fracciones(curva, tamices):
    """Agrupa % de material en Gruesos (>4.75), Medios (1.18-4.75), Finos (<1.18)"""
    gruesos = medios = finos = 0
    for i, t in enumerate(tamices):
        val = curva[i] if i == 0 else curva[i] - curva[i - 1]
        if t > 4.75:
            gruesos += val
        elif 1.18 <= t <= 4.75:
            medios += val
        else:
            finos += val
    return {"gruesos": gruesos, "medios": medios, "finos": finos}


def calcular_mezcla_optima(mezclas, tamices, d_max=25, n=0.5):
    import numpy as np
    from scipy.optimize import minimize
    import pandas as pd

    num_mezclas = len(mezclas)
    curva_ideal = calcular_curva_fuller(tamices, d_max, n)

    # Clasificamos zonas
    zonas = []
    for t in tamices:
        if t > 4.75:
            zonas.append("gruesos")
        elif t > 0.6:
            zonas.append("medios")
        else:
            zonas.append("finos")

    # Mezcla ponderada de curvas
    def mezclar_ponderado(curvas, pesos):
        return [sum(p * curva[i] for p, curva in zip(pesos, curvas)) for i in range(len(tamices))]

    # Función objetivo: minimizar error cuadrático global
    def error(pesos):
        if np.sum(pesos) > 1.01:
            return 1e6
        curva = mezclar_ponderado(mezclas, pesos)
        return np.mean([(c - i) ** 2 for c, i in zip(curva, curva_ideal)])

    # Optimización
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0, 1) for _ in range(num_mezclas)]
    init = [1 / num_mezclas] * num_mezclas
    result = minimize(error, init, method='SLSQP', bounds=bounds, constraints=constraints)

    if not result.success:
        return {"error": "No se pudo encontrar una combinación óptima."}

    pesos_optimos = result.x
    curva_resultante = mezclar_ponderado(mezclas, pesos_optimos)
    diferencias = [r - i for r, i in zip(curva_resultante, curva_ideal)]

    # Desviación por zona
    contribuciones = {"gruesos": [], "medios": [], "finos": []}
    for i, z in enumerate(zonas):
        contribuciones[z].append(diferencias[i])

    promedios_por_zona = {
        z: round(np.mean(vals), 2) if vals else 0.0
        for z, vals in contribuciones.items()
    }

    total_desviacion = sum(abs(v) for v in promedios_por_zona.values())
    pesos_sugeridos = {
        z: round((abs(v) / total_desviacion) * 100, 2) if total_desviacion > 0 else 33.33
        for z, v in promedios_por_zona.items()
    }

    # Mensaje resumen
    mensaje = (
        f"Ajustar mezcla: "
        f"{'aumentar' if promedios_por_zona['gruesos'] < 0 else 'reducir'} gruesos ({abs(promedios_por_zona['gruesos']):.1f}%), "
        f"{'aumentar' if promedios_por_zona['medios'] < 0 else 'reducir'} medios ({abs(promedios_por_zona['medios']):.1f}%), "
        f"{'aumentar' if promedios_por_zona['finos'] < 0 else 'reducir'} finos ({abs(promedios_por_zona['finos']):.1f}%)"
    )

    # DEBUG VISUAL
    print("\n=== Resultados mezcla óptima ===")
    print("Pesos óptimos por mezcla (%):", [round(p * 100, 2) for p in pesos_optimos])
    print("Curva resultante:  ", [round(v, 2) for v in curva_resultante])
    print("Curva ideal:       ", [round(v, 2) for v in curva_ideal])
    for i, (r, i_) in enumerate(zip(curva_resultante, curva_ideal)):
        print(f"  Tamiz {tamices[i]} mm → Δ: {round(r - i_, 2)}%")
    print("Desviación promedio por zona:", promedios_por_zona)
    print("Pesos sugeridos por zona (%):", pesos_sugeridos)
    print("Mensaje sugerido:", mensaje)
    print("Error total:", round(error(pesos_optimos), 4))

    return {
        "pesos_optimos_mezcla": [round(p * 100, 2) for p in pesos_optimos],
        "curva_resultante": [round(v, 2) for v in curva_resultante],
        "curva_ideal": [round(v, 2) for v in curva_ideal],
        "error_total": round(error(pesos_optimos), 4),
        "pesos": pesos_sugeridos,
        "desviacion_promedio_por_zona": promedios_por_zona,
        "mensaje": mensaje
    }



    
    
def mostrar_datos_crudos_entrada(mezclas):
  

    datos_crudos = []
    for mezcla in mezclas:
        nombre = mezcla.get("nombre", "Sin nombre")
        tamices = mezcla.get("tamices", [])
        reales = mezcla.get("porcentajes_reales", [])
        if tamices and reales and len(tamices) == len(reales):
            datos_crudos.append(pd.DataFrame({
                "Nombre mezcla": [nombre] * len(tamices),
                "Tamiz (mm)": tamices,
                "% Real original": reales
            }))

    df_entrada = pd.concat(datos_crudos, ignore_index=True)
    print("=== Datos de entrada ===")
    print(df_entrada.to_string(index=False))

def encontrar_n_optimo(tamices, curva_real, d_max):
    mejor_n = None
    menor_error = float('inf')
    mejor_curva = None

    for n in np.arange(0.3, 0.71, 0.01):  # pasos de 0.01
        curva_ideal = [(d / d_max) ** n * 100 for d in tamices]
        error = np.mean([abs(r - i) for r, i in zip(curva_real, curva_ideal)])

        if error < menor_error:
            menor_error = error
            mejor_n = n
            mejor_curva = curva_ideal

    return mejor_n, mejor_curva[::-1], menor_error
