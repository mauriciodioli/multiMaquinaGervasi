# AUDITORÍA TÉCNICA - MÓDULO DE OPTIMIZACIÓN GRANULOMÉTRICA

**Fecha:** Marzo 23, 2026  
**Módulo:** `/workspaces/multiMaquinaGervasi/src/controller/autoDensidad/calculoPorRetenidos`  
**Rol del Auditor:** Ingeniero Senior en Procesamiento de Granulometría y Sistemas de Optimización Industrial

---

## 1. ESTRUCTURA DEL MÓDULO

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **calculoPorRetenidos.py** | Controlador Flask, orquestación principal (1656 líneas) | ✅ Funcional |
| **core/nucleo_mezcla.py** | Cálculos de mezcla ponderada y conversiones (ret_ind → ret_acum → pasante) | ✅ Funcional |
| **core/nucleo_error.py** | Cálculo de errores lineales por tamiz e identificación de zonas críticas | ✅ Funcional |
| **core/nucleo_decision.py** | Lógica de clasificación de suficiencia y predicción de mejora | ✅ Funcional |
| **core/nucleo_tabla_virtual.py** | Generación de curvas granulométricas ideales (tabla virtual dirigida) | ✅ Funcional |
| **core/nucleo_optimizacion.py** | Optimización de proporciones mediante gradient descent | ✅ Funcional |
| **core/nucleo_iteracion.py** | Control de iteraciones y manejo de historial | ✅ Funcional |
| **core/auditoria_decision.py** | Auditoría completa (6 fases) y decisión de generación de tabla virtual | ✅ Funcional |
| **core/api_integracion.py** | API unificada que integra todos los módulos | ✅ Funcional |
| **calculoPorRetenidos.js** | Frontend: manejo de proporciones y extracción de datos | ✅ Funcional |

### 1.1 Flujo de Datos Principal

```
INPUT: retido_ind_pct (retenidos individuales por material)
  ↓
_acum_desc() → ret_acum (retenido acumulado)
  ↓
[100 - ret_acum] → PASANTE (representación interna del sistema)
  ↓
_mezcla_ponderada_acum() → mix_acum (mezcla ponderada acumulada)
  ↓
calcular_errores_por_tamiz() → error_total, errores_por_zona
  ↓
Validar contra limites (bloco/paver) → cumplimiento_pct
  ↓
generar_tabla_virtual() → pasante_virtual (curva ideal)
  ↓
OUTPUT: auditoria completa (6 fases)
```

---

## 2. VALIDACIÓN DE CAPACIDADES ACTUALES

### Requerimiento de Gervasi: El sistema debe ser capaz de:

1. **✔ Tomar materiales granulométricos reales (retido_ind_pct por tamiz)**
   - **Estado:** ✅ SÍ, implementado
   - **Evidencia:** `calculoPorRetenidos.py:granulometria_retido()` línea 258
   - **Detalles:** Recibe JSON con array de materiales con `retido_ind_pct`, convierte a `ret_acum` y `pasante`

2. **✔ Calcular la curva granulométrica de la mezcla actual (ponderada)**
   - **Estado:** ✅ SÍ, implementado
   - **Evidencia:** `nucleo_mezcla.py:calcular_mezcla_pasante()` línea 47
   - **Detalles:** Realiza mezcla ponderada: `mix[j] = Σ w_i * PASANTE_i[j]`

3. **✔ Compararla contra una curva ideal (tipo Fuller o límites de bloque)**
   - **Estado:** ✅ SÍ, implementado
   - **Evidencia:** `calculoPorRetenidos.py:_validar_faixas()` línea 243
   - **Detalles:** Valida contra límites superiores e inferiores por tamiz

4. **✔ Detectar desviaciones por zona (gruesos, medios, finos)**
   - **Estado:** ✅ SÍ, implementado
   - **Evidencia:** `nucleo_error.py:definir_zonas_automaticas()` línea 103
   - **Detalles:** Divide tamices en terciles (gruesa/media/fina) automáticamente
   - **Complementario:** `calcular_errores_por_zona()` línea 117 agrega errores por zona

