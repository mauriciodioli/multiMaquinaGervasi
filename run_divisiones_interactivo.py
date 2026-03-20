#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCRIPT COMPLETO CON DATOS REALISTAS
Ejecuta 4 corridas → Menú interactivo para explorar detalles
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    comparar_divisiones
)
import json
from datetime import datetime

# ============================================================================
# DATOS MÁS REALISTAS (agregado típico de planta)
# ============================================================================

tamices = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075]

# Retido individual % más realista (curva típica de material)
retido_ind_pct = [
    2.5,    # 12.5
    8.5,    # 9.5
    12.3,   # 6.3
    15.2,   # 4.8
    18.4,   # 2.4
    16.8,   # 1.2
    12.5,   # 0.6
    7.3,    # 0.3
    4.2,    # 0.15
    2.3     # 0.075
]

limites = {
    "bloco": {
        "12.5": [0, 3],
        "9.5": [3, 12],
        "6.3": [12, 27],
        "4.8": [27, 42],
        "2.4": [42, 60],
        "1.2": [60, 77],
        "0.6": [77, 89],
        "0.3": [89, 96],
        "0.15": [96, 99],
        "0.075": [99, 100]
    }
}

def log_func(msg):
    """Logger"""
    print(f"  {msg}")

# ============================================================================
# CORRIDAS
# ============================================================================

print("\n" + "=" * 90)
print("EJECUCIÓN: 4 CORRIDAS AUTOMÁTICAS (2, 3, 4, 5 TABLAS)")
print("=" * 90)
print(f"\nDatos de entrada:")
print(f"  Tamices: {tamices}")
print(f"  Retido %: {retido_ind_pct}")
print(f"  Suma: {sum(retido_ind_pct):.1f}%")

resultados_todos = {}

for n_partes in [2, 3, 4, 5]:
    print("\n" + "-" * 90)
    print(f"CORRIDA {n_partes}: {n_partes} TABLAS")
    print("-" * 90)
    
    result = comparar_divisiones(
        tamices=tamices,
        retido_ind_pct=retido_ind_pct,
        limites=limites,
        opciones=[n_partes],
        log=log_func
    )
    
    if result:
        resultados_todos[n_partes] = result
        
        comp = result['comparativa'][0]
        print(f"\n✓ RESULTADO {n_partes} TABLAS:")
        print(f"  Cortes (índices): {result['cortes_recomendados']}")
        print(f"  Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")
        print(f"  Score físico: {comp['score_fisico']:.2f}")
        print(f"  + Penalización complejidad: +{comp['penalizacion_complejidad']}")
        print(f"  = SCORE TOTAL: {comp['score_total']:.2f}")
        print(f"  Validación: {comp['validacion_pct']:.1f}% dentro de banda")

# ============================================================================
# TABLA COMPARATIVA
# ============================================================================

print("\n\n" + "=" * 90)
print("COMPARATIVA FINAL")
print("=" * 90)

print(f"\n{'N Tablas':<12} {'Score Físico':<18} {'Penalizac.':<15} {'TOTAL':<15} {'Band%':<10}")
print("-" * 90)

mejor_total = None
mejor_score = float('inf')
todas_comparativas = []

for n in [2, 3, 4, 5]:
    if n in resultados_todos:
        result = resultados_todos[n]
        comp = result['comparativa'][0]
        
        marca = " ← RECOMENDADO" if comp['score_total'] < mejor_score else ""
        print(f"{n:<12} {comp['score_fisico']:<18.2f} {comp['penalizacion_complejidad']:<15} "
              f"{comp['score_total']:<15.2f} {comp['validacion_pct']:<10.1f}%{marca}")
        
        todas_comparativas.append({
            'n': n,
            'score_total': comp['score_total'],
            'cortes': result['cortes_recomendados'],
            'proporciones': result['proporciones_optimas'],
            'validacion_pct': comp['validacion_pct']
        })
        
        if comp['score_total'] < mejor_score:
            mejor_score = comp['score_total']
            mejor_total = n

print("-" * 90)

if mejor_total:
    result = resultados_todos[mejor_total]
    print(f"\n✅ MEJOR OPCIÓN: {mejor_total} TABLAS")
    print(f"   Cortes: {result['cortes_recomendados']}")
    print(f"   Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")
    print(f"   Score total: {mejor_score:.2f}")

