#!/usr/bin/env python3
"""
Test script para validar optimización L1 con λ=10
Usando el ejemplo conocido: 3 materiales (difusión 1, 2, 3)
"""

import sys
import json
import numpy as np
from scipy.optimize import minimize

# Simulación de datos del caso anterior
TAMICES_ORDEN = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075, "Fundo"]

# Datos aproximados del caso fallido anterior
materiales_datos = {
    "difusion_1": {  # ~6% - casi todo en 4.8mm
        "ret_acum": [0, 0, 0, 94, 94, 94, 94, 94, 94, 94, 94],
    },
    "difusion_2": {  # ~52% - casi todo en 2.4mm  
        "ret_acum": [0, 0, 0, 0, 100, 100, 100, 100, 100, 100, 100],
    },
    "difusion_3": {  # ~42% - distribuido entre 1.2mm a fundo
        "ret_acum": [0, 0, 0, 0, 0, 0, 15, 35, 50, 60, 100],
    }
}

limites = {
    "bloco": {
        "12.5": [0, 0],
        "9.5": [0, 3],
        "6.3": [0, 12],
        "4.8": [0, 33],
        "2.4": [10, 40],
        "1.2": [37, 66],
        "0.6": [54, 78],
        "0.3": [60, 80],
        "0.15": [65, 85],
        "0.075": [68, 88],
        "Fundo": [98, 100]
    }
}

def test_optimization():
    print("\n" + "="*70)
    print("TEST: Optimización Proporción (λ=10, L1, sin MIN_WEIGHT)")
    print("="*70)
    
    n = len(TAMICES_ORDEN)
    
    # Pesos iniciales originales (del caso fallido)
    w_inicial = np.array([0.06, 0.52, 0.42])
    print(f"\n✓ Pesos iniciales: {np.round(w_inicial, 4)}")
    
    # Retacumulados por material
    ret_acums = [
        np.array(materiales_datos["difusion_1"]["ret_acum"], dtype=float),
        np.array(materiales_datos["difusion_2"]["ret_acum"], dtype=float),
        np.array(materiales_datos["difusion_3"]["ret_acum"], dtype=float),
    ]
    
    # Regularización NUEVA
    LAMBDA_REG = 10.0
    
    def objetivo(pesos):
        """
        Minimizar: error_faixa + λ * Σ|Δw|  (L1, no L2)
        """
        pesos = np.clip(pesos, 0.0, 1.0)
        
        s = sum(pesos)
        if s <= 0:
            return 1e10
        
        w_norm = pesos / s
        
        # Mezcla ponderada
        mix_acum_opt = np.zeros(n)
        for i, m_acum in enumerate(ret_acums):
            mix_acum_opt += w_norm[i] * m_acum
        
        # Error respecto a faixa
        error_faixa = 0.0
        for k, t in enumerate(TAMICES_ORDEN):
            rng = limites["bloco"].get(str(t))
            if not rng:
                continue
            
            lo, hi = float(rng[0]), float(rng[1])
            x = mix_acum_opt[k]
            
            if lo <= x <= hi:
                pass
            else:
                if x < lo:
                    error_faixa += (lo - x) ** 2
                else:
                    error_faixa += (x - hi) ** 2
        
        # Regularización L1: penalizar cambios MODERADAMENTE
        cambios = np.abs(w_norm - w_inicial)
        reg_term = LAMBDA_REG * np.sum(cambios)
        
        total_error = error_faixa + reg_term
        return total_error
    
    # Restricción: suma = 1
    constraints = [
        {"type": "eq", "fun": lambda w: sum(w) - 1.0}
    ]
    
    # Bounds: [0, 1] para cada peso (SIN restricción de mínimo)
    bounds = [(0.0, 1.0) for _ in range(3)]
    
    print(f"✓ Regularización: L1 con LAMBDA_REG={LAMBDA_REG}")
    print(f"✓ Bounds: [0.0, 1.0] para cada peso (SIN restricción mínima)")
    
    # Evaluar error inicial
    error_inicial = objetivo(w_inicial)
    print(f"\n✓ Error inicial: {round(error_inicial, 4)}")
    
    # Calcular mix ponderado inicial para referencia
    mix_inicial = np.zeros(n)
    for i, m_acum in enumerate(ret_acums):
        mix_inicial += w_inicial[i] * m_acum
    print(f"  Mix acumulada inicial: {np.round(mix_inicial, 2)}")
    
    # OPTIMIZAR
    print(f"\n→ Iniciando optimización SLSQP...")
    
    result = minimize(
        objetivo,
        w_inicial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 5000, "ftol": 1e-12}
    )
    
    print(f"  Convergencia: {result.success}")
    print(f"  Mensaje: {result.message}")
    print(f"  Iteraciones: {result.nit if hasattr(result, 'nit') else 'N/A'}")
    
    if not result.success:
        print(f"\n❌ Optimización FALLÓ")
        return False
    
    # Post-process
    w_opt = result.x
    w_opt = np.clip(w_opt, 0.0, 1.0)
    s = sum(w_opt)
    if s <= 0:
        print(f"\n❌ Suma de pesos = 0")
        return False
    w_opt = w_opt / s
    
    # Evaluar error final
    error_final = objetivo(w_opt)
    
    print(f"\n✓ Pesos optimizados: {np.round(w_opt, 4)}")
    print(f"✓ Error final: {round(error_final, 4)}")
    
    # Calcular mix ponderada final
    mix_opt = np.zeros(n)
    for i, m_acum in enumerate(ret_acums):
        mix_opt += w_opt[i] * m_acum
    print(f"  Mix acumulada optimizada: {np.round(mix_opt, 2)}")
    
    # VALIDACIÓN: Comparar con original
    print(f"\n{'─'*70}")
    if error_final >= error_inicial * 0.95:
        print(f"❌ FALLIDA: Mejora insuficiente")
        print(f"   Error inicial: {round(error_inicial, 4)}")
        print(f"   Error final:   {round(error_final, 4)}")
        print(f"   Mejora:        {round((1 - error_final/error_inicial)*100, 1)}% (umbral: 5%)")
        return False
    else:
        mejora_pct = (1 - error_final/error_inicial) * 100
        print(f"✅ EXITOSA: Mejora de {mejora_pct:.1f}%")
        print(f"   Error inicial: {round(error_inicial, 4)}")
        print(f"   Error final:   {round(error_final, 4)}")
        
        # Comparar cambios en pesos
        deltas = np.abs(w_opt - w_inicial)
        print(f"\n  Cambios en pesos:")
        for i, (ini, opt, delta) in enumerate(zip(w_inicial, w_opt, deltas)):
            print(f"    Material {i+1}: {ini:.4f} → {opt:.4f} (Δ={delta:+.4f})")
        
        return True

if __name__ == "__main__":
    success = test_optimization()
    sys.exit(0 if success else 1)
