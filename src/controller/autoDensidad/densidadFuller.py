import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify
from collections import defaultdict
import numpy as np
from flask import jsonify, request
import pandas as pd
from scipy.optimize import minimize
from controller.autoDensidad.calcularMezclaOptima import calcular_mezcla_optima




densidadFuller = Blueprint('densidadFuller', __name__)


curvas_guardadas = []
pesos_optimos = []
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
    global curvas_guardadas, pesos_optimos
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
    parametros_personalizados = data.get("parametros_personalizados", None)

    resultados = []
    curvas_individuales = []
    nombres_mezclas = []

    for mezcla in mezclas:
        nombre = mezcla.get("nombre", "Sin nombre")
        tamices = mezcla.get("tamices", [])
        reales = mezcla.get("porcentajes_reales", [])
        reales = reales[::-1]
        if not tamices or not reales or len(tamices) != len(reales):
            continue  # O agregar error al resultado
        curvas_individuales.append(reales)
        nombres_mezclas.append(nombre)

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
        # Preparar DataFrame para visualizar
        df = pd.DataFrame({
            'Tamiz (mm)': tamices,
            'P reales (%)': reales,
            'P Fuller (%)': curva_fuller,
            'ΔP (%)': diferencias
        })
        # print(df.to_string())

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        evaluacion, error_promedio = evaluar_mezcla(diferencias)  # 💥 Obtenemos la evaluación y el error promedio de cada mezcla
        ajustes = sugerir_ajustes(tamices, diferencias) # 💥 Sugerimos ajustes según las diferencias

        resultados.append({
            "nombre": nombre,
            "curva_ideal": curva_fuller,
            "reales": reales,
            "diferencias": diferencias,
            "grafico": f"data:image/png;base64,{img_base64}",
            "evaluacion": evaluacion,
            "error_promedio": error_promedio,
            "ajustes": ajustes,
            "tamices": tamices
        })


          # 💥 Llamás a la nueva función acá
        curva_resultante = calcular_curva_resultante(mezclas, d_max, n, perfil,parametros_personalizados)
        # Comparar la curva promedio con Fuller ideal
        tamices_res = curva_resultante["tamices"]
        promedios_res = curva_resultante["promedios"]
        curva_fuller_res = calcular_curva_fuller(tamices_res, d_max, n)
        promedios_res1 = promedios_res[::-1]
        diferencias_res = [r - f for r, f in zip(promedios_res1, curva_fuller_res)]
        diferencias_res = diferencias_res[::-1]
        # Evaluar y sugerir
        evaluacion_res, error_prom_res = evaluar_mezcla(diferencias_res)
       
       
       
       
       
       
     # Armar lista de curvas y tamices para la optimización
    resultado_optimo = calcular_mezcla_optima(curvas_individuales, tamices, d_max, n)
    if "pesos" in resultado_optimo:
        for i, r in enumerate(resultados):
            r["proporcion_optima"] = resultado_optimo["pesos"][i]

    for mezcla in mezclas:
        porcentajes = mezcla.get("porcentajes_reales", [])
        if porcentajes:
            curvas_individuales.append(porcentajes)

    if curvas_individuales:
        tamices_base = mezclas[0].get("tamices", [])
        resultado_optimo = calcular_mezcla_optima(curvas_individuales, tamices_base, d_max, n)
    else:
        resultado_optimo = {"error": "No hay mezclas válidas para optimizar."}   

    return jsonify({
        "resultados": resultados,
        "curva_resultante": curva_resultante,
        "mezcla_optima": resultado_optimo,
        "tamices_res": tamices_res 
    })
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@densidadFuller.route('/calcularCurvaCorregida/', methods=['POST'])
def calcular_curva_corregida():  

    data = request.get_json()
    curvas = data.get("curvas")
    pesos = data.get("pesos")
    tamices = data.get("tamices")      
    nombres_materiales = data.get("nombreProductos", [])  # Lista como ["0-8 Reciclado", "Arena fina", ...]
    print(tamices)

    if not curvas or not pesos or not tamices:
        return jsonify({"error": "Faltan datos de curvas, pesos o tamices"}), 400

    total_pesos = sum(pesos)
    if total_pesos == 0:
        return jsonify({"error": "Los pesos no pueden ser todos cero"}), 400

    pesos_normalizados = [p / total_pesos for p in pesos]

    curva_corregida = [
        sum(p * curva[i] for p, curva in zip(pesos_normalizados, curvas))
        for i in range(len(curvas[0]))
    ]

    d_max = max(tamices)
    n = 0.5
    curva_fuller_resultante = [(d / d_max) ** n * 100 for d in tamices]

    curva_promedio = [
        sum(curva[i] for curva in curvas) / len(curvas)
        for i in range(len(curvas[0]))
    ]

    # Calcular diferencias
    diferencias = [real - ideal for real, ideal in zip(curva_promedio, curva_fuller_resultante)]

    # Generar gráfico
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(tamices, curva_promedio, marker='o', label='Promedio Real', color='blue')
    ax.plot(tamices, curva_fuller_resultante, marker='x', label='Fuller Ideal', color='orange')
    ax.plot(tamices, curva_corregida, marker='s', linestyle='--', label='Corregida Óptima', color='green')

    acciones_textuales = []

    # Precalcular curvas individuales con peso aplicado
    pesos_normalizados = [p / sum(pesos) for p in pesos]
    curvas_individuales_por_material = [
        [peso * curva[i] for i in range(len(tamices))]
        for peso, curva in zip(pesos_normalizados, curvas)
    ]
    material_por_indice = {i: nombre for i, nombre in enumerate(nombres_materiales)}

    for i, (t, y_real, y_ideal) in enumerate(zip(tamices, curva_promedio, curva_fuller_resultante)):
        ax.plot([t, t], [y_real, y_ideal], color='red', linestyle='-', linewidth=1)
        diferencia = round(y_real - y_ideal, 1)
    

        # Determinar la zona
        if t > 4:
            zona = "gruesos"
        elif t > 1:
            zona = "medios"
        else:
            zona = "finos"

        etiqueta_valor = f"{diferencia:+.1f}%"
        etiqueta_zona = f"{zona}"

        # Mostrar diferencia (%)
        ax.text(t, y_ideal + 3, etiqueta_valor, color='red', fontsize=8, ha='right', fontweight='normal')

        # Mostrar zona granulométrica en azul y negrita justo debajo
        ax.text(t, y_ideal - 3, f"{etiqueta_zona}", color='blue', fontsize=8, ha='right', fontweight='bold')


        contribuciones_en_punto = [curva[i] for curva in curvas_individuales_por_material]
        indice_material_max = contribuciones_en_punto.index(max(contribuciones_en_punto))
        nombre_material = nombres_materiales[indice_material_max]
        mezcla_origen = material_por_indice.get(indice_material_max, "sconosciuto")
        


        if diferencia > 0:
            accion = f"→ reducir {nombre_material} (de mezcla: {mezcla_origen})"
            acciones_textuales.append(f"Ridurre il materiale {zona} ({nombre_material}) - eccesso di {abs(diferencia):.1f}% (mezcla: {mezcla_origen})")
        elif diferencia < 0:
            accion = f"→ agregar {nombre_material} (de mezcla: {mezcla_origen})"
            acciones_textuales.append(f"Aumentare il materiale {zona} ({nombre_material}) - deficit di {abs(diferencia):.1f}% (mezcla: {mezcla_origen})")
        else:
            accion = ""

        if accion:
            ax.text(t, y_real, accion, color='red', fontsize=8, ha='left', va='center')






    ax.invert_xaxis()
    ax.set_title("Average, Corrected and Fuller Curve")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.grid(True)
    ax.legend()

    # Mostrar DataFrame en consola (debug)
   # Crear DataFrame base con tamices
    df_debug = pd.DataFrame({'Tamiz (mm)': tamices})

    # Curvas individuales sin peso
    for idx, curva in enumerate(curvas):
        df_debug[f"{nombres_materiales[idx]} (sin peso)"] = curva

    # Curvas individuales ponderadas
    for idx, curva in enumerate(curvas):
        ponderada = [p * pesos_normalizados[idx] for p in curva]
        df_debug[f"{nombres_materiales[idx]} (ponderada)"] = ponderada

    # Agregar promedio, corregida e ideal
    df_debug['Promedio'] = curva_promedio
    df_debug['Corregida'] = curva_corregida
    df_debug['Fuller Ideal'] = curva_fuller_resultante
    df_debug['Δ Promedio - Ideal'] = diferencias

    # Mostrar
    print("\n==== Debug Completo de Curvas ====")
    print(df_debug.to_string(index=False))


    # Exportar como imagen base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    interpretaciones = []

    for nombre, peso in zip(nombres_materiales, pesos):
        peso_redondeado = round(peso, 2)
        if peso_redondeado <= 0.01:
            interpretaciones.append(f"{nombre}: {peso_redondeado:.2f}% (❌ scartato per non aver apportato miglioramenti)")
        elif peso_redondeado >= 5:  # o el umbral que consideres "aporta"
            interpretaciones.append(f"{nombre}: {peso_redondeado:.2f}% (⚖️ balanced contribution)")
        else:
            interpretaciones.append(f"{nombre}: {peso_redondeado:.2f}% (❔ marginal contribution)")
    
    return jsonify({
            "curva_corregida": curva_corregida,
            "grafico_base64": f"data:image/png;base64,{img_base64}",
            "diferencias": diferencias,
            "interpretacion_materiales": interpretaciones,
            "acciones_recomendadas": acciones_textuales
            })























