5. **✔ Generar una tabla virtual de propuesta de mezcla**
   - **Estado:** ✅ SÍ, parcialmente implementado
   - **Evidencia:** `nucleo_tabla_virtual.py:generar_tabla_virtual()` línea 151
   - **Detalles:** Genera curva ideal dirigida hacia especificación
   - **PERO:** Genera CURVA, no MATERIALES específicos

6. **❌ Crear virtualmente 3 nuevos agregados (M1, M2, M3)**
   - **Estado:** ❌ NO, FALTA completamente
   - **Detalles:** VER SECCIÓN 3

7. **❌ Reconstruir una nueva curva que se acerque a la ideal**
   - **Estado:** ✅ SÍ, pero INDIRECTAMENTE
   - **Detalles:** Valida tablas virtuales (`validar_tabla_virtual()` línea 310)
   - **PERO:** No propone 3 agregados específicos que implementen la solución

---

## 3. DETECTAR FALTANTES CRÍTICOS

### 3.1 ❌ FALTA CRÍTICA 1: Generación de Nuevos Materiales Virtuales (M1, M2, M3)

**Qué EXISTE hoy:**
- Función `sugerir_division_en_dos()` línea 629: Divide UN material existente en 2 grupos
- Función `sugerir_division_en_tres()` línea 814: Divide UN material en 3 grupos
- Función `sugerir_division_en_n()` línea 1132: Generalización para N divisiones

**Qué NO EXISTE:**
- ❌ NO genera nuevos materiales virtuales con propiedades granulométricas específicas
- ❌ Solo sugiere CÓMO DIVIDIR materiales existentes, no CREA nuevas mezclas virtuales
- ❌ Las tablas virtuales (`generar_tabla_virtual()`) son CURVAS IDEALES abstractas, no materiales concretos que se puedan usar en nuevas mezclas

**Impacto en Requerimiento:**
- Usuario necesita: "Cree 3 nuevos agregados con estas características granulométricas específicas"
- Sistema ofrece: "Divida su material existente en 3 partes en estos puntos"
- **Diferencia:** Uno crea algo nuevo, el otro solo redistribuye lo existente

**Severidad:** 🔴 BLOQUEANTE

---

### 3.2 ❌ FALTA CRÍTICA 2: Algoritmo de Redistribución Granulométrica Dirigida

**Qué EXISTE:**
- `sugerir_division_en_n()` busca puntos óptimos de corte usando búsqueda exhaustiva
- `optimizar_proporciones()` línea 74 ajusta pesos de 3 materiales **ya conocidos**
- Función `_optimizar_proporciones_para_grupos()` línea 1055 optimiza proporciones para N grupos

**Qué NO EXISTE:**
- ❌ NO hay algoritmo para PROPONER nuevas mezclas de 3 agregados que compensen el error residual
- ❌ NO calcula cómo deberían ser las características granulométricas de M1, M2, M3 para alcanzar la curva ideal
- ❌ Solo redistribuye proporciones de materiales YA CONOCIDOS

**Cómo debería funcionar:**
```
INPUT: Curva real + Especificación ideal + Error residual por tamiz

ALGORITMO:
1. Calcular error = especificacion_ideal - curva_real (por tamiz)
2. Dividir error entre 3 agregados: error_m1, error_m2, error_m3
3. Para cada agregado:
   - Crear granulometría que genere su parte del error
   - Especificar retido_ind por tamiz
4. Proporciones: w1, w2, w3 tales que suma contribuciones = especificación

OUTPUT: M1 [ret_ind], M2 [ret_ind], M3 [ret_ind], pesos [w1, w2, w3]
```

**Severidad:** 🔴 BLOQUEANTE

---

### 3.3 ❌ FALTA CRÍTICA 3: Creación de Propuesta Ejecutable

**Qué EXISTE:**
- Tabla virtual generada para entender la curva ideal
- Error residual calculado por tamiz
- Identificación de zona crítica

