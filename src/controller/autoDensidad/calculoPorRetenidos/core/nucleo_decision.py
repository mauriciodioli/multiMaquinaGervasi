"""
NUCLEO DE DECISION (Python)

Lógica de decisión: suficiencia, mejora, parada
"""

# Configuración de decisión (todos los parámetros son configurables)
CONFIG_DECISION = {
    'E_umbral_base': 0.25,              # Umbral de error base
    'cumpl_min_aceptable': 0.95,        # 95% para "muy_bueno"
    'cumpl_min_marginal': 0.80,         # 80% para "marginal"
    'mejora_abs_min': 0.5,              # Mejora absoluta mínima
    'mejora_rel_min': 0.15,             # Mejora relativa mínima (15%)
    'factor_mejora_esperada': 0.30,     # Factor para virtual table
    'iteraciones_maximas': 5,
    'tablas_virtuales_maximas': 4
}


def clasificar_suficiencia(reporte, n_tamices):
    """
    Clasifica suficiencia en 4 niveles
    
    Niveles:
    - perfecto: E=0, cumpl=100%
    - muy_bueno: E pequeño, cumpl >= 95%
    - marginal: E moderado, cumpl >= 80%
    - insuficiente: E grande, cumpl < 80%
    
    Args:
        reporte: dict - Reporte de error
        n_tamices: int - Número de tamices
    
    Returns:
        dict - {nivel, descripcion, E_umbral}
    """
    E = reporte['error_total']
    cumpl = reporte['cumplimiento_total_pct'] / 100.0
    
    # Umbral de error ajustado por cantidad de tamices
    E_umbral = CONFIG_DECISION['E_umbral_base'] * (n_tamices / 10.0)
    
    if E == 0:
        return {
            'nivel': 'perfecto',
            'descripcion': 'Error nulo, cumplimiento total',
            'E_umbral': E_umbral
        }
    elif E <= E_umbral and cumpl >= CONFIG_DECISION['cumpl_min_aceptable']:
        return {
            'nivel': 'muy_bueno',
            'descripcion': f'Error bajo ({E:.3f}), cumplimiento {cumpl*100:.1f}%',
            'E_umbral': E_umbral
        }
    elif E <= E_umbral * 2 and cumpl >= CONFIG_DECISION['cumpl_min_marginal']:
        return {
            'nivel': 'marginal',
            'descripcion': f'Error moderado ({E:.3f}), cumplimiento {cumpl*100:.1f}%',
            'E_umbral': E_umbral
        }
    else:
        return {
            'nivel': 'insuficiente',
            'descripcion': f'Error alto ({E:.3f}), cumplimiento bajo {cumpl*100:.1f}%',
            'E_umbral': E_umbral
        }


def evaluar_mejora(E_anterior, E_actual, reporte):
    """
    Evalúa si hay mejora significativa
    
    Criterio: AMBAS deben cumplirse (AND logic)
    - Mejora absoluta >= mejora_abs_min
    - Mejora relativa >= mejora_rel_min
    
    Args:
        E_anterior: float - Error anterior
        E_actual: float - Error actual
        reporte: dict - Reporte actual
    
    Returns:
        dict - {mejora_significativa, delta_abs, delta_rel_pct, razon}
    """
    delta_abs = E_anterior - E_actual
    delta_rel = (E_anterior - E_actual) / E_anterior if E_anterior > 0 else 0
    delta_rel_pct = delta_rel * 100
    
    mejora_abs_ok = delta_abs >= CONFIG_DECISION['mejora_abs_min']
    mejora_rel_ok = delta_rel >= CONFIG_DECISION['mejora_rel_min']
    
    mejora_significativa = mejora_abs_ok and mejora_rel_ok
    
    if not mejora_abs_ok:
        razon = f"Mejora absoluta insuficiente: {delta_abs:.3f} < {CONFIG_DECISION['mejora_abs_min']}"
    elif not mejora_rel_ok:
        razon = f"Mejora relativa insuficiente: {delta_rel_pct:.2f}% < {CONFIG_DECISION['mejora_rel_min']*100:.1f}%"
    else:
        razon = f"Mejora significativa: {delta_abs:.3f} ABS, {delta_rel_pct:.2f}% REL"
    
    return {
        'mejora_significativa': mejora_significativa,
        'delta_abs': round(delta_abs, 4),
        'delta_rel_pct': round(delta_rel_pct, 2),
        'razon': razon
    }


