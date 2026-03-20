"""
NUCLEO DE ERROR (Python)

Sistema de cálculo de error lineal (NO cuadrático)
Error por tamiz: e_i = max(0, L_i - p_i, p_i - U_i)
Agregación: E_total = Σ e_i
"""

import math


def calcular_error_por_tamiz(pasante, min_pct, max_pct):
    """
    Calcula error lineal para un tamiz
    
    Formula: e_i = max(0, L_i - p_i, p_i - U_i)
    
    Args:
        pasante: float - Valor PASANTE medido
        min_pct: float - Límite inferior (L)
        max_pct: float - Límite superior (U)
    
    Returns:
        dict - {error, tipo, debajo, arriba, en_banda}
    """
    p = float(pasante)
    L = float(min_pct)
    U = float(max_pct)
    
    en_banda = (L <= p <= U)
    
    if en_banda:
        return {
            'error': 0.0,
            'tipo': 'en_banda',
            'debajo': 0.0,
            'arriba': 0.0,
            'en_banda': True,
            'pasante': p
        }
    elif p < L:
        # Por debajo del límite inferior
        delta = L - p
        return {
            'error': delta,
            'tipo': 'debajo',
            'debajo': delta,
            'arriba': 0.0,
            'en_banda': False,
            'pasante': p
        }
    else:  # p > U
        # Por encima del límite superior
        delta = p - U
        return {
            'error': delta,
            'tipo': 'arriba',
            'debajo': 0.0,
            'arriba': delta,
            'en_banda': False,
            'pasante': p
        }


def calcular_errores_por_tamiz(pasante_mezcla, limites, tamices):
    """
    Calcula error para cada tamiz
    
    Args:
        pasante_mezcla: list - PASANTE de la mezcla
        limites: dict - {tamiz: [min, max], ...}
        tamices: list - Nombres de tamices en orden
    
    Returns:
        dict - {errores_por_tamiz: [], E_total, E_debajo, E_arriba}
    """
    errores = []
    E_total = 0.0
    E_debajo = 0.0
    E_arriba = 0.0
    
    for i, tamiz in enumerate(tamices):
        if i >= len(pasante_mezcla):
            break
        
        tamiz_str = str(tamiz)
        
        if tamiz_str not in limites:
            continue
        
        limite = limites[tamiz_str]
        min_pct, max_pct = float(limite[0]), float(limite[1])
        pasante = pasante_mezcla[i]
        
        error_dict = calcular_error_por_tamiz(pasante, min_pct, max_pct)
        
        errores.append({
            'tamiz': tamiz,
            'pasante': pasante,
            'limite_min': min_pct,
            'limite_max': max_pct,
            'error': error_dict['error'],
            'tipo': error_dict['tipo'],
            'en_banda': error_dict['en_banda']
        })
        
        E_total += error_dict['error']
        E_debajo += error_dict['debajo']
        E_arriba += error_dict['arriba']
    
    return {
        'errores_por_tamiz': errores,
        'E_total': round(E_total, 4),
        'E_debajo': round(E_debajo, 4),
        'E_arriba': round(E_arriba, 4)
    }


def definir_zonas_automaticas(tamices):
    """
    Divide tamices en 3 zonas automáticamente
    
    Criterio: Terciles del array de tamices
    - gruesa: primeros 1/3
    - media: segundo 1/3
    - fina: últimos 1/3
    
    Args:
        tamices: list
    
    Returns:
        dict - {gruesa: indices, media: indices, fina: indices}
    """
    n = len(tamices)
    n_tercio = math.ceil(n / 3)
    
    return {
        'gruesa': list(range(0, n_tercio)),
        'media': list(range(n_tercio, 2 * n_tercio)),
        'fina': list(range(2 * n_tercio, n))
    }


def calcular_errores_por_zona(errores_por_tamiz, zonas):
    """
    Agrega errores por zona
    
    Args:
        errores_por_tamiz: list - Array de errores
        zonas: dict - {gruesa, media, fina}
    
    Returns:
        dict - {errores_por_zona, zona_critica}
    """
    errores_zona = {}
    
    for zona_nombre, indices in zonas.items():
        errores_zona[zona_nombre] = {
            'error_total': 0.0,
            'tamices_en_zona': 0,
            'tamices_en_banda': 0,
            'tamices_fuera_banda': 0
        }
        
        for idx in indices:
            if idx < len(errores_por_tamiz):
                e = errores_por_tamiz[idx]
                errores_zona[zona_nombre]['error_total'] += e['error']
                errores_zona[zona_nombre]['tamices_en_zona'] += 1
                
                if e['en_banda']:
                    errores_zona[zona_nombre]['tamices_en_banda'] += 1
                else:
                    errores_zona[zona_nombre]['tamices_fuera_banda'] += 1
    
    # Zona crítica: mayor error total
    zona_critica = max(errores_zona.keys(), 
                       key=lambda z: errores_zona[z]['error_total'])
    
    return {
        'errores_por_zona': errores_zona,
        'zona_critica': zona_critica
    }