**Qué NO EXISTE:**
- ❌ NO hay función que genere una propuesta EJECUTABLE como:
  ```
  M1: Agregado 1
    - 4% en tamiz 12.5mm
    - 8% en tamiz 9.5mm
    - 15% en tamiz 6.3mm
    - ...
    - Proporción recomendada: 35%
  
  M2: Agregado 2
    - Similar con sus valores
    - Proporción recomendada: 35%
  
  M3: Agregado 3
    - Similar con sus valores
    - Proporción recomendada: 30%
  
  VALIDACIÓN: Si mezcla M1 (35%) + M2 (35%) + M3 (30%) → Cumple especificación
  ```
- ❌ NO existe función `crear_material_virtual()` o equivalente

**Severidad:** 🔴 BLOQUEANTE

---

### 3.4 ❌ FALTA SEMI-CRÍTICA 4: Separación Sistemática y Algoritmo de Corrección

**Qué EXISTE (parcial):**
- `definir_zonas_automaticas()` divide tamices en terciles
- `calcular_errores_por_zona()` agrega errores por zona
- Identificación de "zona crítica" (con mayor error)

**Qué NO EXISTE COMO SISTEMA COMPLETO:**
- ❌ NO hay una estrategia sistemática ZONA POR ZONA para crear correctivos
- ❌ NO analiza: "En zona GRUESA tengo +15% error, en zona MEDIA tengo -5%, en zona FINA tengo +8%"
- ❌ NO propone: "M1 debe ser predominantly grueso para compensar zona gruesa"
- ❌ El análisis existe pero NO ESTÁ CONECTADO a la generación de soluciones

**Severidad:** 🟡 IMPORTANTE (complementa falta 1-2)

---

### 3.5 ❌ FALTA SEMI-CRÍTICA 5: Motor Real de Decisión + Recomendación

**Qué EXISTE:**
- Clasificación de suficiencia (perfecto/muy_bueno/marginal/insuficiente)
- Predicción de mejora potencial con tabla virtual
- Evaluación de parada (perfección/aceptable/estancamiento/límite)

**Qué NO EXISTE:**
- ❌ NO hay un "motor de decisión" que diga: **"HAGA ESTO para mejorar"**
- ❌ Solo EVALÚA el status quo, no RECOMIENDA acciones concretas
- ❌ NO propone: "crear M1 con características X, M2 con Y, M3 con Z"
- ❌ NO dice: "Si implementa esta propuesta, ganará +15% de cumplimiento"

**Severidad:** 🟡 IMPORTANTE (es la acción final del usuario)

---

## 4. DIAGNÓSTICO TÉCNICO PROFUNDO

### 4.1 ¿Es el sistema suficiente para cumplir requerimiento de Gervasi?

### 🔴 RESPUESTA CONCLUYENTE: **NO, ES INSUFICIENTE**

### 4.2 Lo que el usuario NECESITA vs Lo que el sistema OFRECE

#### Flujo Ideal (Requerimiento de Gervasi):
```
┌─ INPUT ────────────────────────────┐
│ Curva real medida (retido_ind_pct) │
│ Especificación ideal (banda_min,   │
│                      banda_max)    │
└────────────────────────────────────┘
          ↓
┌─ ANÁLISIS ──────────────────────────┐
│ 1. Detectar desviaciones             │
│ 2. Analizar causa (qué zona)         │
│ 3. Medir error por tamiz             │
└────────────────────────────────────┘
          ↓
┌─ GENERACIÓN ────────────────────────┐
│ 4. GENERAR PROPUESTA:                │
│    "Cree estos 3 agregados..."       │
│    M1: [5%, 10%, 15%, ...]           │
│    M2: [10%, 20%, 25%, ...]          │
│    M3: [15%, 30%, 35%, ...]          │
│    Proporciones: M1=35%, M2=35%...   │
└────────────────────────────────────┘
          ↓
┌─ VALIDACIÓN ────────────────────────┐
│ 5. VALIDAR: "Si mezcla M1+M2+M3      │
│    en esas proporciones,             │
│    alcanza especificación"           │
│    Cumplimiento: 98.5% ✓             │
└────────────────────────────────────┘
          ↓
┌─ OUTPUT ────────────────────────────┐
│ Tabla con M1, M2, M3 específicos     │
│ Proporciones recomendadas            │
│ Validación de curva resultante       │
│ (EJECUTABLE por Gervasi)             │
└────────────────────────────────────┘
```

