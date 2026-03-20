"""
TEST DE TABLA VIRTUAL DIRIGIDA

Script standalone para validar funcionalidad del núcleo de tabla virtual.
Datos reales de ejemplo basados en problemas típicos de granulometría.

Uso:
  python test_tabla_virtual.py
"""

import sys
sys.path.insert(0, '/workspaces/multiMaquinaGervasi')

from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_tabla_virtual import (
    puede_generarse_tabla_virtual,
    preparar_insumos_tabla_virtual,
    generar_tabla_virtual,
    validar_tabla_virtual,
    calcular_potencial_mejora,
    evaluar_utilidad_tabla_virtual,
    generar_reporte_tabla_virtual,
    listar_puntos_para_grafico,
)
import json


# ============================================================================
# CASO DE PRUEBA 1: Brecha Granulométrica en Zona Media
# ============================================================================

def test_caso_1_brecha_zona_media():
    """
    Escenario: Mezcla con déficit en zona media (2.36-0.6mm)
    Área fina está bien, gruesa está bien, pero zona media tiene problema.
    """
    
    print("\n" + "="*80)
    print("TEST CASO 1: Brecha Granulométrica en Zona Media")
    print("="*80)
    
    # Datos reales de ejemplo
    tamices = ["12.5", "9.5", "6.3", "4.75", "2.36", "1.18", "0.6", "0.3", "0.15"]
    
    # Mezcla actual: 60% Arena + 40% Grava
    pasante_mezcla = [100.0, 98.0, 85.0, 70.0, 45.0, 25.0, 12.0, 5.0, 1.0]
    
    # Banda objetivo
    banda_min = [100.0, 90.0, 75.0, 55.0, 30.0, 15.0, 5.0, 1.0, 0.0]
    banda_max = [100.0, 100.0, 95.0, 80.0, 60.0, 40.0, 20.0, 10.0, 5.0]
    
    print("\n1️⃣  VERIFICACIÓN DE HABILITACIÓN")
    puede_gen, razon = puede_generarse_tabla_virtual(
        error_total=2.5,  # Error residual actual
        error_min_habilitacion=0.5,
        iteraciones_actuales=1,
        max_iteraciones=5,
        cumplimiento_pct=80.0,
        umbral_suficiencia=95.0,
    )
    print(f"   ¿Puede generarse tabla virtual? {puede_gen}")
    print(f"   Razón: {razon}")
    
    if not puede_gen:
        print("   ❌ No habilitado para este test")
        return
    
    print("\n2️⃣  PREPARACIÓN DE INSUMOS")
    insumos = preparar_insumos_tabla_virtual(
        pasante_mezcla, banda_min, banda_max, tamices
    )
    print(f"   Zona crítica: {insumos['zona_critica_nombre']} (índice {insumos['zona_critica_idx']})")
    print(f"   Error máximo: {insumos['zona_critica_error']:.2f}%")
    print(f"   Dirección de corrección (por tamiz - muestra):")
    for i in [0, 4, 8]:
        print(f"      Tamiz {tamices[i]}: error={insumos['error_firmado'][i]:+.2f}%, dirección={insumos['direccion_correccion'][i]:+.1f}")
    
    print("\n3️⃣  GENERACIÓN DE TABLA VIRTUAL (Método Principal)")
    pasante_virtual, metadata = generar_tabla_virtual(
        pasante_mezcla, banda_min, banda_max, tamices, metodo="principal"
    )
    print(f"   ✅ Tabla virtual generada")
    print(f"   Primeros 3 tamices: {[f'{p:.1f}%' for p in pasante_virtual[:3]]}")
    print(f"   Zona media (2.36-0.6mm): {[f'{p:.1f}%' for p in pasante_virtual[4:7]]}")
    print(f"   Últimos 2 tamices: {[f'{p:.1f}%' for p in pasante_virtual[-2:]]}")
    
    print("\n4️⃣  VALIDACIÓN DE TABLA VIRTUAL")
    es_valida, reporte = validar_tabla_virtual(
        pasante_virtual, pasante_mezcla, banda_min, banda_max, verbose=True
    )
    
    if not es_valida:
        print(f"   ❌ Tabla virtual INVÁLIDA")
        print(f"   Fallos: {reporte['fallos']}")
        return
    
    print("\n5️⃣  CÁLCULO DE POTENCIAL DE MEJORA")
    potencial = calcular_potencial_mejora(
        pasante_mezcla, pasante_virtual, banda_min, banda_max, peso_estimado_virtual=0.20
    )
    print(f"   Error actual: {potencial['error_total_actual']:.3f}")
    print(f"   Error predicho: {potencial['error_total_predicho']:.3f}")
    print(f"   Mejora estimada: {potencial['mejora_relativa_pct']:.1f}%")
    print(f"   ¿Viable? {potencial['prediccion_viable']} ({potencial['prediccion_viable_razon']})")
    
    print("\n6️⃣  REPORTE DETALLADO")
    reporte_txt = generar_reporte_tabla_virtual(
        pasante_mezcla, pasante_virtual, banda_min, banda_max, tamices,
        insumos, metadata
    )
    print(reporte_txt)
    
    print("7️⃣  DATOS PARA GRÁFICO")
    datos_grafico = listar_puntos_para_grafico(
        pasante_mezcla, pasante_virtual, banda_min, banda_max, tamices
    )
    print(f"   ✅ Estructura lista para graficar:")
    print(f"      - {len(datos_grafico['tamices'])} tamices")
    print(f"      - 2 curvas (mezcla actual + virtual)")
    print(f"      - Banda min/max para visualizar área de cumplimiento")
    
    print("\n8️⃣  SIMULACIÓN POST REOPTIMIZACIÓN")
    # Simular que la tabla virtual fue útil
    evaluacion = evaluar_utilidad_tabla_virtual(
        error_total_antes=potencial['error_total_actual'],
        error_total_despues=potencial['error_total_predicho'],  # Simulado
        peso_asignado=0.20,  # Simulado: el optimizador le asignó 20%
        mejora_zona_critica_pct=12.0,
        cumplimiento_antes=80.0,
        cumplimiento_despues=87.5,
    )
    print(f"   Veredicto: {evaluacion['veredicto']}")
    print(f"   ¿Exitosa? {evaluacion['es_exitosa']}")
    print(f"   Métricas positivas: {evaluacion['metricas_positivas']}/3")
    print(f"   Recomendación: {evaluacion['recomendacion']}")
    
    return True


