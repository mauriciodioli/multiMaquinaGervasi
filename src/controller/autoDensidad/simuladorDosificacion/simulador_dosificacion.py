from flask import Blueprint, request, render_template, send_file, jsonify,redirect
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
from src.utils.auth import current_user

from src.utils.get_textos_menu  import get_textos_menu




simulador_dosificacion = Blueprint('simulador_dosificacion', __name__)




@simulador_dosificacion.route('/pantalla_simulador_densidad/')
def pantalla_simulador_densidad():
    nombres_productos = []
    cookie = request.cookies.get("nombres_productos")
    
    if cookie:
        try:
            decoded = urllib.parse.unquote(cookie)
            nombres_productos = json.loads(decoded)
        except Exception as e:
            print("❌ Error al leer cookie:", e)

    # Asegurate de obtener siempre el usuario
    usuario = current_user()
    if not usuario:
        return redirect("/index.html")

    lang = request.cookies.get("lang", "es")
    t_menu = get_textos_menu(lang)

    return render_template(
        'autoDensidad/simuladorDosificacion.html',
        productos=nombres_productos,
        usuario=usuario,
        t_menu=t_menu
    )



@simulador_dosificacion.route('/simular_mezcla_manual/', methods=['POST'])
def simular_mezcla_manual():
  
    data = request.get_json()
    proporciones = data.get("proporciones", {})
    curvas_usuario = data.get("curvas", {})

    resultado = simular_mezcla_manual_simple(proporciones,curvas_usuario)
    

    if isinstance(resultado, tuple):  # caso de error
        return jsonify(resultado[0]), resultado[1]

    lang = request.cookies.get("lang", "es")
    zonas = resultado.get("zonas", {})
    recomendacion = generar_recomendacion(zonas, lang)
    resultado["recomendacion"] = recomendacion

    return jsonify(resultado)





def generar_recomendacion(zonas, lang="es"):
    traducciones = {
        "es": {
            "equilibrado": "✅ La mezcla está bastante equilibrada. Puedes probarla en planta.",
            "exceso_finos": "⚠️ Hay un exceso de finos. Reduce la arena fina o aumenta la grava gruesa como Piedra Negra.",
            "deficit_finos": "⚠️ Faltan finos. Añade material más fino.",
            "exceso_medios": "⚠️ Exceso de materiales medios. Reduce áridos medios o similares.",
            "deficit_medios": "⚠️ Déficit en materiales medios. Aumenta áridos medios o componentes intermedios.",
            "exceso_gruesos": "⚠️ Exceso de materiales gruesos. Reduce la componente gruesa como Piedra Negra.",
            "deficit_gruesos": "⚠️ Faltan materiales gruesos. Añade Piedra Negra o similares."
        },
        "en": {
            "equilibrado": "✅ The mix is well balanced. You can test it in the plant.",
            "exceso_finos": "⚠️ There is an excess of fines. Reduce fine sand or increase coarse gravel like Black Stone.",
            "deficit_finos": "⚠️ Not enough fines. Add finer material.",
            "exceso_medios": "⚠️ Excess of medium materials. Reduce medium aggregates or similar.",
            "deficit_medios": "⚠️ Deficit in medium materials. Increase medium aggregates or intermediate components.",
            "exceso_gruesos": "⚠️ Excess of coarse materials. Reduce the coarse component like Black Stone.",
            "deficit_gruesos": "⚠️ Not enough coarse materials. Add Black Stone or similar."
        },
        "it": {
            "equilibrado": "✅ Il mix è abbastanza equilibrato. Puoi provarlo in impianto.",
            "exceso_finos": "⚠️ C'è un eccesso di multe. Riduci la grana fine o aumenta quella grossa come la Pietra Nera.",
            "deficit_finos": "⚠️ Mancano le multe. Aggiungi materiale più fine.",
            "exceso_medios": "⚠️ Eccesso di materiali medi. Riduci telai o simili.",
            "deficit_medios": "⚠️ Deficit nei materiali medi. Aumenta telai o componenti intermedi.",
            "exceso_gruesos": "⚠️ Eccesso di materiali grossi. Riduci la componente grossa come la Pietra Nera.",
            "deficit_gruesos": "⚠️ Mancano materiali grossi. Aggiungi Pietra Nera o simili."
        },
        "pt": {
            "equilibrado": "✅ A mistura está bem equilibrada. Você pode testá-la na planta.",
            "exceso_finos": "⚠️ Há um excesso de finos. Reduza a areia fina ou aumente a brita grossa como Pedra Preta.",
            "deficit_finos": "⚠️ Faltam finos. Adicione material mais fino.",
            "exceso_medios": "⚠️ Excesso de materiais médios. Reduza agregados médios ou similares.",
            "deficit_medios": "⚠️ Déficit em materiais médios. Aumente agregados médios ou componentes intermediários.",
            "exceso_gruesos": "⚠️ Excesso de materiais grossos. Reduza o componente grosso como Pedra Preta.",
            "deficit_gruesos": "⚠️ Faltam materiais grossos. Adicione Pedra Preta ou similares."
        },
        "pl": {
            "equilibrado": "✅ Mieszanka jest dobrze wyważona. Możesz ją przetestować w instalacji.",
            "exceso_finos": "⚠️ Nadmiar materiałów drobnych. Zmniejsz piasek drobny lub zwiększ żwir grubego taki jak Czarny Kamień.",
            "deficit_finos": "⚠️ Brakuje materiałów drobnych. Dodaj materiał bardziej drobny.",
            "exceso_medios": "⚠️ Nadmiar materiałów średnich. Zmniejsz kruszywa średnie lub podobne.",
            "deficit_medios": "⚠️ Niedobór materiałów średnich. Zwiększ kruszywa średnie lub komponenty pośrednie.",
            "exceso_gruesos": "⚠️ Nadmiar materiałów grubych. Zmniejsz komponent gruby taki jak Czarny Kamień.",
            "deficit_gruesos": "⚠️ Brakuje materiałów grubych. Dodaj Czarny Kamień lub podobne."
        }
    }

    # Obtén el diccionario de idioma, con fallback a español
    msgs = traducciones.get(lang, traducciones["es"])
    
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
        return msgs["equilibrado"]

    if zona == "finos":
        if valor > 0:
            return msgs["exceso_finos"]
        else:
            return msgs["deficit_finos"]
    elif zona == "medios":
        if valor > 0:
            return msgs["exceso_medios"]
        else:
            return msgs["deficit_medios"]
    elif zona == "gruesos":
        if valor > 0:
            return msgs["exceso_gruesos"]
        else:
            return msgs["deficit_gruesos"]


