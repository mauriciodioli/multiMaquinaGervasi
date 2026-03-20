"""
NUCLEÓ DE DIAGNÓSTICO RESIDUAL (Python)

Formaliza FASE 3: Detecta y explica el error residual que NO se puede corregir
con las tablas actuales, definiendo qué debe corregir la tabla virtual.

Entrada:
- pasante_mezcla: Pasante de la mezcla optimizada
- banda_min, banda_max: Especificación
- tamices: Nombres de tamices

Salida:
- Diagnóstico completo: qué está fuera, por qué, qué debe corregir la TV
"""

import math
from typing import Dict, List, Any


def clasificar_zonas(tamices: List[float]) -> Dict[str, List[int]]:
    """
    Divide tamices en 3 zonas por terciles
    
    Args:
        tamices: Lista de tamaños de tamiz [8, 5, 3.15, 2, 1, 0.5, 0.1]
    
    Returns:
        dict con índices de cada zona:
        - gruesos: primeros 1/3 (grandes)
        - medios: segundo 1/3 (intermedios)
        - finos: últimos 1/3 (chicos)
    """
    n = len(tamices)
    n_tercio = math.ceil(n / 3)
    
    return {
        'gruesos': list(range(0, n_tercio)),
        'medios': list(range(n_tercio, 2 * n_tercio)),
        'finos': list(range(2 * n_tercio, n))
    }


def analizar_error_por_tamiz(
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[float]
) -> Dict[str, Any]:
    """
    Analiza error por tamiz individual
    
    Args:
        pasante_mezcla: Pasante de mezcla optimizada
        banda_min: Límites inferiores por tamiz
        banda_max: Límites superiores por tamiz
        tamices: Tamaños de tamiz
    
    Returns:
        dict con análisis por tamiz:
        {
            'errores_por_tamiz': [
                {
                    'tamiz': x,
                    'pasante': y,
                    'lim_min': a,
                    'lim_max': b,
                    'error': e,
                    'tipo': 'en_banda' | 'debajo_min' | 'encima_max',
                    'deficit': POSITIVO si está DEBAJO,
                    'exceso': POSITIVO si está ENCIMA
                }
            ],
            'tamices_ok': int,
            'tamices_fuera': int,
            'error_total': float
        }
    """
    errores_por_tamiz = []
    tamices_ok = 0
    tamices_fuera = 0
    error_total = 0.0
    
    for i, (tamiz, pasante, min_val, max_val) in enumerate(
        zip(tamices, pasante_mezcla, banda_min, banda_max)
    ):
        # Clasificar estado
        if min_val <= pasante <= max_val:
            tipo = 'en_banda'
            error = 0.0
            deficit = 0.0
            exceso = 0.0
            tamices_ok += 1
        elif pasante < min_val:
            tipo = 'debajo_min'
            deficit = min_val - pasante  # POSITIVO: cuánto falta
            error = deficit
            exceso = 0.0
            tamices_fuera += 1
        else:  # pasante > max_val
            tipo = 'encima_max'
            exceso = pasante - max_val  # POSITIVO: cuánto sobra
            error = exceso
            deficit = 0.0
            tamices_fuera += 1
        
        errores_por_tamiz.append({
            'tamiz': tamiz,
            'pasante': round(pasante, 2),
            'lim_min': min_val,
            'lim_max': max_val,
            'error': round(error, 2),
            'tipo': tipo,
            'deficit': round(deficit, 2),
            'exceso': round(exceso, 2)
        })
        
        error_total += error
    
    return {
        'errores_por_tamiz': errores_por_tamiz,
        'tamices_ok': tamices_ok,
        'tamices_fuera': tamices_fuera,
        'error_total': round(error_total, 2)
    }