def predecir_mejora_tabla_virtual(reporte):
    """
    Predice mejora esperada con tabla virtual
    
    Heurística: E_esp = E_actual × (1 - factor × (1 - cumpl_zona_critica))
    
    Args:
        reporte: dict
    
    Returns:
        dict - {E_esperado, mejora_esperada, factor_aplicado}
    """
    E_actual = reporte['error_total']
    zona_critica = reporte['zona_critica']
    
    datos_zona = reporte['errores_por_zona'][zona_critica]
    tamices_en_banda = datos_zona['tamices_en_banda']
    tamices_en_zona = datos_zona['tamices_en_zona']
    
    cumpl_zona_critica = tamices_en_banda / tamices_en_zona if tamices_en_zona > 0 else 0
    
    factor = CONFIG_DECISION['factor_mejora_esperada']
    reductor = 1.0 - cumpl_zona_critica
    
    E_esperado = E_actual * (1.0 - factor * reductor)
    mejora_esperada = E_actual - E_esperado
    
    return {
        'E_esperado': round(E_esperado, 4),
        'mejora_esperada': round(mejora_esperada, 4),
        'factor_aplicado': factor,
        'cumpl_zona_critica': round(cumpl_zona_critica, 2)
    }


def evaluar_parada(historial, reporte_actual):
    """
    Evalúa si debe detener la iteración
    
    Condiciones de parada:
    1. Perfección: E=0
    2. Aceptable: E <= umbral, cumpl >= 95%
    3. Estancamiento: ΔE < 0.30 en 2 iteraciones
    4. Límite_iters: iters >= max
    
    Args:
        historial: HistorialIteraciones object
        reporte_actual: dict
    
    Returns:
        dict - {debe_parar, razon}
    """
    E_actual = reporte_actual['error_total']
    cumpl = reporte_actual['cumplimiento_total_pct'] / 100.0
    n_tamices = len(reporte_actual['errores_por_tamiz'])
    
    E_umbral = CONFIG_DECISION['E_umbral_base'] * (n_tamices / 10.0)
    
    # Condición 1: Perfección
    if E_actual == 0:
        return {
            'debe_parar': True,
            'razon': 'perfección'
        }
    
    # Condición 2: Aceptable
    if E_actual <= E_umbral and cumpl >= CONFIG_DECISION['cumpl_min_aceptable']:
        return {
            'debe_parar': True,
            'razon': 'aceptable'
        }
    
    # Condición 3: Estancamiento
    if hasattr(historial, 'obtener_ultima'):
        iter_anterior = historial.obtener_anterior(1)
        if iter_anterior:
            E_anterior = iter_anterior.error_total
            delta = abs(E_anterior - E_actual)
            
            if delta < 0.30:
                # Verificar dos veces consecutivas
                iter_2anterior = historial.obtener_anterior(2)
                if iter_2anterior:
                    E_2anterior = iter_2anterior.error_total
                    delta_2 = abs(iter_anterior.error_total - E_2anterior)
                    if delta_2 < 0.30:
                        return {
                            'debe_parar': True,
                            'razon': 'estancamiento'
                        }
    
    # Condición 4: Límite de iteraciones
    n_iters = len(historial.iteraciones) if hasattr(historial, 'iteraciones') else 0
    if n_iters >= CONFIG_DECISION['iteraciones_maximas']:
        return {
            'debe_parar': True,
            'razon': 'límite_iters'
        }
    
    return {
        'debe_parar': False,
        'razon': 'continuar'
    }


