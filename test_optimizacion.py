#!/usr/bin/env python3
"""
Test de optimización de proporciones para múltiples materiales
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    optimizar_proporciones_materiales,
    generar_instruccion_receta
)

# Datos de ejemplo: 3 materiales
materiales = [
    {
        'nombre': 'Agregado 1',
        'pasantes': [0.0, 5.8, 47.3, 80.5, 100.0, 100.0, 100.0, 100.0]
    },
    {
        'nombre': 'Agregado 2',
        'pasantes': [-0.0, -0.0, -0.0, 2.2, 39.8, 64.7, 79.9, 90.6]
    },
    {
        'nombre': 'Agregado 3',
        'pasantes': [0.0, 0.0, 0.0, 0.9, 8.3, 17.3, 43.6, 90.9]
    }
]

# Bandas Paver para Brasil
banda_min = [0, 0, 0, 19, 37, 54, 72, 85]
banda_max = [0, 10, 22, 40, 61, 78, 92, 100]
tamices = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15]

print("🔧 Optimizando proporciones de 3 agregados...")
print(f"Tamices: {tamices}")
print(f"Banda Min: {banda_min}")
print(f"Banda Max: {banda_max}")
print()

# Llamar optimización
mezcla_opt, proporciones = optimizar_proporciones_materiales(
    materiales=materiales,
    banda_min=banda_min,
    banda_max=banda_max,
    tamices=tamices
)

if mezcla_opt and proporciones:
    print("✅ Optimización exitosa!")
    print("\n📊 Mezcla optimizada (Pasantes):")
    for t, p in zip(tamices, mezcla_opt):
        print(f"  {t:>4} mm: {p:>6.2f}%")
    
    print("\n📋 Proporciones:")
    for nombre, pct in sorted(proporciones.items(), key=lambda x: -x[1] if isinstance(x[1], (int, float)) else 0):
        if nombre != 'total_pct':
            print(f"  {nombre}: {pct}%")
    print(f"  TOTAL: {proporciones['total_pct']}%")
    
    print("\n📝 Instrucción para operador:")
    instruccion = generar_instruccion_receta(proporciones)
    print(f"  {instruccion}")
else:
    print("❌ Optimización falló")