def calcular_curva_resultante(mezclas, d_max, n, perfil="hormigon_argentino", parametros_personalizados=None):
    """Calcula la curva promedio de todas las mezclas y devuelve el análisis completo"""
    tamiz_data = defaultdict(list)

    for mezcla in mezclas:
        for t, p in zip(mezcla["tamices"], mezcla["porcentajes_reales"]):
            tamiz_data[t].append(p)

    # ✅ Ordenar tamices de menor a mayor
    tamices_ordenados = sorted(tamiz_data.keys(), reverse=True)
    promedio_reales = [np.mean(tamiz_data[t]) for t in tamiz_data]

    # Calcular curva ideal
    # Calcular curva ideal con tamices en orden ascendente y luego invertir para que coincida con el gráfico
    tamices_asc = sorted(tamiz_data.keys())
    curva_fuller_resultante = calcular_curva_fuller(tamices_asc, d_max, n)[::-1]


    # Clasificar cada tamiz con el perfil adecuado
    clasificaciones = [
        clasificar_tamiz(t, p, perfil, parametros_personalizados)
        for t, p in zip(tamices_ordenados, promedio_reales)
    ]

    # ✅ Calcular diferencias, evaluación y ajustes
    diferencias = [r - f for r, f in zip(promedio_reales, curva_fuller_resultante)]
    evaluacion, error_promedio = evaluar_mezcla(diferencias)# Obenemos la evaluación y el error promedio de cada mezcla
    ajustes = sugerir_ajustes(tamices_ordenados, diferencias)

    # Generar gráfico
    promedios_invertidos = promedio_reales[::-1]
    fig, ax = plt.subplots()
    ax.plot(tamices_ordenados, promedios_invertidos, marker='o', label='Promedio Real')
    ax.plot(tamices_ordenados, curva_fuller_resultante, marker='x', label='Fuller Ideal')
    ax.invert_xaxis()
    ax.set_title("Curva Promedio de Todas las Mezclas")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.grid(True)
    ax.legend()
    df = pd.DataFrame({
            'Tamiz (mm)': tamices_ordenados,
            'P reales (%)': promedios_invertidos,
            'P Fuller (%)': curva_fuller_resultante,
            'ΔP (%)': diferencias
        })
    print(df.to_string())
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    curva_global_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    return {
        "tamices": tamices_ordenados,
        "promedios": promedios_invertidos,
        "clasificaciones": clasificaciones,
        "curva_ideal": curva_fuller_resultante,
        "diferencias": diferencias,
        "evaluacion": evaluacion,
        "error_promedio": error_promedio,
        "ajustes": ajustes,
        "grafico": f"data:image/png;base64,{curva_global_base64}"
    }

    
    
    
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz* segun norma  ASTM C136 o IRAM 1505******************
# Clasificaciones por tamiz******************************************************
# Clasificaciones por tamiz******************************************************


def clasificar_tamiz(tamiz, porcentaje, perfil, parametros_personalizados=None):
    if perfil == "personalizado":
        if not parametros_personalizados:
            return "Personalizado (sin clasificación detallada)"
        c = parametros_personalizados
    else:
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
                          
   
    curva_fuller = np.array(calcular_curva_fuller(tamices_comunes, d_max, n=0.5))

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








