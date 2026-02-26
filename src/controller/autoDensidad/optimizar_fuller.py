from flask import Blueprint, request, jsonify
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import io, base64
from itertools import product

optimizar_fuller = Blueprint('optimizar_fuller', __name__)

# === Objetivos por norma (9 puntos, incluye 12.5 mm = 100%) ===
# 9 tamices (incluye 12.5 y 0.074)
OBJ_TAMICES = [12.5, 9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074]

def objetivo_9(desde_8):
    # Inserta 100% al inicio (12.5 mm) y duplica el último para 0.074 mm
    y = [100.0] + list(map(float, desde_8)) + [float(desde_8[-1])]
    return np.clip(y, 0, 100)

CURVAS_OBJETIVO = {
    "hormigon": objetivo_9([85, 65, 45, 30, 20, 10, 5, 5]),
    "bloques":  objetivo_9([96, 59, 45, 24.6, 14.8, 6.35, 1.26, 1.26]),
    "relleno":  objetivo_9([92, 70, 55, 40, 30, 15, 5, 5]),
}

# Estado global para recordar el "master" (los tamices reales de la planta; p.ej., 14)
MASTER_TAMICES = None

def set_master_tamices(tamices_master):
    """Configurá los tamices 'master' (p.ej., tus 14 tamices reales) ANTES de usar generar_informe_ajuste."""
    global MASTER_TAMICES
    MASTER_TAMICES = list(tamices_master)

def _expandir_objetivo_a_master(curva_objetivo9):
    """
    Interpola el objetivo (9 puntos) a los tamices MASTER_TAMICES (p.ej., 14),
    usando eje log10(tamiz). Si no se seteó master, devuelve los 9 originales.
    """
    if MASTER_TAMICES is None:
        return np.asarray(curva_objetivo9, dtype=float)

    x  = np.log10(np.asarray(OBJ_TAMICES, dtype=float))            # 9
    y  = np.asarray(curva_objetivo9, dtype=float)                  # 9
    xm = np.log10(np.asarray(MASTER_TAMICES, dtype=float))         # L (p.ej., 14)
    return np.interp(xm, x, y, left=y[0], right=y[-1])             # L

@optimizar_fuller.route('/densidadFullerAutoOptimizar/', methods=['POST'])
def auto_optimizar_curva():

    data = request.get_json()
    curvas = data.get("curvas")
    tamices = data.get("tamices")
    nombres_materiales = data.get("nombreProductos", [])

    if not curvas or not tamices:
        return jsonify({"error": "Faltan curvas o tamices"}), 400

    # 🔹 Usamos tu motor real
    w_opt, mezcla_opt, err = auto_optimizar_pesos(curvas, tamices)

    if err:
        return jsonify({"error": err}), 500

    # Fuller solo para graficar
    tamices_np = np.asarray(tamices, dtype=float)
    d_max = float(np.max(tamices_np))
    n = 0.5
    curva_fuller = ((tamices_np / d_max) ** n) * 100.0

    # --------- GRÁFICO INDUSTRIAL ----------
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(tamices, curva_fuller,
            label="Fuller Ideal",
            color='orange',
            marker='x')

    ax.plot(tamices, mezcla_opt,
            label="Óptima",
            color='green',
            marker='s',
            linestyle='--')

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
        f"{nombres_materiales[i]}: {w_opt[i]*100:.2f}%"
        for i in range(len(w_opt))
    ]

    return jsonify({
        "pesos_optimizado": list(map(float, w_opt)),
        "grafico_base64": f"data:image/png;base64,{img_base64}",
        "recomendaciones": recomendaciones
    })

