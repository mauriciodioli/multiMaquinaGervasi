"""
TEST DE TABLA VIRTUAL DIRIGIDA
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

import matplotlib.pyplot as plt
import numpy as np

from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_tabla_virtual import (
    generar_tabla_virtual,
)

# =====================================================
# DATOS
# =====================================================

tamices = np.array([8, 5, 3.15, 2, 1, 0.5, 0.1])

# Datos de pasante acumulado de la tabla proporcionada
pasante = np.array([99.20, 76.60, 35.20, 12.40, 6.50, 4.70, 1.40])
retenido = 100 - pasante

# =====================================================
# NORMA
# =====================================================

tamices_norma = np.array([0.075, 0.15, 0.3, 0.6, 1.18, 2.36, 4.75, 9.5])

banda_min_norma = np.array([0, 0, 19, 37, 54, 70, 90, 100])
banda_max_norma = np.array([0, 33, 51, 66, 80, 90, 100, 100])

# =====================================================
# INTERPOLACION LOG
# =====================================================

log_norma = np.log10(tamices_norma)
# Interpolar usando tamices en orden ascendente (requisito de interp)
tamices_asc = np.sort(tamices)
log_user_asc = np.log10(tamices_asc)
banda_min_asc = np.interp(log_user_asc, log_norma, banda_min_norma)
banda_max_asc = np.interp(log_user_asc, log_norma, banda_max_norma)

# Invertir para mantener orden descendente
# Buscar índices para revertir al orden original de tamices
sort_indices = np.argsort(np.argsort(tamices[::-1]))
banda_min = banda_min_asc[::-1]
banda_max = banda_max_asc[::-1]

# =====================================================
# 🔴 TABLA VIRTUAL
# =====================================================

# La función necesita datos en orden ascendente, así que invertimos temporalmente
pasante_virtual_asc, debug_info = generar_tabla_virtual(
    pasante_mezcla=pasante[::-1].tolist(),  # Invertir a ascendente
    banda_min=banda_min[::-1].tolist(),  # Invertir a ascendente
    banda_max=banda_max[::-1].tolist(),  # Invertir a ascendente
    tamices=[str(x) for x in tamices[::-1]],  # Invertir a ascendente
    metodo="principal",
    factor_suavizado=0.5,
)

# Invertir el resultado nuevamente para mantener orden descendente
pasante_virtual = np.array(pasante_virtual_asc)[::-1]

# =====================================================
# 📊 TABLA COMPARATIVA (CONSOLE)
# =====================================================

print("\n=== TABLA VIRTUAL ===")
for t, r, v in zip(tamices, pasante, pasante_virtual):
    print(f"{t} mm | real: {r:.2f} | virtual: {v:.2f}")

# =====================================================
# FIGURA
# =====================================================

fig, ax1 = plt.subplots(figsize=(10, 8))

# 🟠 EJE IZQUIERDO → RETENIDO
ax1.plot(tamices, retenido, 'o-', linewidth=2, color='orange', label='Retenido acumulado')
ax1.set_ylabel("Retenido acumulado (%)")
ax1.set_ylim(0, 100)

# 🟢 EJE DERECHO → PASANTE
ax2 = ax1.twinx()
ax2.plot(tamices, pasante, 'o-', linewidth=2, color='green', label='Pasante real')
# 🔴 tabla virtual
ax2.plot(
    tamices,
    pasante_virtual,
    'o-',
    color='red',
    linewidth=2,
    label='Tabla virtual'
)
# bandas (en PASANTE - eje derecho)
ax2.plot(tamices, banda_min, '--', label='Banda min')
ax2.plot(tamices, banda_max, '--', label='Banda max')

# zona válida
ax2.fill_between(tamices, banda_min, banda_max, alpha=0.2)

ax2.set_ylabel("Pasante acumulado (%)")
ax2.set_ylim(0, 100)

# =====================================================
# CONFIGURACION
# =====================================================

ax1.set_xscale('log')
ax1.set_xticks(tamices)
ax1.set_xticklabels([str(x) for x in tamices])

ax1.set_xlabel("Tamiz (mm)")

# grid (usar uno solo)
ax1.grid(True, which="both", linestyle='--', linewidth=0.5)

plt.title("Curva granulométrica")

# 🔥 LEGEND COMBINADO
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax2.legend(lines1 + lines2, labels1 + labels2)

# =====================================================
# 📊 TABLA EN GRÁFICO
# =====================================================

# Preparar datos para tabla
tabla_data = []
tabla_data.append(['Tamiz (mm)', 'Real (%)', 'Virtual (%)'])

for t, r, v in zip(tamices, pasante, pasante_virtual):
    tabla_data.append([f'{t:.2f}', f'{r:.1f}', f'{v:.1f}'])

# Crear tabla en figura
table = ax1.table(cellText=tabla_data, cellLoc='center', loc='lower left',
                  bbox=[0.02, -0.35, 0.25, 0.3], fontsize=8)
table.auto_set_font_size(False)
table.set_fontsize(8)

# Estilo de encabezado
for i in range(3):
    table[(0, i)].set_facecolor('#4472C4')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Alternar colores en filas
for i in range(1, len(tabla_data)):
    for j in range(3):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#E7E6E6')
        else:
            table[(i, j)].set_facecolor('#F2F2F2')

plt.tight_layout()
plt.savefig("grafico_final_pro.png", dpi=150)

print("✅ Grafico PRO generado")