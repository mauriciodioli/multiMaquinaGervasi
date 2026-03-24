#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST REAL: Granulometría - Validación completa del módulo
Prueba con datos reales de Gervasi
"""

import sys
import json
from pathlib import Path

# Agregar paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Usar importlib para forzar la recarga del módulo
import importlib.util

# Cargar el módulo calculoPorRetenidos.py desde su ruta
spec = importlib.util.spec_from_file_location(
    "calc_module",
    "/workspaces/multiMaquinaGervasi/src/controller/autoDensidad/calculoPorRetenidos/calculoPorRetenidos.py"
)
calc_module = importlib.util.module_from_spec(spec)
# Registrar en sys.modules para que las importaciones relativas funcionen
sys.modules['calculoPorRetenidos'] = calc_module

spec.loader.exec_module(calc_module)

# Extraer funciones del módulo
_acum_desc = calc_module._acum_desc
_mezcla_ponderada_acum = calc_module._mezcla_ponderada_acum
_validar_faixas = calc_module._validar_faixas
generar_propuesta_3_agregados = calc_module.generar_propuesta_3_agregados


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
    
    # Paso 4: Validar contra faixas
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
# TESTS Y VALIDACIONES
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
                banda_min = d.get('banda_min', 0)
                pasante = d.get('pasante', 0)
                banda_max = d.get('banda_max', 100)
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
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FALLIDA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    success = test_granulometria_completa()
    
    if not success:
        sys.exit(1)