#### Flujo Actual (Lo que el Sistema Realiza):
```
┌─ INPUT ───────────────────────────┐
│ Curva real + Especificación ideal  │
└───────────────────────────────────┘
          ↓
┌─ ANÁLISIS (✅ BIEN) ──────────────┐
│ ✅ Calcula mezcla ponderada        │
│ ✅ Identifica error por tamiz      │
│ ✅ Detecta zona crítica            │
│ ✅ Genera tabla virtual ideal      │
│ ✅ Auditoría en 6 fases            │
└───────────────────────────────────┘
          ↓
┌─ GENERACIÓN (❌ INCOMPLETA) ──────┐
│ ✅ Optimiza proporciones (de qué?) │
│ ✅ Divide materiales en N partes   │
│ ❌ FALTA: Genera M1, M2, M3        │
│ ❌ FALTA: Motor de decisión        │
└───────────────────────────────────┘
          ↓
┌─ OUTPUT (❌ INSUFICIENTE) ─────────┐
│ Sugerencias de división de          │
│ materiales EXISTENTES, no CREACIÓN  │
│ de nuevos (NO EJECUTABLE)           │
└───────────────────────────────────┘
```

---

## 5. LO QUE FUNCIONA BIEN

### 5.1 Módulo de Mezcla Ponderada

| Función | Detalle | Evaluación |
|---------|---------|-----------|
| `calcular_ret_acum()` | Convierte ret_ind → ret_acum correctamente | ⭐⭐⭐⭐⭐ |
| `calcular_pasante()` | Convierte ret_acum → pasante (100 - ret_acum) | ⭐⭐⭐⭐⭐ |
| `calcular_mezcla_pasante()` | Mezcla ponderada sin corrupción de datos | ⭐⭐⭐⭐⭐ |
| `validar_monotonia_pasante()` | Verifica que pasante sea decreciente correctamente | ⭐⭐⭐⭐ |

**Conclusión:** Núcleo de cálculos matemáticos EXCELENTE

### 5.2 Módulo de Error y Zonas

| Función | Detalle | Evaluación |
|---------|---------|-----------|
| `calcular_error_por_tamiz()` | Error lineal (no cuadrático) bien implementado | ⭐⭐⭐⭐⭐ |
| `calcular_errores_por_tamiz()` | Agrega error total, debajo, arriba correctamente | ⭐⭐⭐⭐⭐ |
| `definir_zonas_automaticas()` | División por terciles (gruesa/media/fina) | ⭐⭐⭐⭐ |
| `calcular_errores_por_zona()` | Agregación por zona sin pérdida de datos | ⭐⭐⭐⭐ |

**Conclusión:** Identificación de desviaciones EXCELENTE

### 5.3 Módulo de Tabla Virtual

| Función | Detalle | Evaluación |
|---------|---------|-----------|
| `generar_tabla_virtual()` | Genera curva ideal dirigida a banda | ⭐⭐⭐⭐ |
| `validar_tabla_virtual()` | 6 checks robustos (rango, monot, saltos, etc) | ⭐⭐⭐⭐ |
| `puede_generarse_tabla_virtual()` | Validación de condiciones de habilitación | ⭐⭐⭐⭐ |
| `preparar_insumos_tabla_virtual()` | Cálculo correcto de error firmado y zona crítica | ⭐⭐⭐⭐ |

**Conclusión:** Concepto de tabla virtual bien implementado (aunque no sea exactamente lo que requiere Gervasi)

### 5.4 Módulo de Auditoría

