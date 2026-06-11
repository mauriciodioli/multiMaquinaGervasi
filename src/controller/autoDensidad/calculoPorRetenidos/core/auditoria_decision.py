"""
MÓDULO AUDITORÍA Y DECISIÓN
Evaluación de cumplimiento de banda y generación de tabla virtual dirigida
Fase 1-6 del sistema de optimización granulométrica
"""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from .nucleo_tabla_virtual import generar_tabla_virtual, validar_tabla_virtual


TOLERANCIA_BANDA = 1e-6

TIPO_CURVA_RETENIDO_INDIVIDUAL = "retenido_individual"
TIPO_CURVA_RETENIDO_ACUMULADO = "retenido_acumulado"
TIPO_CURVA_PASANTE_ACUMULADO = "pasante_acumulado"


def _debug_etapa_curva(etapa: str, funcion: str, tipo_curva: str, tamices: np.ndarray, curva: np.ndarray) -> None:
    tamices_list = [float(t) for t in np.array(tamices, dtype=float).tolist()] if len(tamices) else []
    curva_list = [float(v) for v in np.array(curva, dtype=float).tolist()] if len(curva) else []
    print("==== ETAPA ====")
    print(f"ETAPA: {etapa}")
    print(f"FUNCION: {funcion}")
    print(f"TIPO: {tipo_curva}")
    print(f"TAMICES: {tamices_list}")
    print(f"CURVA: {curva_list}")
    print(f"LEN TAMICES: {len(tamices_list)}")
    print(f"LEN CURVA: {len(curva_list)}")


def _limpiar_pasantes(pasante: np.ndarray) -> np.ndarray:
    pasante = np.array(pasante, dtype=float)
    pasante = np.clip(pasante, 0.0, 100.0)
    pasante[np.abs(pasante) < TOLERANCIA_BANDA] = 0.0
    pasante[np.abs(pasante - 100.0) < TOLERANCIA_BANDA] = 100.0
    return pasante


def _esta_dentro_banda(pasante: float, banda_min: float, banda_max: float) -> bool:
    return (banda_min - TOLERANCIA_BANDA) <= pasante <= (banda_max + TOLERANCIA_BANDA)


def _pasante_a_retido_individual(pasante: np.ndarray) -> np.ndarray:
    pasante = _limpiar_pasantes(pasante)
    retido_acum = 100.0 - pasante
    retido_ind = np.diff(np.concatenate(([0.0], retido_acum)))
    return np.clip(retido_ind, 0.0, 100.0)


def _retido_individual_a_acumulado(retido_ind: np.ndarray) -> np.ndarray:
    retido_ind = np.clip(np.array(retido_ind, dtype=float), 0.0, 100.0)
    return np.clip(np.cumsum(retido_ind), 0.0, 100.0)


def _describir_sentido_tamices(tamices: np.ndarray) -> str:
    if len(tamices) < 2:
        return "descendente"
    return "descendente" if float(tamices[0]) >= float(tamices[-1]) else "ascendente"


def _validar_monotonicidad(curva: np.ndarray, tipo_curva: str, sentido_tamices: str) -> Dict[str, Any]:
    print("=== DEBUG MONOTONICIDAD ===")
    print(f"TIPO CURVA: {tipo_curva}")
    print(f"SENTIDO TAMICES: {sentido_tamices}")
    print(f"CURVA: {[round(float(v), 6) for v in curva.tolist()]}")

    if tipo_curva == TIPO_CURVA_RETENIDO_INDIVIDUAL:
        return {
            "aplica": False,
            "es_valida": True,
            "violaciones": [],
            "regla": "No aplica monotonicidad sobre retenido individual.",
        }

    violaciones = []
    if tipo_curva == TIPO_CURVA_PASANTE_ACUMULADO:
        debe_descender = sentido_tamices == "descendente"
        for i in range(len(curva) - 1):
            actual = float(curva[i])
            siguiente = float(curva[i + 1])
            print(
                f"Comparando {i}: {actual} -> {siguiente} | "
                f"tamices {i}={i}"
            )
            if debe_descender and siguiente > actual + TOLERANCIA_BANDA:
                violaciones.append((i, actual, siguiente))
            elif not debe_descender and siguiente + TOLERANCIA_BANDA < actual:
                violaciones.append((i, actual, siguiente))

        regla = (
            "Pasante acumulado debe ser no creciente cuando los tamices están ordenados de grueso a fino."
            if debe_descender
            else "Pasante acumulado debe ser no decreciente cuando los tamices están ordenados de fino a grueso."
        )
    else:
        debe_crecer = sentido_tamices == "descendente"
        for i in range(len(curva) - 1):
            actual = float(curva[i])
            siguiente = float(curva[i + 1])
            print(
                f"Comparando {i}: {actual} -> {siguiente} | "
                f"tamices {i}={i}"
            )
            if debe_crecer and siguiente + TOLERANCIA_BANDA < actual:
                violaciones.append((i, actual, siguiente))
            elif not debe_crecer and siguiente > actual + TOLERANCIA_BANDA:
                violaciones.append((i, actual, siguiente))

        regla = (
            "Retenido acumulado debe ser no decreciente cuando los tamices están ordenados de grueso a fino."
            if debe_crecer
            else "Retenido acumulado debe ser no creciente cuando los tamices están ordenados de fino a grueso."
        )

    return {
        "aplica": True,
        "es_valida": len(violaciones) == 0,
        "violaciones": violaciones,
        "regla": regla,
    }


