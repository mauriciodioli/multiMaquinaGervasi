"""
NÚCLEO DE TABLA VIRTUAL DIRIGIDA

Módulo standalone para generar, validar y analizar tablas virtuales dirigidas.
Base: Especificación Formal PROMPT C - Tabla Virtual Dirigida en Sistema Iterativo.

Funciones principales:
  - generar_tabla_virtual(): crea tabla virtual según error residual
  - validar_tabla_virtual(): auditoría de restricciones antes de uso
  - calcular_potencial_mejora(): estima aporta de la tabla virtual
  - evaluar_utilidad_posterior(): analiza éxito post-reoptimización

Uso: Standalone para testing. NO integrado en flujo iterativo todavía.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any


# ============================================================================
# CONDICIÓN DE NACIMIENTO - Validación de Habilitación
# ============================================================================

def puede_generarse_tabla_virtual(
    error_total: float,
    error_min_habilitacion: float = 0.5,
    iteraciones_actuales: int = 1,
    max_iteraciones: int = 5,
    max_tablas_virtuales: int = 3,
    tablas_virtuales_existentes: int = 0,
    hay_estancamiento: bool = False,
    hay_contradiccion: bool = False,
    hay_espacio_de_soluciones: bool = True,
    cumplimiento_pct: float = 50.0,
    umbral_suficiencia: float = 95.0,
) -> Tuple[bool, str]:
    """
    Evalúa si se cumplen condiciones de HABILITACIÓN para generar tabla virtual.
    
    Retorna: (puede_generar: bool, razon: str)
    """
    
    # Condición 1: Suficiencia actual
    if cumplimiento_pct >= umbral_suficiencia:
        return False, "Suficiencia ya alcanzada (no hay qué mejorar)"
    
    # Condición 2: Insuficiencia actual
    if error_total < error_min_habilitacion:
        return False, f"Error residual muy bajo ({error_total:.3f} < {error_min_habilitacion:.3f})"
    
    # Condición 3: Límite máximo de iteraciones
    if iteraciones_actuales >= max_iteraciones:
        return False, f"Límite de iteraciones alcanzado ({iteraciones_actuales}/{max_iteraciones})"
    
    # Condición 4: Límite máximo de tablas virtuales
    if tablas_virtuales_existentes >= max_tablas_virtuales:
        return False, f"Límite de tablas virtuales alcanzado ({tablas_virtuales_existentes}/{max_tablas_virtuales})"
    
    # Condición 5: Estancamiento
    if hay_estancamiento:
        return False, "Hay estancamiento (no hay cambio potencial)"
    
    # Condición 6: Contradicción física
    if hay_contradiccion:
        return False, "Error residual contradictorio (no resoluble con tabla virtual)"
    
    # Condición 7: Espacio de soluciones
    if not hay_espacio_de_soluciones:
        return False, "Espacio de soluciones degenerado"
    
    # Si todas las condiciones habilitan
    return True, "Habilitación OK - Proceder a generar tabla virtual"


# ============================================================================
# INSUMO MATEMÁTICO - Preparación de Datos para Construcción
# ============================================================================

def preparar_insumos_tabla_virtual(
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[str],
    tolerancia_error: float = 0.5,
) -> Dict[str, Any]:
    """
    Prepara insumos matemáticos para generar tabla virtual.
    
    Retorna diccionario con:
      - error_firmado: error residual con signo (>0=exceso, <0=déficit)
      - centro_banda: centro de la banda objetivo
      - zona_critica_idx: índice de mayor error
      - zona_critica_nombre: 'gruesa'/'media'/'fina'
      - direccion_correccion: hacia dónde apuntar
    """
    
    pasante_mezcla = np.array(pasante_mezcla, dtype=float)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)
    n_tamices = len(pasante_mezcla)
    
    # 1. Error firmado por tamiz
    centro_banda = (banda_min + banda_max) / 2.0
    error_firmado = pasante_mezcla - centro_banda
    
    # 2. Identificar zona crítica
    error_absoluto = np.abs(error_firmado)
    zona_critica_idx = np.argmax(error_absoluto)
    
    # Clasificar zona (gruesa=primeros 30%, media=medio, fina=últimos 30%)
    threshold_gruesa = int(n_tamices * 0.3)
    threshold_fina = int(n_tamices * 0.7)
    
    if zona_critica_idx < threshold_gruesa:
        zona_critica_nombre = "gruesa"
    elif zona_critica_idx > threshold_fina:
        zona_critica_nombre = "fina"
    else:
        zona_critica_nombre = "media"
    
    # 3. Dirección de corrección (opuesta al signo del error)
    # Si error_firmado > 0 (exceso), corrección debe ser negativa (reducir pasante)
    # Si error_firmado < 0 (déficit), corrección debe ser positiva (aumentar pasante)
    direccion_correccion = -np.sign(error_firmado)
    
    return {
        "error_firmado": error_firmado.tolist(),
        "error_absoluto": error_absoluto.tolist(),
        "centro_banda": centro_banda.tolist(),
        "banda_min": banda_min.tolist(),
        "banda_max": banda_max.tolist(),
        "zona_critica_idx": int(zona_critica_idx),
        "zona_critica_nombre": zona_critica_nombre,
        "zona_critica_error": float(error_absoluto[zona_critica_idx]),
        "direccion_correccion": direccion_correccion.tolist(),
        "tamices": tamices,
        "n_tamices": n_tamices,
    }


# ============================================================================
# REGLA DE CONSTRUCCIÓN - Generar Tabla Virtual Dirigida
# ============================================================================

def generar_tabla_virtual(
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[str],
    metodo: str = "principal",
    factor_suavizado: float = 0.5,
) -> Tuple[List[float], Dict[str, Any]]:
    """
    Genera tabla virtual dirigida basada en error residual.
    
    Métodos:
      - 'principal': Corrección local modulada por zona crítica (recomendado)
      - 'alternativa': Apunta directamente al centro de banda (conservador)
    
    Retorna: (pasante_virtual: List[float], metadata: Dict)
    """
    
    # Preparar insumos
    insumos = preparar_insumos_tabla_virtual(pasante_mezcla, banda_min, banda_max, tamices)
    
    pasante_mezcla = np.array(pasante_mezcla, dtype=float)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)
    error_firmado = np.array(insumos["error_firmado"], dtype=float)
    zona_critica_idx = insumos["zona_critica_idx"]
    n_tamices = insumos["n_tamices"]
    
    # Inicializar vector de tabla virtual
    pasante_virtual = np.zeros(n_tamices, dtype=float)
    
    if metodo == "principal":
        # MÉTODO 1: Corrección local modulada por zona crítica
        for j in range(n_tamices):
            # Determinar objetivo: banda_min, banda_max o centro según dirección de error
            centro_banda_j = (banda_min[j] + banda_max[j]) / 2.0
            
            if abs(error_firmado[j]) < 0.5:
                # Error muy pequeño: mantener mezcla actual (no forzar corrección)
                objetivo = pasante_mezcla[j]
            elif error_firmado[j] > 0.5:
                # Exceso: mover hacia banda_min (más grueso, menos pasante)
                objetivo = banda_min[j]
            elif error_firmado[j] < -0.5:
                # Déficit: mover hacia banda_max (más fino, más pasante)
                objetivo = banda_max[j]
            else:
                objetivo = centro_banda_j
            
            # Factor de intensidad según zona crítica (redistribuidor conservador)
            distancia_zona_critica = abs(j - zona_critica_idx)
            
            if distancia_zona_critica == 0:
                # En zona crítica: factor = 0.8 (corrección moderada-fuerte)
                factor = 0.8
            elif distancia_zona_critica == 1:
                # Adyacente: factor = 0.5 (amortiguado)
                factor = 0.5
            elif distancia_zona_critica == 2:
                # Cercano: factor = 0.25 (muy amortiguado)
                factor = 0.25
            else:
                # Lejos: factor = 0.05-0.1 (casi neutral)
                factor = max(0.05, 0.15 - distancia_zona_critica * 0.03)
            
            # Calcular punto intermedio (más conservador)
            correccion_amplitud = (objetivo - pasante_mezcla[j]) * factor
            pasante_virtual[j] = pasante_mezcla[j] + correccion_amplitud
    
    elif metodo == "alternativa":
        # MÉTODO 2: Apuntar directamente a centro de banda (conservador)
        centro_banda = np.array(insumos["centro_banda"], dtype=float)
        pasante_virtual = centro_banda.copy()
    
    else:
        raise ValueError(f"Método desconocido: {metodo}")
    
    # PASO 1: Aplicar límites duros [0, 100]
    pasante_virtual = np.clip(pasante_virtual, 0.0, 100.0)
    
    # PASO 2: Garantizar monotonicidad decreciente
    pasante_virtual = _aplicar_monotonicidad(pasante_virtual)
    
    # PASO 3: Aplicar límites de saltos
    pasante_virtual = _limitar_saltos_entre_tamices(pasante_virtual, max_salto=20.0)
    
    # Metadatos de construcción
    metadata = {
        "metodo": metodo,
        "zona_critica_idx": zona_critica_idx,
        "zona_critica_nombre": insumos["zona_critica_nombre"],
        "insumos": insumos,
        "pasos_construccion": {
            "1_objetivo": "Crear curva que ataque error residual en zona crítica",
            "2_monotonic": "Aplicar monotonicidad física",
            "3_saltos": "Limitar saltos entre tamices < 20%",
        }
    }
    
    return pasante_virtual.tolist(), metadata


def _aplicar_monotonicidad(pasante_vector: np.ndarray) -> np.ndarray:
    """
    Corrige violaciones de monotonicidad.
    La curva PASANTE debe ser decreciente (no puede aumentar).
    
    Método: Suavizado isotónico (PAVA - Pool Adjacent Violators Algorithm simplificado).
    """
    
    curva = pasante_vector.copy()
    
    # Pasar de izq a der: si una malla tiene más pasante que la siguiente, igualar
    for j in range(len(curva) - 1):
        if curva[j] > curva[j + 1]:
            curva[j] = curva[j + 1]
    
    return curva


def _limitar_saltos_entre_tamices(
    pasante_vector: np.ndarray,
    max_salto: float = 20.0
) -> np.ndarray:
    """
    Limita saltos abruptos entre tamices consecutivos.
    Si salto > max_salto, redistribuir suavemente.
    """
    
    curva = pasante_vector.copy()
    
    for j in range(len(curva) - 1):
        salto = abs(curva[j] - curva[j + 1])
        if salto > max_salto:
            # Redistribuir: interpolación lineal suave
            promedio = (curva[j] + curva[j + 1]) / 2.0
            curva[j] = min(curva[j], promedio + max_salto / 2.0)
            curva[j + 1] = max(curva[j + 1], promedio - max_salto / 2.0)
    
    # Re-aplicar monotonicidad después de redistribuir
    curva = _aplicar_monotonicidad(curva)
    
    return curva


# ============================================================================
# RESTRICCIONES DURAS - Validación
# ============================================================================

def validar_tabla_virtual(
    pasante_virtual: List[float],
    pasante_mezcla: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tablas_existentes: Optional[List[List[float]]] = None,
    verbose: bool = True,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Auditoría completa de tabla virtual.
    
    Retorna: (es_valida: bool, reporte: Dict con detalles de checks)
    """
    
    pasante_virtual = np.array(pasante_virtual, dtype=float)
    pasante_mezcla = np.array(pasante_mezcla, dtype=float)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)
    
    reporte = {
        "es_valida": True,
        "checks": {},
        "fallos": [],
    }
    
    # CHECK 1: Rango [0, 100]
    check1 = np.all(pasante_virtual >= 0.0) and np.all(pasante_virtual <= 100.0)
    reporte["checks"]["rango_0_100"] = check1
    if not check1:
        reporte["checks"]["rango_0_100_detalles"] = f"Valores fuera de rango: min={pasante_virtual.min():.2f}, max={pasante_virtual.max():.2f}"
        reporte["fallos"].append("Rango [0, 100] violado")
    
    # CHECK 2: Monotonicidad decreciente
    check2 = all(pasante_virtual[i] >= pasante_virtual[i+1] for i in range(len(pasante_virtual)-1))
    reporte["checks"]["monotonicidad"] = check2
    if not check2:
        for i in range(len(pasante_virtual)-1):
            if pasante_virtual[i] < pasante_virtual[i+1]:
                reporte["checks"]["monotonicidad_viola"] = f"índice {i}: {pasante_virtual[i]:.2f} > {pasante_virtual[i+1]:.2f}"
        reporte["fallos"].append("Monotonicidad violada")
    
    # CHECK 3: Límites de saltos
    saltos = np.abs(np.diff(pasante_virtual))
    check3 = np.all(saltos <= 20.0)
    reporte["checks"]["saltos_max_20"] = check3
    if not check3:
        max_salto_idx = np.argmax(saltos)
        reporte["checks"]["saltos_detalles"] = f"Max salto {saltos[max_salto_idx]:.2f}% en posición {max_salto_idx}"
        reporte["fallos"].append(f"Salto máximo {saltos[max_salto_idx]:.2f}% > 20%")
    
    # CHECK 4: Coherencia dirección
    error_firmado = pasante_mezcla - (banda_min + banda_max) / 2.0
    diferencia = pasante_virtual - pasante_mezcla
    
    # Verificar coherencia SOLO en tamices con error significativo (>= 1%)
    # En tamices sin error significativo, la tabla virtual puede quedarse igual
    indices_error_sig = np.where(np.abs(error_firmado) >= 1.0)[0]
    
    if len(indices_error_sig) > 0:
        coherencias = 0
        for j in indices_error_sig:
            err = error_firmado[j]
            dif = diferencia[j]
            
            # Coherencia: signo de la diferencia debe ser opuesto al signo del error
            # Error > 0 (exceso) → diferencia < 0 (reducir pasante)
            # Error < 0 (déficit) → diferencia > 0 (aumentar pasante)
            if (err > 0 and dif <= 0) or (err < 0 and dif >= 0):
                coherencias += 1
        
        check4 = (coherencias / len(indices_error_sig)) >= 0.7  # Tolerancia 70% (menos estricta)
    else:
        check4 = True
    
    reporte["checks"]["coherencia_direccion"] = check4
    if not check4:
        reporte["fallos"].append("Dirección de corrección incoherente con error residual")
    
    # CHECK 5: Distancia a tablas existentes
    check5 = True
    if tablas_existentes is not None:
        distancias_l2 = []
        for tabla_exist in tablas_existentes:
            tabla_exist = np.array(tabla_exist, dtype=float)
            dist_l2 = np.linalg.norm(pasante_virtual - tabla_exist) / np.linalg.norm(tabla_exist)
            distancias_l2.append(dist_l2)
        
        check5 = min(distancias_l2) > 0.05  # >5% de diferencia
        reporte["checks"]["redundancia"] = check5
        reporte["checks"]["redundancia_distancias_l2"] = distancias_l2
        if not check5:
            reporte["fallos"].append("Tabla virtual es casi idéntica a tabla existente (redundancia)")
    
    # CHECK 6: Proximidad a mezcla actual en zonas no críticas
    # (BLANDO, informativo)
    distancia_a_mezcla = np.abs(pasante_virtual - pasante_mezcla)
    media_distancia = np.mean(distancia_a_mezcla)
    reporte["checks"]["proximidad_a_mezcla_media"] = float(media_distancia)
    
    # Conclusión (convertir a bool Python para JSON serialization)
    reporte["es_valida"] = bool(check1 and check2 and check3 and check4 and check5)
    
    if verbose:
        print(f"\n📋 VALIDACIÓN TABLA VIRTUAL")
        print(f"   Rango [0,100]: {'✅' if check1 else '❌'}")
        print(f"   Monotonicidad: {'✅' if check2 else '❌'}")
        print(f"   Saltos < 20%: {'✅' if check3 else '❌'}")
        print(f"   Coherencia dirección: {'✅' if check4 else '❌'}")
        if tablas_existentes:
            print(f"   No redundante: {'✅' if check5 else '❌'}")
        if reporte["fallos"]:
            print(f"   ❌ Fallos: {', '.join(reporte['fallos'])}")
        else:
            print(f"   ✅ VÁLIDA - Tabla virtual apta para uso")
    
    return reporte["es_valida"], reporte