def generar_informe_ajuste(curvas, nombres, objetivo, paso=0.05, umbral_sugerencia=3.0):
    """
    curvas: lista de arrays/listas YA alineadas al master (mismo largo L: p.ej., 14)
    nombres: lista de nombres (mismo orden)
    objetivo: 'hormigon' | 'bloques' | 'relleno'
    paso: resolución de la búsqueda exhaustiva de pesos (0.01~0.1 razonable)
    umbral_sugerencia: |Δ| (%) para marcar desviación y sugerir ajuste
    """
    # Asegurar arrays y largo objetivo
    curvas = [np.asarray(c, dtype=float) for c in curvas]
    L = len(curvas[0])

    # Verificar que todas las curvas tengan mismo L
    if any(len(c) != L for c in curvas):
        raise ValueError("Todas las curvas deben tener el mismo largo (mismos tamices master).")

    # Expandir objetivo (9) a master (L)
    curva_objetivo9 = np.asarray(CURVAS_OBJETIVO[objetivo], dtype=float)
    curva_objetivo  = _expandir_objetivo_a_master(curva_objetivo9)

    # Seguridad por si no setearon master o hay misajuste de longitud
    if len(curva_objetivo) != L:
        if len(curva_objetivo) < L:
            curva_objetivo = np.pad(curva_objetivo, (0, L - len(curva_objetivo)), constant_values=0.0)
        else:
            curva_objetivo = curva_objetivo[:L]

    rango = np.arange(0, 1 + paso, paso)
    mejor_error = float('inf')
    mejor_comb = None
    mejor_curva = None

    # Búsqueda por rejilla (product) respetando sum(pesos)=1 ± paso
    for pesos in product(rango, repeat=len(curvas)):
        if abs(sum(pesos) - 1.0) > paso:
            continue
        curva_mixta = sum(p * c for p, c in zip(pesos, curvas))  # shape (L,)
        error = float(np.sqrt(np.mean((curva_mixta - curva_objetivo) ** 2)))
        if error < mejor_error:
            mejor_error = error
            mejor_comb = dict(zip(nombres, [round(p*100, 2) for p in pesos]))
            mejor_curva = curva_mixta

    diffs = mejor_curva - curva_objetivo

    # Etiquetas para reporte
    if MASTER_TAMICES is not None and len(MASTER_TAMICES) == L:
        tamices_labels = [f"{t} mm" for t in MASTER_TAMICES]
    else:
        tamices_labels = [f"Tamiz {i+1}" for i in range(L)]

    # Reporte
    informe = "=== Informe de Ajuste de Mezclas ===\n\n"
    informe += "Mejor combinación encontrada:\n"
    for k, v in mejor_comb.items():
        informe += f"- {k}: {v:.2f}%\n"
    informe += f"\nError medio respecto a la curva objetivo: {round(mejor_error, 2)}%\n\n"
    informe += f"Curva resultante:\n{[round(float(x), 2) for x in mejor_curva]}\n"
    informe += f"Curva objetivo (expandida):\n{[round(float(x), 2) for x in curva_objetivo]}\n\n"

    informe += "Diferencias por tamiz (Resultado - Objetivo):\n"
    sugerencia_necesaria = False
    ajustes_recomendados = []
    for i, d in enumerate(diffs):
        estado = "✅"
        if abs(d) > umbral_sugerencia:
            estado = "⚠️"; sugerencia_necesaria = True
            if d > 0:
                ajustes_recomendados.append(f"- {tamices_labels[i]}: reducir (exceso {d:+.2f}%)")
            else:
                ajustes_recomendados.append(f"- {tamices_labels[i]}: aumentar (déficit {d:+.2f}%)")
        informe += f"- {tamices_labels[i]}: {d:+.2f}% {estado}\n"

    if sugerencia_necesaria:
        mezcla_complementaria = generar_mezcla_complementaria(curva_objetivo, mejor_curva)
        informe += "\n🧪 Mezcla sugerida para complementar:\n"
        for i in range(L):
            informe += f"- {tamices_labels[i]}: {mezcla_complementaria[i]:.2f}%\n"
        informe += "\n📉 Conclusión:\nLa combinación actual no se ajusta completamente a la curva ideal expandida.\n"
    else:
        informe += "\n✅ Conclusión:\nLa combinación actual es adecuada. No se requiere mezcla adicional.\n"

    print(informe)
    return informe

def generar_mezcla_complementaria(curva_objetivo, mejor_curva):
    """
    Mezcla complementaria = 'lo que falta' para llegar al objetivo por tamiz (clamp 0..100).
    No duplica el objetivo: solo compensa déficit.
    """
    curva_objetivo = np.asarray(curva_objetivo, dtype=float)
    mejor_curva   = np.asarray(mejor_curva,   dtype=float)
    complemento = np.clip(curva_objetivo - mejor_curva, 0, 100)
    return [round(float(v), 2) for v in complemento]


def auto_optimizar_pesos(curvas, tamices, n=0.5):
    curvas_np = np.asarray(curvas, dtype=float)              # shape: (M, L)
    tamices_np = np.asarray(tamices, dtype=float)            # shape: (L,)
    d_max = float(np.max(tamices_np))
    fuller = ((tamices_np / d_max) ** n) * 100.0             # shape: (L,)

    M = curvas_np.shape[0]
    w0 = np.ones(M) / M

    def obj(w):
        mezcla = w @ curvas_np
        return float(np.mean((mezcla - fuller) ** 2))

    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, 1.0)] * M

    res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=cons)
    if not res.success:
        return None, None, f"Optimización no convergió: {res.message}"

    w_opt = res.x
    mezcla_opt = w_opt @ curvas_np
    return w_opt, mezcla_opt, None

def optimizar_con_objetivo(curvas_alineadas, curva_objetivo):
    curvas_np = np.asarray(curvas_alineadas, dtype=float)   # (M, L)
    obj_np = np.asarray(curva_objetivo, dtype=float)        # (L,)
    M = curvas_np.shape[0]
    w0 = np.ones(M) / M

    def obj(w):
        mezcla = w @ curvas_np
        return float(np.mean((mezcla - obj_np) ** 2))

    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},)
    bounds = [(0.0, 1.0)] * M

    res = minimize(obj, w0, method='SLSQP', bounds=bounds, constraints=cons)
    return res