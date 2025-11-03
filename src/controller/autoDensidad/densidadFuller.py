import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify, redirect
from collections import defaultdict
import numpy as np
from flask import jsonify, request
import pandas as pd
from scipy.optimize import minimize
from controller.autoDensidad.calcularMezclaOptima import calcular_mezcla_optima
from controller.autoDensidad.calcularMezclaOptima import mostrar_datos_crudos_entrada
from controller.autoDensidad.calcularMezclaOptima import encontrar_n_optimo
from controller.autoDensidad.calcularMezclaOptima import calcular_curva_fuller
from controller.autoDensidad.optimizar_fuller import generar_informe_ajuste
from src.utils.auth import current_user

from src.utils.get_textos_menu  import get_textos_menu





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
    
@densidadFuller.route("/pantalla_densidad_fuller_multiple/")
def pantalla_densidad_fuller_multiple():
    usuario = current_user()
    if not usuario:
        return redirect("/login")

    lang = request.cookies.get("lang", "es")
    t_menu = get_textos_menu(lang)

    return render_template(
        "autoDensidad/densidadFullerMultiple.html",
        usuario=usuario,
        t_menu=t_menu
    )






def _redondear_tamiz(x: float, dec=3) -> float:
    # Evita 1.160 vs 1.18 por ruido decimal
    return round(float(x), dec)