# ============================================================================
# GUARDAR RESULTADOS
# ============================================================================

output_file = '/tmp/resultados_divisiones.json'
with open(output_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'datos_entrada': {
            'tamices': tamices,
            'retido_ind_pct': retido_ind_pct,
            'suma': sum(retido_ind_pct)
        },
        'comparativa': todas_comparativas,
        'mejor_opcion': mejor_total
    }, f, indent=2)

print(f"\n✅ Resultados guardados en: {output_file}")

# ============================================================================
# MENÚ INTERACTIVO
# ============================================================================

print("\n" + "=" * 90)
print("MENÚ INTERACTIVO: EXPLORAR DETALLES DE CADA OPCIÓN")
print("=" * 90)

while True:
    print("\nEscoge una opción:")
    print("  2 - Ver detalles de 2 TABLAS")
    print("  3 - Ver detalles de 3 TABLAS")
    print("  4 - Ver detalles de 4 TABLAS")
    print("  5 - Ver detalles de 5 TABLAS")
    print("  0 - Salir")
    
    choice = input("\nOpción (0-5): ").strip()
    
    if choice == '0':
        print("\n✅ Hasta luego!")
        break
    
    try:
        n = int(choice)
    except:
        print("❌ Por favor ingresa un número")
        continue
    
    if n not in [2, 3, 4, 5]:
        print("❌ Opción inválida")
        continue
    
    if n not in resultados_todos:
        print(f"❌ No hay resultado para {n} tablas (no converge con estos datos)")
        continue
    
    result = resultados_todos[n]
    comp = result['comparativa'][0]
    
    print(f"\n" + "=" * 90)
    print(f"DETALLES: {n} TABLAS")
    print("=" * 90)
    
    print(f"\n📍 UBICACIÓN DE CORTES:")
    print(f"  Índices: {result['cortes_recomendados']}")
    print(f"  Tamices de corte:")
    for idx in result['cortes_recomendados']:
        print(f"    - Índice {idx}: {tamices[idx]}mm")
    
    print(f"\n⚖️  PROPORCIONES OPTIMIZADAS:")
    for i, prop in enumerate(result['proporciones_optimas'], 1):
        print(f"  Tabla {i}: {prop*100:.2f}%")
    
    print(f"\n📊 ESTRUCTURA DE TABLAS:")
    for i, tabla in enumerate(result['tablas_resultantes'], 1):
        inicio = tabla['inicio']
        fin = tabla['fin']
        t_sieves = [str(t) for t in tamices[inicio:fin]]
        print(f"\n  Tabla {i}:")
        print(f"    Índices: {inicio}-{fin}")
        print(f"    Tamices: {t_sieves}")
        print(f"    Retido norm.: {[f'{v:.1f}%' for v in tabla['retido_norm'][:5]]}..." 
              if len(tabla['retido_norm']) > 5 else f"    Retido norm.: {[f'{v:.1f}%' for v in tabla['retido_norm']]}")
    
    print(f"\n📈 CURVA RECONSTRUIDA (MIX):")
    print(f"  {'Tamiz':<10} {'MIX %':<10} {'Rango':<15} {'Status':<10}")
    print("  " + "-" * 45)
    for tamiz, val in zip(tamices, result['curva_reconstruida']):
        banda = limites['bloco'].get(str(tamiz), [0, 100])
        lo, hi = banda[0], banda[1]
        marker = "✓" if lo <= val <= hi else "×"
        print(f"  {tamiz:<10.2f} {val:<10.2f} [{lo:>3.0f}-{hi:<3.0f}]    {marker:<10}")
    
    print(f"\n📋 EVALUACIÓN:")
    print(f"  Score físico:              {comp['score_fisico']:.2f}")
    print(f"  Penalización complejidad:  +{comp['penalizacion_complejidad']}")
    print(f"  ─────────────────────────────────────")
    print(f"  SCORE TOTAL:               {comp['score_total']:.2f}")
    print(f"  Validación (dentro banda): {comp['validacion_pct']:.1f}%")
    
    print(f"\n🎯 RECOMENDACIÓN:")
    print(f"  {result['recomendacion']}")

print("\n✅ FIN DEL PROGRAMA")
