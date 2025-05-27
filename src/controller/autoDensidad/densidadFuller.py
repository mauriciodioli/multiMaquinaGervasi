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
from controller.autoDensidad.calcularMezclaOptima import mostrar_datos_crudos_entrada
from controller.autoDensidad.calcularMezclaOptima import encontrar_n_optimo




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



 
    
# calcular_curva_fuller ******************************************************
# calcular_curva_fuller ******************************************************
# calcular_curva_fuller ******************************************************
# calcular_curva_fuller ******************************************************
# calcular_curva_fuller ******************************************************
def calcular_curva_fuller(tamices, d_max, n=0.5):
    return [(d / d_max) ** n * 100 for d in tamices]









@densidadFuller.route('/densidadFullerMultiple/', methods=['POST'])
def densidad_fuller_multiple():

    data = request.get_json()
  
    mezclas = data.get("mezclas", [])
    d_max = float(data.get("d_max", 25))    
    n = float(data.get("n", 0.45))
    perfil = data.get("perfil", "0.5")
    parametros_personalizados = data.get("parametros_personalizados", None)
   
    resultados = []
    curvas_individuales = []
    nombres_mezclas = []
    curva_resultante = []
    mostrar_datos_crudos_entrada(mezclas)


    for mezcla in mezclas:
        nombre = mezcla.get("nombre", "Sin nombre")
        tamices = mezcla.get("tamices", [])
        reales = mezcla.get("porcentajes_reales", [])
        reales = reales
        if not tamices or not reales or len(tamices) != len(reales):
            continue  # O agregar error al resultado
        curvas_individuales.append(reales)
        nombres_mezclas.append(nombre)
        n_optimo, curva_fuller_resultante, error_promedio = encontrar_n_optimo(tamices, reales, d_max)

        curva_fuller = calcular_curva_fuller(tamices, d_max, n_optimo)
        diferencias = [r - f for r, f in zip(reales, curva_fuller)]
        # Valores de X (los tamices, de mayor a menor)
      

        # Valores de Y constantes en 1
        y_constante = [0] * len(tamices)
        # Generar gráfico
        fig, ax = plt.subplots()
        ax.plot(tamices, reales, marker='o', label='Vero')
        ax.plot(tamices, curva_fuller, marker='x', label='Ideale più completo')             
        # Graficar la línea horizontal
        ax.plot(tamices, y_constante, linestyle='-', marker='o', label='milimeters' , color='black', alpha=0.5)  
        # Mostrar los valores de tamiz sobre los puntos de la curva horizontal
        for x in tamices:
            ax.text(x, 0.5, str(x), color='black', fontsize=8, ha='center')
        
        # Líneas verticales desde la curva negra a los valores máximos por tamiz
        for i, x in enumerate(tamices):
            y_max = max(reales[i], curva_fuller[i])
            ax.plot([x, x], [0, y_max], linestyle='--', color='gray', alpha=0.4)


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
            'ΔP (%)': diferencias,
            'd_max': d_max,
            'n': n_optimo
        })
        print(df.to_string())

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
    curva_resultante = calcular_curva_resultante(resultados, d_max, n)
    print("=== Curva Resultante ===")
        
        
    # 🔍 Evaluar y sugerir usando la curva promedio
    evaluacion_res = evaluar_mezcla_promedio(
        curva_resultante["tamices"],
        curva_resultante["diferencias"]
    )
    

    # 🖨 Mostrar por consola para debug
    print("=== Evaluación de Curva Promedio ===")
    print(f"Estado: {evaluacion_res['estado']}")
    print(f"Error promedio: {evaluacion_res['error_promedio']}")
    print("Recomendaciones:")
    for r in evaluacion_res["recomendaciones"]:
        print(" -", r)
       
       
       
       
       
     # Armar lista de curvas y tamices para la optimización
    resultado_optimo = calcular_mezcla_optima(curvas_individuales,  curva_resultante["tamices"], d_max, n)
    if "pesos" in resultado_optimo:
        for i, r in enumerate(resultados):
            print(f"Peso óptimo para {r['nombre']}: {resultado_optimo['pesos']}")
            r["proporcion_optima"] = resultado_optimo["pesos"]

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
        "tamices_res":  curva_resultante["tamices"],
        "evaluacion_promedio": evaluacion_res  # 🔥 Esto se agrega
    })

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def ajustar_pesos_por_factor(pesos_por_zona, factor):
    """
    Ajusta los pesos por zona aplicando un factor de corrección hacia el ideal.
    Por ejemplo, si el factor es 0.5, se hace una corrección del 50%.
    """
    pesos_ajustados = {}

    for mezcla, zonas in pesos_por_zona.items():
        total_original = sum(zonas.values())
        pesos_ajustados[mezcla] = {}

        for zona, valor in zonas.items():
            # Aplica el factor de ajuste proporcional
            ajuste = (valor - (total_original / 3)) * factor
            nuevo_valor = (total_original / 3) + ajuste
            pesos_ajustados[mezcla][zona] = round(nuevo_valor, 2)

    return pesos_ajustados  
    
    
    
    
    
    
    
    