| Función | Detalle | Evaluación |
|---------|---------|-----------|
| `generar_auditoria_completa()` | 6 fases bien estructuradas | ⭐⭐⭐⭐ |
| `evaluar_criterios_decision()` | Evaluación de cumplimiento de banda | ⭐⭐⭐⭐ |
| Validación de JSON | Todas las respuestas validan correctamente | ⭐⭐⭐⭐ |

**Conclusión:** Auditoría BUENA pero no cierra el ciclo con solución

### 5.5 División Inteligente de Materiales

| Función | Detalle | Evaluación |
|---------|---------|-----------|
| `sugerir_division_en_dos()` | Detecta salto máximo con ruido filtering | ⭐⭐⭐⭐ |
| `sugerir_division_en_tres()` | Optimización de cortes con búsqueda combinatoria | ⭐⭐⭐⭐ |
| `sugerir_division_en_n()` | Generalización a N partes (2-5) | ⭐⭐⭐⭐ |
| `_optimizar_proporciones_para_grupos()` | Gradient descent con constraints | ⭐⭐⭐⭐ |

**Conclusión:** EXCELENTE para dividir lo existente, pero no para crear lo nuevo

---

## 6. LO QUE ESTÁ CONCEPTUALMENTE MAL

| Concepto | El código hace | Debería hacer | Impacto |
|----------|----------------|---------------|---------|
| **"Tabla virtual"** | Genera una curva ideal abstracta en espacio de pasante | ✅ Correcto lógicamente | N/A |
| **"Material virtual"** | ❌ NO genera materiales concretos con datos específicos | Debería proponer M1, M2, M3 con retido_ind específicos | BLOQUEANTE |
| **"Solución"** | Optimiza proporciones de materiales conocidos | Debería crear nuevos materiales si es necesario | BLOQUEANTE |
| **"Corrección"** | Identifica el problema (diagnóstico) | Debería proponer acción ejecutable (receta) | BLOQUEANTE |
| **"Integración"** | Cada módulo funciona aislado | Debería fluir: Análisis → Propuesta → Validación → Output | IMPORTANTE |

### Analogía Clínica:

```
Sistema actual = MÉDICO DIAGNOSTICADOR
  "Usted tiene presión alta en la zona X"
  "El colesterol está 20 puntos arriba del ideal"
  "La insulina tiene desviación media de 5%"
  Conclusión: "Necesita mejora"
  
Sistema que necesita = MÉDICO EJECUTIVO
  "Tome medicina M1 (componente A) 35% del día"
  "Tome medicina M2 (componente B) 35% del día"  
  "Tome medicina M3 (componente C) 30% del día"
  Validación: "Con esta combinación, sus valores llegan a rango normal"
```

---

## 7. RIESGO GENERAL

### 🔴 RIESGO: **ALTO**

#### 7.1 Por qué el riesgo es alto:

1. **Requerimiento NO cumplido (Critical):**
   - Sistema NO crea los agregados virtuales específicos (M1, M2, M3) que Gervasi pidió explícitamente
   - Usuario esperará: "Cree 3 nuevos materiales"
   - Sistema entrega: "Divida 1 material en 3 partes"
   - **Diferencia funcional:** Uno es creatividad, otro es redistribución

2. **Desconexión entre análisis y acción (Critical):**
   - Detecta perfectamente problemas
   - Pero NO propone soluciones concretas
   - Usuario tendrá que deducir qué hacer basado en diagnóstico
   - **Impacto:** No es un sistema de RECOMENDACIÓN, es de OBSERVACIÓN

3. **Confusión funcional (High):**
   - Función "tabla virtual" genera CURVAS, no MATERIALES
   - Usuario podría pensar que "tabla virtual" = "material virtual"
   - No son lo mismo en el contexto de Gervasi

4. **Falta de integración end-to-end (High):**
   - Cada módulo funciona aislado
   - No hay un flujo completo: problema → análisis → propuesta → validación → output
   - El último paso (generar propuesta ejecutable) NO existe

#### 7.2 Evidencia de incompletitud:

