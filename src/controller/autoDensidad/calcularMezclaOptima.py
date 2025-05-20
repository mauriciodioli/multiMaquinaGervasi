import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify
from collections import defaultdict
import numpy as np
from flask import jsonify, request
from scipy.optimize import minimize




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
    num_mezclas = len(mezclas)
    curva_ideal = calcular_curva_fuller(tamices, d_max, n)

    def error(pesos):
        if np.sum(pesos) > 1.01:  # Penalizamos si superan el 100%
            return 1e6
        curva = mezclar_ponderado(mezclas, pesos)
        return np.mean([(c - i) ** 2 for c, i in zip(curva, curva_ideal)])

    # Restricción: suma de pesos = 1 (100%)
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = [(0, 1) for _ in range(num_mezclas)]
    init = [1 / num_mezclas] * num_mezclas

    result = minimize(error, init, method='SLSQP', bounds=bounds, constraints=constraints)

    if not result.success:
        return {"error": "No se pudo encontrar una combinación óptima."}

    pesos_optimos = result.x
    curva_resultante = mezclar_ponderado(mezclas, pesos_optimos)
    fracciones = calcular_fracciones(curva_resultante, tamices)
    error_prom = error(pesos_optimos)

    return {
        "pesos": [round(p * 100, 2) for p in pesos_optimos],
        "curva_resultante": [round(v, 2) for v in curva_resultante],
        "curva_ideal": [round(v, 2) for v in curva_ideal],
        "fracciones": {k: round(v, 2) for k, v in fracciones.items()},
        "error_total": round(error_prom, 4),
        "mensaje": "Curva óptima calculada con éxito."
    }