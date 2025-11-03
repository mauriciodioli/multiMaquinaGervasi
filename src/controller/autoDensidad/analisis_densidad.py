# controller/autoDensidad/analisis_densidad.py

from controller.autoDensidad.densidadFuller import evaluar_mezcla_promedio
from controller.autoDensidad.calcularMezclaOptima import calcular_curva_fuller
from flask import Blueprint, request, render_template, send_file, jsonify
import urllib.parse
import json
from controller.autoDensidad.calcularMezclaOptima import calcular_mezcla_optima
from controller.autoDensidad.calcularMezclaOptima import mostrar_datos_crudos_entrada
from controller.autoDensidad.calcularMezclaOptima import encontrar_n_optimo
from controller.autoDensidad.optimizar_fuller import generar_informe_ajuste
import math
import io, base64
import matplotlib.pyplot as plt


analisis_densidad = Blueprint('analisis_densidad', __name__)

# Norma 9 puntos (incluye 12.5 mm)
TAMICES_DEFAULT = [12.5, 9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074]


# --------- HELPERS ---------
def _to_float_list(x):
    if x is None:
        return []
    return [float(v) for v in x]

def alinear_curva_a_master(valores_reales, tamices_curva, master):
    """
    Alinea una curva cualquiera al vector master de tamices:
    - Si falta un tamiz del master -> rellena 0.0
    - Si sobran tamices (no están en master) -> se ignoran
    """
    vals = _to_float_list(valores_reales)
    ts   = _to_float_list(tamices_curva) if tamices_curva else []

    # Si no nos dieron tamices, asumimos que ya viene en orden master y rellenamos si faltan
    if not ts:
        aligned = [0.0] * len(master)
        for i, v in enumerate(vals[:len(master)]):
            aligned[i] = v
        return aligned

    # Mapear tamiz->valor y reconstruir en orden master
    mapa = {float(t): float(v) for t, v in zip(ts, vals)}
    return [float(mapa.get(float(t), 0.0)) for t in master]

def normalizar_pesos_porcentuales(proporciones):
    """
    Recibe {'arena': 40, 'grava': 60} y devuelve [0.4, 0.6] en el mismo orden de keys().
    Si todo es 0 o vacío, reparte uniforme.
    """
    nombres = list(proporciones.keys())
    brutos  = [max(0.0, float(proporciones[n])) for n in nombres]
    total   = sum(brutos)
    if total <= 0:
        n = max(1, len(brutos))
        return nombres, [1.0/n]*n
    return nombres, [b/total for b in brutos]

def calcular_curva_resultante_simple(curvas_alineadas, pesos_norm):
    """Combinación ponderada punto a punto (todas mismas longitudes)."""
    L = len(curvas_alineadas[0])
    res = []
    for i in range(L):
        res.append(sum(p * curva[i] for curva, p in zip(curvas_alineadas, pesos_norm)))
    return res


# --------- API SIMPLE DE TEST ---------
def simular_mezcla_manual_simple(proporciones, curvas_usuario):
    nombres, pesos_norm = normalizar_pesos_porcentuales(proporciones)

    curvas_alineadas = []
    for nombre in nombres:
        datos = curvas_usuario.get(nombre)
        if not datos or 'reales' not in datos:
            return {"error": f"❌ Faltan datos de curva para '{nombre}'"}, 400

        reales  = datos.get('reales', [])
        tamices = datos.get('tamices') or datos.get('mallas')
        curva_a_9 = alinear_curva_a_master(reales, tamices, TAMICES_DEFAULT)
        curvas_alineadas.append(curva_a_9)

    if not curvas_alineadas:
        return {"error": "❌ No se encontraron curvas válidas"}, 400

    # Curva resultante ponderada
    curva_resultante = calcular_curva_resultante_simple(curvas_alineadas, pesos_norm)

    # Fuller usando d_max del master (12.5)
    d_max = max(TAMICES_DEFAULT)
    curva_fuller = calcular_curva_fuller(TAMICES_DEFAULT, d_max=d_max, n=0.5)

    # Dif y zonas
    diferencias = [abs(a - b) for a, b in zip(curva_resultante, curva_fuller)]
    zonas = evaluar_mezcla_promedio(TAMICES_DEFAULT, diferencias)

    # === NUEVO: gráfico base64 ===
    grafico_base64 = _grafico_curvas_base64(
        tamices=TAMICES_DEFAULT,
        curva_fuller=curva_fuller,
        curva_resultante=curva_resultante,
        curvas_alineadas=curvas_alineadas,
        nombres=nombres
    )

    return {
        "tamices": TAMICES_DEFAULT,
        "curvas_alineadas": curvas_alineadas,
        "pesos_normalizados": pesos_norm,
        "curva_resultante": curva_resultante,
        "curva_fuller": curva_fuller,
        "zonas": zonas,
        "grafico_base64": grafico_base64,   # ← úsalo directo en <img src="...">
    }

    
    
    

# --- helper de plotting ---
def _grafico_curvas_base64(tamices, curva_fuller, curva_resultante, curvas_alineadas=None, nombres=None):
    """
    Devuelve data URI base64 con:
      - Curva Fuller (línea sólida, marcadores)
      - Curva resultante (línea discontinua)
      - (opcional) Curvas alineadas por material, finas en gris
    Eje X en log(mm) e invertido (de gruesos a finos).
    """
    fig, ax = plt.subplots(figsize=(7, 4.2))

    # Curva Fuller
    ax.plot(tamices, curva_fuller, marker='o', linewidth=1.8, label='Fuller (ideal)')

    # Curva resultante
    ax.plot(tamices, curva_resultante, marker='s', linestyle='--', linewidth=1.8, label='Resultante')

    # Curvas individuales (opcionales)
    if curvas_alineadas:
        for i, c in enumerate(curvas_alineadas):
            label = f"{nombres[i]} (alineada)" if nombres and i < len(nombres) else "mezcla"
            ax.plot(tamices, c, linewidth=1.0, alpha=0.35, label=label)

    ax.set_xscale('log')
    ax.invert_xaxis()  # de grueso (izq) a fino (der)
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.set_title("Curva resultante vs Fuller")
    ax.grid(True, which='both', linewidth=0.4, alpha=0.5)
    ax.legend(loc='best', fontsize='small')

    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format='png', dpi=140)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f"data:image/png;base64,{b64}"