def analizar_error_por_zona(
    errores_por_tamiz: List[Dict],
    zonas: Dict[str, List[int]],
    tamices: List[float]
) -> Dict[str, Any]:
    """
    Agrega errores por zona (gruesos/medios/finos)
    
    Args:
        errores_por_tamiz: Lista de errores individuales
        zonas: Clasificación de zonas
        tamices: Nombres de tamices
    
    Returns:
        dict con análisis por zona:
        {
            'gruesos': {error_total, tamices_en_zona, ok, fuera, tamices_lista},
            'medios': {...},
            'finos': {...},
            'zona_critica': nombre de zona con mayor error,
            'concentracion_pct': porcentaje del error total en zona crítica
        }
    """
    errores_por_zona = {}
    
    for zona_nombre, indices in zonas.items():
        error_zona = 0.0
        ok_zona = 0
        fuera_zona = 0
        tamices_zona = []
        
        for idx in indices:
            if idx < len(errores_por_tamiz):
                e = errores_por_tamiz[idx]
                error_zona += e['error']
                tamices_zona.append(e['tamiz'])
                
                if e['tipo'] == 'en_banda':
                    ok_zona += 1
                else:
                    fuera_zona += 1
        
        errores_por_zona[zona_nombre] = {
            'error_total': round(error_zona, 2),
            'tamices_en_zona': len(tamices_zona),
            'tamices_ok': ok_zona,
            'tamices_fuera': fuera_zona,
            'tamices': tamices_zona
        }
    
    # Zona crítica: mayor error total
    zona_critica = max(
        errores_por_zona.keys(),
        key=lambda z: errores_por_zona[z]['error_total']
    )
    
    # Concentración del error en zona crítica
    error_total_sistema = sum(z['error_total'] for z in errores_por_zona.values())
    concentracion_pct = (
        (errores_por_zona[zona_critica]['error_total'] / error_total_sistema * 100)
        if error_total_sistema > 0 else 0
    )
    
    return {
        'errores_por_zona': errores_por_zona,
        'zona_critica': zona_critica,
        'concentracion_pct': round(concentracion_pct, 1)
    }


def generar_explicacion_residual(
    analisis_tamiz: Dict,
    analisis_zona: Dict,
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[float]
) -> str:
    """
    Genera explicación técnica clara del residual
    
    Formato:
    "No se puede cumplir la banda con las tablas actuales porque existe
     [DÉFICIT/EXCESO] en la zona [ZONA] (tamices [X, Y, Z]).
     Específicamente: [DETALLES POR TAMIZ]."
    
    Args:
        analisis_tamiz: Del análisis por tamiz
        analisis_zona: Del análisis por zona
        pasante_mezcla, banda_min, banda_max, tamices: Datos originales
    
    Returns:
        str con explicación técnica
    """
    zona_critica = analisis_zona['zona_critica']
    errores_zona = analisis_zona['errores_por_zona'][zona_critica]
    tamices_criticos = errores_zona['tamices']
    
    # Detectar tipo de problema (déficit o exceso)
    deficits = [e for e in analisis_tamiz['errores_por_tamiz'] if e['deficit'] > 0]
    excesos = [e for e in analisis_tamiz['errores_por_tamiz'] if e['exceso'] > 0]
    
    if deficits and not excesos:
        tipo_problema = "DÉFICIT"
        lista_problemas = deficits
    elif excesos and not deficits:
        tipo_problema = "EXCESO"
        lista_problemas = excesos
    else:
        tipo_problema = "MIXTO"
        lista_problemas = deficits + excesos
    
    # Construir lista de tamices críticos
    tamices_str = ", ".join([f"{t:.2f}mm" for t in tamices_criticos])
    
    # Detalles por tamiz
    detalles = []
    for e in lista_problemas:
        if e['deficit'] > 0:
            detalles.append(
                f"  • {e['tamiz']:.2f}mm: pasante {e['pasante']:.1f}% "
                f"(necesita mín {e['lim_min']:.1f}%, falta {e['deficit']:.1f}%)"
            )
        else:
            detalles.append(
                f"  • {e['tamiz']:.2f}mm: pasante {e['pasante']:.1f}% "
                f"(supera máx {e['lim_max']:.1f}%, sobra {e['exceso']:.1f}%)"
            )
    detalles_str = "\n".join(detalles)
    
    # Explicación final
    explicacion = (
        f"No se puede cumplir la banda con las tablas actuales porque existe "
        f"{tipo_problema} en la zona {zona_critica.upper()} (tamices: {tamices_str}).\n"
        f"Concretamente:\n"
        f"{detalles_str}\n"
        f"Error residual total en esta zona: {errores_zona['error_total']:.2f}%\n"
        f"La tabla virtual debe corregir estos puntos para lograr cumplimiento."
    )
    
    return explicacion


