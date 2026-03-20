#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST: Simular POST al endpoint granulometria_retido
Verificar que retorna divisiones_n_tablas en el JSON
"""

import sys
import json
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from flask import Flask, request
from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import granulometria_retido, calculoPorRetenidos

# Crear app Flask para testear
app = Flask(__name__)
app.register_blueprint(calculoPorRetenidos)

# Datos exactos del usuario
payload = {
    'tamices': [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.075],
    'materiales': [
        {
            'nombre': 'difusion 1',
            'proporcion_pct': 100,
            'retido_ind_pct': [0.8, 22.6, 41.4, 22.8, 5.9, 1.8, 1.4],
            'normalizar': False
        }
    ],
    'limites': {
        'bloco': {
            '12.5': [0, 0], '9.5': [0, 0], '6.3': [0, 15],
            '4.8': [0, 33], '2.4': [19, 51], '1.2': [37, 66],
            '0.6': [54, 78], '0.3': [68, 90], '0.15': [80, 97],
            '0.075': [90, 100], 'Fundo': [100, 100]
        },
        'paver': {
            '12.5': [0, 0], '9.5': [0, 0], '6.3': [0, 10],
            '4.8': [0, 22], '2.4': [19, 40], '1.2': [37, 61],
            '0.6': [54, 78], '0.3': [72, 92], '0.15': [85, 100],
            '0.075': [95, 100], 'Fundo': [100, 100]
        }
    },
    'debug': True
}

print("\n" + "=" * 100)
print("TEST: Llamada HTTP POST a /calculoPorRetenidos/granulometria/retido/?debug=1")
print("=" * 100)

with app.test_client() as client:
    response = client.post(
        '/calculoPorRetenidos/granulometria/retido/?debug=1',
        json=payload,
        content_type='application/json'
    )
    
    print(f"\n📡 STATUS: {response.status_code}")
    
    data = response.get_json()
    
    print("\n✅ RESPUESTA JSON (campos principales):")
    print(f"   - ok: {data.get('ok')}")
    print(f"   - tamices: {data.get('tamices')}")
    print(f"   - mix_acum: {data.get('mix_acum')}")
    print(f"   - sugerencia_division: {'SÍ' if data.get('sugerencia_division') else 'NO'}")
    print(f"   - sugerencia_optimizacion: {'SÍ' if data.get('sugerencia_optimizacion') else 'NO'}")
    
    # ===== MOSTRAR DIVISIONES EN N TABLAS =====
    divisiones = data.get('divisiones_n_tablas')
    
    if divisiones:
        print(f"\n{'='*100}")
        print(f"📊 DIVISIONES EN N TABLAS")
        print(f"{'='*100}")
        
        print(f"\n✓ Mejor opción: {divisiones['mejor_opcion']} TABLAS")
        print(f"  Cortes: {divisiones['cortes_recomendados']}")
        print(f"  Proporciones: {[f'{p*100:.1f}%' for p in divisiones['proporciones_optimas']]}")
        print(f"  Recomendación: {divisiones['recomendacion']}")
        
        print(f"\n📋 TABLAS RESULTANTES:")
        for i, tabla in enumerate(divisiones['tablas_resultantes'], 1):
            tamices_str = ', '.join([str(t) for t in tabla['tamices']])
            retido_str = ', '.join([f'{v:.1f}%' for v in tabla['retido_norm']])
            print(f"\n  Tabla {i}:")
            print(f"    Tamices: {tamices_str}")
            print(f"    Retido normalizado: [{retido_str}]")
        
        print(f"\n📈 CURVA RECONSTRUIDA:")
        for tamiz, val in zip(data['tamices'], divisiones['curva_reconstruida']):
            print(f"    {tamiz:>6}: {val:>6.2f}%")
        
        print(f"\n📊 COMPARATIVA (2, 3, 4, 5 TABLAS):")
        print(f"  {'N':<5} {'Cortes':<20} {'Score Físico':<16} {'Penalización':<15} {'TOTAL':<15} {'Band%':<10}")
        print(f"  {'-'*80}")
        for comp in divisiones['comparativa']:
            n = comp['n_partes']
            cortes = str(comp['cortes'])
            score = comp['score_fisico']
            penal = comp['penalizacion_complejidad']
            total = comp['score_total']
            band = comp['validacion_pct']
            marca = " ← MEJOR" if n == divisiones['mejor_opcion'] else ""
            print(f"  {n:<5} {cortes:<20} {score:<16.2f} {penal:<15} {total:<15.2f} {band:<9.1f}%{marca}")
        
        print(f"\n✅ DIVISIONES EN N TABLAS ESTÁN EN LA RESPUESTA JSON")
    else:
        print(f"\n❌ ERROR: divisiones_n_tablas NO está en la respuesta")

print("\n" + "=" * 100)