@densidadFuller.route('/calcularCurvaCorregida/', methods=['POST'])
def calcular_curva_corregida():  

    data = request.get_json()
    curvas = data.get("curvas")
    pesos = data.get("pesos")
    tamices = data.get("tamices")    
    factor = data.get("factor",1)  # Factor de ajuste, por defecto 0.5  
    nombres_materiales = data.get("nombreProductos", [])
    print("\n=== DEBUG: Datos recibidos ===")
    print("Curvas:", curvas)
    print("Pesos:", pesos)
    print("Tamices:", tamices)
    print("Nombres de materiales:", nombres_materiales)
    print("Tipo de curvas:", type(curvas))
    print("Tipo de pesos:", type(pesos))

    pesos_por_zona_dicts = pesos  # Guardamos el original antes de transformarlo

    # Llamar a función solo con los dicts originales
    pesos_finales_normalizados = calcular_pesos_finales_normalizados(pesos_por_zona_dicts)

    # Ahora sí transformar pesos para otras cosas si hace falta
    if isinstance(pesos, dict):
        pesos = list(pesos.values())
    elif isinstance(pesos, list) and isinstance(pesos[0], dict):
        pesos = [list(p.values())[0] for p in pesos]
    if not curvas or not pesos or not tamices:
        return jsonify({"error": "Faltan datos de curvas, pesos o tamices"}), 400

    

    total_pesos = sum(pesos)
    if total_pesos == 0:
        return jsonify({"error": "Los pesos no pueden ser todos cero"}), 400

    pesos_normalizados = [p / total_pesos for p in pesos]
   

  


    d_max = max(tamices)
    n_optimo, curva_fuller_resultante, error_promedio = encontrar_n_optimo(tamices, curvas, d_max)
    curva_fuller_resultante = [(d / d_max) ** n_optimo * 100 for d in tamices]

    curva_promedio = [
        sum(curva[i] for curva in curvas) / len(curvas)
        for i in range(len(curvas[0]))
    ]
    curva_corregida = calcular_curva_corregida_con_ajuste(curva_promedio, curva_fuller_resultante, factor)
    diferencias = [real - ideal for real, ideal in zip(curva_promedio, curva_fuller_resultante)]
    # Valores de Y constantes en 0
    y_constante = [0] * len(tamices)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(tamices, curva_promedio, marker='o', label='Media effettiva', color='blue')
    ax.plot(tamices, curva_fuller_resultante, marker='x', label='Ideale più completo', color='orange')
    ax.plot(tamices, curva_corregida, marker='s', linestyle='--', label='Corretto Ottimale', color='green')
    ax.plot(tamices, y_constante, linestyle='-', marker='o', label='milimeters' , color='black', alpha=0.5)  
    
    
    for x in tamices:
        ax.text(x, 0.5, str(x), color='black', fontsize=8, ha='center')
    
    # Líneas verticales desde la curva negra a los valores máximos por tamiz
    for i, x in enumerate(tamices):
        y_max = max(curva_promedio[i], curva_fuller_resultante[i])
        ax.plot([x, x], [0, y_max], linestyle='--', color='gray', alpha=0.4)
  

    acciones_textuales = []
    curvas_individuales_por_material = [
        [peso * curva[i] for i in range(len(tamices))]
        for peso, curva in zip(pesos_normalizados, curvas)
    ]
    material_por_indice = {i: nombre for i, nombre in enumerate(nombres_materiales)}

    zonas_materiales = {nombre: {"gruesos": 0, "medios": 0, "finos": 0} for nombre in nombres_materiales}
    zonas_totales = {"gruesos": 0, "medios": 0, "finos": 0}

    for i, (t, y_real, y_ideal) in enumerate(zip(tamices, curva_promedio, curva_fuller_resultante)):
        ax.plot([t, t], [y_real, y_ideal], color='red', linestyle='-', linewidth=1)
        diferencia = y_real - y_ideal
        diferencia_ajustada = diferencia * factor  # ← Aplicamos el factor

        if t > 4:
            zona = "gruesos"
        elif t > 1:
            zona = "medios"
        else:
            zona = "finos"

        etiqueta_valor = f"{diferencia_ajustada:+.1f}%"
        ax.text(t, y_ideal + 3, etiqueta_valor, color='red', fontsize=8, ha='right')
        ax.text(t, y_ideal - 3, f"{zona}", color='blue', fontsize=8, ha='right', fontweight='bold')

        contribuciones_en_punto = [curva[i] for curva in curvas_individuales_por_material]
        total_punto = sum(contribuciones_en_punto)
        if total_punto == 0:
            continue

        for idx, contrib in enumerate(contribuciones_en_punto):
            nombre = nombres_materiales[idx]
            zonas_materiales[nombre][zona] += contrib
            zonas_totales[zona] += contrib

        indice_material_max = contribuciones_en_punto.index(max(contribuciones_en_punto))
        nombre_material = nombres_materiales[indice_material_max]
        mezcla_origen = material_por_indice.get(indice_material_max, "sconosciuto")

        if diferencia_ajustada > 0:
            accion = f"→ reducir {nombre_material} (de mezcla: {mezcla_origen})"
            acciones_textuales.append(
                f"Ridurre il materiale {zona} ({nombre_material}) - eccesso di {abs(diferencia_ajustada):.1f}% (mezcla: {mezcla_origen})"
            )
        elif diferencia_ajustada < 0:
            accion = f"→ agregar {nombre_material} (de mezcla: {mezcla_origen})"
            acciones_textuales.append(
                f"Aumentare il materiale {zona} ({nombre_material}) - deficit di {abs(diferencia_ajustada):.1f}% (mezcla: {mezcla_origen})"
            )
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

    df_debug = pd.DataFrame({'Tamiz (mm)': tamices})
    for idx, curva in enumerate(curvas):
        df_debug[f"{nombres_materiales[idx]} (sin peso)"] = curva
    for idx, curva in enumerate(curvas):
        ponderada = [p * pesos_normalizados[idx] for p in curva]
        df_debug[f"{nombres_materiales[idx]} (ponderada)"] = ponderada
    df_debug['Promedio'] = curva_promedio
    df_debug['Corregida'] = curva_corregida
    df_debug['Fuller Ideal'] = curva_fuller_resultante
    df_debug['Δ Promedio - Ideal'] = diferencias
    df_debug['d_max'] = d_max
    df_debug['n'] = n_optimo

    print("\n==== Debug Completo de Curvas ====")
    print(df_debug.to_string(index=False))

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
        elif peso_redondeado >= 5:
            interpretaciones.append(f"{nombre}: {peso_redondeado:.2f}% (⚖️ balanced contribution)")
        else:
            interpretaciones.append(f"{nombre}: {peso_redondeado:.2f}% (❔ marginal contribution)")
   
    # Calcular pesos redistribuidos por zona
    pesos_por_zona = {}
    for nombre in nombres_materiales:
        contribs = zonas_materiales[nombre]
        redistrib = {
            zona: round((contribs[zona] / zonas_totales[zona]) * 100, 2) if zonas_totales[zona] > 0 else 0.0
            for zona in ["gruesos", "medios", "finos"]
        }
        pesos_por_zona[nombre] = redistrib

    print("\n=== Pesos redistribuidos por mezcla y zona ===")
    for nombre, zonas in pesos_por_zona.items():
        print(f"{nombre}: {zonas}")
    # Aplica ajuste con un factor de 0.5 (50%)
    pesos_ajustados = ajustar_pesos_por_factor(pesos_por_zona, factor)

    return jsonify({
        "curva_corregida": curva_corregida,
        "grafico_base64": f"data:image/png;base64,{img_base64}",
        "diferencias": diferencias,
        "interpretacion_materiales": interpretaciones,
        "acciones_recomendadas": acciones_textuales,
        "pesos_por_zona": pesos_ajustados
    })
    
    
    
    
    