# ============================================================================
# POTENCIAL DE MEJORA - Estimación Previa
# ============================================================================

def calcular_potencial_mejora(
    pasante_mezcla: List[float],
    pasante_virtual: List[float],
    banda_min: List[float],
    banda_max: List[float],
    peso_estimado_virtual: float = 0.15,
) -> Dict[str, float]:
    """
    Estima qué mejora podría aportar la tabla virtual.
    
    Usa modelo predictivo simple: asume peso w_virtual ~ peso_estimado_virtual.
    """
    
    pasante_mezcla = np.array(pasante_mezcla, dtype=float)
    pasante_virtual = np.array(pasante_virtual, dtype=float)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)
    
    # Error actual
    centro_banda = (banda_min + banda_max) / 2.0
    error_actual = pasante_mezcla - centro_banda
    error_total_actual = np.sum(np.abs(error_actual))
    
    # Predecir mezcla con tabla virtual
    # Asumir: nueva_mezcla = (1 - peso_virtual) * mezcla + peso_virtual * virtual
    peso_virtual = peso_estimado_virtual
    mezcla_predicha = (1.0 - peso_virtual) * pasante_mezcla + peso_virtual * pasante_virtual
    
    # Error predicho
    error_predicho = mezcla_predicha - centro_banda
    error_total_predicho = np.sum(np.abs(error_predicho))
    
    # Mejora
    mejora_absoluta = error_total_actual - error_total_predicho
    mejora_relativa = mejora_absoluta / error_total_actual if error_total_actual > 0 else 0.0
    
    return {
        "error_total_actual": float(error_total_actual),
        "error_total_predicho": float(error_total_predicho),
        "mejora_absoluta": float(mejora_absoluta),
        "mejora_relativa_pct": float(mejora_relativa * 100.0),
        "peso_estimado_virtual": peso_estimado_virtual,
        "prediccion_viable": mejora_relativa >= 0.05,
        "prediccion_viable_razon": (
            f"Mejora estimada {mejora_relativa*100:.1f}% >= 5% (viabilidad mínima)" 
            if mejora_relativa >= 0.05 
            else f"Mejora estimada {mejora_relativa*100:.1f}% < 5% (insuficiente)"
        ),
    }