def crear_reporte_decision(reporte_error, historial, n_tamices):
    """
    Genera reporte de decisión completo
    
    Args:
        reporte_error: dict
        historial: HistorialIteraciones
        n_tamices: int
    
    Returns:
        dict - Reporte decisión con suficiencia, mejora, parada, recomendación
    """
    suficiencia = clasificar_suficiencia(reporte_error, n_tamices)
    
    # Evaluar mejora si hay iteración anterior
    mejora = None
    if hasattr(historial, 'obtener_ultima') and historial.obtener_ultima():
        iter_anterior = historial.obtener_anterior(1)
        if iter_anterior:
            mejora = evaluar_mejora(iter_anterior.error_total, reporte_error['error_total'], reporte_error)
        else:
            mejora = {
                'mejora_significativa': False,
                'delta_abs': 0,
                'delta_rel_pct': 0,
                'razon': 'Primera iteración'
            }
    else:
        mejora = {
            'mejora_significativa': False,
            'delta_abs': 0,
            'delta_rel_pct': 0,
            'razon': 'Sin historial'
        }
    
    parada = evaluar_parada(historial, reporte_error)
    
    prediccion_virtual = predecir_mejora_tabla_virtual(reporte_error)
    
    recomendacion = generar_recomendacion(suficiencia, mejora, parada)
    proximos_pasos = generar_proximos_pasos(suficiencia, mejora, parada, prediccion_virtual)
    
    return {
        'iteracion_actual': len(historial.iteraciones) if hasattr(historial, 'iteraciones') else 0,
        'estado_suficiencia': suficiencia,
        'mejora': mejora,
        'parada': parada,
        'prediccion_virtual': prediccion_virtual,
        'recomendacion': recomendacion,
        'proximos_pasos': proximos_pasos
    }


def generar_recomendacion(suficiencia, mejora, parada):
    """
    Genera recomendación legible
    
    Args:
        suficiencia: dict
        mejora: dict
        parada: dict
    
    Returns:
        str
    """
    if parada['razon'] == 'perfección':
        return "✓ Solución perfecta alcanzada. Mezcla óptima."
    elif parada['razon'] == 'aceptable':
        return "✓ Solución aceptable. Mezcla cumple especificaciones."
    elif parada['razon'] == 'estancamiento':
        return "✗ Error estancado. No hay mejora. Considerar tabla virtual."
    elif parada['razon'] == 'límite_iters':
        return "⚠ Límite de iteraciones alcanzado. Usar mejora actual o generar tabla virtual."
    elif suficiencia['nivel'] == 'insuficiente':
        return "✗ Suficiencia insuficiente. Debe continuar optimización."
    elif suficiencia['nivel'] == 'marginal':
        return "△ Suficiencia marginal. Puede mejorar con ajustes."
    else:
        return "→ Continuando optimización..."


def generar_proximos_pasos(suficiencia, mejora, parada, prediccion):
    """
    Genera lista de próximos pasos
    
    Args:
        suficiencia: dict
        mejora: dict
        parada: dict
        prediccion: dict
    
    Returns:
        list of str
    """
    pasos = []
    
    if parada['razon'] in ['perfección', 'aceptable']:
        pasos.append("1. Usar proporciones actuales")
        pasos.append("2. Validar con datos reales")
        pasos.append("3. Guardar mezcla óptima")
    elif parada['razon'] == 'estancamiento':
        pasos.append("1. Generar tabla virtual en zona crítica")
        pasos.append("2. Re-optimizar con nueva tabla")
        pasos.append("3. Comparar mejora predicha vs actual")
    elif not mejora['mejora_significativa']:
        pasos.append("1. Ajustar proporciones automáticamente")
        pasos.append("2. Evaluar zona crítica")
        pasos.append("3. Considerar tabla virtual")
    else:
        pasos.append("1. Continuar iteración")
        pasos.append("2. Monitorear convergencia")
        pasos.append("3. Reintentar optimización")
    
    return pasos


if __name__ == '__main__':
    # Test simple
    reporte_test = {
        'error_total': 0.5,
        'cumplimiento_total_pct': 96.0,
        'errores_por_tamiz': [{'en_banda': True}] * 10,
        'errores_por_zona': {
            'gruesa': {'tamices_en_banda': 3, 'tamices_en_zona': 3},
            'media': {'tamices_en_banda': 3, 'tamices_en_zona': 4},
            'fina': {'tamices_en_banda': 2, 'tamices_en_zona': 3}
        },
        'zona_critica': 'fina'
    }
    
    suficiencia = clasificar_suficiencia(reporte_test, 10)
    print("Suficiencia:", suficiencia['nivel'])
    
    mejora = evaluar_mejora(1.5, 0.5, reporte_test)
    print("Mejora:", mejora['mejora_significativa'])
