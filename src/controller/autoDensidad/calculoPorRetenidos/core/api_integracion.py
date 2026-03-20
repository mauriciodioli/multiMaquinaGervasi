"""
API DE INTEGRACION (Python)

Interfaz unificada para optimización de mezclas
Integra: mezcla + error + decisión + optimización + iteración
"""

from .nucleo_mezcla import calcular_mezcla_pasante
from .nucleo_error import crear_reporte_error
from .nucleo_decision import crear_reporte_decision
from .nucleo_iteracion import HistorialIteraciones, EstadoIteracion, ejecutar_optimizacion_completa


def validar_configuracion(config):
    """
    Valida estructura de entrada
    
    Args:
        config: dict
    
    Returns:
        dict - {valido, errores}
    """
    errores = []
    
    if 'materiales' not in config or not isinstance(config['materiales'], list):
        errores.append("Campo 'materiales' debe ser un array")
    elif len(config['materiales']) == 0:
        errores.append("Se requiere al menos 1 material")
    else:
        # Validar cada material
        for i, m in enumerate(config['materiales']):
            if 'pasante' not in m or not isinstance(m['pasante'], list):
                errores.append(f"Material {i} debe tener array 'pasante'")
            if 'w' not in m or not isinstance(m['w'], (int, float)):
                errores.append(f"Material {i} debe tener peso 'w' numérico")
    
    if 'limites' not in config or not isinstance(config['limites'], dict):
        errores.append("Campo 'limites' debe ser un objeto {tamiz: [min, max]}")
    elif len(config['limites']) == 0:
        errores.append("Se requieren al menos 1 límite por tamiz")
    
    if 'tamices' not in config or not isinstance(config['tamices'], list):
        errores.append("Campo 'tamices' debe ser un array de strings")
    elif len(config['tamices']) == 0:
        errores.append("Se requieren al menos 1 tamiz")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


