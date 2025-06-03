from flask import Blueprint, request, render_template, send_file, jsonify
import urllib.parse
import json
from controller.autoDensidad.calcularMezclaOptima import calcular_mezcla_optima
from controller.autoDensidad.calcularMezclaOptima import mostrar_datos_crudos_entrada
from controller.autoDensidad.calcularMezclaOptima import encontrar_n_optimo
from controller.autoDensidad.optimizar_fuller import generar_informe_ajuste
from controller.autoDensidad.calcularMezclaOptima import calcular_curva_fuller
from controller.autoDensidad.densidadFuller import calcular_curva_resultante
from controller.autoDensidad.densidadFuller import evaluar_mezcla_promedio
from controller.autoDensidad.analisis_densidad import simular_mezcla_manual_simple




simulador_dosificacion = Blueprint('simulador_dosificacion', __name__)




@simulador_dosificacion.route('/pantalla_simulador_densidad/')
def pantalla_simulador_densidad():
    nombres_productos = []
    cookie = request.cookies.get("nombres_productos")
    if cookie:
        try:
            decoded = urllib.parse.unquote(cookie)  # ← decodifica %5B%22...%22%5D
            nombres_productos = json.loads(decoded)  # ← convierte a lista Python
        except Exception as e:
            print("❌ Error al leer cookie:", e)
    return render_template('autoDensidad/simuladorDosificacion.html', productos=nombres_productos)





@simulador_dosificacion.route('/simular_mezcla_manual/', methods=['POST'])
def simular_mezcla_manual():
  
    data = request.get_json()
    proporciones = data.get("proporciones", {})
    curvas_usuario = data.get("curvas", {})

    resultado = simular_mezcla_manual_simple(proporciones,curvas_usuario)
    

    if isinstance(resultado, tuple):  # caso de error
        return jsonify(resultado[0]), resultado[1]

    zonas = resultado.get("zonas", {})
    recomendacion = generar_recomendacion(zonas)
    resultado["recomendacion"] = recomendacion

    return jsonify(resultado)





def generar_recomendacion(zonas):
    errores = zonas.get("error_por_zona", {})
    gruesos = errores.get("gruesos", 0)
    medios = errores.get("medios", 0)
    finos = errores.get("finos", 0)

    delta = 5  # Tolerancia mínima para sugerencia

    zona_dominante = max(
        [("gruesos", gruesos), ("medios", medios), ("finos", finos)],
        key=lambda x: abs(x[1])
    )

    zona, valor = zona_dominante

    if abs(valor) < delta:
        return "✅ Il mix è abbastanza equilibrato. Puoi provarlo in impianto."

    if zona == "finos":
        if valor > 0:
            return "⚠️ C'è un eccesso di multe. Riduci la grana fine o aumenta quella grossa come la Pietra Nera."
        else:
            return "⚠️ Mancano le multe. Aggiungi materiale più fine."
    elif zona == "medios":
        if valor > 0:
            return "⚠️ Eccesso di materiali medi. Riduci telai o simili."
        else:
            return "⚠️ Deficit nei materiali medi. Aumenta telai o componenti intermedi."
    elif zona == "gruesos":
        if valor > 0:
            return "⚠️ Eccesso di materiali grossi. Riduci la componente grossa come la Pietra Nera."
        else:
            return "⚠️ Mancano materiali grossi. Aggiungi Pietra Nera o simili."