- ❌ Línea 1656 del código: NO existe función que genere "Propuesta de M1, M2, M3"
- ❌ Línea 1078 de integración: Llama a optimización, pero NO a generación de nuevos materiales
- ❌ Cero referencias a "crear_material_virtual()", "generar_agregados()", "propuesta_correctiva()" etc.
- ❌ Endpoint `/calculoPorRetenidos/auditoria` retorna análisis, no propuesta

#### 7.3 Escenario de uso real:

```
Gervasi: "El concreto no cumple especificación, necesito 3 materiales corregidos"

Sistema dice:
  ✅ "La curva real tiene error de +12% en zona gruesa"
  ✅ "La zona crítica está en tamiz 9.5mm"
  ✅ "Necesitaría mezcla de 3 agregados optimizados"
  ❌ "Pero no sé cuáles son específicamente"
  ❌ "Y cómo ajustar cada uno en cada tamiz"

Resultado: Gervasi sigue sin solución ejecutable
```

---

## 8. LÓGICA FALTANTE: DESGLOSE FUNCIÓN A FUNCIÓN

### Función que FALTA: `generar_propuesta_3_agregados()`

```python
def generar_propuesta_3_agregados(
    pasante_real: List[float],      # Curva actual medida
    banda_min: List[float],          # Especificación mín
    banda_max: List[float],          # Especificación máx
    tamices: List[str]               # Lista de tamices
) -> Dict:
    """
    Genera propuesta EJECUTABLE de 3 agregados correctivos
    
    ENTRADA:
      - Curva real [98.5, 79.2, 50.1, 35.8, 15.2, 5.0, 0.1]
      - Banda mín [85, 70, 50, 35, 15, 5, 0]
      - Banda máx [100, 90, 75, 60, 30, 15, 10]
      - Tamices ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.075']
    
    PROCESO:
      1. Calcular ideal = (banda_min + banda_max) / 2
         ideal = [92.5, 80, 62.5, 47.5, 22.5, 10, 5]
      
      2. Error residual = pasante_real - ideal
         error = [6, -0.8, -12.4, -11.7, -7.3, -5, -4.9]
      
      3. Distribuir error entre 3 agregados
         error_m1 = error * 0.35
         error_m2 = error * 0.35
         error_m3 = error * 0.30
      
      4. CREAR MATERIALES:
         Para M1: retido_ind = inversión de cómo ese error se distribuye en tamices
         Para M2: ídem
         Para M3: ídem
      
      5. Calcular proporciones (0.35, 0.35, 0.30)
      
      6. VALIDAR: mix_resultado = M1*0.35 + M2*0.35 + M3*0.30
         ¿Entra en banda?
    
    SALIDA:
      {
        'm1': {
          'nombre': 'Agregado Correctivo 1 (Grueso)',
          'retido_ind_pct': [2.1, 4.5, 5.2, 3.1, 2.0, 1.0, 0.0],
          'retido_acum': [2.1, 6.6, 11.8, 14.9, 16.9, 17.9, 17.9],
          'proporcion_recomendada_pct': 35.0,
          'razon': 'Compensa principalmente zona gruesa'
        },
        'm2': { ... },
        'm3': { ... },
        'validacion': {
          'curva_resultante_pasante': [97.9, 80.1, 62.8, 48.2, 23.1, 10.0, 4.5],
          'cumple_especificacion': True,
          'cumplimiento_pct': 99.2,
          'error_residual': 0.3
        }
      }
    """
    # IMPLEMENTATION MISSING
    pass
```

**Ubicación donde debería estar:** `calculoPorRetenidos.py` línea 1156 (tras `sugerir_division_en_n()`)

**Complejidad estimada:** ~200 líneas de código

---

## 9. SIGUIENTE PASO EXACTO (RECOMENDADO)

### Opción A: Extensión Operativa Inmediata (RECOMENDADO)

#### Paso 1: Crear función de propuesta de agregados

Insertar en `calculoPorRetenidos.py` después de línea 1156:

```python
def generar_propuesta_3_agregados(pasante_real, banda_min, banda_max, tamices, log=None):
    """Genera propuesta de 3 agregados correctivos basada en error residual"""
    # [Ver sección 8 para algoritmo completo]
    # ~200 líneas de lógica
    pass
```

#### Paso 2: Integrar en endpoint `/calculoPorRetenidos/granulometria/retido/`

En línea 1368-1375, agregar:

```python
# Nueva sección: Propuesta de agregados correctivos
propuesta_agregados = None
if divisiones_n_tablas and divisiones_n_tablas.get('mejor_opcion') == 3:
    try:
        propuesta_agregados = generar_propuesta_3_agregados(
            pasante_real=mix_pasante,
            banda_min=[limites['bloco'].get(str(t), [0,100])[0] for t in tamices_ord],
            banda_max=[limites['bloco'].get(str(t), [0,100])[1] for t in tamices_ord],
            tamices=tamices_ord,
            log=log
        )
    except Exception as e:
        log(f"[ERROR] Generación de propuesta: {str(e)}")
```

#### Paso 3: Retornar en JSON

```python
return jsonify({
    ...(respuesta anterior)...,
    "propuesta_agregados_correctivos": propuesta_agregados if propuesta_agregados else None
}), 200
```

#### Paso 4: Actualizar frontend si es necesario

En `calculoPorRetenidos.js`, agregar visualización de propuesta en tabla HTML

---

### Opción B: Crear Módulo de R&D Separado

Si se requiere explorar múltiples estrategias de corrección:

```
core/
  nucleo_generacion_agregados.py  ← Nuevo módulo
    ├─ generar_agregados_por_error_residual()
    ├─ generar_agregados_por_zona_critica()
    └─ generar_agregados_por_optimizacion_l1()
```

**Ventaja:** Permite exploración sin afectar endpoint actual  
**Desventaja:** Demora disponibilidad

---

## 10. IMPACTO Y ESFUERZO ESTIMADO

| Aspecto | Estimación |
|---------|-----------|
| Líneas de código nuevo | 200-300 |
| Tiempo de implementación | 2-4 horas |
| Riesgo de regresión | BAJO (función nueva, no modifica existentes) |
| Impacto en código existente | BAJO (solo agregar function + update return) |
| Complejidad algorítmica | MEDIA (basada en error residual) |
| Testing requerido | MEDIO (validar con datos reales de Gervasi) |

---

## 11. RECOMENDACIÓN FINAL

### ✅ IMPLEMENTAR OPCIÓN A INMEDIATAMENTE

**Justificación:**
1. Cierra el gap más crítico (falta de propuesta ejecutable)
2. Bajo riesgo de regresión
3. Integración simple en endpoint existente
4. Entrega valor inmediato a Gervasi
5. No bloquea otras features

**Timeline**
- Desarrollo: 2-3 horas
- Testing: 1 hora
- Documentación: 30 minutos
- **Total: 4 horas**

---

## 12. TABLA RESUMEN EJECUTIVO

| Pregunta | Respuesta | Evidencia |
|----------|-----------|-----------|
| ¿Funciona el análisis granulométrico? | ✅ SÍ, muy bien | `nucleo_error.py`, `auditoria_decision.py` |
| ¿Funciona la generación de soluciones? | ❌ NO, es crítico | No existe función "generar_propuesta_*" |
| ¿Qué le falta exactamente? | Crear M1, M2, M3 con retido_ind específicos | Función no existe, impacta 100% requerimiento |
| ¿Riesgo actual? | 🔴 ALTO - Diagnóstico sin solución | Usuario no puede ejecutar recomendación |
| ¿Cuánto trabajo? | ~4 horas | 200-300 líneas + testing |
| ¿Recomendación? | Implementar Función A NOW | Cierra gap crítico |
| ¿Impacto en código existente? | BAJO | Solo agregar, no modificar |

---

**Auditoría completada:** Marzo 23, 2026  
**Conclusión:** Sistema excelente en diagnóstico, insuficiente en solución. Implementación de propuesta de agregados resolverá 95% del gap.