def optimizar_mezcla(config):
    """
    API PRINCIPAL: Optimiza mezcla en un paso
    
    Args:
        config: dict
        {
            materiales: [{nombre, pasante, w}, ...],
            limites: {tamiz: [min, max], ...},
            tamices: [...],
            opciones: {
                max_iteraciones: 5,
                max_tablas_virtuales: 3,
                verbose: false
            }
        }
    
    Returns:
        dict - Resultado completo
    """
    # Validación
    validacion = validar_configuracion(config)
    if not validacion['valido']:
        return {
            'exito': False,
            'error': 'Validación fallida',
            'detalles_error': validacion['errores'],
            'proporciones_optimizadas': None,
            'mensaje': '; '.join(validacion['errores'])
        }
    
    # Opciones por defecto
    opciones = {
        'max_iteraciones': 5,
        'max_tablas_virtuales': 3,
        'verbose': False
    }
    if 'opciones' in config:
        opciones.update(config['opciones'])
    
    # Normalizar pesos iniciales
    suma_w = sum(m.get('w', 0) for m in config['materiales'])
    materiales_normalizados = []
    for m in config['materiales']:
        m_norm = dict(m)
        m_norm['w'] = m.get('w', 0) / suma_w if suma_w > 0 else 1.0 / len(config['materiales'])
        materiales_normalizados.append(m_norm)
    
    # Ejecutar optimización completa
    resultado_opt = ejecutar_optimizacion_completa(
        {
            'materiales': materiales_normalizados,
            'limites': config['limites'],
            'tamices': config['tamices'],
            'max_iteraciones': opciones['max_iteraciones'],
            'max_tablas_virtuales': opciones['max_tablas_virtuales']
        },
        lambda prog: print(f"[OPT] {prog}") if opciones['verbose'] else None
    )
    
    # Formatear resultado
    proporciones = resultado_opt.get('proporciones_finales', [])
    proporciones_pct = [round(p * 100, 2) for p in proporciones]
    
    # Nombres de materiales en proporciones
    proporciones_formato = []
    for i, p in enumerate(proporciones_pct):
        if i < len(config['materiales']):
            nombre = config['materiales'][i].get('nombre', f'Material {i}')
            proporciones_formato.append(f"{nombre}: {p}%")
    
    return {
        'exito': resultado_opt.get('exito', False),
        'proporciones_optimizadas': proporciones,
        'proporciones_pct': proporciones_pct,
        'proporciones_formato': proporciones_formato,
        'error_minimo': resultado_opt.get('error_final', float('inf')),
        'mejora_total': resultado_opt['resumen'].get('mejora_total', 0),
        'mejora_total_pct': round(resultado_opt['resumen'].get('mejora_total_relativa', 0) * 10000) / 100,
        'cumplimiento_pct': round(resultado_opt.get('cumplimiento_final', 0) * 10000) / 100,
        'iteraciones_realizadas': resultado_opt.get('iteracion_final', 0),
        'tablas_virtuales_usadas': resultado_opt['resumen'].get('tablas_virtuales_usadas', 0),
        'razon_parada': resultado_opt.get('razon_parada', 'desconocida'),
        'detalles_error': {
            'error_total': resultado_opt.get('error_final'),
            'errores_por_zona': resultado_opt['reporte_error_final'].get('errores_por_zona', {}) 
                                if resultado_opt.get('reporte_error_final') else {},
            'zona_critica': resultado_opt['reporte_error_final'].get('zona_critica', 'desconocida')
                            if resultado_opt.get('reporte_error_final') else 'desconocida'
        },
        'detalles_decision': {
            'suficiencia': resultado_opt['reporte_decision_final'].get('estado_suficiencia', {}).get('nivel')
                          if resultado_opt.get('reporte_decision_final') else 'desconocida',
            'mejora_detectada': resultado_opt['reporte_decision_final'].get('mejora', {}).get('mejora_significativa')
                               if resultado_opt.get('reporte_decision_final') else False,
            'recomendacion': resultado_opt['reporte_decision_final'].get('recomendacion', '')
                            if resultado_opt.get('reporte_decision_final') else ''
        },
        'historial_completo': {
            'trayectoria': resultado_opt['historial'].obtener_trayectoria() if resultado_opt.get('historial') else [],
            'resumen': resultado_opt.get('resumen', {})
        },
        'mensaje': generar_mensaje_resultado(resultado_opt)
    }


def analizar_mezcla_actual(config):
    """
    Analiza mezcla actual sin optimizar
    
    Args:
        config: dict
    
    Returns:
        dict - Análisis actual
    """
    validacion = validar_configuracion(config)
    if not validacion['valido']:
        return {
            'exito': False,
            'error': 'Validación fallida',
            'errores': validacion['errores']
        }
    
    # Calcular mezcla
    pasante_mezcla = calcular_mezcla_pasante(config['materiales'])
    
    # Evaluar error
    reporte_error = crear_reporte_error(
        pasante_mezcla,
        config['limites'],
        config['tamices']
    )
    
    # Historial dummy para decisión
    historial_dummy = HistorialIteraciones(5)
    estado_dummy = EstadoIteracion(0)
    historial_dummy.agregar_iteracion(estado_dummy)
    
    reporte_decision = crear_reporte_decision(
        reporte_error,
        historial_dummy,
        len(config['tamices'])
    )
    
    return {
        'exito': True,
        'pasante_mezcla': pasante_mezcla,
        'error_total': reporte_error['error_total'],
        'cumplimiento_pct': reporte_error['cumplimiento_total_pct'],
        'errores_por_tamiz': reporte_error['errores_por_tamiz'],
        'errores_por_zona': reporte_error['errores_por_zona'],
        'zona_critica': reporte_error['zona_critica'],
        'suficiencia': reporte_decision['estado_suficiencia']['nivel'],
        'recomendacion': reporte_decision['recomendacion'],
        'mensaje': f"Análisis completado: {reporte_decision['recomendacion']}"
    }


