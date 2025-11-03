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
    """
    proporciones: {'arena':40, 'qwe':30, ...}  (en %)
    curvas_usuario: {
      'arena': {'tamices':[... opcional ...], 'reales':[...]},
      'qwe':   {'tamices':[...],               'reales':[...]}
    }
    Alinea TODO a TAMICES_DEFAULT, completa faltantes con 0 y calcula resultado.
    """
    # 1) pesos normalizados
    nombres, pesos_norm = normalizar_pesos_porcentuales(proporciones)

    # 2) alinear curvas a master, rellenando 0 donde falte
    curvas_alineadas = []
    for nombre in nombres:
        datos = curvas_usuario.get(nombre)
        if not datos or 'reales' not in datos:
            return {"error": f"❌ Faltan datos de curva para '{nombre}'"}, 400

        reales  = datos.get('reales', [])
        tamices = datos.get('tamices') or datos.get('mallas')  # soporta dos nombres de campo
        curva_a_9 = alinear_curva_a_master(reales, tamices, TAMICES_DEFAULT)
        curvas_alineadas.append(curva_a_9)

    if not curvas_alineadas:
        return {"error": "❌ No se encontraron curvas válidas"}, 400

    # 3) curva resultante ponderada
    curva_resultante = calcular_curva_resultante_simple(curvas_alineadas, pesos_norm)

    # 4) curva de Fuller usando d_max = max(tamices) (→ 12.5)
    d_max = max(TAMICES_DEFAULT)
    curva_fuller = calcular_curva_fuller(TAMICES_DEFAULT, d_max=d_max, n=0.5)

    # 5) diferencias y evaluación por zonas
    diferencias = [abs(a - b) for a, b in zip(curva_resultante, curva_fuller)]
    zonas = evaluar_mezcla_promedio(TAMICES_DEFAULT, diferencias)

    return {
        "tamices": TAMICES_DEFAULT,
        "curvas_alineadas": curvas_alineadas,       # útil para debug
        "pesos_normalizados": pesos_norm,           # en fracción
        "curva_resultante": curva_resultante,
        "curva_fuller": curva_fuller,
        "zonas": zonas
    }