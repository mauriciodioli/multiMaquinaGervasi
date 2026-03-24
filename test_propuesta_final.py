#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST REAL: Granulometría - Validación completa del módulo con datos Gervasi

Ejecutar desde raíz del workspace:
  python test_propuesta_final.py
"""

import sys
import json
from pathlib import Path

# Establecer path ANTES de cualquier importación relativa
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')
sys.path.insert(0, '/workspaces/multiMaquinaGervasi/src')

import numpy as np
import matplotlib.pyplot as plt

# Ahora importar el módulo como si fuera Flask
from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    _acum_desc,
    _mezcla_ponderada_acum,
    _validar_faixas,
    generar_propuesta_3_agregados
)


# ============================================================================
# DATOS DE ENTRADA (Exactamente como solicitado)
# ============================================================================

TAMICES = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15]

MATERIALES_INPUT = [
    {
        "nombre": "BRITA",
        "proporcion_pct": 26.6,
        "retido_ind_pct": [5.7, 40.9, 32.8, 19.2, 0, 0, 0, 0],
        "normalizar": False
    },
    {
        "nombre": "PO_DE_PEDRA",
        "proporcion_pct": 26.6,
        "retido_ind_pct": [0, 0, 1.8, 31.4, 20.8, 12.6, 9.0, 7.8],
        "normalizar": False
    },
    {
        "nombre": "AREIA",
        "proporcion_pct": 46.6,
        "retido_ind_pct": [0, 0, 0.9, 7.3, 8.8, 25.9, 46.5, 9.0],
        "normalizar": False
    }
]

LIMITES = {
    "bloco": {
        "9.5": [100, 100],
        "6.3": [90, 100],
        "4.8": [75, 100],
        "2.4": [55, 85],
        "1.2": [40, 70],
        "0.6": [25, 55],
        "0.3": [15, 40],
        "0.15": [5, 20]
    }
}


# ============================================================================
# FUNCIONES AUXILIARES PARA PROCESAMIENTO
# ============================================================================

def simple_logger(msg):
    """Logger simple para debugging"""
    print(f"  [LOG] {msg}")


def procesar_granulometria(materiales_in, tamices, limites):
    """
    Procesa granulometría siguiendo el flujo real del módulo
    Sin depender de Flask
    """
    
    log = simple_logger
    
    # Paso 1: Normalizar proporciones
    total_pct = sum(float(m.get('proporcion_pct', 0.0)) for m in materiales_in) or 100.0
    
    log(f"Total proporciones declaradas: {round(total_pct, 2)}%")
    
    materiales = []
    n_tamices = len(tamices)
    
    for m in materiales_in:
        nombre = m.get('nombre', 'sin_nombre')
        p = float(m.get('proporcion_pct', 0.0))
        w = p / total_pct
        
        ret_ind = m.get('retido_ind_pct', [])
        ret_ind_norm = [float(v) for v in ret_ind]
        
        # Validar suma
        suma_ret = sum(ret_ind_norm)
        if suma_ret > 0 and abs(suma_ret - 100) > 1e-6:
            # Normalizar si es necesario
            ret_ind_norm = [(v / suma_ret) * 100 for v in ret_ind_norm]
        
        ret_acum = _acum_desc(ret_ind_norm)
        
        materiales.append({
            "nombre": nombre,
            "proporcion_pct": round(p, 2),
            "w": round(w, 6),
            "ret_ind": [round(x, 2) for x in ret_ind_norm],
            "ret_acum": ret_acum
        })
        
        log(f"  {nombre}: w={round(w*100, 1)}%, ret_acum={[round(x,1) for x in ret_acum[:3]]}...")
    
    # Paso 2: Calcular mezcla ponderada
    mix_acum = _mezcla_ponderada_acum(materiales)
    
    log(f"Mezcla acumulada: {[round(x, 1) for x in mix_acum[:3]]}...")
    
    # Paso 3: Convertir a PASANTE
    mix_pasante = [round(100 - v, 1) for v in mix_acum]
    
    log(f"Mezcla pasante: {[round(x, 1) for x in mix_pasante[:3]]}...")
    
    # Paso 4: Validar contra faixas (la función espera mix_pasante aunque el parámetro se llama mix_acum)
    valid = _validar_faixas(mix_pasante, tamices, limites)
    
    errores = 0
    if "bloco" in valid:
        errores = sum(1 for d in valid["bloco"] if d.get("ok") == False)
    
    log(f"Errores en bloco: {errores}/{len(tamices)}")
    
    # Paso 5: Generar propuesta si hay desviación
    propuesta_agregados = None
    
    if errores >= 2 and limites and "bloco" in limites:
        log("Generando propuesta de 3 agregados...")
        
        banda_min_valores = []
        banda_max_valores = []
        
        for t in tamices:
            t_str = str(t)
            if t_str in limites.get("bloco", {}):
                min_v, max_v = limites["bloco"][t_str]
                banda_min_valores.append(float(min_v))
                banda_max_valores.append(float(max_v))
            else:
                banda_min_valores.append(0.0)
                banda_max_valores.append(100.0)
        
        propuesta_agregados = generar_propuesta_3_agregados(
            mix_pasante=mix_pasante,
            banda_min=banda_min_valores,
            banda_max=banda_max_valores,
            tamices=[str(t) for t in tamices],
            log=log
        )
    
    return {
        'tamices': tamices,
        'materiales': materiales,
        'mix_acum': mix_acum,
        'mix_pasante': mix_pasante,
        'validacion': valid,
        'propuesta_agregados_correctivos': propuesta_agregados,
        'log': log
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

def test_granulometria_completa():
    """
    TEST PRINCIPAL: Granulometría con propuesta de agregados
    """
    
    print("\n" + "="*80)
    print("TEST REAL: GRANULOMETRÍA - VALIDACIÓN COMPLETA")
    print("="*80)
    
    try:
        # ===== PASO 1: Procesar granulometría =====
        print("\n[1] Procesando granulometría...")
        resultado = procesar_granulometria(MATERIALES_INPUT, TAMICES, LIMITES)
        
        assert resultado is not None, "El resultado no debe ser None"
        print("✅ Granulometría procesada")
        
        # ===== PASO 2: IMPRIMIR CURVA ACTUAL =====
        print("\n" + "-"*80)
        print("CURVA ACTUAL")
        print("-"*80)
        
        print("\nMateriales constituintes:")
        for m in resultado['materiales']:
            print(f"  {m['nombre']:15} | w={m['w']*100:5.1f}% | ret_ind={[f'{x:.1f}' for x in m['ret_ind'][:3]]}...")
        
        print("\nMezcla ponderada (PASANTE):")
        tamices_str = [f"{t:.1f}mm" for t in resultado['tamices']]
        mix_pasante = resultado['mix_pasante']
        
        print("  Tamiz     | Pasante%")
        print("  " + "-"*25)
        for i, t_str in enumerate(tamices_str):
            print(f"  {t_str:>8} | {mix_pasante[i]:>7.1f}")
        
        # ===== PASO 3: DIAGNÓSTICO =====
        print("\n" + "-"*80)
        print("DIAGNÓSTICO")
        print("-"*80)
        
        valid = resultado['validacion']
        
        if "bloco" in valid:
            bloco_data = valid["bloco"]
            cumplimiento = sum(1 for d in bloco_data if d.get("ok") == True)
            total = len(bloco_data)
            cumplimiento_pct = (cumplimiento / total) * 100
            
            print(f"\nCumplimiento de especificación: {cumplimiento}/{total} ({cumplimiento_pct:.1f}%)")
            
            print("\nDetalle por tamiz:")
            print("  Tamiz     | Banda Min | Pasante | Banda Max | Estado")
            print("  " + "-"*55)
            
            for d in bloco_data:
                tamiz = d.get('tamiz', '?')
                # La función _validar_faixas retorna 'min' y 'max', no 'banda_min'/'banda_max'
                banda_min = d.get('min', d.get('banda_min', 0))
                pasante = d.get('mix', d.get('pasante', 0))
                banda_max = d.get('max', d.get('banda_max', 100))
                ok = d.get('ok', None)
                
                estado_icon = "✓" if ok else "✗" if ok is False else "?"
                estado_color = "OK" if ok else "FUERA"
                
                print(f"  {str(tamiz):>8} | {banda_min:>9.1f} | {pasante:>7.1f} | {banda_max:>9.1f} | {estado_icon} {estado_color}")
        
        # ===== PASO 4: PROPUESTA DE AGREGADOS =====
        print("\n" + "-"*80)
        print("PROPUESTA DE AGREGADOS CORRECTIVOS")
        print("-"*80)
        
        propuesta = resultado['propuesta_agregados_correctivos']
        
        # Validaciones de estructura
        assert propuesta is not None, "Debe haber propuesta de agregados"
        assert propuesta.get('exito') == True, "Propuesta debe ser exitosa"
        print("✅ Propuesta generada exitosamente")
        
        prop_data = propuesta.get('propuesta', {})
        
        assert 'm1' in prop_data, "Debe existir M1"
        assert 'm2' in prop_data, "Debe existir M2"
        assert 'm3' in prop_data, "Debe existir M3"
        print("✅ Los 3 agregados presentes (M1, M2, M3)")
        
        # Validar estructura de cada agregado
        for agg_name in ['m1', 'm2', 'm3']:
            agg = prop_data[agg_name]
            
            assert 'nombre' in agg, f"{agg_name} debe tener 'nombre'"
            assert 'retido_ind_pct' in agg, f"{agg_name} debe tener 'retido_ind_pct'"
            assert 'retido_acum_pct' in agg, f"{agg_name} debe tener 'retido_acum_pct'"
            assert 'pasante_pct' in agg, f"{agg_name} debe tener 'pasante_pct'"
            assert 'proporcion_recomendada_pct' in agg, f"{agg_name} debe tener 'proporcion_recomendada_pct'"
            assert 'razon_tecnica' in agg, f"{agg_name} debe tener 'razon_tecnica'"
            
            # Validar rangos
            assert 0 <= agg['proporcion_recomendada_pct'] <= 100, \
                f"{agg_name} proporción fuera de rango"
            
            for val in agg['retido_ind_pct']:
                assert 0 <= val <= 100, f"{agg_name} retido_ind fuera de rango: {val}"
            
            for val in agg['pasante_pct']:
                assert 0 <= val <= 100, f"{agg_name} pasante fuera de rango: {val}"
        
        print("✅ Estructura de agregados validada")
        
        # Imprimir propuesta
        proporciones = propuesta.get('proporciones', [])
        
        print("\nAgregados recomendados:")
        print()
        
        for i, agg_name in enumerate(['m1', 'm2', 'm3']):
            agg = prop_data[agg_name]
            prop_pct = agg['proporcion_recomendada_pct']
            
            print(f"  {agg_name.upper()} [{prop_pct:.1f}%]")
            print(f"    Nombre: {agg['nombre']}")
            print(f"    Retido IND: {[f'{x:.1f}' for x in agg['retido_ind_pct'][:3]]}...")
            print(f"    Pasante:    {[f'{x:.1f}' for x in agg['pasante_pct'][:3]]}...")
            print(f"    Razón: {agg['razon_tecnica']}")
            print()
        
        # ===== PASO 5: MEZCLA CORREGIDA =====
        print("-"*80)
        print("MEZCLA CORREGIDA")
        print("-"*80)
        
        validacion = propuesta.get('validacion', {})
        mix_resultado = validacion.get('mix_resultado_pasante', [])
        
        assert len(mix_resultado) > 0, "Debe haber mezcla resultado"
        print("✅ Mezcla corregida calculada")
        
        # Validar que está en rango
        cumplimiento_corregido = validacion.get('cumplimiento_pct', 0)
        assert 0 <= cumplimiento_corregido <= 100, "Cumplimiento fuera de rango"
        
        cumple = validacion.get('cumple_especificacion', False)
        
        print(f"\nCumplimiento esperado: {cumplimiento_corregido:.1f}%")
        print(f"Especificación cumplida: {'✓ SÍ' if cumple else '✗ NO'}")
        
        print("\nCurva corregida (PASANTE):")
        print("  Tamiz     | Correg.% | Banda Min | Banda Max | Estado")
        print("  " + "-"*55)
        
        for i, t_str in enumerate(tamices_str):
            if i < len(mix_resultado):
                val = mix_resultado[i]
                
                banda_min = LIMITES['bloco'].get(str(TAMICES[i]), [0, 100])[0]
                banda_max = LIMITES['bloco'].get(str(TAMICES[i]), [0, 100])[1]
                
                en_banda = banda_min <= val <= banda_max
                estado = "✓ OK" if en_banda else "✗ FUERA"
                
                print(f"  {t_str:>8} | {val:>7.1f} | {banda_min:>9.1f} | {banda_max:>9.1f} | {estado}")
        
        # ===== RESUMEN FINAL =====
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        
        print(f"\n✅ Materiales procesados: {len(resultado['materiales'])}")
        print(f"✅ Tamices analizados: {len(resultado['tamices'])}")
        print(f"✅ Propuesta generada: {'SÍ' if propuesta else 'NO'}")
        print(f"✅ Cumplimiento actual: {cumplimiento_pct:.1f}%")
        print(f"✅ Cumplimiento esperado: {cumplimiento_corregido:.1f}%")
        print(f"✅ Mejora: {cumplimiento_corregido - cumplimiento_pct:.1f}%")
        
        print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        
        # Retornar todo para generar gráficos
        return True, resultado, cumplimiento_pct, cumplimiento_corregido, propuesta
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FALLIDA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None, None, None
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None, None, None


# ============================================================================
# FUNCIONES PARA GRÁFICOS E INSTRUCCIONES OPERATIVAS
# ============================================================================

def generar_graficos_y_instrucciones(resultado, cumplimiento_pct, cumplimiento_corregido, propuesta):
    """
    Genera gráficos comparativos e instrucciones operativas para el operador
    """
    
    # Datos
    tamices = resultado['tamices']
    mix_pasante_actual = resultado['mix_pasante']
    validacion = resultado['validacion']
    
    # Para tabla virtual/corregida
    validacion_correg = propuesta.get('validacion', {})
    mix_resultado = validacion_correg.get('mix_resultado_pasante', [])
    
    # ===== GRÁFICOS =====
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    
    # Gráfico 1: Comparación actual vs corregida
    ax1 = fig.add_subplot(gs[0, :])
    ax1.semilogx(tamices, mix_pasante_actual, 'o-', linewidth=3, markersize=10, 
                 label='ACTUAL (Mezcla actual)', color='blue')
    ax1.semilogx(tamices, mix_resultado, 's-', linewidth=3, markersize=10, 
                 label='CORREGIDA (Con propuesta)', color='red')
    
    # Bandas de especificación
    banda_min_list = []
    banda_max_list = []
    for t in tamices:
        t_str = str(t)
        if t_str in LIMITES['bloco']:
            min_v, max_v = LIMITES['bloco'][t_str]
            banda_min_list.append(min_v)
            banda_max_list.append(max_v)
    
    if banda_min_list:
        ax1.fill_between(tamices, banda_min_list, banda_max_list, alpha=0.15, color='green', 
                        label='Banda especificación')
        
        centro_banda = [(b + a) / 2 for a, b in zip(banda_min_list, banda_max_list)]
        banda_ideal_min = [c - 5.5 for c in centro_banda]
        banda_ideal_max = [c + 5.5 for c in centro_banda]
        ax1.fill_between(tamices, banda_ideal_min, banda_ideal_max, alpha=0.25, color='orange', 
                        label='Banda ideal (±5.5%)')
    
    ax1.set_xscale('log')
    ax1.set_xticks(tamices)
    ax1.set_xticklabels([f'{t}' for t in tamices], fontsize=11)
    ax1.set_ylabel("Pasante acumulado (%)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Tamiz (mm)", fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 105)
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11, framealpha=0.95)
    ax1.set_title("COMPARACIÓN: Curva Actual vs Curva Corregida con Propuesta de 3 Agregados", 
                 fontsize=13, fontweight='bold')
    
    # Gráfico 2: Error por tamiz
    ax2 = fig.add_subplot(gs[1, 0])
    
    error_actual = []
    error_correg = []
    for t, actual, correg in zip(tamices, mix_pasante_actual, mix_resultado):
        t_str = str(t)
        if t_str in LIMITES['bloco']:
            band_min, band_max = LIMITES['bloco'][t_str]
            err_act = max(0, band_min - actual, actual - band_max)
            err_cor = max(0, band_min - correg, correg - band_max)
            error_actual.append(err_act)
            error_correg.append(err_cor)
    
    x_pos = np.arange(len(tamices))
    width = 0.35
    ax2.bar(x_pos - width/2, error_actual, width, label='Actual', color='blue', 
            alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.bar(x_pos + width/2, error_correg, width, label='Corregida', color='red', 
            alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f'{t}' for t in tamices], fontsize=10)
    ax2.set_ylabel("Error (%)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Tamiz (mm)", fontsize=11, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.set_title("ERROR por Tamiz: Actual vs Corregida", fontsize=12, fontweight='bold')
    ax2.grid(True, axis='y', alpha=0.3)
    
    # Gráfico 3: Cumplimiento
    ax3 = fig.add_subplot(gs[1, 1])
    
    cumpl_actual = sum(1 for bloco in validacion.get('bloco', []) if bloco.get('ok') == True)
    cumpl_correg = sum(1 for i in range(len(mix_resultado)) 
                      if i < len(tamices) and 
                      (LIMITES['bloco'].get(str(tamices[i]), [0, 100])[0] <= mix_resultado[i] <= 
                       LIMITES['bloco'].get(str(tamices[i]), [0, 100])[1]))
    total_tamices = len(tamices)
    
    categorias = ['Cumplimiento\nActual', 'Cumplimiento\nCorregida']
    valores = [cumpl_actual, cumpl_correg]
    colores = ['blue', 'red']
    
    bars = ax3.bar(categorias, valores, color=colores, alpha=0.7, edgecolor='black', linewidth=2, width=0.5)
    
    for bar, val in zip(bars, valores):
        altura = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., altura + 0.2,
                f'{int(val)}/{total_tamices}\n({(val/total_tamices)*100:.0f}%)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax3.set_ylim(0, total_tamices + 1)
    ax3.set_ylabel("Tamices en especificación", fontsize=11, fontweight='bold')
    ax3.set_title("CUMPLIMIENTO de Especificación", fontsize=12, fontweight='bold')
    ax3.grid(True, axis='y', alpha=0.3)
    
    # Tabla 1: Curva actual
    ax_tabla1 = fig.add_subplot(gs[2, 0])
    ax_tabla1.axis('tight')
    ax_tabla1.axis('off')
    
    tabla1_datos = [['Tamiz (mm)', 'Pasante Actual (%)', 'Estado']]
    for t, p in zip(tamices, mix_pasante_actual):
        t_str = str(t)
        if t_str in LIMITES['bloco']:
            band_min, band_max = LIMITES['bloco'][t_str]
            en_banda = band_min <= p <= band_max
            estado = '✓ OK' if en_banda else f'✗ FUERA'
        else:
            estado = '?'
        tabla1_datos.append([f'{t:.2f}', f'{p:.2f}', estado])
    
    tabla1_datos.append(['TOTAL', f'{cumpl_actual}/{total_tamices}', f'{(cumpl_actual/total_tamices)*100:.0f}%'])
    
    tabla1 = ax_tabla1.table(cellText=tabla1_datos, cellLoc='center', loc='center',
                            bbox=[0, 0, 1, 1], colWidths=[0.25, 0.35, 0.40])
    tabla1.auto_set_font_size(False)
    tabla1.set_fontsize(9)
    tabla1.scale(1, 2)
    
    # Colores tabla1
    for i in range(3):
        tabla1[(0, i)].set_facecolor('#4472C4')
        tabla1[(0, i)].set_text_props(weight='bold', color='white')
    for i in range(1, len(tabla1_datos)-1):
        for j in range(3):
            tabla1[(i, j)].set_facecolor('#E7E6E6' if i % 2 == 0 else '#F2F2F2')
    for j in range(3):
        tabla1[(len(tabla1_datos)-1, j)].set_facecolor('#FFD966')
        tabla1[(len(tabla1_datos)-1, j)].set_text_props(weight='bold')
    
    ax_tabla1.set_title("CURVA ACTUAL", fontsize=11, fontweight='bold', pad=10)
    
    # Tabla 2: Curva corregida
    ax_tabla2 = fig.add_subplot(gs[2, 1])
    ax_tabla2.axis('tight')
    ax_tabla2.axis('off')
    
    tabla2_datos = [['Tamiz (mm)', 'Pasante Corregida (%)', 'Estado']]
    for t, p in zip(tamices, mix_resultado):
        t_str = str(t)
        if t_str in LIMITES['bloco']:
            band_min, band_max = LIMITES['bloco'][t_str]
            en_banda = band_min <= p <= band_max
            estado = '✓ OK' if en_banda else f'✗ FUERA'
        else:
            estado = '?'
        tabla2_datos.append([f'{t:.2f}', f'{p:.2f}', estado])
    
    tabla2_datos.append(['TOTAL', f'{cumpl_correg}/{total_tamices}', f'{(cumpl_correg/total_tamices)*100:.0f}%'])
    
    tabla2 = ax_tabla2.table(cellText=tabla2_datos, cellLoc='center', loc='center',
                            bbox=[0, 0, 1, 1], colWidths=[0.25, 0.35, 0.40])
    tabla2.auto_set_font_size(False)
    tabla2.set_fontsize(9)
    tabla2.scale(1, 2)
    
    # Colores tabla2
    for i in range(3):
        tabla2[(0, i)].set_facecolor('#C00000')
        tabla2[(0, i)].set_text_props(weight='bold', color='white')
    for i in range(1, len(tabla2_datos)-1):
        for j in range(3):
            tabla2[(i, j)].set_facecolor('#F4CCCC' if i % 2 == 0 else '#FCE4D6')
    for j in range(3):
        tabla2[(len(tabla2_datos)-1, j)].set_facecolor('#92D050')
        tabla2[(len(tabla2_datos)-1, j)].set_text_props(weight='bold')
    
    ax_tabla2.set_title("CURVA CORREGIDA", fontsize=11, fontweight='bold', pad=10)
    
    plt.savefig('/workspaces/multiMaquinaGervasi/test_propuesta_graficos.png', dpi=150, bbox_inches='tight')
    print("\n✅ Gráficos guardados: test_propuesta_graficos.png")
    
    # ===== INSTRUCCIONES OPERATIVAS =====
    print("\n" + "="*80)
    print("INSTRUCCIONES OPERATIVAS PARA EL OPERADOR")
    print("="*80)
    
    prop_data = propuesta.get('propuesta', {})
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   CARGA DE AGREGADOS EN LA MÁQUINA                         ║
║                  Solución: 3 Agregados Correctivos (M1, M2, M3)           ║
╚════════════════════════════════════════════════════════════════════════════╝

📊 RESUMEN DE MEJORA:
   • Cumplimiento actual:    {cumplimiento_pct:>6.1f}% ({cumpl_actual}/{total_tamices} tamices)
   • Cumplimiento esperado:  {cumplimiento_corregido:>6.1f}% ({cumpl_correg}/{total_tamices} tamices)
   • Mejora neta:            {cumplimiento_corregido - cumplimiento_pct:>+6.1f}% puntos

─────────────────────────────────────────────────────────────────────────────

🔹 AGREGADO M1 (ZONA GRUESA) - Cantidad: {prop_data['m1']['proporcion_recomendada_pct']:.1f}%
   ┌─ Función: {prop_data['m1']['razon_tecnica']}
   ├─ Distribución por tamiz:
""")
    
    for i, (tamiz, ret) in enumerate(zip(tamices, prop_data['m1']['retido_ind_pct'])):
        if ret > 0.1:
            print(f"   │   Tamiz {tamiz:>6} mm: {ret:>6.2f}% de M1")
    
    print(f"""   └─ Pasante total M1: {[round(x, 1) for x in prop_data['m1']['pasante_pct'][:3]]}...

─────────────────────────────────────────────────────────────────────────────

🔹 AGREGADO M2 (ZONA MEDIA) - Cantidad: {prop_data['m2']['proporcion_recomendada_pct']:.1f}%
   ┌─ Función: {prop_data['m2']['razon_tecnica']}
   ├─ Distribución por tamiz:
""")
    
    for i, (tamiz, ret) in enumerate(zip(tamices, prop_data['m2']['retido_ind_pct'])):
        if ret > 0.1:
            print(f"   │   Tamiz {tamiz:>6} mm: {ret:>6.2f}% de M2")
    
    print(f"""   └─ Pasante total M2: {[round(x, 1) for x in prop_data['m2']['pasante_pct'][:3]]}...

─────────────────────────────────────────────────────────────────────────────

🔹 AGREGADO M3 (ZONA FINA) - Cantidad: {prop_data['m3']['proporcion_recomendada_pct']:.1f}%
   ┌─ Función: {prop_data['m3']['razon_tecnica']}
   ├─ Distribución por tamiz:
""")
    
    for i, (tamiz, ret) in enumerate(zip(tamices, prop_data['m3']['retido_ind_pct'])):
        if ret > 0.1:
            print(f"   │   Tamiz {tamiz:>6} mm: {ret:>6.2f}% de M3")
    
    print(f"""   └─ Pasante total M3: {[round(x, 1) for x in prop_data['m3']['pasante_pct'][:3]]}...

═════════════════════════════════════════════════════════════════════════════

⚙️  PROCEDIMIENTO DE CARGA OPERATIVA:

PASO 1 - Preparación inicial:
   ✓ Vaciar la máquina o trabajar con cantidad mínima de mezcla anterior
   ✓ Limpiar bandejas y tamices para especificación
   ✓ Verificar básculas calibradas

PASO 2 - Cargar secuencialmente por tamiz (comenzar por mayor):
   
""")
    
    # Calcular cantidades para cada zona por tamiz (asumiendo 100 kg total)
    total_cantidad = 100.0  # kg de referencia
    
    # M1, M2, M3 en kg
    m1_kg = (prop_data['m1']['proporcion_recomendada_pct'] / 100) * total_cantidad
    m2_kg = (prop_data['m2']['proporcion_recomendada_pct'] / 100) * total_cantidad
    m3_kg = (prop_data['m3']['proporcion_recomendada_pct'] / 100) * total_cantidad
    
    for tamiz, ret_m1, ret_m2, ret_m3 in zip(
        tamices,
        prop_data['m1']['retido_ind_pct'],
        prop_data['m2']['retido_ind_pct'],
        prop_data['m3']['retido_ind_pct']
    ):
        # Cantidad en cada bandeja por tamiz
        cant_m1_tamiz = (ret_m1 / 100) * m1_kg
        cant_m2_tamiz = (ret_m2 / 100) * m2_kg
        cant_m3_tamiz = (ret_m3 / 100) * m3_kg
        cant_total_tamiz = cant_m1_tamiz + cant_m2_tamiz + cant_m3_tamiz
        
        if cant_total_tamiz > 0.1:
            print(f"""   📍 TAMIZ {tamiz:>6} mm:
      M1: {cant_m1_tamiz:>7.2f} kg  ({ret_m1:>6.2f}%)
      M2: {cant_m2_tamiz:>7.2f} kg  ({ret_m2:>6.2f}%)
      M3: {cant_m3_tamiz:>7.2f} kg  ({ret_m3:>6.2f}%)
      ─────────────────
      TOTAL: {cant_total_tamiz:>6.2f} kg (100%)
""")
    
    print(f"""
PASO 3 - Verificación Final:
   ✓ M1 total: {m1_kg:>6.2f} kg ({prop_data['m1']['proporcion_recomendada_pct']:.1f}%)
   ✓ M2 total: {m2_kg:>6.2f} kg ({prop_data['m2']['proporcion_recomendada_pct']:.1f}%)
   ✓ M3 total: {m3_kg:>6.2f} kg ({prop_data['m3']['proporcion_recomendada_pct']:.1f}%)
   ✓ TOTAL:    {total_cantidad:>6.2f} kg (100.0%)

PASO 4 - Test de Calidad:
   ✓ Ejecutar tamizado de muestra
   ✓ Comparar resultados con banda especificación
   ✓ Validar cumplimiento ≥ {cumplimiento_corregido:.0f}% tamices

═════════════════════════════════════════════════════════════════════════════

✅ NOTAS IMPORTANTES:
   • Las cantidades mostradas son PROPORCIONALES a 100 kg
   • Escalar proporcionalmente a su cantidad disponible
   • M1 → Agregado grueso (zona 9.5-4.8 mm)
   • M2 → Agregado medio (zona 2.4-0.6 mm)
   • M3 → Agregado fino (zona 0.3-0.15 mm)
   • Mezclar homogéneamente antes de tamizado final
""")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    success, resultado, cumpl_pct, cumpl_correg, propuesta = test_granulometria_completa()
    
    if success and resultado is not None:
        generar_graficos_y_instrucciones(resultado, cumpl_pct, cumpl_correg, propuesta)
    elif not success:
        sys.exit(1)