def calcular_curva_corregida_con_ajuste(curva_promedio, curva_fuller, factor=1.0):
    """
    Genera una curva corregida a partir de la curva promedio y la curva ideal (Fuller),
    aplicando un factor de corrección.

    :param curva_promedio: List[float], valores reales promedio
    :param curva_fuller: List[float], valores ideales de Fuller
    :param factor: float, cuánta proporción de la corrección aplicar (entre 0 y 1)
    :return: List[float], curva corregida
    """
    if len(curva_promedio) != len(curva_fuller):
        raise ValueError("Las curvas deben tener la misma longitud")

    return [
        curva_promedio[i] + factor * (curva_fuller[i] - curva_promedio[i])
        for i in range(len(curva_promedio))
    ]

def calcular_pesos_finales_normalizados(pesos_por_zona):
    pesos_finales = []
    for zonas in pesos_por_zona:
        total = zonas.get("gruesos", 0) + zonas.get("medios", 0) + zonas.get("finos", 0)
        pesos_finales.append(total)

    suma = sum(pesos_finales)
    if suma == 0:
        return [1 / len(pesos_finales)] * len(pesos_finales)

    return [p / suma for p in pesos_finales]






 

   
















































def calcular_curva_resultante(resultados, d_max, n_optimo):
 
    if not resultados:
        return None

    # 1. Extraer curvas reales y curvas ideales de todas las mezclas
    todas_reales = [r["reales"] for r in resultados]
    todas_fuller = [r["curva_ideal"] for r in resultados]
    tamices = resultados[0]["tamices"]  # Asumimos que son iguales en todas

    # 2. Convertir a arrays para cálculo vectorizado
    reales_array = np.array(todas_reales)
    fuller_array = np.array(todas_fuller)

    # 3. Calcular promedios
    promedio_reales = list(np.mean(reales_array, axis=0))
    promedio_fuller = list(np.mean(fuller_array, axis=0))

    # 4. Diferencias entre curva promedio real y curva promedio ideal
    diferencias = [r - f for r, f in zip(promedio_reales, promedio_fuller)]

    # 5. Evaluar y sugerir ajustes
    evaluacion, error_promedio = evaluar_mezcla(diferencias)
    
    print("Diferencias que se pasan a sugerir_ajustes:")
    print(diferencias)
    ajustes = sugerir_ajustes(tamices, diferencias)
    # Valores de Y constantes en 0
    y_constante = [0] * len(tamices)
    # 6. Graficar
    fig, ax = plt.subplots()
    ax.plot(tamices, promedio_reales, marker='o', label='Media effettiva')
    ax.plot(tamices, promedio_fuller, marker='x', label='Media di Fuller')
    ax.plot(tamices, y_constante, linestyle='-', marker='o', label='milimeters' , color='black', alpha=0.5)  
    # Mostrar los valores de tamiz sobre los puntos de la curva horizontal
    for x in tamices:
        ax.text(x, 0.5, str(x), color='black', fontsize=8, ha='center')
    
    # Líneas verticales desde la curva negra a los valores máximos por tamiz
    for i, x in enumerate(tamices):
        y_max = max(promedio_reales[i], promedio_fuller[i])
        ax.plot([x, x], [0, y_max], linestyle='--', color='gray', alpha=0.4)



    # 💬 Anotar valores sobre cada punto
    for x, y in zip(tamices, promedio_reales):
        ax.text(x, y + 2, f"{y:.1f}%", ha='center', fontsize=8, color='blue')

    for x, y in zip(tamices, promedio_fuller):
        ax.text(x, y - 4, f"{y:.1f}%", ha='center', fontsize=8, color='orange')
        
    # Mostrar diferencia en % entre curvas, coloreado por zona
    zonas = []
    diferencias_grafico  = []
    for x, real, ideal in zip(tamices, promedio_reales, promedio_fuller):
        diferencia = real - ideal
        diferencias_grafico.append(diferencia)
        etiqueta = f"{diferencia:+.1f}%"

        if x > 4.75:
            zona = "gruesos"
            color = "darkred"
        elif x > 0.6:
            zona = "medios"
            color = "darkorange"
        else:
            zona = "finos"
            color = "green"

        zonas.append(zona)
        ax.text(x, (real + ideal) / 2, etiqueta, fontsize=8, color=color, ha='left')

    ax.invert_xaxis()
    ax.set_title("Curva Promedio de Todas las Mezclas")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.grid(True)
    ax.legend()

    df = pd.DataFrame({
    'Tamiz (mm)': tamices,
    'Prom reales (%)': promedio_reales,
    'Prom Fuller (%)': promedio_fuller,
    'ΔProm (%)': diferencias,
    'Zona': zonas,
    'd_max': d_max,
    'n': n_optimo
    })
    print(df.to_string())

    # Mostrar promedios por zona
    errores_por_zona = df.groupby("Zona")["ΔProm (%)"].mean().round(2)
    print("\n=== Diferencia promedio por zona ===")
    for zona, valor in errores_por_zona.items():
        signo = "+" if valor >= 0 else ""
        print(f" - {zona.capitalize()}: {signo}{valor}%")

    # 8. Convertir gráfico a imagen base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    curva_global_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()

    # 9. Devolver todo
    return {
        "tamices": tamices,
        "promedios": promedio_reales,
        "curva_ideal": promedio_fuller,
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
        if t <= 0.6:
            zonas["finos"].append(d)
        elif t <= 4.75:
            zonas["medios"].append(d)
        else:
            zonas["gruesos"].append(d)

    ajustes = []

    for zona, valores in zonas.items():
        if not valores:
            ajustes.append(f"{zona.capitalize()}: sin datos.")
            continue

        promedio = np.mean(valores)
        signo = "+" if promedio >= 0 else "-"

        if promedio > 0:
            ajustes.append(f"Reducir material {zona} (exceso de {promedio:.1f}%)")
        elif promedio < 0:
            ajustes.append(f"Aumentar material {zona} (déficit de {abs(promedio):.1f}%)")
        else:
            ajustes.append(f"Material {zona} equilibrado (±0%)")

    return ajustes






def evaluar_mezcla_promedio(tamices, diferencias):
    zonas = []
    errores_por_zona = {"gruesos": [], "medios": [], "finos": []}
    recomendaciones = []

    for i, tamiz in enumerate(tamices):
        delta = diferencias[i]

        # Clasificación por zona granulométrica
        if tamiz > 4.75:
            zona = "gruesos"
        elif tamiz > 0.6:
            zona = "medios"
        else:
            zona = "finos"

        zonas.append(zona)
        errores_por_zona[zona].append(abs(delta))

        # Recomendaciones individuales si querés mantenerlas
        if delta > 10:
            recomendaciones.append(f"Tamiz {tamiz} mm: exceso → reducir material en este rango.")
        elif delta < -10:
            recomendaciones.append(f"Tamiz {tamiz} mm: déficit → agregar material en este rango.")
        else:
            recomendaciones.append(f"Tamiz {tamiz} mm: en rango aceptable.")

    # Calcular error promedio por zona
    resumen_zonal = {}
    for zona in ["gruesos", "medios", "finos"]:
        if errores_por_zona[zona]:
            error_prom_zona = sum(errores_por_zona[zona]) / len(errores_por_zona[zona])
            resumen_zonal[zona] = round(error_prom_zona, 2)
        else:
            resumen_zonal[zona] = 0.0

    # Calcular error promedio general
    total_error = sum(abs(d) for d in diferencias)
    error_promedio = total_error / len(diferencias)

    # Clasificación global
    if error_promedio <= 10:
        estado = "Excelente"
    elif error_promedio <= 25:
        estado = "Aceptable"
    else:
        estado = "Desviada"

    return {
        "estado": estado,
        "error_promedio": round(error_promedio, 2),
        "recomendaciones": recomendaciones,
        "error_por_zona": resumen_zonal
    }








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