def _reconstruir_curvas_material(material: Dict[str, Any], n_tamices: int) -> Optional[Dict[str, Any]]:
    nombre = material.get("nombre", "Material sin nombre")
    retido_ind = material.get("retido_ind_pct")
    if isinstance(retido_ind, list) and len(retido_ind) >= n_tamices:
        retido_ind_arr = np.clip(np.array(retido_ind[:n_tamices], dtype=float), 0.0, 100.0)
        retido_acum_arr = _retido_individual_a_acumulado(retido_ind_arr)
        pasante_arr = _limpiar_pasantes(100.0 - retido_acum_arr)
        return {
            "nombre": nombre,
            "tipo_curva_origen": TIPO_CURVA_RETENIDO_INDIVIDUAL,
            "retido_individual": retido_ind_arr,
            "retenido_acumulado": retido_acum_arr,
            "pasante_acumulado": pasante_arr,
        }

    pasantes = material.get("pasantes")
    if isinstance(pasantes, list) and len(pasantes) == n_tamices:
        pasante_arr = _limpiar_pasantes(np.array(pasantes, dtype=float))
        retido_ind_arr = _pasante_a_retido_individual(pasante_arr)
        retido_acum_arr = _retido_individual_a_acumulado(retido_ind_arr)
        return {
            "nombre": nombre,
            "tipo_curva_origen": TIPO_CURVA_PASANTE_ACUMULADO,
            "retido_individual": retido_ind_arr,
            "retenido_acumulado": retido_acum_arr,
            "pasante_acumulado": pasante_arr,
        }

    return None


def _material_a_pasante(material: Dict[str, Any], n_tamices: int) -> Optional[np.ndarray]:
    pasantes = material.get("pasantes")
    if isinstance(pasantes, list) and len(pasantes) == n_tamices:
        return _limpiar_pasantes(np.array(pasantes, dtype=float))

    retido_ind = material.get("retido_ind_pct")
    if isinstance(retido_ind, list) and len(retido_ind) >= n_tamices:
        retido = np.clip(np.array(retido_ind[:n_tamices], dtype=float), 0.0, 100.0)
        retido_acum = np.cumsum(retido)
        return _limpiar_pasantes(100.0 - retido_acum)

    return None


def _obtener_proporcion_material(material: Dict[str, Any], proporciones_optimizadas: Optional[Dict[str, float]]) -> Optional[float]:
    nombre = material.get("nombre")
    if proporciones_optimizadas and nombre in proporciones_optimizadas:
        return float(proporciones_optimizadas[nombre])

    if material.get("proporcion_pct") is not None:
        return float(material.get("proporcion_pct"))

    if material.get("peso") is not None:
        peso = float(material.get("peso"))
        return peso * 100.0 if peso <= 1.0 else peso

    return None


def _tamiz_label(tamiz: float) -> str:
    return f"{float(tamiz):.3f}".rstrip("0").rstrip(".") + " mm"


def _agregar_problema(contenedor: List[Dict[str, str]], severidad: str, titulo: str, detalle: str) -> None:
    contenedor.append({
        "severidad": severidad,
        "titulo": titulo,
        "detalle": detalle,
    })


def _analizar_monotonicidad_y_saltos(
    curva: np.ndarray,
    tamices: np.ndarray,
    tipo_curva: str = TIPO_CURVA_PASANTE_ACUMULADO,
    detectar_serrucho: bool = False,
) -> Dict[str, Any]:
    problemas = []
    saltos = []
    violaciones = []
    sentido_tamices = _describir_sentido_tamices(tamices)
    print(f"TAMICES: {[round(float(t), 6) for t in tamices.tolist()]}")
    monotonia = _validar_monotonicidad(curva, tipo_curva, sentido_tamices)

    for i in range(len(curva) - 1):
        actual = float(curva[i])
        siguiente = float(curva[i + 1])
        print(
            f"Comparando {tamices[i]}->{tamices[i + 1]} | "
            f"{actual} -> {siguiente}"
        )
        salto = actual - siguiente
        salto_abs = abs(salto)

        saltos.append({
            "tamiz_superior": float(tamices[i]),
            "tamiz_inferior": float(tamices[i + 1]),
            "salto": round(salto, 2),
            "salto_abs": round(salto_abs, 2),
        })

        if monotonia["aplica"]:
            coincide_violacion = any(v[0] == i for v in monotonia["violaciones"])
        else:
            coincide_violacion = False

        if coincide_violacion:
            magnitud = abs(actual - siguiente)
            if magnitud > 5.0:
                severidad = "ERROR CRITICO"
            elif magnitud > 2.0:
                severidad = "ERROR MODERADO"
            else:
                severidad = "ADVERTENCIA"

            detalle = (
                f"La curva {tipo_curva} rompe monotonicidad entre {_tamiz_label(tamices[i])} y "
                f"{_tamiz_label(tamices[i + 1])} con cambio de {magnitud:.2f}%. "
                f"{monotonia['regla']} Esto sugiere "
                "datos inconsistentes, mezcla mal reconstruida o inversión de tamices."
            )
            _agregar_problema(problemas, severidad, "Monotonicidad violada", detalle)
            violaciones.append(detalle)

        if salto_abs > 20.0:
            detalle = (
                f"Salto de {salto_abs:.2f}% entre {_tamiz_label(tamices[i])} y {_tamiz_label(tamices[i + 1])}. "
                "Es brusco para una curva estable y puede indicar mezcla artificial, material mal representado "
                "o corrección demasiado agresiva del algoritmo."
            )
            _agregar_problema(problemas, "ERROR MODERADO", "Salto brusco entre tamices", detalle)

    variaciones_salto = []
    if detectar_serrucho:
        for i in range(len(saltos) - 1):
            delta = abs(saltos[i]["salto_abs"] - saltos[i + 1]["salto_abs"])
            if delta > 18.0 and max(saltos[i]["salto_abs"], saltos[i + 1]["salto_abs"]) > 12.0:
                variaciones_salto.append(
                    f"Cambio abrupto de patrón entre {_tamiz_label(saltos[i]['tamiz_superior'])} y {_tamiz_label(saltos[i + 1]['tamiz_inferior'])}: Δsaltos={delta:.2f}%."
                )

    if detectar_serrucho and len(variaciones_salto) >= 2:
        _agregar_problema(
            problemas,
            "ADVERTENCIA",
            "Comportamiento serrucho",
            "Se observan oscilaciones artificiales repetidas en una curva acumulada. Puede ser una reconstrucción imposible o una corrección virtual demasiado agresiva.",
        )

    return {
        "problemas": problemas,
        "saltos": saltos,
        "violaciones": violaciones,
        "serrucho": variaciones_salto,
        "tipo_curva": tipo_curva,
        "sentido_tamices": sentido_tamices,
        "regla_monotonicidad": monotonia["regla"],
        "es_monotona": len(violaciones) == 0,
    }


