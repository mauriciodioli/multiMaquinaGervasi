import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify
from collections import defaultdict
import numpy as np
from flask import jsonify, request
from scipy.optimize import minimize




densidadFuller = Blueprint('densidadFuller', __name__)


PERFILES_TAMICES = {
    "hormigon_argentino": {
        "grueso": { "umbral_min": 4.75, "limites": { "ok": 40 } },
        "medio":  { "umbral_min": 0.6, "umbral_max": 4.75, "limites": { "exceso_grave": 70, "limite_superior": 50, "ok": 0 } },
        "fino":   { "umbral_max": 0.6, "limites": { "exceso_grave": 60, "exceso": 40, "ok": 0 } }
    },
    "granulometria_italiana": {
        "grueso": { "umbral_min": 5, "limites": { "ok": 35 } },
        "medio":  { "umbral_min": 0.8, "umbral_max": 5, "limites": { "exceso_grave": 75, "limite_superior": 55, "ok": 0 } },
        "fino":   { "umbral_max": 0.8, "limites": { "exceso_grave": 65, "exceso": 45, "ok": 0 } }
    }
}





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
    perfil = data.get("perfil", "0.5")

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
        curva_resultante = calcular_curva_resultante(mezclas, d_max, n, perfil)
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


def calcular_curva_resultante(mezclas, d_max, n, perfil="hormigon_argentino"):
    """Calcula la curva promedio de todas las mezclas y devuelve la imagen en base64 + datos"""
    tamiz_data = defaultdict(list)

    for mezcla in mezclas:
        for t, p in zip(mezcla["tamices"], mezcla["porcentajes_reales"]):
            tamiz_data[t].append(p)

    # Ordenar y calcular promedio por tamiz
    tamices_ordenados = sorted(tamiz_data.keys(), reverse=True)
    promedio_reales = [np.mean(tamiz_data[t]) for t in tamices_ordenados]
    curva_fuller_resultante = [(t / d_max) ** n * 100 for t in tamices_ordenados]

    # Clasificaciones por tamiz
    clasificaciones = [clasificar_tamiz(t, p,perfil) for t, p in zip(tamices_ordenados, promedio_reales)]

    # Generar gráfico
    fig, ax = plt.subplots()
    ax.plot(tamices_ordenados, promedio_reales, marker='o', label='Promedio Real')
    ax.plot(tamices_ordenados, curva_fuller_resultante, marker='x', label='Fuller Ideal')
    ax.invert_xaxis()
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
        "clasificaciones": clasificaciones,
        "grafico": f"data:image/png;base64,{curva_global_base64}"
    }
    
    
    
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz* segun norma  ASTM C136 o IRAM 1505******************
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz******************************************************


def clasificar_tamiz(tamiz, porcentaje, perfil="hormigon_argentino"):
    c = PERFILES_TAMICES.get(perfil)
    if not c:
        raise ValueError(f"Perfil desconocido: {perfil}")

    if tamiz > c["grueso"]["umbral_min"]:
        tipo = "Grueso"
        return f"{tipo} ( OK)" if porcentaje >= c["grueso"]["limites"]["ok"] else f"{tipo} ( Bajo aporte)"
    elif c["medio"]["umbral_min"] <= tamiz <= c["medio"]["umbral_max"]:
        tipo = "Medio"
        if porcentaje > c["medio"]["limites"]["exceso_grave"]:
            return f"{tipo} ( Exceso grave)"
        elif porcentaje > c["medio"]["limites"]["limite_superior"]:
            return f"{tipo} ( Limite superior)"
        else:
            return f"{tipo} ( OK)"
    else:
        tipo = "Fino"
        if porcentaje > c["fino"]["limites"]["exceso_grave"]:
            return f"{tipo} ( Exceso grave)"
        elif porcentaje > c["fino"]["limites"]["exceso"]:
            return f"{tipo} ( Exceso)"
        else:
            return f"{tipo} ( OK)"
    
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

        # Generar etiquetas de mezcla y diccionario con pesos en %
    etiquetas_mezclas = {
        mezcla["nombre"]: round(p * 100, 2)
        for mezcla, p in zip(mezclas, pesos)
    }

    explicacion = interpretar_mezcla_optima(etiquetas_mezclas, round(error_total(pesos), 2))
 
    # Devolver todo junto
    return jsonify({
        "pesos": list(etiquetas_mezclas.values()),
        "nombres_mezclas": list(etiquetas_mezclas.keys()),
        "tamices": tamices_comunes,
        "curva_optima": list(curva_optima),
        "curva_ideal": list(curva_fuller),
        "error_promedio": round(error_total(pesos), 2),
        "explicacion": explicacion
    })








def interpretar_mezcla_optima(mezclas, error_promedio, error_anterior=None):
    explicaciones = []
    resumen = []

    for nombre, porcentaje in mezclas.items():
        if porcentaje == 0:
            explicaciones.append(f"🔸 **{nombre} (0%)**: No aporta valor a la mezcla óptima y fue descartada automáticamente.")
        elif porcentaje < 20:
            explicaciones.append(f"🔸 **{nombre} ({porcentaje:.2f}%)**: Aporta en menor medida, posiblemente para ajustar detalles finos.")
        elif porcentaje < 50:
            explicaciones.append(f"🔸 **{nombre} ({porcentaje:.2f}%)**: Contribuye equilibradamente a mejorar la distribución de tamaños.")
        else:
            explicaciones.append(f"🔸 **{nombre} ({porcentaje:.2f}%)**: Representa la mayor parte de la mezcla y corrige un déficit clave.")

    resumen.append(f"🧠 **Mezcla Óptima Calculada**")
    resumen.append(f"**Error promedio**: {error_promedio:.2f}%")

    if error_anterior is not None:
        mejora = error_anterior - error_promedio
        resumen.append(f"📉 Se redujo el error desde {error_anterior:.2f}% a {error_promedio:.2f}%, logrando una curva más cercana a la ideal.")

    resumen.append("\n**Interpretación de las proporciones:**")
    resumen.extend(explicaciones)

    return "\n".join(resumen)








