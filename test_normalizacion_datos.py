#!/usr/bin/env python3
"""
Test de validación: Sistema de normalización de datos granulométricos
Verifica que el endpoint acepte correctamente:
- retido_ind_pct (formato legacy)
- retido_acum_pct 
- pasante_pct
- datos en escala 0-1 o 0-100
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:5000"

def test_caso(nombre, payload, esperado_ok=True):
    """
    Ejecuta un caso de test
    
    Args:
        nombre: Descripción del caso
        payload: JSON a enviar
        esperado_ok: True si se espera respuesta exitosa
    """
    print(f"\n{'='*80}")
    print(f"📋 TEST: {nombre}")
    print(f"{'='*80}")
    
    # Mostrar payload simplificado
    print(f"\n📤 Payload:")
    print(f"  - Tamices: {payload.get('tamices')}")
    print(f"  - Material: {payload['materiales'][0].get('nombre')}")
    print(f"  - Formato datos: {payload['materiales'][0].get('retido_ind_pct', payload['materiales'][0].get('retido_acum_pct', payload['materiales'][0].get('pasante_pct')))[:3]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/calculoPorRetenidos/granulometria/retido/?debug=1",
            json=payload,
            timeout=10
        )
        
        status = response.status_code
        result = response.json() if response.status_code == 200 else None
        
        # Validar resultado
        if esperado_ok:
            if status == 200 and result and result.get('ok'):
                print(f"\n✅ EXITOSO (HTTP {status})")
                print(f"  - MIX PASANTE: {result.get('mix_pasante', [])[:3]}...")
                print(f"  - Módulo de finura: {result.get('modulo_finura')}")
                print(f"  - Validación bloco: {[('✓' if d.get('ok') else '×') for d in result.get('faixas', {}).get('bloco', [])]}")
                return True
            else:
                print(f"\n❌ FALLÓ (HTTP {status})")
                if result:
                    print(f"  Error: {result.get('error', 'unknown')}")
                return False
        else:
            if status != 200:
                print(f"\n✅ RECHAZADO CORRECTAMENTE (HTTP {status})")
                return True
            else:
                print(f"\n❌ DEBERÍA FALLAR PERO PASÓ")
                return False
    
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        return False


# ================================================================================
# CASOS DE TEST
# ================================================================================

TAMICES = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15]
LIMITES = {
    "bloco": {
        "9.5": [0, 15],
        "6.3": [0, 33],
        "4.8": [19, 51],
        "2.4": [37, 66],
        "1.2": [54, 78],
        "0.6": [68, 90],
        "0.3": [80, 97],
        "0.15": [90, 100],
    }
}

resultados = {}

# CASO 1: Legacy - Retenido Individual (suma ≈ 100)
resultados["CASO 1: Retenido Individual"] = test_caso(
    "Retenido Individual (suma ≈ 100)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Arena fina",
                "proporcion_pct": 100,
                "retido_ind_pct": [1.4, 9.8, 5.1, 20.2, 12.4, 22.7, 12.0, 16.4],
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 2: Retenido Acumulado (creciente, último ≈100)
resultados["CASO 2: Retenido Acumulado"] = test_caso(
    "Retenido Acumulado (creciente → será convertido a individual)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Arena media",
                "proporcion_pct": 100,
                "retido_ind_pct": [1.4, 11.2, 16.3, 36.5, 48.9, 71.6, 83.6, 100.0],  # acumulado
                "formato": "ret_acum",  # Forzar interpretación
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 3: Pasante Acumulado (decreciente, primero ≈100)
resultados["CASO 3: Pasante Acumulado"] = test_caso(
    "Pasante Acumulado (decreciente → será convertido a individual)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Arena gruesa",
                "proporcion_pct": 100,
                "retido_ind_pct": [98.6, 88.8, 83.7, 63.5, 51.1, 28.4, 16.4, 0.0],  # pasante
                "formato": "pasante",  # Forzar interpretación
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 4: Escala 0-1 (será multiplicado por 100)
resultados["CASO 4: Escala 0-1"] = test_caso(
    "Datos en escala 0-1 (será normalizado a 0-100)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Arena escala 0-1",
                "proporcion_pct": 100,
                "retido_ind_pct": [0.014, 0.098, 0.051, 0.202, 0.124, 0.227, 0.120, 0.164],
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 5: Pasante en escala 0-1
resultados["CASO 5: Pasante escala 0-1"] = test_caso(
    "Pasante en escala 0-1 (será normalizado a 0-100)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Pasante escala 0-1",
                "proporcion_pct": 100,
                "retido_ind_pct": [0.986, 0.888, 0.837, 0.635, 0.511, 0.284, 0.164, 0.0],
                "formato": "pasante",
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 6: 3 materiales (mix) con diferentes formatos
resultados["CASO 6: Mix de 3 materiales"] = test_caso(
    "Mix de 3 materiales con formatos mixtos",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "M1 - Retenido Ind",
                "proporcion_pct": 33.3,
                "retido_ind_pct": [0.5, 5.0, 3.0, 15.0, 15.0, 25.0, 20.0, 16.5],
                "normalizar": False
            },
            {
                "nombre": "M2 - Retenido Acum",
                "proporcion_pct": 33.3,
                "retido_ind_pct": [2.0, 12.0, 18.0, 38.0, 50.0, 72.0, 84.0, 100.0],
                "formato": "ret_acum",
                "normalizar": False
            },
            {
                "nombre": "M3 - Pasante",
                "proporcion_pct": 33.4,
                "retido_ind_pct": [95.0, 85.0, 75.0, 55.0, 40.0, 20.0, 12.0, 2.0],
                "formato": "pasante",
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# CASO 7: Formato unknown (debería inferir automáticamente)
resultados["CASO 7: Formato auto-detectado"] = test_caso(
    "Formato unknown → auto-detecta como retenido individual (suma ≈100)",
    {
        "tamices": TAMICES,
        "materiales": [
            {
                "nombre": "Arena auto-detectada",
                "proporcion_pct": 100,
                "retido_ind_pct": [1.4, 9.8, 5.1, 20.2, 12.4, 22.7, 12.0, 16.4],
                # Sin especificar formato → detectará automáticamente
                "normalizar": False
            }
        ],
        "limites": LIMITES,
        "debug": True
    }
)

# ================================================================================
# RESUMEN
# ================================================================================

print(f"\n\n{'='*80}")
print(f"📊 RESUMEN DE TESTS")
print(f"{'='*80}")

total = len(resultados)
exitosos = sum(1 for v in resultados.values() if v)
fallidos = total - exitosos

print(f"\nTotal: {total}")
print(f"✅ Exitosos: {exitosos}")
print(f"❌ Fallidos: {fallidos}")
print(f"\nTasa de éxito: {round((exitosos/total)*100, 1)}%")

print(f"\n{'='*80}")
print(f"\n📋 Detalle por caso:")
for nombre, result in resultados.items():
    status = "✅" if result else "❌"
    print(f"  {status} {nombre}")

if fallidos > 0:
    print(f"\n⚠️ {fallidos} caso(s) fallido(s)")
else:
    print(f"\n✨ ¡TODOS LOS CASOS PASARON!")