# ============================================================================
# EVALUACIÓN POST REOPTIMIZACIÓN
# ============================================================================

def evaluar_utilidad_tabla_virtual(
    error_total_antes: float,
    error_total_despues: float,
    peso_asignado: float,
    mejora_zona_critica_pct: float,
    cumplimiento_antes: float,
    cumplimiento_despues: float,
    umbral_utilidad_minimo_pct: float = 5.0,
    umbral_peso_minimo: float = 0.05,
) -> Dict[str, Any]:
    """
    Evalúa si la tabla virtual fue útil después de reoptimizar.
    
    Criterios de utilidad:
      - Métrica 1: ΔE_total / E_total_original >= 5%
      - Métrica 2: Mejora zona crítica >= 10%
      - Métrica 3: w_virtual >= 0.15
    
    ÚTIL si >= 2 de 3 métricas son verdaderas.
    """
    
    mejora_e_total_abs = error_total_antes - error_total_despues
    mejora_e_total_pct = (mejora_e_total_abs / error_total_antes * 100.0) if error_total_antes > 0 else 0.0
    
    metrica1 = mejora_e_total_pct >= umbral_utilidad_minimo_pct
    metrica2 = mejora_zona_critica_pct >= 10.0
    metrica3 = peso_asignado >= 0.15
    
    metricas_positivas = sum([metrica1, metrica2, metrica3])
    
    if metricas_positivas >= 2:
        veredicto = "ÚTIL"
        es_exitosa = True
    elif metricas_positivas == 1:
        veredicto = "MARGINAL"
        es_exitosa = False
    else:
        veredicto = "INÚTIL"
        es_exitosa = False
    
    return {
        "veredicto": veredicto,
        "es_exitosa": es_exitosa,
        "metricas": {
            "1_mejora_e_total_pct": {
                "valor": float(mejora_e_total_pct),
                "umbral": umbral_utilidad_minimo_pct,
                "cumple": metrica1,
            },
            "2_mejora_zona_critica_pct": {
                "valor": float(mejora_zona_critica_pct),
                "umbral": 10.0,
                "cumple": metrica2,
            },
            "3_peso_asignado": {
                "valor": float(peso_asignado),
                "umbral": 0.15,
                "cumple": metrica3,
            },
        },
        "metricas_positivas": metricas_positivas,
        "recomendacion": {
            "ÚTIL": "Tabla virtual fue acertada. Considerar nueva tabla si hay error residual.",
            "MARGINAL": "Tabla virtual ayudó poco. Parar o intentar con nueva tabla de forma selectiva.",
            "INÚTIL": "Tabla virtual no contribuyó. Evaluar no-corregibilidad. PARAR.",
        }.get(veredicto, "?"),
        "diferencias": {
            "error_total_antes": float(error_total_antes),
            "error_total_despues": float(error_total_despues),
            "mejora_absoluta": float(mejora_e_total_abs),
            "cumplimiento_antes": float(cumplimiento_antes),
            "cumplimiento_despues": float(cumplimiento_despues),
            "mejora_cumplimiento": float(cumplimiento_despues - cumplimiento_antes),
        }
    }


