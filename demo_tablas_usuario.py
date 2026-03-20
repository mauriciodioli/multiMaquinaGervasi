#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN CON DATOS EXACTOS DEL USUARIO
Material: difusion 1 (100%)
Tamices: [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.075]
Retido: [0.8, 22.6, 41.4, 22.8, 5.9, 1.8, 1.4]
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    comparar_divisiones
)

# DATOS EXACTOS DEL DEBUG
tamices = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.075]
retido_ind_pct = [0.8, 22.6, 41.4, 22.8, 5.9, 1.8, 1.4]

limites = {
    "bloco": {
        "9.5": [0, 0],
        "4.75": [0, 33],
        "2.36": [19, 51],
        "1.18": [37, 66],
        "0.6": [54, 78],
        "0.3": [68, 90],
        "0.075": [90, 100]
    }
}

def log_func(msg):
    print(f"  {msg}")

print("\n" + "=" * 100)
print("DEMOSTRACIÓN: DIVISIÓN DE CURVA EN 2, 3, 4, 5 TABLAS")
print("=" * 100)

print(f"\n📦 DATOS DE ENTRADA:")
print(f"   Material: difusion 1 (100%)")
print(f"   Tamices: {tamices}")
print(f"   Retido ind %: {retido_ind_pct}")
print(f"   Suma: {sum(retido_ind_pct):.1f}%")

# Ejecutar 4 corridas
resultados = {}

for n in [2, 3, 4, 5]:
    print(f"\n\n" + "=" * 100)
    print(f"CORRIDA {n}: DIVISIÓN EN {n} TABLAS")
    print("=" * 100)
    
    result = comparar_divisiones(
        tamices=tamices,
        retido_ind_pct=retido_ind_pct,
        limites=limites,
        opciones=[n],
        log=log_func
    )
    
    if result:
        resultados[n] = result
        comp = result['comparativa'][0]
        
        print(f"\n✅ RESULTADO {n} TABLAS:")
        print(f"   Cortes en índices: {result['cortes_recomendados']}")
        print(f"   Tamices de corte: ", end="")
        for idx in result['cortes_recomendados']:
            print(f"{tamices[idx]}mm", end=" ")
        print()
        
        print(f"\n   ⚖️  PROPORCIONES OPTIMIZADAS:")
        for i, prop in enumerate(result['proporciones_optimas'], 1):
            print(f"      Tabla {i}: {prop*100:>6.1f}%")
        
        print(f"\n   📊 TABLAS RESULTANTES:")
        
        for i, tabla in enumerate(result['tablas_resultantes'], 1):
            inicio = tabla['inicio']
            fin = tabla['fin']
            t_range = [str(t) for t in tamices[inicio:fin]]
            
            print(f"\n      ┌─ TABLA {i} ─────────────────────────────────┐")
            print(f"      │ Tamices: {', '.join(t_range)}")
            print(f"      │ Retido norm. (a 100%): {[f'{v:.1f}%' for v in tabla['retido_norm']]}")
            print(f"      │ Proporción en mezcla: {result['proporciones_optimas'][i-1]*100:.1f}%")
            print(f"      └────────────────────────────────────────────┘")
        
        print(f"\n   📈 CURVA RECONSTRUIDA (MIX FINAL):")
        print(f"      {'Tamiz':<10} {'MIX %':<10} {'Banda':<15} {'Status':<10}")
        print(f"      {'-'*45}")
        for tamiz, val in zip(tamices, result['curva_reconstruida']):
            banda = limites['bloco'].get(str(tamiz), [0, 100])
            lo, hi = banda[0], banda[1]
            marker = "✓" if lo <= val <= hi else "×"
            print(f"      {tamiz:<10.2f} {val:<10.2f} [{lo:>3.0f}-{hi:<3.0f}]     {marker:<10}")
        
        print(f"\n   🎯 EVALUACIÓN:")
        print(f"      Score físico:          {comp['score_fisico']:>10.2f}")
        print(f"      Penalización complejidad: +{comp['penalizacion_complejidad']:>6}")
        print(f"      ─────────────────────────────────────")
        print(f"      SCORE TOTAL:           {comp['score_total']:>10.2f}")
        print(f"      Validación en banda:   {comp['validacion_pct']:>9.1f}%")
    else:
        print(f"   ❌ NO CONVERGE para {n} tablas")

# Comparativa final
print(f"\n\n" + "=" * 100)
print("COMPARATIVA FINAL: CUÁL ES LA MEJOR OPCIÓN")
print("=" * 100)

print(f"\n   {'N':<5} {'Cortes':<20} {'Proporciones':<30} {'Score Total':<15} {'Band%':<10}")
print(f"   {'-'*80}")

mejor_n = None
mejor_score = float('inf')

for n in [2, 3, 4, 5]:
    if n in resultados:
        result = resultados[n]
        comp = result['comparativa'][0]
        
        cortes_str = str(result['cortes_recomendados'])
        props_str = ' / '.join([f"{p*100:.0f}%" for p in result['proporciones_optimas']])
        
        marca = "  ← RECOMENDADO" if comp['score_total'] < mejor_score else ""
        
        print(f"   {n:<5} {cortes_str:<20} {props_str:<30} {comp['score_total']:<15.2f} "
              f"{comp['validacion_pct']:<10.1f}%{marca}")
        
        if comp['score_total'] < mejor_score:
            mejor_score = comp['score_total']
            mejor_n = n

print(f"   {'-'*80}")

if mejor_n:
    result = resultados[mejor_n]
    print(f"\n✅ RECOMENDACIÓN: {mejor_n} TABLAS es la mejor opción")
    print(f"   Score total mínimo: {mejor_score:.2f}")
    print(f"   Cortes: {result['cortes_recomendados']}")
    print(f"   Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")

print("\n" + "=" * 100)
print("✅ FIN DE LA DEMOSTRACIÓN")
print("=" * 100)
