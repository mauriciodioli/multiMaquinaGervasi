#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCRIPT DE PRUEBA FINAL
Ejecuta 4 corridas consecutivas: 2, 3, 4, 5 tablas
Datos del ejemplo debug: difusion 1, 2, 3 con proporciones [23%, 42%, 35%]

MISMO EXCEL DE ENTRADA → 4 corridas diferentes → elegir mejor opción
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    comparar_divisiones
)
import json
from datetime import datetime

# ============================================================================
# DATOS DEL EJEMPLO (del debug que pasaste)
# ============================================================================

tamices = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.075]

# Retido individual % de "excel misma entrada"
retido_ind_pct = [0.8, 23.0, 65.0, 87.7, 93.5, 95.3, 100.0]  # ACUMULADO
# Mejor: individual
retido_ind_pct_individual = [0.8, 22.2, 42.0, 22.7, 5.8, 1.8, 4.7]

limites = {
    "bloco": {
        "12.5": [0, 0],
        "9.5": [0, 0],
        "6.3": [0, 15],
        "4.8": [0, 33],
        "2.4": [19, 51],
        "1.2": [37, 66],
        "0.6": [54, 78],
        "0.3": [68, 90],
        "0.15": [80, 97],
        "0.075": [90, 100]
    },
    "paver": {
        "12.5": [0, 0],
        "9.5": [0, 0],
        "6.3": [0, 10],
        "4.8": [0, 22],
        "2.4": [19, 40],
        "1.2": [37, 61],
        "0.6": [54, 78],
        "0.3": [72, 92],
        "0.15": [85, 100],
        "0.075": [95, 100]
    }
}

def log_func(msg):
    """Logger simple"""
    print(f"  {msg}")

# ============================================================================
# EJECUTAR 4 CORRIDAS
# ============================================================================

resultados_todos = {}

for n_partes in [2, 3, 4, 5]:
    print("\n" + "=" * 90)
    print(f"CORRIDA {n_partes}: Evaluando división en {n_partes} TABLAS")
    print("=" * 90)
    
    result = comparar_divisiones(
        tamices=tamices,
        retido_ind_pct=retido_ind_pct_individual,
        limites=limites,
        opciones=[n_partes],  # Solo evaluar esta N
        log=log_func
    )
    
    if result:
        resultados_todos[n_partes] = result
        
        print(f"\n✓ RESULTADO {n_partes} TABLAS:")
        print(f"  Cortes (índices): {result['cortes_recomendados']}")
        print(f"  Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")
        
        # Mostrar score
        comp = result['comparativa'][0]
        print(f"  Score físico: {comp['score_fisico']:.2f}")
        print(f"  Penalización complejidad: +{comp['penalizacion_complejidad']}")
        print(f"  SCORE TOTAL: {comp['score_total']:.2f}")
        print(f"  Validación: {comp['validacion_pct']:.1f}% dentro de banda")
        
        # Mostrar recomendación
        print(f"\n  📝 Recomendación:")
        print(f"     {result['recomendacion']}")
    else:
        print(f"❌ Error en corrida {n_partes}")

# ============================================================================
# COMPARATIVA FINAL
# ============================================================================

print("\n\n" + "=" * 90)
print("COMPARATIVA FINAL: 2 vs 3 vs 4 vs 5 TABLAS")
print("=" * 90)

print(f"\n{'N Tablas':<12} {'Score Físico':<18} {'Penalización':<15} {'SCORE TOTAL':<15} {'Band%':<10}")
print("-" * 90)

mejor_total = None
mejor_score = float('inf')

all_comparativas = []

for n in [2, 3, 4, 5]:
    if n in resultados_todos:
        result = resultados_todos[n]
        comp = result['comparativa'][0]
        
        print(f"{n:<12} {comp['score_fisico']:<18.2f} {comp['penalizacion_complejidad']:<15} "
              f"{comp['score_total']:<15.2f} {comp['validacion_pct']:<10.1f}%")
        
        all_comparativas.append({
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
    print(f"\n✅ MEJOR OPCIÓN: {mejor_total} TABLAS")
    result = resultados_todos[mejor_total]
    print(f"   Cortes: {result['cortes_recomendados']}")
    print(f"   Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")
    print(f"   Score total: {mejor_score:.2f}")

# ============================================================================
# GUARDAR RESULTADOS EN JSON
# ============================================================================

output_file = '/tmp/resultados_divisiones.json'
with open(output_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'comparativa': all_comparativas,
        'mejor_opcion': mejor_total,
        'mejor_score': float(mejor_score)
    }, f, indent=2)

print(f"\n✅ Resultados guardados en: {output_file}")

# ============================================================================
# MENÚ INTERACTIVO PARA ELEGIR Y VER DETALLES
# ============================================================================

print("\n" + "=" * 90)
print("MENÚ INTERACTIVO")
print("=" * 90)

while True:
    print("\nOpciones:")
    print("  1-5: Ver detalles de N tablas")
    print("  0: Salir")
    
    choice = input("\nElige opción (0, 2, 3, 4, 5): ").strip()
    
    if choice == '0':
        print("✅ Hasta luego!")
        break
    
    n = int(choice) if choice.isdigit() else None
    
    if n not in [2, 3, 4, 5]:
        print("❌ Opción inválida")
        continue
    
    if n not in resultados_todos:
        print(f"❌ No hay resultado para {n} tablas")
        continue
    
    result = resultados_todos[n]
    
    print(f"\n{' ' * 30}DETALLES {n} TABLAS{' ' * 30}")
    print("=" * 90)
    
    print(f"\n📊 ESTRUCTURA:")
    print(f"  Cortes (índices de tamices): {result['cortes_recomendados']}")
    print(f"  Número de tablas: {n}")
    
    print(f"\n📈 PROPORCIONES OPTIMIZADAS:")
    for i, prop in enumerate(result['proporciones_optimas'], 1):
        print(f"  Tabla {i}: {prop*100:.2f}%")
    
    print(f"\n📋 TABLAS RESULTANTES:")
    for i, tabla in enumerate(result['tablas_resultantes'], 1):
        print(f"\n  Tabla {i}:")
        print(f"    Inicio (índice): {tabla['inicio']}")
        print(f"    Fin (índice): {tabla['fin']}")
        print(f"    Tamices: {[tamices[j] for j in range(tabla['inicio'], tabla['fin'])]}")
        print(f"    Retido normalizado: {[f'{v:.2f}%' for v in tabla['retido_norm'][:3]]}...")
    
    print(f"\n🎯 CURVA RECONSTRUIDA (MIX):")
    for i, (tamiz, val) in enumerate(zip(tamices, result['curva_reconstruida'])):
        banda = limites['bloco'][str(tamiz)] if str(tamiz) in limites['bloco'] else [0, 100]
        marker = "✓" if banda[0] <= val <= banda[1] else "×"
        print(f"  {tamiz:>6} mm: {val:>6.2f}% {marker} [{banda[0]}-{banda[1]}]")
    
    print(f"\n📊 EVALUACIÓN:")
    comp = result['comparativa'][0]
    print(f"  Score físico: {comp['score_fisico']:.2f}")
    print(f"  Penalización complejidad: +{comp['penalizacion_complejidad']}")
    print(f"  Score total: {comp['score_total']:.2f}")
    print(f"  Validación: {comp['validacion_pct']:.1f}% dentro de banda")
    
    print(f"\n💡 RECOMENDACIÓN:")
    print(f"  {result['recomendacion']}")

print("\n✅ FIN DEL SCRIPT")
