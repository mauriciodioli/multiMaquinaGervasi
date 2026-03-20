"""
AUDITORÍA COMPLETA DEL SISTEMA
Pasos:
1. Entrada de datos originales mock
2. Partición en dos + mejora
3. Tabla virtual + verificación banda ideal (±5.5% centro)
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

import numpy as np
import matplotlib.pyplot as plt
from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_tabla_virtual import (
    generar_tabla_virtual,
)

# =====================================================
# PASO 1: DATOS ORIGINALES MOCK
# =====================================================

print("\n" + "="*70)
print("PASO 1: ENTRADA DE DATOS ORIGINALES")
print("="*70)

tamices = np.array([8, 5, 3.15, 2, 1, 0.5, 0.1])

# Tabla 1: Arena gruesa
tabla1_retenido = np.array([0.8, 23.4, 64.8, 87.6, 93.5, 95.3, 98.6])
tabla1_pasante = 100 - tabla1_retenido

# Tabla 2: Agregado fino
tabla2_retenido = np.array([2.0, 5.0, 18.0, 45.0, 72.0, 88.0, 96.0])
tabla2_pasante = 100 - tabla2_retenido

# Proporción inicial: 50% tabla1, 50% tabla2
w1_inicial = 0.5
w2_inicial = 0.5

print(f"\nTABLA 1 (Arena gruesa) - {w1_inicial*100:.0f}%:")
for t, p in zip(tamices, tabla1_pasante):
    print(f"  {t:5.2f} mm: {p:6.2f}%")

print(f"\nTABLA 2 (Agregado fino) - {w2_inicial*100:.0f}%:")
for t, p in zip(tamices, tabla2_pasante):
    print(f"  {t:5.2f} mm: {p:6.2f}%")

# Especificación (PAVER/BLOCK standard)
banda_min = np.array([85, 65, 35, 15, 5, 2, 0])
banda_max = np.array([100, 90, 65, 45, 20, 10, 5])

print(f"\nESPECIFICACIÓN LÍMITES:")
print(f"  Banda mín: {banda_min}")
print(f"  Banda máx: {banda_max}")

# =====================================================
# PASO 2: MEZCLA INICIAL Y EVALUACIÓN
# =====================================================

print("\n" + "="*70)
print("PASO 2: MEZCLA INICIAL (50%-50%)")
print("="*70)

mezcla_inicial = w1_inicial * tabla1_pasante + w2_inicial * tabla2_pasante

print("\nMEZCLA INICIAL:")
error_inicial_total = 0
cumpl_inicial = 0
for i, (t, mezcla, min_b, max_b) in enumerate(zip(tamices, mezcla_inicial, banda_min, banda_max)):
    en_banda = min_b <= mezcla <= max_b
    error_tamiz = max(0, min_b - mezcla, mezcla - max_b)
    error_inicial_total += error_tamiz
    if en_banda:
        cumpl_inicial += 1
    estado = "✓" if en_banda else "✗"
    print(f"  {t:5.2f} mm: {mezcla:6.2f}% [{min_b:5.1f}-{max_b:5.1f}] {estado} error={error_tamiz:5.2f}")

cumpl_inicial_pct = (cumpl_inicial / len(tamices)) * 100
print(f"\n  Cumplimiento inicial: {cumpl_inicial}/{len(tamices)} ({cumpl_inicial_pct:.1f}%)")
print(f"  Error total inicial: {error_inicial_total:.2f}%")

# =====================================================
# PASO 3: INTENTO DE MEJORA CON OPTIMIZACIÓN DE PROPORCIONES
# =====================================================

print("\n" + "="*70)
print("PASO 3: OPTIMIZACIÓN DE PROPORCIONES (2 TABLAS)")
print("="*70)

from scipy.optimize import minimize

def error_mezcla(w, tabla1_p, tabla2_p, min_b, max_b):
    """Calcula error de mezcla ponderada"""
    if len(w) == 2:
        w1, w2 = w[0], 1 - w[0]  # constraint: w1 + w2 = 1
    else:
        return 1e10
    
    mezcla = w1 * tabla1_p + w2 * tabla2_p
    error_total = 0
    for m, min_val, max_val in zip(mezcla, min_b, max_b):
        error_total += max(0, min_val - m, m - max_val)**2
    return error_total

# Optimizar
result_opt = minimize(
    error_mezcla,
    x0=[0.5],
    args=(tabla1_pasante, tabla2_pasante, banda_min, banda_max),
    method='SLSQP',
    bounds=[(0.0, 1.0)]
)

w1_opt = result_opt.x[0]
w2_opt = 1 - w1_opt

mezcla_optimizada = w1_opt * tabla1_pasante + w2_opt * tabla2_pasante

print(f"\nProporción optimizada:")
print(f"  Tabla 1: {w1_opt*100:.1f}%")
print(f"  Tabla 2: {w2_opt*100:.1f}%")

print("\nMEZCLA OPTIMIZADA:")
error_opt_total = 0
cumpl_opt = 0
for i, (t, mezcla, min_b, max_b) in enumerate(zip(tamices, mezcla_optimizada, banda_min, banda_max)):
    en_banda = min_b <= mezcla <= max_b
    error_tamiz = max(0, min_b - mezcla, mezcla - max_b)
    error_opt_total += error_tamiz
    if en_banda:
        cumpl_opt += 1
    estado = "✓" if en_banda else "✗"
    print(f"  {t:5.2f} mm: {mezcla:6.2f}% [{min_b:5.1f}-{max_b:5.1f}] {estado} error={error_tamiz:5.2f}")

cumpl_opt_pct = (cumpl_opt / len(tamices)) * 100
mejora_pct = ((error_inicial_total - error_opt_total) / error_inicial_total * 100) if error_inicial_total > 0 else 0

print(f"\n  Cumplimiento optimizado: {cumpl_opt}/{len(tamices)} ({cumpl_opt_pct:.1f}%)")
print(f"  Error total optimizado: {error_opt_total:.2f}%")
print(f"  MEJORA: {mejora_pct:.1f}%")

# =====================================================
# PASO 4: DECISIÓN - ¿NECESITA TABLA VIRTUAL?
# =====================================================

print("\n" + "="*70)
print("PASO 4: DECISIÓN - ¿NECESITA TABLA VIRTUAL?")
print("="*70)

CUMPL_ACEPTABLE = 95.0
MEJORA_MINIMA = 15.0

necesita_tv = cumpl_opt_pct < CUMPL_ACEPTABLE

print(f"\nCriterios:")
print(f"  Cumplimiento mínimo requerido: {CUMPL_ACEPTABLE:.1f}%")
print(f"  Cumplimiento actual: {cumpl_opt_pct:.1f}%")
print(f"  ¿Necesita tabla virtual? {['NO', 'SÍ'][necesita_tv]}")

if necesita_tv:
    print("\n  → GENERANDO TABLA VIRTUAL...")
    
    # =====================================================
    # PASO 5: GENERAR TABLA VIRTUAL
    # =====================================================
    
    print("\n" + "="*70)
    print("PASO 5: GENERACIÓN DE TABLA VIRTUAL DIRIGIDA")
    print("="*70)
    
    pasante_virtual, debug_info = generar_tabla_virtual(
        pasante_mezcla=mezcla_optimizada[::-1].tolist(),
        banda_min=banda_min[::-1].tolist(),
        banda_max=banda_max[::-1].tolist(),
        tamices=[str(x) for x in tamices[::-1]],
        metodo="principal",
        factor_suavizado=0.5,
    )
    
    pasante_virtual = np.array(pasante_virtual)[::-1]
    
    print("\nTABLA VIRTUAL GENERADA:")
    for t, p_real, p_virt in zip(tamices, mezcla_optimizada, pasante_virtual):
        print(f"  {t:5.2f} mm: Real={p_real:6.2f}%, Virtual={p_virt:6.2f}%")
    
    # =====================================================
    # PASO 6: REOPTIMIZACIÓN CON 3 TABLAS (2 originales + 1 virtual)
    # =====================================================
    
    print("\n" + "="*70)
    print("PASO 6: REOPTIMIZACIÓN CON 3 TABLAS (incluye tabla virtual)")
    print("="*70)
    
    def error_mezcla_3t(w, t1_p, t2_p, t3_p, min_b, max_b):
        """Error con 3 tablas, suma de pesos = 1"""
        if len(w) == 2:
            w1, w2 = w[0], w[1]
            w3 = 1 - w1 - w2
        else:
            return 1e10
        
        if min(w1, w2, w3) < 0 or max(w1, w2, w3) > 1:
            return 1e10
        
        mezcla = w1 * t1_p + w2 * t2_p + w3 * t3_p
        error_total = 0
        for m, min_val, max_val in zip(mezcla, min_b, max_b):
            error_total += max(0, min_val - m, m - max_val)**2
        return error_total
    
    result_opt3 = minimize(
        error_mezcla_3t,
        x0=[w1_opt * 0.8, w2_opt * 0.8],
        args=(tabla1_pasante, tabla2_pasante, pasante_virtual, banda_min, banda_max),
        method='SLSQP',
        bounds=[(0.0, 1.0), (0.0, 1.0)]
    )
    
    w1_opt3 = result_opt3.x[0]
    w2_opt3 = result_opt3.x[1]
    w3_opt3 = 1 - w1_opt3 - w2_opt3
    
    mezcla_final = w1_opt3 * tabla1_pasante + w2_opt3 * tabla2_pasante + w3_opt3 * pasante_virtual
    
    print(f"\nProporción final (3 tablas):")
    print(f"  Tabla 1 (Arena gruesa): {w1_opt3*100:.1f}%")
    print(f"  Tabla 2 (Agregado fino): {w2_opt3*100:.1f}%")
    print(f"  Tabla 3 (Virtual): {w3_opt3*100:.1f}%")
    
    print("\nMEZCLA FINAL:")
    error_final_total = 0
    cumpl_final = 0
    for i, (t, mezcla, min_b, max_b) in enumerate(zip(tamices, mezcla_final, banda_min, banda_max)):
        en_banda = min_b <= mezcla <= max_b
        error_tamiz = max(0, min_b - mezcla, mezcla - max_b)
        error_final_total += error_tamiz
        if en_banda:
            cumpl_final += 1
        estado = "✓" if en_banda else "✗"
        print(f"  {t:5.2f} mm: {mezcla:6.2f}% [{min_b:5.1f}-{max_b:5.1f}] {estado} error={error_tamiz:5.2f}")
    
    cumpl_final_pct = (cumpl_final / len(tamices)) * 100
    mejora_final_pct = ((error_inicial_total - error_final_total) / error_inicial_total * 100) if error_inicial_total > 0 else 0
    
    print(f"\n  Cumplimiento final: {cumpl_final}/{len(tamices)} ({cumpl_final_pct:.1f}%)")
    print(f"  Error total final: {error_final_total:.2f}%")
    print(f"  MEJORA TOTAL: {mejora_final_pct:.1f}%")
    
else:
    print("\n  → NO se necesita tabla virtual")
    mezcla_final = mezcla_optimizada
    cumpl_final = cumpl_opt
    cumpl_final_pct = cumpl_opt_pct
    error_final_total = error_opt_total
    mejora_final_pct = mejora_pct

# =====================================================
# PASO 7: VERIFICACIÓN BANDA IDEAL (±5.5% centro)
# =====================================================

print("\n" + "="*70)
print("PASO 7: VERIFICACIÓN BANDA IDEAL (±5.5% DEL CENTRO)")
print("="*70)

centro_banda = (banda_min + banda_max) / 2
banda_ideal_min = centro_banda - 5.5
banda_ideal_max = centro_banda + 5.5

print("\nCOMPARACIÓN CON BANDA IDEAL (±5.5%):")
desviaciones = []
cumpl_ideal = 0
for i, (t, mezcla, centro, ideal_min, ideal_max) in enumerate(zip(tamices, mezcla_final, centro_banda, banda_ideal_min, banda_ideal_max)):
    en_banda_ideal = ideal_min <= mezcla <= ideal_max
    desviacion = abs(mezcla - centro)
    desviaciones.append(desviacion)
    if en_banda_ideal:
        cumpl_ideal += 1
    estado = "✓✓" if en_banda_ideal else "✓" if (banda_min[i] <= mezcla <= banda_max[i]) else "✗"
    print(f"  {t:5.2f} mm: {mezcla:6.2f}% Centro={centro:6.2f}% (±5.5%: [{ideal_min:6.1f}-{ideal_max:6.1f}]) {estado} desv={desviacion:5.2f}%")

cumpl_ideal_pct = (cumpl_ideal / len(tamices)) * 100
desv_promedio = np.mean(desviaciones)

print(f"\nRESULTADO FINAL:")
print(f"  ✓✓ Cumplimiento banda ideal (±5.5%): {cumpl_ideal}/{len(tamices)} ({cumpl_ideal_pct:.1f}%)")
print(f"  ✓  Cumplimiento band especificación: {cumpl_final}/{len(tamices)} ({cumpl_final_pct:.1f}%)")
print(f"  Desviación promedio del centro: {desv_promedio:.2f}%")

# Criterio de éxito
EXITO = cumpl_ideal_pct >= 85.0  # Al menos 6 de 7 tamices en banda ideal

print(f"\n{'='*70}")
if EXITO:
    print(f"✅ OBJETIVO LOGRADO - Sistema dentro de banda ideal en {cumpl_ideal_pct:.1f}% de tamices")
else:
    print(f"⚠️  OBJETIVO PARCIAL - Cumplimiento ideal: {cumpl_ideal_pct:.1f}% (necesario ≥85%)")
print(f"{'='*70}\n")

# =====================================================
# PASO 8: GRÁFICO DE RESULTADOS
# =====================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico 1: Comparación de mezclas
ax1.semilogx(tamices, mezcla_inicial, 'o-', linewidth=2, label='Mezcla inicial (50-50)', color='gray')
ax1.semilogx(tamices, mezcla_optimizada, 's-', linewidth=2, label='Optimizada (2 tablas)', color='orange')
ax1.semilogx(tamices, mezcla_final, '^-', linewidth=2.5, label='Final (con TV)', color='green')

ax1.fill_between(tamices, banda_min, banda_max, alpha=0.15, color='blue', label='Banda especificación')
ax1.fill_between(tamices, banda_ideal_min, banda_ideal_max, alpha=0.25, color='green', label='Banda ideal (±5.5%)')

ax1.set_xscale('log')
ax1.set_xticks(tamices)
ax1.set_xticklabels([str(x) for x in tamices])
ax1.set_ylabel("Pasante acumulado (%)")
ax1.set_xlabel("Tamiz (mm)")
ax1.set_ylim(0, 105)
ax1.grid(True, which='both', linestyle='--', alpha=0.3)
ax1.legend(loc='upper left')
ax1.set_title("Evolución de Mezclas")

# Gráfico 2: Error por tamiz
x_pos = np.arange(len(tamices))
error_inicial_por_tamiz = np.array([max(0, banda_min[i] - mezcla_inicial[i], mezcla_inicial[i] - banda_max[i]) for i in range(len(tamices))])
error_opt_por_tamiz = np.array([max(0, banda_min[i] - mezcla_optimizada[i], mezcla_optimizada[i] - banda_max[i]) for i in range(len(tamices))])
error_final_por_tamiz = np.array([max(0, banda_min[i] - mezcla_final[i], mezcla_final[i] - banda_max[i]) for i in range(len(tamices))])

width = 0.25
ax2.bar(x_pos - width, error_inicial_por_tamiz, width, label='Inicial', color='gray', alpha=0.7)
ax2.bar(x_pos, error_opt_por_tamiz, width, label='Optimizada', color='orange', alpha=0.7)
ax2.bar(x_pos + width, error_final_por_tamiz, width, label='Final', color='green', alpha=0.7)

ax2.set_xticks(x_pos)
ax2.set_xticklabels([str(t) for t in tamices])
ax2.set_ylabel("Error (%)")
ax2.set_xlabel("Tamiz (mm)")
ax2.legend()
ax2.set_title("Error por Tamiz - Comparación")
ax2.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("audit_objetivo_resultado.png", dpi=150)
print("✅ Gráfico guardado: audit_objetivo_resultado.png")
plt.close()
