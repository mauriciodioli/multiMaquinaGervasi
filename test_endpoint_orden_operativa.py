#!/usr/bin/env python3
"""
Test HTTP real al endpoint POST /calculoPorRetenidos/auditoria
"""

import json
import requests
import time

print("\n" + "="*80)
print("🔌 TEST HTTP: Llamada POST al endpoint /calculoPorRetenidos/auditoria")
print("="*80 + "\n")

# URL del endpoint
url = "http://127.0.0.1:5000/calculoPorRetenidos/auditoria"

# Payload de ejemplo con materiales
payload = {
    "pasante_real": [100, 98.5, 78.2, 45.1, 25.3, 12.1, 5.3, 1.2],
    "banda_min": [100, 90, 50, 20, 10, 5, 2, 0],
    "banda_max": [100, 100, 90, 50, 30, 15, 8, 3],
    "tamices": [12.5, 9.5, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15],
    "materiales": [
        {
            "nombre": "Material A",
            "pasantes": [100, 98.5, 78.2, 45.1, 25.3, 12.1, 5.3, 1.2]
        },
        {
            "nombre": "Material B",
            "pasantes": [100, 95.2, 65.3, 35.2, 18.1, 8.5, 3.2, 0.8]
        },
        {
            "nombre": "Material C",
            "pasantes": [100, 99.1, 88.5, 58.3, 38.2, 22.1, 12.3, 5.1]
        }
    ]
}

print("📤 ENVIANDO PAYLOAD:")
print(json.dumps(payload, indent=2))

try:
    print("\n⏳ Esperando respuesta del servidor...")
    response = requests.post(url, json=payload, timeout=30)
    
    print(f"✅ Respuesta recibida: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("="*80)
        print("📥 RESPUESTA JSON COMPLETA DEL SERVIDOR:")
        print("="*80)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extrae y muestra orden_operativa específicamente
        if data.get("exito") and data.get("data", {}).get("orden_operativa"):
            print("\n" + "="*80)
            print("📋 ORDEN OPERATIVA EXTRAÍDA:")
            print("="*80)
            orden = data["data"]["orden_operativa"]
            
            for paso in orden:
                print(f"\n  ✔️  PASO {paso['paso']}: {paso['material']}")
                print(f"      └─ Tipo: {paso['tipo'].upper()}")
                print(f"      └─ Proporción: {paso['proporcion_pct']}%")
                print(f"      └─ Acción: {paso['accion']}")
                if paso['malla']:
                    print(f"      └─ Malla: {paso['malla']}")
                print(f"      └─ Resultado: {paso['resultado']}")
                print(f"      └─ Uso: {paso['uso']}")
        
        if data.get("exito") and data.get("data", {}).get("propuesta_agregados_correctivos"):
            print("\n" + "="*80)
            print("⚙️  ACCIONES ZARANDA EXTRAÍDAS:")
            print("="*80)
            acciones = data["data"]["propuesta_agregados_correctivos"].get("acciones_zaranda", [])
            for i, accion in enumerate(acciones, 1):
                print(f"  {i}. {accion}")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se pudo conectar al servidor.")
    print("   Asegúrate de que el servidor Flask está ejecutándose en http://127.0.0.1:5000")
    print("\n   Para iniciar el servidor:")
    print("   cd /workspaces/multiMaquinaGervasi/src")
    print("   python3 -m flask run")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "="*80 + "\n")
