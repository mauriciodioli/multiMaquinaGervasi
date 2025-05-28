from flask import Blueprint, request, jsonify
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import io, base64
from itertools import product

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





def generar_informe_ajuste(curvas, nombres, curva_objetivo, paso=0.05, umbral_sugerencia=3.0):
    """
    curvas: lista de arrays numpy con las curvas de cada mezcla (8 valores)
    nombres: lista de nombres de esas mezclas (en mismo orden)
    curva_objetivo: array numpy de 8 valores objetivo
    paso: resolución de búsqueda (entre 0.01 y 0.1 idealmente)
    umbral_sugerencia: desviación (%) a partir de la cual se recomienda una mezcla nueva
    """
    rango = np.arange(0, 1 + paso, paso)
    mejor_error = float('inf')
    mejor_comb = None
    mejor_curva = None

    # Evaluar todas las combinaciones de pesos
    for pesos in product(rango, repeat=len(curvas)):
        if abs(sum(pesos) - 1.0) > paso:
            continue
        curva_mixta = sum(p * c for p, c in zip(pesos, curvas))
        error = np.sqrt(np.mean((curva_mixta - curva_objetivo)**2))
        if error < mejor_error:
            mejor_error = error
            mejor_comb = dict(zip(nombres, [round(p*100, 2) for p in pesos]))
            mejor_curva = curva_mixta

    # Diferencias
    diffs = mejor_curva - curva_objetivo
    tamices = ["9.5 mm", "4.75 mm", "2.36 mm", "1.18 mm", "0.6 mm", "0.3 mm", "0.15 mm", "0.074 mm"]

    # Generar informe
    informe = "=== Informe de Ajuste de Mezclas ===\n\n"
    informe += "Mejor combinación encontrada:\n"
    for k, v in mejor_comb.items():
        informe += f"- {k}: {v:.2f}%\n"
    informe += f"\nError medio respecto a la curva objetivo: {round(mejor_error, 2)}%\n\n"
    informe += f"Curva resultante:\n{[round(x, 2) for x in mejor_curva]}\n"
    informe += f"Curva objetivo:\n{[round(x, 2) for x in curva_objetivo]}\n\n"

    informe += "Diferencias por tamiz (Resultado - Objetivo):\n"
    sugerencia_necesaria = False
    for i, d in enumerate(diffs):
        estado = "✅"
        if abs(d) > umbral_sugerencia:
            estado = "⚠️"
            sugerencia_necesaria = True
        informe += f"- Tamiz {tamices[i]}: {d:+.2f}% {estado}\n"

    if sugerencia_necesaria:
        informe += "\nConclusión:\nCon la combinación actual no se alcanza completamente la curva ideal.\n"
        informe += "👉 Se recomienda buscar una mezcla nueva con las siguientes características:\n\n"
        for i in range(len(tamices)):
            informe += f"- Tamiz {tamices[i]}: ~{curva_objetivo[i]}%\n"
    else:
        informe += "\nConclusión:\nLa combinación actual es adecuada, no se requiere mezcla adicional."
    print(informe)
    return informe