def alinear_mezclas_por_tamices(mezclas, dec=3, tol=0.0):
    """
    Devuelve:
      master_tamices (list[float], orden desc)
      mezclas_alineadas (list[dict] con mismas keys que 'mezclas', pero tamices/porcentajes_reales alineados)
    - dec: redondeo de tamices para normalizar (p.ej. 3 decimales).
    - tol: tolerancia opcional para *agrupar* tamices casi iguales (si la querés usar más adelante).
    """
    # 1) Unificar todos los tamices (redondeados) en un master
    master_set = set()
    normalizados = []
    for m in mezclas:
        t_raw = m.get("tamices", []) or []
        r_raw = m.get("porcentajes_reales", []) or []
        # Filtra pares inválidos
        pares = [( _redondear_tamiz(t, dec), float(r) ) for t, r in zip(t_raw, r_raw)]
        normalizados.append({"nombre": m.get("nombre", "Sin nombre"), "pares": pares})
        for t, _ in pares:
            master_set.add(t)

    # 2) Orden convención de tamices: de mayor a menor
    master_tamices = sorted(master_set, reverse=True)

    # 3) Mapear cada mezcla al master; si falta tamiz -> 0.0
    mezclas_alineadas = []
    for item in normalizados:
        nombre = item["nombre"]
        mapa = {}
        for t, r in item["pares"]:
            # si el mismo tamiz aparece varias veces, sumá o tomá el último; acá usamos último
            mapa[t] = r
        reales_alineados = [mapa.get(t, 0.0) for t in master_tamices]
        mezclas_alineadas.append({
            "nombre": nombre,
            "tamices": master_tamices,
            "porcentajes_reales": reales_alineados
        })

    return master_tamices, mezclas_alineadas




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

  # 💥 NUEVO: alinear todas las mezclas a un mismo set de tamices
    master_tamices, mezclas_alineadas = alinear_mezclas_por_tamices(mezclas, dec=3, tol=0.0)

    for mezcla in mezclas_alineadas:  # <— usar las alineadas
        nombre = mezcla.get("nombre", "Sin nombre")
        tamices = mezcla.get("tamices", [])              # ya son master_tamices
        reales = mezcla.get("porcentajes_reales", [])    # ya rellenados con 0

        # con el alineado, estas validaciones ya deberían pasar
        if not tamices or not reales or len(tamices) != len(reales):
            continue

        curvas_individuales.append(reales)
        nombres_mezclas.append(nombre)

        n_optimo, curva_fuller_resultante, error_promedio = encontrar_n_optimo(tamices, reales, d_max)
        curva_fuller = calcular_curva_fuller(tamices, d_max, n_optimo)
        diferencias = [r - f for r, f in zip(reales, curva_fuller)]

        # Valores de X (los tamices, de mayor a menor)
      
        fig, ax_main = plt.subplots()

        # Escala logarítmica para el gráfico original
        ax_main.set_xscale('log')
        ax_main.plot(tamices, reales, marker='o', label='Media effettiva')
        ax_main.plot(tamices, curva_fuller, marker='x', label='Media di Fuller')

      

        # Crear segundo eje inferior solo para etiquetas personalizadas
        ax_main.set_xticks(tamices)
        ax_main.set_xticklabels([str(x) for x in tamices])
        ax_main.tick_params(axis='x', rotation=0)

        # Invertir el eje X para seguir la convención de tamices
        ax_main.invert_xaxis()

        # Estilo
        ax_main.set_title(f"{nombre} - Curva de Fuller")
        ax_main.set_xlabel("Tamiz (mm)")
        ax_main.set_ylabel("% que pasa")
        ax_main.grid(True)
        ax_main.legend()
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
        comentario = ajustes.pop()  # ⚠️ El último ítem es la conclusión general

        resultados.append({
            "nombre": nombre,
            "curva_ideal": curva_fuller,
            "reales": reales,
            "diferencias": diferencias,
            "grafico": f"data:image/png;base64,{img_base64}",
            "evaluacion": evaluacion,
            "error_promedio": error_promedio,
            "ajustes": ajustes,
            "comentario": comentario,  # el diagnóstico global
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
       
       
       
       # ✅ Optimización: una sola vez y con el eje coherente
    resultado_optimo = calcular_mezcla_optima(curvas_individuales, master_tamices, d_max, n)
    if "pesos" in resultado_optimo:
        for r in resultados:
            r["proporcion_optima"] = resultado_optimo["pesos"]

    return jsonify({
        "resultados": resultados,
        "curva_resultante": curva_resultante,
        "mezcla_optima": resultado_optimo,
        "tamices_res": curva_resultante["tamices"],
        "evaluacion_promedio": evaluacion_res
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
    
    
    
    
    
def clasificar_zona_por_tamiz(t):
    """Gruesos: t>4; Medios: 1<t<=4; Finos: t<=1 (tu criterio actual)."""
    if t > 4:
        return "gruesos"
    elif t > 1:
        return "medios"
    return "finos"
    
@densidadFuller.route('/calcularCurvaCorregida/', methods=['POST'])
def calcular_curva_corregida():  

    data = request.get_json()
    curvas = data.get("curvas")
    pesos = data.get("pesos")
    tamices = data.get("tamices")    
    factor = data.get("factor",1)  # Factor de ajuste, por defecto 0.5  
    nombres_materiales = data.get("nombreProductos", [])
    tipo_objetivo = data.get("tipo_objetivo", "bloques")
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

    # Convertir los tamices a etiquetas string
    etiquetas_x = [str(t) for t in tamices]
    posiciones_eje_x = list(range(len(tamices)))  # Posiciones enteras para el eje X

    fig, ax = plt.subplots(figsize=(6, 4))
    
    ax.plot(posiciones_eje_x, curva_promedio, marker='o', label='Media effettiva', color='blue')
    ax.plot(posiciones_eje_x, curva_fuller_resultante, marker='x', label='Ideale più completo', color='orange')
    ax.plot(posiciones_eje_x, curva_corregida, marker='s', linestyle='--', label='Corretto Ottimale', color='green')

    acciones_textuales = []
    curvas_individuales_por_material = [
        [peso * curva[i] for i in range(len(tamices))]
        for peso, curva in zip(pesos_normalizados, curvas)
    ]
    
    # Colores predefinidos para cada tipo de curva
    colores_fijos = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']  # Se repiten si hay más
    estilos_sin_peso = [':'] * len(curvas)
    estilos_ponderado = ['--'] * len(curvas)

    # Agregar curvas individuales originales (sin peso)
    for idx, curva in enumerate(curvas):
        color = colores_fijos[idx % len(colores_fijos)]
        ax.plot(posiciones_eje_x, curva, linestyle=estilos_sin_peso[idx], color=color, alpha=0.4, label=f"{nombres_materiales[idx]} (sin peso)")

    # Agregar curvas ponderadas
    for idx, curva in enumerate(curvas_individuales_por_material):
        color = colores_fijos[idx % len(colores_fijos)]
        ax.plot(posiciones_eje_x, curva, linestyle=estilos_ponderado[idx], color=color, alpha=0.6, label=f"{nombres_materiales[idx]} (ponderada)")

    material_por_indice = {i: nombre for i, nombre in enumerate(nombres_materiales)}
    zonas_materiales = {nombre: {"gruesos": 0, "medios": 0, "finos": 0} for nombre in nombres_materiales}
    zonas_totales = {"gruesos": 0, "medios": 0, "finos": 0}

    for i, (tamiz, y_real, y_ideal) in enumerate(zip(tamices, curva_promedio, curva_fuller_resultante)):
        ax.plot([i, i], [y_real, y_ideal], color='red', linestyle='-', linewidth=1)
        diferencia = y_real - y_ideal
        diferencia_ajustada = diferencia * factor

        if tamiz > 4:
            zona = "gruesos"
        elif tamiz > 1:
            zona = "medios"
        else:
            zona = "finos"

        etiqueta_valor = f"{diferencia_ajustada:+.1f}%"
        ax.text(i, y_ideal + 3, etiqueta_valor, color='red', fontsize=8, ha='right')
        ax.text(i, y_ideal - 3, f"{zona}", color='blue', fontsize=8, ha='right', fontweight='bold')

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
            ax.text(i, y_real, accion, color='red', fontsize=8, ha='left', va='center')

    ax.set_xticks(posiciones_eje_x)
    ax.set_xticklabels(etiquetas_x)
  
    ax.set_title("Average, Corrected and Fuller Curve")
    ax.set_xlabel("Tamiz (mm)")
    ax.set_ylabel("% que pasa")
    ax.grid(True)
    ax.legend(loc='best', fontsize='small')

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

    # Aplica ajuste con el factor (hacia 1/3-1/3-1/3 manteniendo total)
    pesos_ajustados = ajustar_pesos_por_factor(pesos_por_zona, factor)

    informe = generar_informe_ajuste(
        curvas=[np.array(c) for c in curvas],
        nombres=nombres_materiales,
        objetivo=tipo_objetivo
    )

    return jsonify({
        "curva_corregida": curva_corregida,
        "grafico_base64": f"data:image/png;base64,{img_base64}",
        "diferencias": diferencias,
        "interpretacion_materiales": interpretaciones,
        "acciones_recomendadas": acciones_textuales,
        "pesos_por_zona": pesos_ajustados,
        "reporte_ajuste": informe
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

def calcular_pesos_finales_normalizados(pesos_por_zona_dicts):
    """
    Acepta:
      - dict: {"arena": {"gruesos":..,"medios":..,"finos":..}, "qwe": 12.3, ...}
      - list de dicts: [{"arena": {...}}, {"qwe": {...}}, ...]  (se respeta el orden)
      - dict con listas/tuplas: {"arena": [g,m,f], ...}
      - dict con número: {"arena": 12.0, ...}  (se toma como total directo)
    Devuelve lista de pesos normalizados (suman 1.0) en el mismo orden de entrada.
    """
    def _total(v):
        if v is None:
            return 0.0
        # dict con zonas
        if isinstance(v, dict):
            g = float(v.get("gruesos", 0) or 0)
            m = float(v.get("medios", 0)  or 0)
            f = float(v.get("finos", 0)   or 0)
            return g + m + f
        # lista/tupla/ndarray → suma
        if isinstance(v, (list, tuple)):
            try:
                return float(sum((x or 0) for x in v))
            except Exception:
                return 0.0
        # número suelto → usar tal cual
        try:
            return float(v)
        except Exception:
            return 0.0

    materiales = []
    totales = []

    if isinstance(pesos_por_zona_dicts, list):
        # lista de dicts: [{"arena": {...}}, {"qwe": {...}}]
        for d in pesos_por_zona_dicts:
            if isinstance(d, dict):
                for k, v in d.items():  # respeta el orden en la lista
                    materiales.append(k)
                    totales.append(_total(v))
            else:
                # item inesperado; ignoro sin romper
                continue
    elif isinstance(pesos_por_zona_dicts, dict):
        # dict plano: respeta el orden de inserción
        for k, v in pesos_por_zona_dicts.items():
            materiales.append(k)
            totales.append(_total(v))
    else:
        # caso extremo: si te pasaron una lista de números alineada a curvas
        try:
            nums = [float(x) for x in (pesos_por_zona_dicts or [])]
            s = sum(nums)
            if s <= 0:
                n = max(1, len(nums))
                return [1.0 / n] * n
            return [x / s for x in nums]
        except Exception:
            return [1.0]  # fallback mínimo

    total = sum(totales)
    if total <= 0:
        n = max(1, len(totales))
        return [1.0 / n] * n
    return [t / total for t in totales]







 

   
















































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
    
    
    
    # Convertir los tamices a etiquetas string
    etiquetas_x = [str(t) for t in tamices]
    x = list(range(len(tamices)))  # Posiciones para eje X lineal
    fig, ax = plt.subplots()
   # Curvas
    ax.plot(x, promedio_reales, marker='o', label='Media effettiva')
    ax.plot(x, promedio_fuller, marker='x', label='Media di Fuller')
    


  # Anotar valores individuales
    for xi, y in zip(x, promedio_reales):
        ax.text(xi, y + 2, f"{y:.1f}%", ha='center', fontsize=8, color='blue')

    for xi, y in zip(x, promedio_fuller):
        ax.text(xi, y - 4, f"{y:.1f}%", ha='center', fontsize=8, color='orange')
        
    # Mostrar diferencia en % entre curvas, coloreado por zona
    zonas = []
    diferencias_grafico  = []
  # Diferencias + zona como texto
    for xi, tamiz, real, ideal in zip(x, tamices, promedio_reales, promedio_fuller):
        diferencia = real - ideal
        etiqueta = f"{diferencia:+.1f}%"

        if tamiz > 4.75:
            zona = "gruesos"
            color = "darkred"
        elif tamiz > 0.6:
            zona = "medios"
            color = "darkorange"
        else:
            zona = "finos"
            color = "green"

        zonas.append(zona)
          # Diferencia entre curvas
        ax.text(xi, (real + ideal) / 2, etiqueta, fontsize=8, color=color, ha='left')
   
  
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas_x)
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
    resumen = {}

    for zona, valores in zonas.items():
        if not valores:
            ajustes.append(f"{zona.capitalize()}: sin datos.")
            resumen[zona] = 0
            continue

        promedio = np.mean(valores)
        resumen[zona] = promedio

        if promedio > 0:
            ajustes.append(f"Reducir material {zona} (exceso de {promedio:.1f}%)")
        elif promedio < 0:
            ajustes.append(f"Aumentar material {zona} (déficit de {abs(promedio):.1f}%)")
        else:
            ajustes.append(f"Material {zona} equilibrado (±0%)")

    # Diagnóstico general automático
    comentario = "Conclusión: "
    partes = []

    if resumen["gruesos"] > 5:
        partes.append("demasiadas partículas gruesas")
    elif resumen["gruesos"] < -5:
        partes.append("faltan partículas gruesas")

    if resumen["medios"] > 5:
        partes.append("demasiadas partículas medias")
    elif resumen["medios"] < -5:
        partes.append("faltan partículas medias")

    if resumen["finos"] > 3:
        partes.append("exceso de finos")
    elif resumen["finos"] < -3:
        partes.append("déficit de finos")

    if partes:
        comentario += ", ".join(partes).capitalize() + ". Esto podría afectar la trabajabilidad y cohesión de la mezcla."
    else:
        comentario += "la mezcla está bien balanceada respecto a la curva ideal."

    return ajustes + [comentario]







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