def generar_mensaje_resultado(resultado):
    """
    Genera mensaje legible del resultado
    
    Args:
        resultado: dict
    
    Returns:
        str
    """
    msg = ""
    
    if resultado.get('exito'):
        msg += f"✓ OPTIMIZACIÓN EXITOSA en {resultado.get('iteracion_final', 0)} iteraciones\n"
        msg += f"  Error final: {resultado.get('error_final', 0):.3f}\n"
        msg += f"  Mejora total: {resultado['resumen'].get('mejora_total', 0):.3f} " \
               f"({resultado['resumen'].get('mejora_total_relativa', 0)*100:.1f}%)\n"
        msg += f"  Cumplimiento: {resultado.get('cumplimiento_final', 0)*100:.1f}%\n"
        if resultado['resumen'].get('tablas_virtuales_usadas', 0) > 0:
            msg += f"  Tablas virtuales generadas: {resultado['resumen']['tablas_virtuales_usadas']}\n"
    else:
        msg += f"✗ OPTIMIZACIÓN INCOMPLETA\n"
        msg += f"  Razón: {resultado.get('razon_parada', 'desconocida')}\n"
        msg += f"  Iteraciones realizadas: {resultado.get('iteracion_final', 0)}\n"
        msg += f"  Error alcanzado: {resultado.get('error_final', 0):.3f}\n"
    
    return msg


def exportar_resultado(resultado_opt):
    """
    Exporta resultado en formato JSON-compatible para API
    
    Args:
        resultado_opt: dict
    
    Returns:
        dict
    """
    return {
        'status': 'success' if resultado_opt.get('exito') else 'partial',
        'optimizacion': {
            'proporciones': [round(p, 6) for p in resultado_opt.get('proporciones_optimizadas', [])],
            'proporciones_porcentaje': resultado_opt.get('proporciones_pct', []),
            'error_final': round(resultado_opt.get('error_final', 0), 3),
            'mejora_total': round(resultado_opt['resumen'].get('mejora_total', 0), 3),
            'cumplimiento_porcentaje': round(resultado_opt.get('cumplimiento_final', 0) * 10000) / 100
        },
        'proceso': {
            'iteraciones': resultado_opt.get('iteracion_final', 0),
            'tablas_virtuales': resultado_opt['resumen'].get('tablas_virtuales_usadas', 0),
            'razon_parada': resultado_opt.get('razon_parada', 'desconocida'),
            'convergio': resultado_opt.get('exito', False)
        },
        'diagnostico': {
            'zona_critica': resultado_opt.get('reporte_error_final', {}).get('zona_critica'),
            'errores_por_zona': resultado_opt.get('reporte_error_final', {}).get('errores_por_zona'),
            'recomendacion': resultado_opt.get('reporte_decision_final', {}).get('recomendacion')
        },
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test simple
    from .nucleo_mezcla import crear_material
    
    mat1 = crear_material("Arena", [0, 5, 15, 25, 35, 40, 45, 50, 55, 60], 0.35)
    mat2 = crear_material("Grava", [0, 2, 8, 15, 20, 25, 30, 35, 40, 45], 0.65)
    
    config = {
        'materiales': [mat1, mat2],
        'limites': {
            '12.5': [0, 10],
            '9.5': [10, 30],
            '6.3': [30, 50],
            '4.8': [50, 65],
            '2.4': [65, 80],
            '1.2': [80, 90],
            '0.6': [88, 95],
            '0.3': [92, 98],
            '0.15': [95, 100],
            '0.075': [98, 100]
        },
        'tamices': ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.6', '0.3', '0.15', '0.075'],
        'opciones': {
            'max_iteraciones': 5,
            'max_tablas_virtuales': 3,
            'verbose': True
        }
    }
    
    resultado = optimizar_mezcla(config)
    print("Resultado:")
    print(f"  Exito: {resultado['exito']}")
    print(f"  Proporciones: {resultado['proporciones_pct']}")
    print(f"  Error: {resultado['error_minimo']:.3f}")
