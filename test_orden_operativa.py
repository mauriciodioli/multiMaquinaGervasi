#!/usr/bin/env python3
"""
Test script para ver el JSON de salida con orden_operativa
"""

import json
import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi/src')

from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import generar_orden_operativa

# ===== TEST 1: Datos de ejemplo con materiales =====
print("\n" + "="*80)
print("TEST 1: Generando orden_operativa con materiales de ejemplo")
print("="*80 + "\n")

materiales_test = [
    {
        "nombre": "Material A",
        "retido_ind_pct": [45.2, 38.1, 12.5, 3.2, 1.0],  # max_index=0 → grueso
        "proporcion_pct": 45.5
    },
    {
        "nombre": "Material B", 
        "retido_ind_pct": [5.1, 15.2, 65.3, 12.1, 2.3],  # max_index=2 → grueso/medio
        "proporcion_pct": 30.0
    },
    {
        "nombre": "Material C",
        "retido_ind_pct": [2.1, 5.2, 8.3, 12.1, 72.3],  # max_index=4 → medio/fino
        "proporcion_pct": 24.5
    }
]

orden = generar_orden_operativa(materiales_test)

print("📋 ORDEN OPERATIVA GENERADA:")
print(json.dumps(orden, indent=2, ensure_ascii=False))

# ===== TEST 2: Simulación de respuesta completa =====
print("\n" + "="*80)
print("TEST 2: Simulación de respuesta JSON completa del endpoint")
print("="*80 + "\n")

respuesta_json = {
    "exito": True,
    "data": {
        "fase_1": {
            "cumpl_count": 6,
            "n_tamices": 8,
            "cumplimiento_pct": 75.0,
            "error_total": -15.3,
            "estado": "DENTRO_DE_BANDA"
        },
        "fase_2_4_criterios": {
            "cumple_banda": True,
            "es_buena_calidad": True
        },
        "propuesta_agregados_correctivos": {
            "exito": True,
            "acciones_zaranda": [
                "GRUESO: Re-zarandear por malla media (2.4–1.2 mm) y reducir uso",
                "MEDIO: Re-zarandear por malla fina (0.6–0.3 mm)",
                "FINO: Aumentar proporción (generar desde medio si es necesario)"
            ],
            "proporciones": [0.455, 0.300, 0.245],
            "propuesta": {
                "m1": {
                    "nombre": "Material A",
                    "retido_ind_pct": [45.2, 38.1, 12.5, 3.2, 1.0]
                },
                "m2": {
                    "nombre": "Material B",
                    "retido_ind_pct": [5.1, 15.2, 65.3, 12.1, 2.3]
                },
                "m3": {
                    "nombre": "Material C",
                    "retido_ind_pct": [2.1, 5.2, 8.3, 12.1, 72.3]
                }
            }
        },
        "orden_operativa": orden,
        "para_grafico": {
            "tamices": [12.5, 9.5, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15],
            "banda_min": [0, 85, 50, 20, 10, 5, 2, 0],
            "banda_max": [0, 100, 90, 50, 30, 15, 8, 0],
            "pasante_real": [100, 98.5, 78.2, 45.1, 25.3, 12.1, 5.3, 1.2]
        }
    }
}

print("✅ RESPUESTA JSON COMPLETA (bien formateada):")
print(json.dumps(respuesta_json, indent=2, ensure_ascii=False))

# ===== TEST 3: Mostrar solo orden_operativa =====
print("\n" + "="*80)
print("TEST 3: SOLO orden_operativa extraída")
print("="*80 + "\n")

if respuesta_json["data"].get("orden_operativa"):
    print("📌 Orden Operativa:")
    for paso in respuesta_json["data"]["orden_operativa"]:
        print(f"\n  Paso {paso['paso']}: {paso['material']}")
        print(f"    Tipo: {paso['tipo'].upper()}")
        print(f"    Proporción: {paso['proporcion_pct']}%")
        print(f"    Acción: {paso['accion']}")
        if paso['malla']:
            print(f"    Malla: {paso['malla']}")
        print(f"    Resultado: {paso['resultado']}")
        print(f"    Uso: {paso['uso']}")

print("\n" + "="*80)
print("✅ TEST COMPLETADO")
print("="*80 + "\n")