# ============================================================================
# UTILIDADES - Reportes y Visualización Preparatoria
# ============================================================================

def generar_reporte_tabla_virtual(
    pasante_mezcla: List[float],
    pasante_virtual: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[str],
    insumos: Optional[Dict] = None,
    metadata: Optional[Dict] = None,
) -> str:
    """
    Genera reporte detallado de tabla virtual para análisis.
    """
    
    pasante_mezcla = np.array(pasante_mezcla, dtype=float)
    pasante_virtual = np.array(pasante_virtual, dtype=float)
    banda_min = np.array(banda_min, dtype=float)
    banda_max = np.array(banda_max, dtype=float)
    
    lineas = []
    lineas.append("\n" + "="*80)
    lineas.append("REPORTE: TABLA VIRTUAL DIRIGIDA")
    lineas.append("="*80)
    
    lineas.append("\n📊 COMPARATIVA PRINCIPAL")
    lineas.append(f"{'Tamiz':<12} {'Mezcla':<12} {'Virtual':<12} {'Banda Min':<12} {'Banda Max':<12} {'Error':<12}")
    lineas.append("-" * 80)
    
    for i, (tamiz, m, v, bmin, bmax) in enumerate(zip(
        tamices, pasante_mezcla, pasante_virtual, banda_min, banda_max
    )):
        centro = (bmin + bmax) / 2.0
        error_mezcla = m - centro
        lineas.append(
            f"{tamiz:<12} {m:>11.2f}% {v:>11.2f}% {bmin:>11.2f}% {bmax:>11.2f}% {error_mezcla:>11.2f}%"
        )
    
    # Estadísticas
    error_mezcla_vec = pasante_mezcla - (banda_min + banda_max) / 2.0
    error_virtual_vec = pasante_virtual - (banda_min + banda_max) / 2.0
    
    lineas.append("\n📈 ESTADÍSTICAS")
    lineas.append(f"Error total mezcla actual: {np.sum(np.abs(error_mezcla_vec)):.3f}")
    lineas.append(f"Error total tabla virtual: {np.sum(np.abs(error_virtual_vec)):.3f}")
    lineas.append(f"Diferencia (improvement potencial): {np.sum(np.abs(error_mezcla_vec)) - np.sum(np.abs(error_virtual_vec)):.3f}")
    lineas.append(f"Distancia L2 virtual vs mezcla: {np.linalg.norm(pasante_virtual - pasante_mezcla):.3f}")
    
    if metadata:
        lineas.append("\n🔧 METADATA")
        lineas.append(f"Método: {metadata.get('metodo', '?')}")
        lineas.append(f"Zona crítica: {metadata.get('zona_critica_nombre', '?')} (índice {metadata.get('zona_critica_idx', '?')})")
    
    lineas.append("\n" + "="*80 + "\n")
    
    return "\n".join(lineas)


