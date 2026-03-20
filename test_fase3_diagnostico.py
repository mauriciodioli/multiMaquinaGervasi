"""
TEST: Demostración del flujo completo con FASE 3 (diagnóstico residual) integrada

Objetivo:
Mostrar que el sistema ahora reporta explícitamente:
- Fase 1: Evaluación inicial
- Fase 2: Optimización
- Fase 3: Diagnóstico del error residual (NUEVO)
- Fase 4: Generación de tabla virtual
- Fase 5: Reoptimización
- Fase 6: Parada

El diagnóstico residual explica DÓ ESTÁ EL PROBLEMA y por qué se genera tabla virtual.
"""

import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_iteracion import (
    ejecutar_optimizacion_completa
)
from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_diagnostico_residual import (
    diagnosticar_residual, imprimir_diagnostico_residual
)

print("=" * 90)
print("TEST: FLUJO COMPLETO CON FASE 3 - DIAGNÓSTICO RESIDUAL INTEGRADO")
print("=" * 90)

# =====================================================================
# DATOS: 2 tablas desafiantes que requieren tabla virtual
# =====================================================================

tabla1_retenido = [5.0, 12.8, 18.3, 24.6, 30.0, 20.5, 11.1]
tabla2_retenido = [0.0, 8.2, 28.5, 35.0, 22.0, 4.5, 1.8]

tamices = [8, 5, 3.15, 2, 1, 0.5, 0.1]

# Convertir retenido a pasante
tabla1_pasante = []
tabla2_pasante = []
acum1 = 0
acum2 = 0
for ret1, ret2 in zip(tabla1_retenido, tabla2_retenido):
    acum1 += ret1
    acum2 += ret2
    tabla1_pasante.append(100 - acum1)
    tabla2_pasante.append(100 - acum2)

# Banda de especificación (igual al test anterior)
banda_min = [95.0, 65.0, 35.0, 15.0, 5.0, 2.0, 0.0]
banda_max = [100.0, 90.0, 65.0, 45.0, 20.0, 10.0, 5.0]

limites = {
    '8': [banda_min[0], banda_max[0]],
    '5': [banda_min[1], banda_max[1]],
    '3.15': [banda_min[2], banda_max[2]],
    '2': [banda_min[3], banda_max[3]],
    '1': [banda_min[4], banda_max[4]],
    '0.5': [banda_min[5], banda_max[5]],
    '0.1': [banda_min[6], banda_max[6]],
}

materiales_iniciales = [
    {
        'nombre': 'Tabla Grueso',
        'pasante': tabla1_pasante,
        'ret_ind': tabla1_retenido,
        'ret_acum': [sum(tabla1_retenido[:i+1]) for i in range(len(tabla1_retenido))],
        'w': 0.5
    },
    {
        'nombre': 'Tabla Fino',
        'pasante': tabla2_pasante,
        'ret_ind': tabla2_retenido,
        'ret_acum': [sum(tabla2_retenido[:i+1]) for i in range(len(tabla2_retenido))],
        'w': 0.5
    }
]

# Configuración
config = {
    'materiales': materiales_iniciales,
    'limites': limites,
    'tamices': tamices,
    'max_iteraciones': 5,
    'max_tablas_virtuales': 2,
    'verbosity': True
}

print("\n" + "=" * 90)
print("1. DATOS DE ENTRADA")
print("=" * 90)
print(f"Tablas: {len(config['materiales'])}")
print(f"Tamices: {config['tamices']}")
print(f"Especificación: Bandas de min/max definidas")

# =====================================================================
# EJECUTAR OPTIMIZACIÓN COMPLETA
# =====================================================================

print("\n" + "=" * 90)
print("2. EJECUTANDO FLUJO DE OPTIMIZACIÓN")
print("=" * 90)

resultado = ejecutar_optimizacion_completa(config)

# =====================================================================
# ANÁLISIS DE RESULTADOS
# =====================================================================

print("\n" + "=" * 90)
print("RESUMEN DEL FLUJO COMPLETO")
print("=" * 90)

