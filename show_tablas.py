#!/usr/bin/env python
import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')
from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import comparar_divisiones

tamices = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.075]
retido_ind_pct = [0.8, 22.6, 41.4, 22.8, 5.9, 1.8, 1.4]
limites = {"bloco": {"9.5": [0, 0], "4.75": [0, 33], "2.36": [19, 51], "1.18": [37, 66], "0.6": [54, 78], "0.3": [68, 90], "0.075": [90, 100]}}

print("\n" + "█" * 100)
print("█ DIVISIÓN DE CURVA ORIGINAL EN N TABLAS (2, 3, 4, 5)")
print("█" * 100)
print(f"\n  Tamices: {tamices}")
print(f"  Retido ind %: {retido_ind_pct}")
print(f"  Suma: {sum(retido_ind_pct):.1f}%")

resultados = {}
for n in [2, 3, 4, 5]:
    result = comparar_divisiones(tamices, retido_ind_pct, limites, [n], lambda x: None)
    if result:
        resultados[n] = result

# MOSTRAR 4 OPCIONES
print("\n" + "█" * 100)
for n in [2, 3, 4, 5]:
    if n not in resultados:
        print(f"█\n█ OPCIÓN {n}: NO CONVERGE\n█")
        continue
    
    result = resultados[n]
    comp = result['comparativa'][0]
    
    print(f"█\n█ ┌─ OPCIÓN {n} TABLAS ─────────────────────────────────────────────────────────────────┐")
    print(f"█ │")
    print(f"█ │  CORTES: {result['cortes_recomendados']} → Tamices: {[tamices[i] for i in result['cortes_recomendados']]}")
    print(f"█ │")
    
    print(f"█ │  ESTRUCTURA DE TABLAS:")
    for i, tabla in enumerate(result['tablas_resultantes'], 1):
        inicio, fin = tabla['inicio'], tabla['fin']
        t_list = [str(t) for t in tamices[inicio:fin]]
        retido_str = '[' + ', '.join([f'{v:.1f}%' for v in tabla['retido_norm']]) + ']'
        print(f"█ │    Tabla {i}: {', '.join(t_list):<30} → Retido normalizado: {retido_str}")
    
    print(f"█ │")
    print(f"█ │  PROPORCIONES OPTIMIZADAS:")
    props_str = ' + '.join([f'{p*100:.1f}%' for p in result['proporciones_optimas']])
    print(f"█ │    {props_str}")
    
    print(f"█ │")
    print(f"█ │  EVALUACIÓN:")
    print(f"█ │    • Score físico:      {comp['score_fisico']:>10.2f}")
    print(f"█ │    • Penalización:      +{comp['penalizacion_complejidad']:>9}")
    print(f"█ │    • SCORE TOTAL:       {comp['score_total']:>10.2f}")
    print(f"█ │    • Validación banda:  {comp['validacion_pct']:>9.1f}%")
    print(f"█ │")
    print(f"█ └──────────────────────────────────────────────────────────────────────────────────────┘")

# COMPARATIVA Y RECOMENDACIÓN
print(f"\n█" + "─" * 98 + "█")
print(f"█ COMPARATIVA Y RECOMENDACIÓN")
print(f"█" + "─" * 98 + "█")

mejor = min(resultados.items(), key=lambda x: x[1]['comparativa'][0]['score_total'])[0] if resultados else None

print(f"█")
print(f"█  {'N':<5} │ {'Proporciones':<25} │ {'Score':<12} │ {'Band%':<8} │ Status")
print(f"█  {'-'*5}-+-{'-'*25}-+-{'-'*12}-+-{'-'*8}-+-{'-'*20}")

for n in [2, 3, 4, 5]:
    if n in resultados:
        comp = resultados[n]['comparativa'][0]
        props = ' + '.join([f"{p*100:.0f}%" for p in resultados[n]['proporciones_optimas']])
        marca = "✅ RECOMENDADO" if n == mejor else ""
        print(f"█  {n:<5} │ {props:<25} │ {comp['score_total']:>10.2f} │ {comp['validacion_pct']:>6.1f}% │ {marca}")

print(f"█")
print(f"█" + "█" * 98)

if mejor:
    result = resultados[mejor]
    print(f"\n✅ MEJOR OPCIÓN: {mejor} TABLAS")
    print(f"   Cortes: {result['cortes_recomendados']}")
    print(f"   Proporciones: {[f'{p*100:.1f}%' for p in result['proporciones_optimas']]}")
    print(f"   Score total: {result['comparativa'][0]['score_total']:.2f}")
