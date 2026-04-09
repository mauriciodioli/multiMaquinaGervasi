"""
MÓDULO AUDITORÍA Y DECISIÓN
Evaluación de cumplimiento de banda y generación de tabla virtual dirigida
Fase 1-6 del sistema de optimización granulométrica
"""

import numpy as np
from typing import Dict, List, Tuple
from .nucleo_tabla_virtual import generar_tabla_virtual, validar_tabla_virtual


TOLERANCIA_BANDA = 1e-6


def _limpiar_pasantes(pasante: np.ndarray) -> np.ndarray:
    pasante = np.array(pasante, dtype=float)
    pasante = np.clip(pasante, 0.0, 100.0)
    pasante[np.abs(pasante) < TOLERANCIA_BANDA] = 0.0
    pasante[np.abs(pasante - 100.0) < TOLERANCIA_BANDA] = 100.0
    return pasante


def _esta_dentro_banda(pasante: float, banda_min: float, banda_max: float) -> bool:
    return (banda_min - TOLERANCIA_BANDA) <= pasante <= (banda_max + TOLERANCIA_BANDA)


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
    tamices: List[float]
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
    
    if criterios['generar_tabla_virtual']:
        try:
            # Generar tabla virtual
            pasante_virtual, debug_info = generar_tabla_virtual(
                pasante_mezcla=pasante_real[::-1].tolist(),
                banda_min=banda_min[::-1].tolist(),
                banda_max=banda_max[::-1].tolist(),
                tamices=[str(x) for x in tamices[::-1]],
                metodo="principal",
                factor_suavizado=0.5,
            )
            pasante_virtual = _limpiar_pasantes(np.array(pasante_virtual)[::-1])
            
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
    
    # ===== FASE 6: RECETA FINAL =====
    if not criterios['generar_tabla_virtual']:
        # No requiere tabla virtual
        proporciones = {
            "tabla_real_pct": 100.0,
            "tabla_virtual_pct": 0.0,
            "total_pct": 100.0,
        }
        semaforo = "🟢 OK - USAR DIRECTAMENTE"
        instruction = "Usar directamente los materiales en las proporciones de la tabla real."
    else:
        # Requiere mezcla
        proporciones = {
            "tabla_real_pct": 50.0,
            "tabla_virtual_pct": 50.0,
            "total_pct": 100.0,
        }
        
        if es_valida:
            semaforo = "🟢 OK - MEZCLAR TABLAS"
            instruction = "Mezclar partes iguales de tabla real y tabla virtual (generada)."
        else:
            semaforo = "🟡 OK CON ADVERTENCIA"
            instruction_warning = f"⚠ La tabla virtual tiene problemas: {reporte_validacion.get('fallos', 'desconocido')}"
            instruction = f"Mezclar partes iguales. {instruction_warning}"
    
    return {
        "fase_1": {
            "cumplimiento_pct": round(cumpl_inicial_pct, 1),
            "cumpl_count": int(cumpl_inicial),
            "n_tamices": len(tamices),
            "error_total": round(float(error_real), 2),
            "estado": "PARCIAL" if cumpl_inicial_pct < 100 else "PERFECTO"
        },
        
        "fase_2_4_criterios": {
            "cumplimiento_banda_pct": round(criterios['cumplimiento_banda_pct'], 1),
            "cumple_banda": bool(criterios['cumple_banda']),
            "desviacion_media_centro": round(criterios['desviacion_media_centro'], 2),
            "es_buena_calidad": bool(criterios['es_buena_calidad']),
            "decision": criterios['decision'],
            "razon": criterios['razon'],
        },
        
        "fase_5_virtual": {
            "generada": bool(criterios['generar_tabla_virtual']),
            "valida": bool(es_valida),
            "cumplimiento_pct": round(cumpl_virtual_pct, 1),
            "cumpl_count": int(cumpl_virtual) if criterios['generar_tabla_virtual'] else 0,
            "error_total": round(float(error_virtual), 2),
            "mejora_cumplimiento": int(cumpl_virtual - cumpl_inicial) if criterios['generar_tabla_virtual'] else 0,
            "mejora_error": round(float(mejora_error), 2),
        },
        
        "fase_6_receta": {
            "proporciones": proporciones,
            "semaforo": semaforo,
            "instruction": instruction,
            "tabla_real_pasante": [float(round(float(p), 2)) for p in pasante_real],
            "tabla_virtual_pasante": [float(round(float(p), 2)) for p in pasante_virtual],
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