def diagnosticar_residual(
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[float]
) -> Dict[str, Any]:
    """
    FUNCIÓN PRINCIPAL - Diagnóstiza el error residual completo
    
    Entrada:
        pasante_mezcla: Pasante de mezcla optimizada
        banda_min: Límites inferiores
        banda_max: Límites superiores
        tamices: Tamaños de tamiz
    
    Salida:
        Diccionario estructurado con diagnóstico completo:
        {
            'error_por_tamiz': [
                {tamiz, pasante, lim_min, lim_max, error, tipo, deficit, exceso}
            ],
            'zonas': {
                'gruesos': {error_total, tamices_en_zona, ok, fuera, tamices},
                'medios': {...},
                'finos': {...}
            },
            'zona_critica': 'gruesos' | 'medios' | 'finos',
            'tamices_criticos': [x, y, z],
            'residual_total': float,
            'explicacion': "Texto técnico claro"
        }
    """
    # Paso 1: Clasificar zonas
    zonas = clasificar_zonas(tamices)
    
    # Paso 2: Analizar por tamiz
    analisis_tamiz = analizar_error_por_tamiz(
        pasante_mezcla, banda_min, banda_max, tamices
    )
    
    # Paso 3: Analizar por zona
    analisis_zona = analizar_error_por_zona(
        analisis_tamiz['errores_por_tamiz'],
        zonas,
        tamices
    )
    
    # Paso 4: Identificar tamices críticos
    tamices_criticos = analisis_zona['errores_por_zona'][
        analisis_zona['zona_critica']
    ]['tamices']
    
    # Paso 5: Generar explicación técnica
    explicacion = generar_explicacion_residual(
        analisis_tamiz,
        analisis_zona,
        pasante_mezcla,
        banda_min,
        banda_max,
        tamices
    )
    
    # Retornar diagnóstico estructurado
    return {
        'error_por_tamiz': analisis_tamiz['errores_por_tamiz'],
        'zonas': analisis_zona['errores_por_zona'],
        'zona_critica': analisis_zona['zona_critica'],
        'tamices_criticos': tamices_criticos,
        'residual_total': analisis_tamiz['error_total'],
        'tamices_ok': analisis_tamiz['tamices_ok'],
        'tamices_fuera': analisis_tamiz['tamices_fuera'],
        'concentracion_pct': analisis_zona['concentracion_pct'],
        'explicacion': explicacion
    }


# =====================================================================
# PARA TRAZABILIDAD EN CONSOLA (llamada desde nucleo_iteracion)
# =====================================================================

def imprimir_diagnostico_residual(diagnostico: Dict) -> None:
    """
    Imprime diagnóstico residual en formato legible para auditoría
    
    Args:
        diagnostico: Dict retornado por diagnosticar_residual()
    """
    print("\n" + "=" * 85)
    print("FASE 3 - DIAGNÓSTICO DEL ERROR RESIDUAL")
    print("=" * 85)
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Error total no corregible: {diagnostico['residual_total']:.2f}%")
    print(f"   • Tamices en banda: {diagnostico['tamices_ok']}/{diagnostico['tamices_ok'] + diagnostico['tamices_fuera']}")
    print(f"   • Zona crítica: {diagnostico['zona_critica'].upper()} ({diagnostico['concentracion_pct']:.1f}% del error)")
    
    print(f"\n🎯 TAMICES CRÍTICOS:")
    for e in diagnostico['error_por_tamiz']:
        if e['tipo'] != 'en_banda':
            if e['deficit'] > 0:
                print(f"   ✗ {e['tamiz']:.2f}mm: pasante {e['pasante']:.1f}% (BAJO, necesita {e['lim_min']:.1f}%, falta {e['deficit']:.1f}%)")
            else:
                print(f"   ✗ {e['tamiz']:.2f}mm: pasante {e['pasante']:.1f}% (ALTO, máx {e['lim_max']:.1f}%, sobra {e['exceso']:.1f}%)")
    
    print(f"\n📋 ANÁLISIS POR ZONA:")
    for zona_nombre, zona_data in diagnostico['zonas'].items():
        print(f"\n   {zona_nombre.upper()}:")
        print(f"      • Error total: {zona_data['error_total']:.2f}%")
        print(f"      • Tamices: {zona_data['tamices_ok']}/{zona_data['tamices_en_zona']} en banda")
        tamices_zona_str = ", ".join([f"{t:.2f}" for t in zona_data['tamices']])
        print(f"      • Tamaños: {tamices_zona_str}mm")
    
    print(f"\n💡 EXPLICACIÓN TÉCNICA:")
    for linea in diagnostico['explicacion'].split('\n'):
        print(f"   {linea}")
    
    print("\n" + "=" * 85)


if __name__ == '__main__':
    # TEST
    print("TEST: Diagnóstico de error residual")
    
    pasante_mezcla = [99.20, 76.60, 35.20, 12.40, 6.50, 4.70, 1.40]
    banda_min =      [95.0,  65.0,  35.0,  15.0,  5.0,  2.0,  0.0]
    banda_max =      [100.0, 90.0, 65.0,  45.0,  20.0, 10.0, 5.0]
    tamices =        [8.0,   5.0,  3.15,  2.0,   1.0,  0.5,  0.1]
    
    diagnostico = diagnosticar_residual(pasante_mezcla, banda_min, banda_max, tamices)
    
    print(f"\nResidual total: {diagnostico['residual_total']:.2f}%")
    print(f"Zona crítica: {diagnostico['zona_critica']}")
    print(f"Tamices críticos: {diagnostico['tamices_criticos']}")
    print(f"\nExplicación:\n{diagnostico['explicacion']}")