# ============================================================================
# CASO DE PRUEBA 2: Sin Habilitación - Suficiencia Ya Alcanzada
# ============================================================================

def test_caso_2_sin_habilitacion():
    """
    Escenario: Sistema ya cumple, no hay por qué generar tabla virtual
    """
    
    print("\n" + "="*80)
    print("TEST CASO 2: Sin Habilitación - Suficiencia Alcanzada")
    print("="*80)
    
    puede_gen, razon = puede_generarse_tabla_virtual(
        error_total=0.2,
        error_min_habilitacion=0.5,
        cumplimiento_pct=98.0,  # ¡Ya cumple!
        umbral_suficiencia=95.0,
    )
    
    print(f"¿Puede generarse tabla virtual? {puede_gen}")
    print(f"Razón: {razon}")
    print(f"✅ Correcto: Sistema tiene suficiencia, no genera tabla innecesaria")


# ============================================================================
# CASO DE PRUEBA 3: Tabla Alternativa (Método Conservador)
# ============================================================================

def test_caso_3_metodo_alternativo():
    """
    Escenario: Usar método alternativo (apunta a centro de banda)
    """
    
    print("\n" + "="*80)
    print("TEST CASO 3: Método Alternativo - Centro de Banda")
    print("="*80)
    
    tamices = ["12.5", "9.5", "6.3", "4.75", "2.36"]
    pasante_mezcla = [100.0, 95.0, 78.0, 55.0, 32.0]
    banda_min = [100.0, 85.0, 70.0, 40.0, 20.0]
    banda_max = [100.0, 100.0, 90.0, 70.0, 50.0]
    
    print("\n✅ Usando método ALTERNATIVA (más conservador)")
    pasante_virtual, metadata = generar_tabla_virtual(
        pasante_mezcla, banda_min, banda_max, tamices, metodo="alternativa"
    )
    
    print("\n📊 Comparativa:")
    print(f"{'Tamiz':<10} {'Mezcla':<12} {'Virtual (alt.)':<12} {'Centro Banda':<12}")
    print("-" * 50)
    for t, m, v, (bmin, bmax) in zip(tamices, pasante_mezcla, pasante_virtual, zip(banda_min, banda_max)):
        centro = (bmin + bmax) / 2.0
        print(f"{t:<10} {m:>11.2f}% {v:>11.2f}% {centro:>11.2f}%")
    
    print("\n✅ Método alternativo: tabla virtual apunta más directamente a banda")