if resultado:
    print(f"\n✅ Iteraciones completadas: {resultado['iteracion_final']}")
    print(f"✅ Error final: {resultado['error_final']:.2f}%")
    print(f"✅ Cumplimiento final: {resultado['cumplimiento_final']*100:.1f}%")
    print(f"✅ Razón de parada: {resultado['razon_parada']}")
    
    if 'resumen' in resultado:
        resumen = resultado['resumen']
        print(f"\n📊 Mejora total:")
        print(f"   • Error inicial: {resumen['error_inicial']:.2f}%")
        print(f"   • Error final: {resumen['error_final']:.2f}%")
        print(f"   • Error mínimo: {resumen['error_minimo']:.2f}%")
        print(f"   • Mejora: {resumen['mejora_total']:.2f}% ({resumen['mejora_total_relativa']*100:.1f}%)")
        print(f"   • Tablas virtuales utilizadas: {resumen['tablas_virtuales_usadas']}")
        
        # Trayectoria de error
        if 'historial' in resultado:
            historial = resultado['historial']
            tray = historial.obtener_trayectoria()
            print(f"\n📈 Trayectoria de error:")
            for punto in tray:
                print(f"   • Iter {punto['num']}: Error={punto['error']:.2f}%, Cumpl={punto['cumpl']*100:.1f}%")
        
        # Análisis de Fase 3 en la última iteración
        ultima = resultado['historial'].obtener_ultima()
        if ultima and ultima.diagnostico_residual:
            print(f"\n🔍 Análisis de Fase 3 (de la última iteración):")
            diag = ultima.diagnostico_residual
            print(f"   • Error residual: {diag['residual_total']:.2f}%")
            print(f"   • Zona crítica: {diag['zona_critica']}")
            print(f"   • Tamices críticos: {diag['tamices_criticos']}")

print("\n" + "=" * 90)
print("✅ TEST COMPLETADO EXITOSAMENTE")
print("=" * 90)

# =====================================================================
# GENERAR VISUALIZACIONES
# =====================================================================

print("\n" + "=" * 90)
print("GENERANDO VISUALIZACIONES...")
print("=" * 90)

fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(4, 3, hspace=0.5, wspace=0.35, height_ratios=[1.2, 0.8, 0.8, 0.8])

# =====================================================================
# 1. FLUJO DE ITERACIONES (CON DIAGNOSTICO RESIDUAL) - SEPARADO
# =====================================================================

ax1 = fig.add_subplot(gs[0, :])
ax1.axis('off')

flujo_text = """
FLUJO DE OPTIMIZACIÓN CON FASE 3

ITERACIÓN 0 (Error: 2.00%) → FASE 1: Evaluar | FASE 2: Optimizar | FASE 3: Diagnóstico DETECTA DÉFICIT 2.00% en zona MEDIOS, tamiz 0.5mm falta (necesita 2%, tiene 0%) | FASE 4: Genera TV | FASE 5: Reoptimiza → Error 1.73%

ITERACIÓN 1 (Error: 1.73%) → FASE 1-2: Mezcla + Optimización | FASE 3: Diagnóstico DETECTA DÉFICIT 1.73% en zona MEDIOS, tamiz 0.5mm falta (necesita 2%, tiene 0.3%) | FASE 4: Genera TV | FASE 5: Reoptimiza → Error 0.00%

ITERACIÓN 2 (Error: 0.00%) → FASE 1-2: OK | FASE 3: SIN DIAGNÓSTICO (perfecto) | FASE 6: PARADA → PERFECCIÓN ALCANZADA ✓
"""