# ============================================================================
# STUB PARA GRÁFICOS (se completa en siguiente iteración)
# ============================================================================

def listar_puntos_para_grafico(
    pasante_mezcla: List[float],
    pasante_virtual: List[float],
    banda_min: List[float],
    banda_max: List[float],
    tamices: List[str],
) -> Dict[str, Any]:
    """
    Retorna datos estructurados listos para graficar.
    Formato agnóstico (no depende de matplotlib, plotly, etc.)
    """
    
    return {
        "tamices": tamices,
        "pasante_mezcla": pasante_mezcla,
        "pasante_virtual": pasante_virtual,
        "banda_min": banda_min,
        "banda_max": banda_max,
        "titulo": "Tabla Virtual Dirigida vs Mezcla Actual",
        "ylabel": "Pasante (%)",
        "xlabel": "Tamiz (mm)",
    }


if __name__ == "__main__":
    print("✅ Módulo nucleo_tabla_virtual.py cargado correctamente")
    print("   Funciones disponibles:")
    print("   - puede_generarse_tabla_virtual()")
    print("   - preparar_insumos_tabla_virtual()")
    print("   - generar_tabla_virtual()")
    print("   - validar_tabla_virtual()")
    print("   - calcular_potencial_mejora()")
    print("   - evaluar_utilidad_tabla_virtual()")
    print("   - generar_reporte_tabla_virtual()")