def crear_reporte_error(pasante_mezcla, limites, tamices):
    """
    Genera reporte de error completo
    
    Args:
        pasante_mezcla: list
        limites: dict
        tamices: list
    
    Returns:
        dict - Reporte completo con error, zonas, cumplimiento, etc
    """
    # Calcular errores
    result_errores = calcular_errores_por_tamiz(pasante_mezcla, limites, tamices)
    
    # Definir zonas
    zonas = definir_zonas_automaticas(tamices)
    
    # Calcular por zona
    result_zonas = calcular_errores_por_zona(result_errores['errores_por_tamiz'], zonas)
    
    # Cumplimiento total
    tamices_en_banda = sum(1 for e in result_errores['errores_por_tamiz'] if e['en_banda'])
    cumplimiento_total_pct = (tamices_en_banda / len(result_errores['errores_por_tamiz']) * 100) if result_errores['errores_por_tamiz'] else 0
    
    # Detectar si es perfecto o aceptable
    es_perfecto = result_errores['E_total'] == 0
    es_aceptable = result_errores['E_total'] <= 0.5 and cumplimiento_total_pct >= 95
    
    return {
        'error_total': result_errores['E_total'],
        'error_debajo': result_errores['E_debajo'],
        'error_arriba': result_errores['E_arriba'],
        'error_normalizado': result_errores['E_total'] / len(result_errores['errores_por_tamiz']) if result_errores['errores_por_tamiz'] else 0,
        'errores_por_tamiz': result_errores['errores_por_tamiz'],
        'cumplimiento_total_pct': round(cumplimiento_total_pct, 1),
        'tamices_en_banda': tamices_en_banda,
        'errores_por_zona': result_zonas['errores_por_zona'],
        'zona_critica': result_zonas['zona_critica'],
        'es_perfecto': es_perfecto,
        'es_aceptable': es_aceptable
    }


def detectar_no_correcible(reporte, error_anterior=None):
    """
    Detecta si el error es no-corregible (3 señales)
    
    Señales:
    1. Estancamiento: ΔE < 0.01
    2. Concentración: > 80% del error en una zona
    3. Contradicción: límites incompatibles
    
    Args:
        reporte: dict - Reporte de error
        error_anterior: float - Error de iteración anterior
    
    Returns:
        dict - {detectado, razon, senal}
    """
    errores_zona = reporte['errores_por_zona']
    error_actual = reporte['error_total']
    
    # Señal 1: Estancamiento
    if error_anterior is not None:
        delta = abs(error_anterior - error_actual)
        if delta < 0.01:
            return {
                'detectado': True,
                'razon': f'Estancamiento: ΔE={delta:.4f} < 0.01',
                'senal': 'estancamiento'
            }
    
    # Señal 2: Concentración en una zona
    total_zone_error = sum(z['error_total'] for z in errores_zona.values())
    if total_zone_error > 0:
        for zona, datos in errores_zona.items():
            pct_zona = datos['error_total'] / total_zone_error * 100
            if pct_zona > 80:
                return {
                    'detectado': True,
                    'razon': f'Concentración: {pct_zona:.1f}% del error en zona {zona}',
                    'senal': 'concentracion'
                }
    
    # Señal 3: Contradicción (límites incompatibles)
    # Esto ocurre cuando no hay forma de satisfacer los límites
    # Por ahora, lo detectamos si tiene errores muy persistentes
    
    return {
        'detectado': False,
        'razon': 'Sin señales de no-corregibilidad',
        'senal': None
    }


if __name__ == '__main__':
    # Test
    pasante = [100, 95, 80, 65, 45, 28, 15, 8, 3, 1]
    limites = {
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
    }
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.6', '0.3', '0.15', '0.075']
    
    reporte = crear_reporte_error(pasante, limites, tamices)
    print("Error Total:", reporte['error_total'])
    print("Cumplimiento:", reporte['cumplimiento_total_pct'])
    print("Zona Crítica:", reporte['zona_critica'])
