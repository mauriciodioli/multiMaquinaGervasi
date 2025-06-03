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





analisis_densidad = Blueprint('analisis_densidad', __name__)




# Curvas predefinidas para simulación rápida
CURVAS_SIMULADAS = {
    'telares_2_': [100, 90, 60, 30, 15, 8, 2, 0.5],
    'piedra_negra_': [100, 85, 50, 25, 10, 5, 1, 0.2],
    'telares_1_': [100, 92, 65, 40, 22, 10, 3, 0.7],
}

TAMICES_DEFAULT = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074]

def simular_mezcla_manual_simple( proporciones, curvas_usuario):
    pesos = []
    curvas = []

    for nombre, porcentaje in proporciones.items():
        datos_curva = curvas_usuario.get(nombre)

        if not datos_curva:
            return {"error": f"❌ Faltan datos de curva para '{nombre}'"}, 400

        curva = datos_curva.get("reales")
        if not curva:
            return {"error": f"❌ La curva de '{nombre}' no tiene datos reales"}, 400

        curvas.append(curva)
        pesos.append(porcentaje / 100)

    if not curvas or not pesos:
        return {"error": "❌ No se encontraron curvas válidas"}, 400

    curva_resultante = calcular_curva_resultante_simple(curvas, pesos)
    curva_fuller = calcular_curva_fuller(TAMICES_DEFAULT, d_max=9.5, n=0.5)
    diferencias = [abs(a - b) for a, b in zip(curva_resultante, curva_fuller)]
    zonas = evaluar_mezcla_promedio(TAMICES_DEFAULT, diferencias)

    return {
        "curva_resultante": curva_resultante,
        "curva_fuller": curva_fuller,
        "zonas": zonas
    }



def calcular_curva_resultante_simple(curvas, pesos):
    """Calcula la curva combinada ponderada por pesos."""
    curva_resultante = []
    for i in range(len(curvas[0])):
        suma = sum(peso * curva[i] for curva, peso in zip(curvas, pesos))
        curva_resultante.append(suma)
    return curva_resultante