def _analizar_materiales(
    materiales: Optional[List[Dict[str, Any]]],
    tamices: np.ndarray,
    proporciones_optimizadas: Optional[Dict[str, float]],
) -> Dict[str, Any]:
    if not materiales:
        return {
            "resumen": "No se recibieron materiales individuales; no es posible validar representatividad física por agregado.",
            "problemas": [],
            "materiales_unicos": [],
            "materiales_ignorados": [],
            "dominancia": [],
            "materiales_originales": [],
            "trazabilidad": [],
        }

    nombres = []
    materiales_validos = []
    curvas_material = []
    problemas = []
    materiales_unicos = []
    materiales_ignorados = []
    dominancia = []
    materiales_originales = []

    for material in materiales:
        curvas = _reconstruir_curvas_material(material, len(tamices))
        if curvas is None:
            continue
        materiales_validos.append(material)
        curvas_material.append(curvas)
        nombres.append(curvas["nombre"])

    for idx, nombre in enumerate(nombres):
        ret_i = curvas_material[idx]["retido_individual"]
        proporcion = _obtener_proporcion_material(materiales_validos[idx], proporciones_optimizadas)
        zona_idx = int(np.argmax(ret_i)) if len(ret_i) else 0

        if zona_idx < max(1, len(tamices) // 3):
            zona = "gruesa"
        elif zona_idx < max(2, 2 * len(tamices) // 3):
            zona = "media"
        else:
            zona = "fina"

        dominancia.append({
            "material": nombre,
            "zona": zona,
            "tamiz_dominante": _tamiz_label(tamices[zona_idx]),
            "aporte_maximo_retido": round(float(ret_i[zona_idx]), 2),
            "proporcion_pct": None if proporcion is None else round(proporcion, 2),
        })

        materiales_originales.append({
            "material": nombre,
            "proporcion_pct": None if proporcion is None else round(proporcion, 2),
            "zona": zona,
            "tamiz_dominante": _tamiz_label(tamices[zona_idx]),
            "aporte_maximo_retido": round(float(ret_i[zona_idx]), 2),
            "tiene_firma_unica": False,
        })

        unique_idx = []
        if len(curvas_material) > 1:
            for j, valor in enumerate(ret_i):
                otros = [float(curvas_material[k]["retido_individual"][j]) for k in range(len(curvas_material)) if k != idx]
                otros_max = max(otros) if otros else 0.0
                if valor >= 5.0 and (otros_max <= 1.0 or valor >= otros_max + 12.0):
                    unique_idx.append(j)

        if unique_idx:
            tamices_unicos = [_tamiz_label(tamices[j]) for j in unique_idx]
            materiales_unicos.append({
                "material": nombre,
                "tamices": tamices_unicos,
                "proporcion_pct": None if proporcion is None else round(proporcion, 2),
            })

            for material_original in materiales_originales:
                if material_original["material"] == nombre:
                    material_original["tiene_firma_unica"] = True
                    material_original["tamices_unicos"] = tamices_unicos
                    break

            if proporcion is not None and proporcion <= 0.5:
                detalle = (
                    f"{nombre} tiene firma granulométrica propia en {', '.join(tamices_unicos)} y quedó en {proporcion:.2f}%. "
                    "Industrialmente es sospechoso: esa fracción debería dejar huella en la curva final y su desaparición puede ocultar un sobreajuste matemático."
                )
                _agregar_problema(problemas, "ERROR CRITICO", "Material único eliminado", detalle)
                materiales_ignorados.append({"material": nombre, "detalle": detalle})
            elif proporcion is not None and proporcion < 1.0:
                detalle = (
                    f"{nombre} conserva zonas únicas ({', '.join(tamices_unicos)}), pero quedó por debajo de 1%. "
                    "La participación es demasiado baja para un material que aporta granulometría propia; revisar si la optimización lo está anulando artificialmente."
                )
                _agregar_problema(problemas, "ERROR MODERADO", "Representación marginal de material único", detalle)
            elif proporcion is not None and proporcion <= 5.0:
                detalle = (
                    f"{nombre} aporta una fracción específica en {', '.join(tamices_unicos)} y quedó en {proporcion:.2f}%. "
                    "Es aceptable solo si esa huella aún se observa en la curva auditada y la dosificación es estable en planta."
                )
                _agregar_problema(problemas, "ADVERTENCIA", "Material único con aporte pequeño", detalle)

    resumen = (
        f"Se evaluaron {len(nombres)} materiales. "
        f"{len(materiales_unicos)} presentan contenido diferencial por tamiz y {len(materiales_ignorados)} quedaron industrialmente subrepresentados."
    )

    return {
        "resumen": resumen,
        "problemas": problemas,
        "materiales_unicos": materiales_unicos,
        "materiales_ignorados": materiales_ignorados,
        "dominancia": dominancia,
        "materiales_originales": materiales_originales,
        "trazabilidad": [
            {
                "material": curvas["nombre"],
                "tipo_curva_origen": curvas["tipo_curva_origen"],
                "tipo_curva_derivada_1": TIPO_CURVA_RETENIDO_ACUMULADO,
                "tipo_curva_derivada_2": TIPO_CURVA_PASANTE_ACUMULADO,
            }
            for curvas in curvas_material
        ],
    }


def _validar_tabla_virtual_industrial(
    fase5: Dict[str, Any],
    reporte_validacion: Dict[str, Any],
    analisis_virtual: Dict[str, Any],
) -> Dict[str, Any]:
    problemas = []

    if not fase5["generada"]:
        resumen = "No se generó tabla virtual porque la mezcla auditada ya quedó en condición suficiente o el flujo no la necesitó."
        return {
            "resumen": resumen,
            "problemas": problemas,
            "estado": "NO APLICA",
        }

    if fase5["cumplimiento_pct"] <  fase5.get("cumplimiento_real_pct", fase5["cumplimiento_pct"]):
        _agregar_problema(
            problemas,
            "ERROR CRITICO",
            "Tabla virtual empeora cumplimiento",
            "La tabla virtual baja el porcentaje de tamices dentro de banda. Debe invalidarse porque corrige en dirección opuesta a la necesidad real.",
        )

    if fase5["mejora_error"] < 0:
        _agregar_problema(
            problemas,
            "ERROR CRITICO",
            "Tabla virtual aumenta error",
            "La tabla virtual incrementa el error residual. Matemáticamente y operativamente no agrega valor.",
        )

    if not fase5["valida"]:
        detalle = ", ".join(reporte_validacion.get("fallos", [])) or "Validación física fallida"
        _agregar_problema(problemas, "ERROR CRITICO", "Tabla virtual inválida", detalle)

    for problema in analisis_virtual.get("problemas", []):
        if problema["severidad"] in {"ERROR CRITICO", "ERROR MODERADO"}:
            _agregar_problema(
                problemas,
                problema["severidad"],
                f"Curva virtual: {problema['titulo']}",
                problema["detalle"],
            )

    resumen = "Tabla virtual aceptable para análisis" if not problemas else "La tabla virtual requiere reservas industriales antes de usarse en planta"
    estado = "VALIDA" if not problemas else "OBSERVADA"

    return {
        "resumen": resumen,
        "problemas": problemas,
        "estado": estado,
    }


def _tabla_virtual_es_aplicable_industrialmente(
    fase5: Dict[str, Any],
    validacion_tv: Dict[str, Any],
    analisis_materiales: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    motivos = []

    if not fase5.get("generada"):
        motivos.append("No se generó tabla virtual necesaria para análisis.")
    if not fase5.get("valida"):
        motivos.append("La tabla virtual no superó la validación física base.")
    if fase5.get("cumplimiento_pct", 0) < fase5.get("cumplimiento_real_pct", 0):
        motivos.append("La tabla virtual reduce el cumplimiento frente a la mezcla real.")
    if fase5.get("mejora_error", 0) <= 0:
        motivos.append("La tabla virtual no reduce el error residual real.")
    if fase5.get("mejora_cumplimiento", 0) <= 0:
        motivos.append("La tabla virtual no agrega mejora de tamices dentro de banda.")
    if validacion_tv.get("estado") != "VALIDA":
        motivos.append("La tabla virtual quedó observada industrialmente.")
    if analisis_materiales.get("materiales_ignorados"):
        motivos.append("Su uso ocultaría materiales reales con firma diferencial.")

    return len(motivos) == 0, motivos


def _construir_auditoria_industrial(
    pasante_real: np.ndarray,
    pasante_virtual: np.ndarray,
    banda_min: np.ndarray,
    banda_max: np.ndarray,
    tamices: np.ndarray,
    criterios: Dict[str, Any],
    fase1: Dict[str, Any],
    fase5: Dict[str, Any],
    reporte_validacion: Dict[str, Any],
    materiales: Optional[List[Dict[str, Any]]] = None,
    proporciones_optimizadas: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    analisis_real = _analizar_monotonicidad_y_saltos(
        pasante_real,
        tamices,
        tipo_curva=TIPO_CURVA_PASANTE_ACUMULADO,
        detectar_serrucho=False,
    )
    analisis_virtual = _analizar_monotonicidad_y_saltos(
        pasante_virtual,
        tamices,
        tipo_curva=TIPO_CURVA_PASANTE_ACUMULADO,
        detectar_serrucho=bool(fase5["generada"]),
    )
    analisis_materiales = _analizar_materiales(materiales, tamices, proporciones_optimizadas)
    validacion_tv = _validar_tabla_virtual_industrial(fase5, reporte_validacion, analisis_virtual)
    tabla_virtual_aplicable, motivos_bloqueo_tv = _tabla_virtual_es_aplicable_industrialmente(
        fase5,
        validacion_tv,
        analisis_materiales,
    )

    problemas_matematicos = []
    problemas_fisicos = list(analisis_real["problemas"])
    problemas_criticos = []
    problemas_industriales = list(analisis_materiales["problemas"])
    riesgos_operativos = []
    recomendaciones = []

    tamices_fuera = []
    for i, (pasante, minimo, maximo) in enumerate(zip(pasante_real, banda_min, banda_max)):
        if _esta_dentro_banda(float(pasante), float(minimo), float(maximo)):
            continue
        if pasante < minimo:
            detalle = (
                f"{_tamiz_label(tamices[i])}: pasante {float(pasante):.2f}% por debajo del mínimo {float(minimo):.2f}%. "
                "Hay déficit de material más fino que el requerido para ese corte."
            )
        else:
            detalle = (
                f"{_tamiz_label(tamices[i])}: pasante {float(pasante):.2f}% por encima del máximo {float(maximo):.2f}%. "
                "Hay exceso de finos o falta de gruesos en ese rango."
            )
        tamices_fuera.append(detalle)
        _agregar_problema(problemas_matematicos, "ERROR MODERADO", "Tamiz fuera de banda", detalle)

    if fase1["error_total"] == 0 and not criterios["cumple_banda"]:
        _agregar_problema(
            problemas_matematicos,
            "ERROR CRITICO",
            "Inconsistencia de error residual",
            "El sistema reporta error total nulo pese a incumplimiento de banda. Revisar construcción de bandas o pasantes auditados.",
        )

    if criterios["cumple_banda"] and not criterios["es_buena_calidad"]:
        _agregar_problema(
            riesgos_operativos,
            "ADVERTENCIA",
            "Cumple pero con centrado inestable",
            "La mezcla entra en banda, pero queda lejos del centro. Puede volverse no conforme con pequeñas variaciones de humedad, carga o desgaste de mallas.",
        )

    if analisis_materiales["materiales_ignorados"]:
        _agregar_problema(
            riesgos_operativos,
            "ERROR MODERADO",
            "Riesgo de pérdida de trazabilidad de material",
            "Hay materiales con aporte diferencial que la receta deja casi anulados. En planta eso suele terminar en cambios erráticos de curva y dificultad para explicar el resultado al laboratorio.",
        )

    if fase5["generada"] and fase5["mejora_error"] <= 0:
        _agregar_problema(
            problemas_industriales,
            "ERROR CRITICO",
            "Optimización sin beneficio real",
            "La corrección virtual no reduce el error residual. Es una optimización irreal porque agrega complejidad sin mejorar la producibilidad.",
        )

    if fase5["generada"] and not tabla_virtual_aplicable:
        _agregar_problema(
            problemas_industriales,
            "ERROR CRITICO",
            "Tabla virtual no operable",
            "La tabla virtual queda restringida a simulación auxiliar: " + " ".join(motivos_bloqueo_tv),
        )

    problemas_industriales.extend(validacion_tv["problemas"])

    for coleccion in (problemas_fisicos, problemas_matematicos, problemas_industriales):
        for problema in coleccion:
            if problema["severidad"] == "ERROR CRITICO":
                problemas_criticos.append(problema)

    if not criterios["cumple_banda"]:
        recomendaciones.append("No liberar mezcla tal como está. Corregir primero la zona fuera de banda con ajuste físico verificable en laboratorio.")
    else:
        recomendaciones.append("Mantener la receta dentro de una ventana operativa estrecha y repetir control si cambia humedad, zaranda o alimentación.")

    if analisis_materiales["materiales_unicos"]:
        recomendaciones.append("No eliminar materiales con firma propia sin una justificación física explícita. Si se baja su porcentaje, verificar que su tamiz característico siga visible en la curva final.")

    for material in analisis_materiales.get("materiales_originales", []):
        if material.get("proporcion_pct") is None:
            continue
        recomendaciones.append(
            f"{material['material']}: preservar su firma {material['zona']} alrededor de {material['tamiz_dominante']} ({material['aporte_maximo_retido']:.2f}% de aporte máximo) con dosificación real {material['proporcion_pct']:.2f}%."
        )

    if any(salto["salto_abs"] > 20.0 for salto in analisis_real["saltos"]):
        recomendaciones.append("Revisar separación por mallas y consistencia de análisis de laboratorio en los tamices donde aparecen saltos mayores a 20%.")

    if fase5["generada"] and tabla_virtual_aplicable:
        recomendaciones.append("La tabla virtual puede conservarse solo como simulación auxiliar validada; no debe convertirse en receta automática de producción.")
    elif fase5["generada"]:
        recomendaciones.append("La mezcla actual no puede corregirse automáticamente sin perder coherencia física o representatividad industrial.")

    if problemas_criticos:
        decision_estado = "NO LIBERAR"
        if any("Material único eliminado" == p["titulo"] for p in problemas_criticos) or any("Tabla virtual" in p["titulo"] for p in problemas_criticos):
            decision_estado = "REQUIERE REFORMULACION"
    elif not criterios["cumple_banda"]:
        decision_estado = "REVISAR LABORATORIO"
    elif riesgos_operativos:
        decision_estado = "REVISAR LABORATORIO"
    else:
        decision_estado = "APTO PRODUCCION"

    diagnostico_partes = [
        f"Cumplimiento actual: {fase1['cumpl_count']}/{fase1['n_tamices']} tamices ({fase1['cumplimiento_pct']}%).",
        f"Error residual: {fase1['error_total']:.2f}%.",
        "Curva físicamente coherente." if analisis_real["es_monotona"] else "Curva con inconsistencias físicas de monotonicidad.",
        analisis_materiales["resumen"],
    ]

    if tamices_fuera:
        diagnostico_partes.append(f"Tamices fuera de banda: {len(tamices_fuera)}.")

    if decision_estado == "APTO PRODUCCION":
        justificacion = "Se recomienda liberar a producción porque cumple banda y no aparecen objeciones físicas críticas."
    elif fase5.get("generada") and not tabla_virtual_aplicable:
        justificacion = "La mezcla actual no puede corregirse automáticamente sin perder coherencia física o representatividad industrial."
    else:
        justificacion = "La mezcla necesita intervención antes de producción por riesgo físico, operativo o industrial."

    return {
        "diagnostico_general": {
            "texto": " ".join(diagnostico_partes),
            "cumple_banda": bool(criterios["cumple_banda"]),
            "es_buena_calidad": bool(criterios["es_buena_calidad"]),
        },
        "problemas_criticos": problemas_criticos,
        "problemas_fisicos": problemas_fisicos,
        "problemas_matematicos": problemas_matematicos,
        "problemas_industriales": problemas_industriales,
        "validacion_materiales": {
            "resumen": analisis_materiales["resumen"],
            "materiales_unicos": analisis_materiales["materiales_unicos"],
            "dominancia": analisis_materiales["dominancia"],
            "materiales_originales": analisis_materiales["materiales_originales"],
            "problemas": analisis_materiales["problemas"],
            "trazabilidad": analisis_materiales["trazabilidad"],
        },
        "validacion_tabla_virtual": validacion_tv,
        "control_operacional": {
            "tabla_virtual_habilitada": tabla_virtual_aplicable,
            "motivos_bloqueo_tabla_virtual": motivos_bloqueo_tv,
            "priorizar_materiales_originales": True,
        },
        "riesgos_operativos": riesgos_operativos,
        "recomendaciones_reales_planta": recomendaciones,
        "decision_final": {
            "estado": decision_estado,
            "justificacion": justificacion,
            "riesgos_calidad": [problema["detalle"] for problema in problemas_criticos[:3]] or tamices_fuera[:3],
            "riesgos_planta": [riesgo["detalle"] for riesgo in riesgos_operativos[:3]],
        },
    }


def evaluar_criterios_decision(
    pasante: np.ndarray,
    banda_min: np.ndarray,
    banda_max: np.ndarray,
    tamices: np.ndarray,
    umbral_cumplimiento: float = 95.0,
    umbral_calidad: float = 5.5
) -> Dict:
    """
    Evalúa los dos criterios de decisión del sistema:
    1. CUMPLIMIENTO DE BANDA (obligatorio)
    2. DESVIACIÓN DEL CENTRO (calidad opcional)
    
    Args:
        pasante: Array de porcentajes pasante
        banda_min: Array de mínimo por tamiz
        banda_max: Array de máximo por tamiz
        tamices: Array de tamices
        umbral_cumplimiento: Mínimo requerido para cumplir (default 95%)
        umbral_calidad: Máximo de desviación % para buena calidad (default ±5.5%)
    
    Returns:
        Dict con evaluación de criterios y recomendación de decisión
    """
    
    # Cálculo 1: Cumplimiento de banda
    pasante = _limpiar_pasantes(pasante)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)

    cumpl_inicial = sum([1 for p, min_b, max_b in zip(pasante, banda_min, banda_max) if _esta_dentro_banda(p, min_b, max_b)])
    cumplimiento_banda_pct = (cumpl_inicial / len(tamices)) * 100
    
    # Cálculo 2: Desviación del centro
    centro_banda = (banda_min + banda_max) / 2
    desviaciones = [abs(p - c) for p, c in zip(pasante, centro_banda)]
    desviacion_media_centro = np.mean(desviaciones)
    
    # Evaluación de criterios
    cumple_banda = bool(cumplimiento_banda_pct >= umbral_cumplimiento)
    es_buena_calidad = bool(desviacion_media_centro <= umbral_calidad)
    
    # Decisión
    if cumple_banda:
        decision = "NO GENERAR tabla virtual"
        razon = "La solución actual ya satisface la especificación."
        generar_tv = False
    else:
        decision = "GENERAR tabla virtual"
        razon = "La solución actual NO satisface la especificación."
        generar_tv = True
    
    return {
        "cumplimiento_banda_pct": round(cumplimiento_banda_pct, 1),
        "cumpl_inicial": cumpl_inicial,
        "n_tamices": len(tamices),
        "umbral_cumplimiento": umbral_cumplimiento,
        "cumple_banda": cumple_banda,
        
        "desviacion_media_centro": round(desviacion_media_centro, 2),
        "umbral_calidad": umbral_calidad,
        "es_buena_calidad": es_buena_calidad,
        
        "decision": decision,
        "razon": razon,
        "generar_tabla_virtual": generar_tv,
    }


def generar_auditoria_completa(
    pasante_real: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[float],
    materiales: Optional[List[Dict[str, Any]]] = None,
    proporciones_optimizadas: Optional[Dict[str, float]] = None,
) -> Dict:
    """
    Genera auditoría completa con decisión y generación de tabla virtual
    
    Args:
        pasante_real: Pasante real (%)
        banda_min: Mínimo de especificación por tamiz
        banda_max: Máximo de especificación por tamiz
        tamices: Tamices en ordem
    
    Returns:
        Dict con resultado completo de auditoría
    """
    
    # Convertir a numpy
    pasante_real = _limpiar_pasantes(np.array(pasante_real))
    banda_min = np.array(banda_min)
    banda_max = np.array(banda_max)
    tamices = np.array(tamices)

    _debug_etapa_curva(
        etapa='generar_auditoria_completa.entrada',
        funcion='generar_auditoria_completa',
        tipo_curva=TIPO_CURVA_PASANTE_ACUMULADO,
        tamices=tamices,
        curva=pasante_real,
    )
    
    # ===== FASE 1: EVALUACIÓN INICIAL =====
    cumpl_inicial = sum([1 for p, min_b, max_b in zip(pasante_real, banda_min, banda_max) if _esta_dentro_banda(p, min_b, max_b)])
    cumpl_inicial_pct = (cumpl_inicial / len(tamices)) * 100
    
    # Error total
    error_real = sum([
        max(0, banda_min[i] - pasante_real[i], pasante_real[i] - banda_max[i])
        if not _esta_dentro_banda(pasante_real[i], banda_min[i], banda_max[i]) else 0
        for i in range(len(tamices))
    ])
    
    # ===== FASE 2-4: EVALUACIÓN DE CRITERIOS Y DECISIÓN =====
    criterios = evaluar_criterios_decision(
        pasante_real, banda_min, banda_max, tamices
    )
    
    # ===== FASE 5: GENERACIÓN DE TABLA VIRTUAL SI REQUERIDA =====
    pasante_virtual = pasante_real.copy()
    es_valida = True
    reporte_validacion = {'valido': True}
    mejora_cumplimiento = 0
    mejora_error = 0.0
    cumpl_virtual_pct = cumpl_inicial_pct
    error_virtual = error_real
    
    cumpl_virtual = cumpl_inicial

    if criterios['generar_tabla_virtual']:
        try:
            # Generar tabla virtual
            _debug_etapa_curva(
                etapa='generar_auditoria_completa.pre_generar_tabla_virtual.reverse_input',
                funcion='generar_auditoria_completa',
                tipo_curva='pasante_acumulado_fino_a_grueso',
                tamices=tamices[::-1],
                curva=pasante_real[::-1],
            )
            pasante_virtual, debug_info = generar_tabla_virtual(
                pasante_mezcla=pasante_real[::-1].tolist(),
                banda_min=banda_min[::-1].tolist(),
                banda_max=banda_max[::-1].tolist(),
                tamices=[str(x) for x in tamices[::-1]],
                metodo="principal",
                factor_suavizado=0.5,
            )
            _debug_etapa_curva(
                etapa='generar_auditoria_completa.post_generar_tabla_virtual.asc',
                funcion='generar_tabla_virtual',
                tipo_curva='pasante_acumulado_fino_a_grueso',
                tamices=tamices[::-1],
                curva=np.array(pasante_virtual, dtype=float),
            )
            pasante_virtual = _limpiar_pasantes(np.array(pasante_virtual)[::-1])
            _debug_etapa_curva(
                etapa='generar_auditoria_completa.post_reverse_tabla_virtual.desc',
                funcion='generar_auditoria_completa',
                tipo_curva=TIPO_CURVA_PASANTE_ACUMULADO,
                tamices=tamices,
                curva=pasante_virtual,
            )
            
            # Validar
            es_valida, reporte_validacion = validar_tabla_virtual(
                pasante_virtual=pasante_virtual.tolist(),
                pasante_mezcla=pasante_real.tolist(),
                banda_min=banda_min.tolist(),
                banda_max=banda_max.tolist()
            )
            es_valida = bool(es_valida)  # Convertir a bool Python para JSON
            
            # Calcular mejora
            cumpl_virtual = sum([1 for p, min_b, max_b in zip(pasante_virtual, banda_min, banda_max) if _esta_dentro_banda(p, min_b, max_b)])
            cumpl_virtual_pct = (cumpl_virtual / len(tamices)) * 100
            mejora_cumplimiento = cumpl_virtual - cumpl_inicial
            
            error_virtual = sum([
                max(0, banda_min[i] - pasante_virtual[i], pasante_virtual[i] - banda_max[i])
                if not _esta_dentro_banda(pasante_virtual[i], banda_min[i], banda_max[i]) else 0
                for i in range(len(tamices))
            ])
            mejora_error = error_real - error_virtual
            
        except Exception as e:
            pasante_virtual = pasante_real.copy()
            es_valida = False
            reporte_validacion = {'fallos': str(e)}
    
    virtual_usable_basica = bool(
        criterios['generar_tabla_virtual']
        and es_valida
        and cumpl_virtual_pct >= cumpl_inicial_pct
        and mejora_cumplimiento > 0
        and mejora_error > 0
    )

    # ===== FASE 6: RECETA FINAL =====
    proporciones = {
        "tabla_real_pct": 100.0,
        "tabla_virtual_pct": 0.0,
        "total_pct": 100.0,
    }

    if not criterios['generar_tabla_virtual']:
        semaforo = "🟢 OK - USAR DIRECTAMENTE"
        instruction = "Usar directamente los materiales en las proporciones reales validadas."
    elif virtual_usable_basica:
        semaforo = "🟡 ANALISIS AUXILIAR"
        instruction = "La tabla virtual solo puede utilizarse como simulación auxiliar validada. No debe mostrarse ni ejecutarse como receta automática de producción."
    else:
        semaforo = "🔴 SIN CORRECCION AUTOMATICA"
        instruction = "La mezcla actual no puede corregirse automáticamente sin perder coherencia física o representatividad industrial."
    
    fase_1 = {
        "cumplimiento_pct": round(cumpl_inicial_pct, 1),
        "cumpl_count": int(cumpl_inicial),
        "n_tamices": len(tamices),
        "error_total": round(float(error_real), 2),
        "estado": "PARCIAL" if cumpl_inicial_pct < 100 else "PERFECTO"
    }

    fase_2_4 = {
        "cumplimiento_banda_pct": round(criterios['cumplimiento_banda_pct'], 1),
        "cumple_banda": bool(criterios['cumple_banda']),
        "desviacion_media_centro": round(criterios['desviacion_media_centro'], 2),
        "es_buena_calidad": bool(criterios['es_buena_calidad']),
        "decision": criterios['decision'],
        "razon": criterios['razon'],
    }

    fase_5 = {
        "generada": bool(criterios['generar_tabla_virtual']),
        "valida": bool(es_valida),
        "cumplimiento_pct": round(cumpl_virtual_pct, 1),
        "cumpl_count": int(cumpl_virtual) if criterios['generar_tabla_virtual'] else 0,
        "cumplimiento_real_pct": round(cumpl_inicial_pct, 1),
        "error_total": round(float(error_virtual), 2),
        "mejora_cumplimiento": int(cumpl_virtual - cumpl_inicial) if criterios['generar_tabla_virtual'] else 0,
        "mejora_error": round(float(mejora_error), 2),
    }

    auditoria_industrial = _construir_auditoria_industrial(
        pasante_real=pasante_real,
        pasante_virtual=pasante_virtual,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices,
        criterios=fase_2_4,
        fase1=fase_1,
        fase5=fase_5,
        reporte_validacion=reporte_validacion,
        materiales=materiales,
        proporciones_optimizadas=proporciones_optimizadas,
    )

    return {
        "fase_1": fase_1,
        "fase_2_4_criterios": fase_2_4,
        "fase_5_virtual": fase_5,
        
        "fase_6_receta": {
            "proporciones": proporciones,
            "semaforo": semaforo,
            "instruction": instruction,
            "tabla_virtual_analisis_auxiliar": virtual_usable_basica,
            "tabla_real_pasante": [float(round(float(p), 2)) for p in pasante_real],
            "tabla_virtual_pasante": [float(round(float(p), 2)) for p in pasante_virtual],
        },

        "auditoria_industrial": auditoria_industrial,

        "trazabilidad_curvas": {
            "entrada_principal": TIPO_CURVA_PASANTE_ACUMULADO,
            "tipos_soportados_material": [
                TIPO_CURVA_RETENIDO_INDIVIDUAL,
                TIPO_CURVA_RETENIDO_ACUMULADO,
                TIPO_CURVA_PASANTE_ACUMULADO,
            ],
            "sentido_tamices": _describir_sentido_tamices(tamices),
            "regla_fisica": {
                TIPO_CURVA_RETENIDO_INDIVIDUAL: "Puede tener picos; no aplica monotonicidad.",
                TIPO_CURVA_RETENIDO_ACUMULADO: "Monotonicidad solo sobre curva acumulada.",
                TIPO_CURVA_PASANTE_ACUMULADO: "Monotonicidad solo sobre curva acumulada.",
            },
        },
        
        "para_grafico": {
            "tamices": [float(t) for t in tamices],
            "banda_min": [float(b) for b in banda_min],
            "banda_max": [float(b) for b in banda_max],
            "fuller_ideal": [float(round(100.0 - (100.0 * (float(tamiz) / 12.5) ** 0.45), 2)) if tamiz > 0 else 0.0 for tamiz in tamices],
            "pasante_real": [float(p) for p in pasante_real],
            "pasante_virtual": [float(p) for p in pasante_virtual],
        }
    }
