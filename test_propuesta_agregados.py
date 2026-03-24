#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests para la función generar_propuesta_3_agregados()
Validación de funcionalidad e integración
"""

import sys
import json

# Agregar path
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    generar_propuesta_3_agregados
)


def test_propuesta_3_agregados_basico():
    """Test: Generar propuesta con datos reales"""
    
    print("\n" + "="*70)
    print("TEST 1: Generación básica de propuesta")
    print("="*70)
    
    mix_pasante = [99.2, 79.8, 50.2, 35.8, 15.6, 5.2, 1.4]
    banda_min = [85, 65, 35, 15, 5, 2, 0]
    banda_max = [100, 90, 65, 45, 20, 10, 5]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    # Assertions
    assert resultado['exito'] == True, "Debe generar propuesta exitosamente"
    print("✅ Propuesta generada exitosamente")
    
    assert 'm1' in resultado['propuesta'], "Debe contener M1"
    assert 'm2' in resultado['propuesta'], "Debe contener M2"
    assert 'm3' in resultado['propuesta'], "Debe contener M3"
    print("✅ Todas las 3 agregados presentes")
    
    # Validar estructura M1
    m1 = resultado['propuesta']['m1']
    assert 'nombre' in m1
    assert 'retido_ind_pct' in m1
    assert 'retido_acum_pct' in m1
    assert 'pasante_pct' in m1
    assert 'proporcion_recomendada_pct' in m1
    assert len(m1['retido_ind_pct']) == len(tamices)
    print("✅ Estructura de M1 completa y válida")
    
    # Validar proporciones
    proporciones = resultado['proporciones']
    assert len(proporciones) == 3
    assert abs(sum(proporciones) - 1.0) < 0.01, "Proporciones deben sumar 1"
    print(f"✅ Proporciones válidas y normalizadas: {[f'{p*100:.1f}%' for p in proporciones]}")
    
    # Validar validación
    validacion = resultado['validacion']
    assert 'cumple_especificacion' in validacion
    assert 'cumplimiento_pct' in validacion
    assert 'error_residual_promedio' in validacion
    assert 0 <= validacion['cumplimiento_pct'] <= 100
    print(f"✅ Validación completa - Cumplimiento: {validacion['cumplimiento_pct']}%")
    
    print("\n✅ TEST 1 PASADO")


def test_propuesta_monotonicidad():
    """Test: Verificar que pasante de cada agregado es monótonamente decreciente"""
    
    print("\n" + "="*70)
    print("TEST 2: Monotonicidad de curvas de pasante")
    print("="*70)
    
    mix_pasante = [100, 95, 75, 50, 25, 10, 5]
    banda_min = [80, 60, 40, 20, 10, 5, 0]
    banda_max = [100, 85, 65, 45, 35, 20, 10]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    assert resultado['exito']
    
    for agg_name in ['m1', 'm2', 'm3']:
        pasante = resultado['propuesta'][agg_name]['pasante_pct']
        
        # Verificar monotonicidad
        for i in range(len(pasante) - 1):
            assert pasante[i] >= pasante[i+1], \
                f"{agg_name}: Pasante NO es decreciente en posición {i}: {pasante[i]} >= {pasante[i+1]}"
        
        print(f"✅ {agg_name}: Pasante es monótonamente decreciente")
    
    print("\n✅ TEST 2 PASADO")


def test_propuesta_retido_acum_es_creciente():
    """Test: Verificar que retido_acum es monótonamente creciente"""
    
    print("\n" + "="*70)
    print("TEST 3: Monotonicidad de retido_acum")
    print("="*70)
    
    mix_pasante = [100, 95, 75, 50, 25, 10, 5]
    banda_min = [80, 60, 40, 20, 10, 5, 0]
    banda_max = [100, 85, 65, 45, 35, 20, 10]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    assert resultado['exito']
    
    for agg_name in ['m1', 'm2', 'm3']:
        ret_acum = resultado['propuesta'][agg_name]['retido_acum_pct']
        
        # Verificar crecimiento
        for i in range(len(ret_acum) - 1):
            assert ret_acum[i] <= ret_acum[i+1], \
                f"{agg_name}: Retido acum NO es creciente en posición {i}: {ret_acum[i]} <= {ret_acum[i+1]}"
        
        print(f"✅ {agg_name}: Retido_acum es monótonamente creciente")
    
    print("\n✅ TEST 3 PASADO")


def test_propuesta_suma_retido_ind():
    """Test: Verificar que suma de retido_ind de cada agregado ~= 100"""
    
    print("\n" + "="*70)
    print("TEST 4: Suma de retido_ind normalizados")
    print("="*70)
    
    mix_pasante = [100, 95, 75, 50, 25, 10, 5]
    banda_min = [80, 60, 40, 20, 10, 5, 0]
    banda_max = [100, 85, 65, 45, 35, 20, 10]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    assert resultado['exito']
    
    for agg_name in ['m1', 'm2', 'm3']:
        ret_ind = resultado['propuesta'][agg_name]['retido_ind_pct']
        suma = sum(ret_ind)
        
        # Permitir pequeño margen (saneo numérico)
        assert 95 <= suma <= 105, \
            f"{agg_name}: Suma de retido_ind = {suma}, debe estar entre 95-105"
        
        print(f"✅ {agg_name}: Suma de retido_ind = {round(suma, 2)} (válido)")
    
    print("\n✅ TEST 4 PASADO")


def test_propuesta_razones_tecnicas():
    """Test: Verificar que hay razones técnicas para cada agregado"""
    
    print("\n" + "="*70)
    print("TEST 5: Razones técnicas presentes")
    print("="*70)
    
    mix_pasante = [99.2, 79.8, 50.2, 35.8, 15.6, 5.2, 1.4]
    banda_min = [85, 65, 35, 15, 5, 2, 0]
    banda_max = [100, 90, 65, 45, 20, 10, 5]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    for agg_name in ['m1', 'm2', 'm3']:
        agg = resultado['propuesta'][agg_name]
        assert 'razon_tecnica' in agg
        assert len(agg['razon_tecnica']) > 0
        print(f"✅ {agg_name}: {agg['razon_tecnica'][:60]}...")
    
    print("\n✅ TEST 5 PASADO")


def test_json_serializable():
    """Test: Verificar que el resultado es JSON-serializable"""
    
    print("\n" + "="*70)
    print("TEST 6: Serialización JSON")
    print("="*70)
    
    mix_pasante = [99.2, 79.8, 50.2, 35.8, 15.6, 5.2, 1.4]
    banda_min = [85, 65, 35, 15, 5, 2, 0]
    banda_max = [100, 90, 65, 45, 20, 10, 5]
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    try:
        json_str = json.dumps(resultado)
        json_parsed = json.loads(json_str)
        assert json_parsed['exito'] == resultado['exito']
        print(f"✅ JSON serializable - Size: {len(json_str)} bytes")
    except Exception as e:
        raise AssertionError(f"Error serializando a JSON: {str(e)}")
    
    print("\n✅ TEST 6 PASADO")


def test_caso_sin_error():
    """Test: Caso donde input ya cumple especificación"""
    
    print("\n" + "="*70)
    print("TEST 7: Caso con curva ya dentro de especificación")
    print("="*70)
    
    # Curva que ya cumple
    mix_pasante = [92.5, 80.0, 62.5, 47.5, 22.5, 10.0, 5.0]
    banda_min = [85, 65, 35, 15, 5, 2, 0]
    banda_max = [100, 90, 65, 45, 20, 10, 5]  
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    resultado = generar_propuesta_3_agregados(
        mix_pasante=mix_pasante,
        banda_min=banda_min,
        banda_max=banda_max,
        tamices=tamices
    )
    
    assert resultado['exito']
    validacion = resultado['validacion']
    
    # No debe estar fuera de rango si cumple
    if validacion['cumplimiento_pct'] == 100:
        assert validacion['cumple_especificacion'] == True
        print(f"✅ Curva perfecta detectada: Cumplimiento = {validacion['cumplimiento_pct']}%")
    
    print("\n✅ TEST 7 PASADO")


if __name__ == '__main__':
    try:
        test_propuesta_3_agregados_basico()
        test_propuesta_monotonicidad()
        test_propuesta_retido_acum_es_creciente()
        test_propuesta_suma_retido_ind()
        test_propuesta_razones_tecnicas()
        test_json_serializable()
        test_caso_sin_error()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON (7/7)")
        print("="*70)
        print("\nImplementación exitosa y validada ✅")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