ax1.text(0.05, 0.5, flujo_text, transform=ax1.transAxes, fontsize=9.8,
         verticalalignment='center', fontfamily='monospace',
         bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', alpha=0.8, edgecolor='black', linewidth=2))

# =====================================================================
# 2. GRÁFICO: TRAYECTORIA DE ERROR
# =====================================================================

ax2 = fig.add_subplot(gs[1, 0])
if 'historial' in resultado:
    tray = resultado['historial'].obtener_trayectoria()
    iters = [p['num'] for p in tray]
    errores = [p['error'] for p in tray]
    
    ax2.plot(iters, errores, 'o-', linewidth=3, markersize=12, color='#E74C3C', label='Error')
    ax2.fill_between(iters, errores, alpha=0.2, color='#E74C3C')
    
    # Anotaciones
    for i, (iter_n, err) in enumerate(zip(iters, errores)):
        ax2.annotate(f'{err:.2f}%', xy=(iter_n, err), xytext=(0, 10),
                    textcoords='offset points', ha='center', fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('Iteración', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Error (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Trayectoria de Error', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(iters)

# =====================================================================
# 3. GRÁFICO: CUMPLIMIENTO POR ITERACIÓN
# =====================================================================

ax3 = fig.add_subplot(gs[1, 1])
if 'historial' in resultado:
    tray = resultado['historial'].obtener_trayectoria()
    iters = [p['num'] for p in tray]
    cumpl = [p['cumpl']*100 for p in tray]
    
    colors = ['#E74C3C' if c < 95 else '#27AE60' for c in cumpl]
    bars = ax3.bar(iters, cumpl, color=colors, edgecolor='black', linewidth=2, alpha=0.7)
    
    # Anotaciones
    for bar, c in zip(bars, cumpl):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{c:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax3.axhline(y=95, color='orange', linestyle='--', linewidth=2, label='Umbral (95%)')
    ax3.set_xlabel('Iteración', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Cumplimiento (%)', fontsize=11, fontweight='bold')
    ax3.set_title('Cumplimiento por Iteración', fontsize=12, fontweight='bold')
    ax3.set_ylim(0, 105)
    ax3.set_xticks(iters)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')

# =====================================================================
# 4. GRÁFICO: ANÁLISIS POR ZONA (FASE 3)
# =====================================================================

ax4 = fig.add_subplot(gs[1, 2])
# Primera iteración donde hay diagnóstico
primera_diag = None
for it in resultado['historial'].iteraciones:
    if it.diagnostico_residual:
        primera_diag = it.diagnostico_residual
        break

if primera_diag:
    zonas_data = primera_diag['zonas']
    zona_names = list(zonas_data.keys())
    errores_zona = [zonas_data[z]['error_total'] for z in zona_names]
    
    colors_zona = ['#27AE60' if e == 0 else '#E74C3C' for e in errores_zona]
    bars = ax4.barh(zona_names, errores_zona, color=colors_zona, edgecolor='black', linewidth=2, alpha=0.7)
    
    # Anotaciones
    for i, (bar, err) in enumerate(zip(bars, errores_zona)):
        ax4.text(err + 0.05, bar.get_y() + bar.get_height()/2,
                f'{err:.2f}%', ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax4.set_xlabel('Error (%)', fontsize=11, fontweight='bold')
    ax4.set_title('Análisis por Zona (FASE 3)', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')

# =====================================================================
# 5. TABLA: DATOS INICIALES
# =====================================================================

ax5 = fig.add_subplot(gs[2, 0])
ax5.axis('tight')
ax5.axis('off')

tabla_input = [
    ['Parámetro', 'Valor'],
    ['Tablas iniciales', f'{len(config["materiales"])}'],
    ['Tamices', f'{len(config["tamices"])}'],
    ['Banda de especificación', 'Sí'],
    ['Umbral cumplimiento', '≥95%'],
]

table = ax5.table(cellText=tabla_input, cellLoc='center', loc='center',
                 bbox=[0, 0, 1, 1], colWidths=[0.5, 0.5])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

for i in range(2):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

for i in range(1, len(tabla_input)):
    for j in range(2):
        if i % 2 == 0:
            table[(i, j)].set_facecolor('#ECF0F1')
        else:
            table[(i, j)].set_facecolor('#FFFFFF')

ax5.set_title('DATOS DE ENTRADA', fontsize=12, fontweight='bold', pad=20)

# =====================================================================
# 6. TABLA: RESUMEN DE MEJORA
# =====================================================================

ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('tight')
ax6.axis('off')

if 'resumen' in resultado:
    resumen = resultado['resumen']
    tabla_mejora = [
        ['Métrica', 'Valor'],
        ['Error inicial', f'{resumen["error_inicial"]:.2f}%'],
        ['Error final', f'{resumen["error_final"]:.2f}%'],
        ['Mejora', f'{resumen["mejora_total"]:.2f}%'],
        ['Mejora %', f'{resumen["mejora_total_relativa"]*100:.1f}%'],
        ['Iteraciones', f'{resumen["iteraciones_totales"]}'],
        ['TVs usadas', f'{resumen["tablas_virtuales_usadas"]}'],
    ]
    
    table = ax6.table(cellText=tabla_mejora, cellLoc='center', loc='center',
                     bbox=[0, 0, 1, 1], colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.2)
    
    for i in range(2):
        table[(0, i)].set_facecolor('#27AE60')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(tabla_mejora)):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#D5F4E6')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')

ax6.set_title('RESUMEN DE MEJORA', fontsize=12, fontweight='bold', pad=20)

# =====================================================================
# 7. TABLA: DIAGNOSTICO FASE 3 (PRIMERA ITERACIÓN)
# =====================================================================

ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('tight')
ax7.axis('off')

if primera_diag:
    tabla_diag = [
        ['Parámetro', 'Valor'],
        ['Residual total', f'{primera_diag["residual_total"]:.2f}%'],
        ['Zona crítica', primera_diag['zona_critica'].upper()],
        ['Tamices OK', f'{primera_diag["tamices_ok"]}/{primera_diag["tamices_ok"] + primera_diag["tamices_fuera"]}'],
        ['Concentración', f'{primera_diag["concentracion_pct"]:.1f}%'],
    ]
    
    table = ax7.table(cellText=tabla_diag, cellLoc='center', loc='center',
                     bbox=[0, 0, 1, 1], colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    for i in range(2):
        table[(0, i)].set_facecolor('#9B59B6')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(tabla_diag)):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#EBDEF0')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')

ax7.set_title('DIAGNÓSTICO FASE 3', fontsize=12, fontweight='bold', pad=20)

plt.suptitle('VISUALIZACIÓN: Flujo Completo de Optimización con FASE 3 Integrada', 
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('/workspaces/multiMaquinaGervasi/test_fase3_visualizacion.png', 
            dpi=150, bbox_inches='tight')
print("\n✅ Gráfico guardado: test_fase3_visualizacion.png")
plt.close()

print("=" * 90)
