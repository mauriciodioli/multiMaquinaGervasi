from flask import Blueprint, request, jsonify
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import io, base64

optimizar_fuller = Blueprint('optimizar_fuller', __name__)

@optimizar_fuller.route('/densidadFullerAutoOptimizar/', methods=['POST'])
def auto_optimizar_curva():
    data = request.get_json()
    curvas = data.get("curvas")
    tamices = data.get("tamices")
    nombres_materiales = data.get("nombreProductos", [])

    if not curvas or not tamices:
        return jsonify({"error": "Faltan curvas o tamices"}), 400

    d_max = max(tamices)
    n = 0.5
    curva_fuller = [(d / d_max) ** n * 100 for d in tamices]

    def error_total(pesos):
        total = sum(pesos)
        if total == 0:
            return float('inf')
        normalizados = [p / total for p in pesos]
        curva_corregida = [
            sum(p * curva[i] for p, curva in zip(normalizados, curvas))
            for i in range(len(tamices))
        ]
        return sum((curva_corregida[i] - curva_fuller[i]) ** 2 for i in range(len(tamices)))

    res = minimize(error_total, x0=[1]*len(curvas), bounds=[(0, 1)]*len(curvas))
    pesos_optimos = res.x / sum(res.x)

    curva_corregida = [
        sum(p * curva[i] for p, curva in zip(pesos_optimos, curvas))
        for i in range(len(tamices))
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(tamices, curva_fuller, label="Fuller Ideal", color='orange', marker='x')
    ax.plot(tamices, curva_corregida, label="Corregida Óptima", color='green', marker='s', linestyle='--')

    ax.invert_xaxis()
    ax.set_title("Optimización Automática de Mezcla")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.legend()
    ax.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    recomendaciones = [
        f"{nombres_materiales[i]}: {peso*100:.2f}%" for i, peso in enumerate(pesos_optimos)
    ]

    return jsonify({
        "pesos_optimizado": list(pesos_optimos),
        "grafico_base64": f"data:image/png;base64,{img_base64}",
        "recomendaciones": recomendaciones
    })
