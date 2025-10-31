from flask import Blueprint, request, jsonify
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import io, base64
from itertools import product

optimizar_fuller = Blueprint('optimizar_fuller', __name__)


CURVAS_OBJETIVO = {
    "hormigon":     [100, 85, 65, 45, 30, 20, 10, 5],
    "bloques":      [100, 96, 59, 45, 24.6, 14.8, 6.35, 1.26],
    "relleno":      [100, 92, 70, 55, 40, 30, 15, 5],
}



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


# 🔧 helper: mismo largo, sin inventar
def alinear_longitudes(a, b):
    """
    Recorta ambos arrays/listas al mismo largo (el mínimo).
    No rellena, no interpola, no inventa tamices.
    """
    la = len(a)
    lb = len(b)
    lmin = min(la, lb)
    return np.array(a[:lmin], dtype=float), np.array(b[:lmin], dtype=float)



def generar_informe_ajuste(curvas, nombres, objetivo, paso=0.05, umbral_sugerencia=3.0):
    """
    curvas: lista de arrays/listas con las curvas de cada mezcla (pueden ser de largo variable)
    nombres: lista de nombres de esas mezclas (en mismo orden)
    objetivo: clave de curva objetivo dentro del diccionario CURVAS_OBJETIVO
    paso: resolución de búsqueda (entre 0.01 y 0.1 idealmente)
    umbral_sugerencia: desviación (%) a partir de la cual se recomienda una mezcla nueva
    """

    # 1) tomar curva objetivo
    curva_objetivo = CURVAS_OBJETIVO.get(objetivo)
    if curva_objetivo is None:
        curva_objetivo = CURVAS_OBJETIVO.get("hormigon")

    rango = np.arange(0, 1 + paso, paso)
    mejor_error = float("inf")
    mejor_comb = None
    mejor_curva = None

    # 2) barrido de combinaciones
    for pesos in product(rango, repeat=len(curvas)):
        # evitar combinaciones que no suman 1 (dentro del paso)
        if abs(sum(pesos) - 1.0) > paso:
            continue

        # curva construida con las reales
        curva_mixta = sum(p * np.array(c, dtype=float) for p, c in zip(pesos, curvas))

        # 🔴 acá alineamos con la ideal
        curva_mixta_al, curva_objetivo_al = alinear_longitudes(curva_mixta, curva_objetivo)

        # error sobre la parte realmente comparable
        error = np.sqrt(np.mean((curva_mixta_al - curva_objetivo_al) ** 2))
        if error < mejor_error:
            mejor_error = error
            mejor_comb = dict(zip(nombres, [round(p * 100, 2) for p in pesos]))
            mejor_curva = curva_mixta_al  # ojo: ya alineada
            curva_objetivo_final = curva_objetivo_al  # misma longitud

    # 3) armar salida
    # tamices base (los tuyos), pero solo hasta el largo real que se pudo comparar
    tamices_base = [
        "9.5 mm",
        "6.35 mm",
        "4.75 mm",
        "2.36 mm",
        "1.18 mm",
        "0.6 mm",
        "0.3 mm",
        "0.15 mm",
        "0.074 mm",
        "<fino>",
    ]
    tamices = tamices_base[: len(mejor_curva)]

    # diferencias reales
    diffs = mejor_curva - curva_objetivo_final

    informe = "=== Informe de Ajuste de Mezclas ===\n\n"
    informe += "Mejor combinación encontrada:\n"
    for k, v in mejor_comb.items():
        informe += f"- {k}: {v:.2f}%\n"

    informe += f"\nError medio respecto a la curva objetivo: {round(mejor_error, 2)}%\n\n"
    informe += f"Curva resultante (real, alineada):\n{[round(x, 2) for x in mejor_curva]}\n"
    informe += f"Curva objetivo (alineada):\n{[round(x, 2) for x in curva_objetivo_final]}\n\n"

    informe += "Diferencias por tamiz (Resultado - Objetivo):\n"

    sugerencia_necesaria = False
    ajustes_recomendados = []

    for i, d in enumerate(diffs):
        estado = "✅"
        if abs(d) > umbral_sugerencia:
            estado = "⚠️"
            sugerencia_necesaria = True
            if d > 0:
                ajustes_recomendados.append(
                    f"- Tamiz {tamices[i]}: reducir este rango (exceso de {d:+.2f}%)"
                )
            else:
                ajustes_recomendados.append(
                    f"- Tamiz {tamices[i]}: aumentar este rango (déficit de {d:+.2f}%)"
                )
        informe += f"- Tamiz {tamices[i]}: {d:+.2f}% {estado}\n"

    # 4) sugerencia de mezcla complementaria SOLO sobre lo que existe
    if sugerencia_necesaria:
        mezcla_complementaria = generar_mezcla_complementaria(
            curva_objetivo_final, mejor_curva
        )
        informe += "\n🧪 Mezcla sugerida para complementar:\n"
        for i in range(len(tamices)):
            informe += f"- Tamiz {tamices[i]}: {mezcla_complementaria[i]:.2f}%\n"

        informe += "\n📉 Conclusión:\n"
        informe += "La combinación actual no se ajusta completamente a la curva ideal (en el rango disponible).\n"
        informe += "👉 Para mejorarla, se recomienda una nueva mezcla que compense las siguientes diferencias:\n\n"
        for ajuste in ajustes_recomendados:
            informe += ajuste + "\n"
        informe += "\n🧭 Como referencia, la curva ideal (recortada al mismo rango) es:\n"
        for i in range(len(tamices)):
            informe += f"- Tamiz {tamices[i]}: ~{curva_objetivo_final[i]:.2f}%\n"
    else:
        informe += "\n✅ Conclusión:\nLa combinación actual es adecuada en el rango realmente medido. No se requiere mezcla adicional.\n"

    print(informe)
    return informe

def generar_mezcla_complementaria(curva_objetivo, mejor_curva):
    """
    Genera una mezcla complementaria que compensa las diferencias entre la curva actual y la curva objetivo.
    Retorna una lista con los valores sugeridos para cada tamiz.
    """
    diferencias = curva_objetivo - mejor_curva
    mezcla_sugerida = np.clip(diferencias + curva_objetivo, 0, 100)
    return [round(v, 2) for v in mezcla_sugerida]