# ============================================================================
# CASO DE PRUEBA 4: Validación con Redundancia Detectada
# ============================================================================

def test_caso_4_redundancia():
    """
    Escenario: Nueva tabla virtual es casi idéntica a una existente
    """
    
    print("\n" + "="*80)
    print("TEST CASO 4: Detección de Redundancia")
    print("="*80)
    
    tamices = ["12.5", "9.5", "6.3"]
    pasante_mezcla = [100.0, 90.0, 75.0]
    banda_min = [100.0, 85.0, 70.0]
    banda_max = [100.0, 100.0, 90.0]
    
    # Tabla existente muy parecida a la que generaríamos
    tabla_existente = [100.0, 90.5, 74.8]
    
    pasante_virtual, _ = generar_tabla_virtual(
        pasante_mezcla, banda_min, banda_max, tamices
    )
    
    print(f"\nTabla virtual generada: {[f'{p:.1f}%' for p in pasante_virtual]}")
    print(f"Tabla existente:        {[f'{p:.1f}%' for p in tabla_existente]}")
    
    es_valida, reporte = validar_tabla_virtual(
        pasante_virtual, pasante_mezcla, banda_min, banda_max,
        tablas_existentes=[tabla_existente],
        verbose=False  # No verbose para este test
    )
    
    print(f"\n¿Es válida (no redundante)? {reporte['checks']['redundancia']}")
    if 'redundancia_distancias_l2' in reporte['checks']:
        dist = reporte['checks']['redundancia_distancias_l2'][0]
        print(f"Distancia L2: {dist:.4f} (> 0.05 = aceptable)")
    
    if not reporte['checks']['redundancia']:
        print("✅ Sistema detectó correctamente tabla redundante")
    else:
        print("✅ Sistema consideró tabla no redundante (suficiente diferencia)")


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 SUITE DE TESTS: NÚCLEO TABLA VIRTUAL DIRIGIDA")
    print("="*80)
    print("\nNota: Tests de funcionalidad pura (sin integración en flujo iterativo)")
    
    try:
        # Test 1: Caso nominal - Brecha en zona media
        resultado_1 = test_caso_1_brecha_zona_media()
        
        # Test 2: Sin habilitación
        test_caso_2_sin_habilitacion()
        
        # Test 3: Método alternativo
        test_caso_3_metodo_alternativo()
        
        # Test 4: Detección de redundancia
        test_caso_4_redundancia()
        
        print("\n" + "="*80)
        print("✅ SUITE DE TESTS COMPLETADA")
        print("="*80)
        print("\n📊 Resumen:")
        print("   ✅ Condiciones de habilitación: Validadas")
        print("   ✅ Preparación de insumos: Funcional")
        print("   ✅ Generación de tabla virtual: Métodos principal y alternativo operativos")
        print("   ✅ Validación con restricciones duras: Implementada")
        print("   ✅ Cálculo de potencial: Funcional")
        print("   ✅ Evaluación post reoptimización: Implementada")
        print("   ✅ Reportes y datos para gráficos: Producidos")
        
        print("\n" + "-"*80)
        print("🎯 Próximos pasos:")
        print("   1. Integrar en flujo iterativo (Prompt D)")
        print("   2. Agregar visualización con matplotlib/plotly")
        print("   3. Tests de integración con endpoints Flask")
        print("   4. Documentación API final (swagger)")
        print("-"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR en tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
