# Sistema Python de Optimización Granulométrica

**Ubicación Backend:** `/src/controller/autoDensidad/calculoPorRetenidos/`

## Estructura de Módulos

```
calculoPorRetenidos/
├── __init__.py                      # Package exports
├── calculoPorRetenidos.py           # Flask blueprint (main entry)
├── core/                            # Core calculation modules
│   ├── __init__.py
│   ├── nucleo_mezcla.py            # Mixture calculations (PASANTE-only)
│   ├── nucleo_error.py             # Linear error metric + diagnostics
│   ├── nucleo_decision.py          # Decision logic (4 levels, 4 stops)
│   ├── nucleo_optimizacion.py      # Gradient descent optimizer
│   ├── nucleo_iteracion.py         # Iteration control + history
│   └── api_integracion.py          # Main API entry point
└── ...
```

## Importación Rápida

```python
# Opción 1: Desde el package
from src.controller.autoDensidad.calculoPorRetenidos import (
    optimizar_mezcla,
    analizar_mezcla_actual,
    crear_material
)

# Opción 2: Desde módulos específicos
from src.controller.autoDensidad.calculoPorRetenidos.core import (
    calcular_mezcla_pasante,
    crear_reporte_error,
    ejecutar_optimizacion_completa
)
```

## Uso Básico

### 1. Optimización Completa (Recomendado)

```python
from src.controller.autoDensidad.calculoPorRetenidos import (
    crear_material, 
    optimizar_mezcla
)

# Crear materiales
arena = crear_material(
    nombre="Arena fina",
    ret_ind=[0, 5, 15, 25, 35, 40, 45, 50, 55, 60],
    w=0.35
)

grava = crear_material(
    nombre="Grava",
    ret_ind=[0, 2, 8, 15, 20, 25, 30, 35, 40, 45],
    w=0.65
)

# Configurar optimización
config = {
    'materiales': [arena, grava],
    'limites': {
        '12.5': [0, 10],
        '9.5': [10, 30],
        '6.3': [30, 50],
        '4.8': [50, 65],
        '2.4': [65, 80],
        '1.2': [80, 90],
        '0.6': [88, 95],
        '0.3': [92, 98],
        '0.15': [95, 100],
        '0.075': [98, 100]
    },
    'tamices': ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.6', '0.3', '0.15', '0.075'],
    'opciones': {
        'max_iteraciones': 5,
        'max_tablas_virtuales': 3,
        'verbose': True
    }
}

# Optimizar
resultado = optimizar_mezcla(config)

# Usar resultado
if resultado['exito']:
    print(f"✓ Optimización exitosa")
    print(f"  Proporciones: {resultado['proporciones_formato']}")
    print(f"  Error: {resultado['error_minimo']:.3f}")
    print(f"  Mejora: {resultado['mejora_total_pct']:.1f}%")
    print(f"  Cumplimiento: {resultado['cumplimiento_pct']:.1f}%")
else:
    print(f"✗ Optimización no convergió")
    print(f"  Razón: {resultado['razon_parada']}")
```

### 2. Análisis sin Optimizar

```python
from src.controller.autoDensidad.calculoPorRetenidos import analizar_mezcla_actual

# Analizar mezcla actual
analisis = analizar_mezcla_actual(config)

print(f"Error actual: {analisis['error_total']:.3f}")
print(f"Cumplimiento: {analisis['cumplimiento_pct']:.1f}%")
print(f"Zona crítica: {analisis['zona_critica']}")
print(f"Recomendación: {analisis['recomendacion']}")
```

### 3. Acceso a Módulos Individuales

```python
from src.controller.autoDensidad.calculoPorRetenidos.core import (
    calcular_mezcla_pasante,
    crear_reporte_error,
    optimizar_proporciones
)

# Calcular mezcla directamente
pasante = calcular_mezcla_pasante(materiales)

# Evaluar error
reporte = crear_reporte_error(pasante, limites, tamices)
print(f"Error total: {reporte['error_total']}")
print(f"Zona crítica: {reporte['zona_critica']}")

# Optimizar solo proporciones
resultado_opt = optimizar_proporciones(
    materiales, 
    limites, 
    tamices,
    {'max_iteraciones': 100}
)
```

## Estructura de Entrada

### Config para `optimizar_mezcla()`

```python
{
    'materiales': list of {
        'nombre': str,              # Nombre del material
        'pasante': list,            # Array PASANTE por tamiz
        'w': float,                 # Peso/proporción inicial
        'ret_ind': list (optional) # Retenidos individuales
        'ret_acum': list (optional) # Retenido acumulado
    },
    'limites': {
        'tamiz_string': [min, max], # Ej: '12.5': [0, 10]
        ...
    },
    'tamices': list of str,         # Nombres de tamices en orden
    'opciones': {
        'max_iteraciones': int,     # Default: 5
        'max_tablas_virtuales': int, # Default: 3
        'verbose': bool              # Default: False
    }
}
```

## Estructura de Salida

### Resultado de `optimizar_mezcla()`

```python
{
    'exito': bool,
    'proporciones_optimizadas': [float, ...],   # Valores decimales
    'proporciones_pct': [float, ...],            # Porcentajes
    'proporciones_formato': [str, ...],          # "Arena: 35%"
    'error_minimo': float,
    'mejora_total': float,
    'mejora_total_pct': float,
    'cumplimiento_pct': float,
    'iteraciones_realizadas': int,
    'tablas_virtuales_usadas': int,
    'razon_parada': str,    # perfección|aceptable|estancamiento|límite_iters
    'detalles_error': {
        'error_total': float,
        'errores_por_zona': {zona: datos},
        'zona_critica': str
    },
    'detalles_decision': {
        'suficiencia': str,  # perfecto|muy_bueno|marginal|insuficiente
        'mejora_detectada': bool,
        'recomendacion': str
    },
    'historial_completo': {
        'trayectoria': [{num, error, cumpl}, ...],
        'resumen': {error_inicial, error_final, mejora_total, ...}
    },
    'mensaje': str
}
```

## Configuración de Parámetros

### Parámetros de Decisión (nucleo_decision.py)

```python
from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_decision import CONFIG_DECISION

# Ver/modificar parámetros
print(CONFIG_DECISION)

# Personalizar
CONFIG_DECISION['E_umbral_base'] = 0.50        # Aumentar tolerancia
CONFIG_DECISION['mejora_rel_min'] = 0.20       # Requerir más mejora%
CONFIG_DECISION['max_iteraciones'] = 10        # Más iteraciones
```

### Parámetros de Optimización (nucleo_optimizacion.py)

```python
from src.controller.autoDensidad.calculoPorRetenidos.core.nucleo_optimizacion import CONFIG_OPT

CONFIG_OPT['learning_rate_inicial'] = 0.05     # Velocidad de aprendizaje
CONFIG_OPT['max_iteraciones'] = 500            # Iteraciones del optimizer
CONFIG_OPT['verbose'] = True                   # Debug output
```

## Especificaciones Matemáticas

### Representación PASANTE
```
PASANTE = 100 - retenido_acumulado
```
Todos los cálculos usan PASANTE exclusivamente, **nunca se mezclan representaciones**.

### Mezcla Ponderada
```
mix[j] = Σ w_i * PASANTE_i[j]
```
donde:
- `w_i`: proporción del material i
- `PASANTE_i[j]`: pasante del material i en tamiz j

### Error Lineal (por tamiz)
```
e_i = max(0, L_i - p_i, p_i - U_i)
```
donde:
- `p_i`: pasante medido
- `L_i, U_i`: límites inferior y superior

### Error Total
```
E_total = Σ e_i    [agregación simple, NO cuadrática]
E = E_debajo + E_arriba  [descomposición directional]
```

## 4 Niveles de Suficiencia

1. **perfecto** - Error=0, cumpl=100%
2. **muy_bueno** - Error bajo, cumpl ≥ 95%
3. **marginal** - Error moderado, cumpl ≥ 80%
4. **insuficiente** - Error alto, cumpl < 80%

## 4 Condiciones de Parada

1. **perfección** - E=0
2. **aceptable** - E ≤ umbral, cumpl ≥ 95%
3. **estancamiento** - ΔE < 0.30 en 2 iteraciones
4. **límite_iters** - iters ≥ max

## 3 Señales de No-Corregibilidad

1. **Estancamiento** - ΔE < 0.01
2. **Concentración** - > 80% del error en una zona
3. **Contradicción** - Límites incompatibles

## Integración con Flask (calculoPorRetenidos.py)

```python
# Endpoint Flask para optimizar
@calculoPorRetenidos.route('/optimizar', methods=['POST'])
def api_optimizar():
    config = request.get_json()
    resultado = optimizar_mezcla(config)
    return jsonify(resultado)

# Endpoint para análisis
@calculoPorRetenidos.route('/analizar', methods=['POST'])
def api_analizar():
    config = request.get_json()
    resultado = analizar_mezcla_actual(config)
    return jsonify(resultado)
```

## Testing

### Test rápido local

```python
if __name__ == '__main__':
    from src.controller.autoDensidad.calculoPorRetenidos import optimizar_mezcla, crear_material
    
    # Crear test data
    mat1 = crear_material("Material1", [0, 5, 15, 25, 35, 40, 45, 50, 55, 60], 0.35)
    mat2 = crear_material("Material2", [0, 2, 8, 15, 20, 25, 30, 35, 40, 45], 0.65)
    
    config = {
        'materiales': [mat1, mat2],
        'limites': {
            '12.5': [0, 10], '9.5': [10, 30], '6.3': [30, 50],
            '4.8': [50, 65], '2.4': [65, 80], '1.2': [80, 90],
            '0.6': [88, 95], '0.3': [92, 98], '0.15': [95, 100],
            '0.075': [98, 100]
        },
        'tamices': ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.6', '0.3', '0.15', '0.075'],
        'opciones': {'verbose': False}
    }
    
    resultado = optimizar_mezcla(config)
    print(f"Exito: {resultado['exito']}")
    print(f"Proporciones: {resultado['proporciones_pct']}")
    print(f"Error: {resultado['error_minimo']:.3f}")
```

## Notas Importantes

1. **Representación PASANTE:** Todos los cálculos internos usan PASANTE. Si tienes retenidos, convierte primero:
   ```python
   from src.controller.autoDensidad.calculoPorRetenidos.core import crear_material
   material = crear_material(nombre, retenidos_individuales, w)
   # Ya incluye conversión a PASANTE internamente
   ```

2. **Normalización de Pesos:** Los pesos se normalizan automáticamente. No es necesario que sumen 1.

3. **Orden de Tamices:** Los tamices deben estar en orden decreciente (mayor a menor).

4. **Configuración Flexible:** Todos los parámetros de decisión y optimización son configurables.

5. **Historial Completo:** El resultado incluye la trayectoria completa de iteraciones para análisis posterior.

## Solución de Problemas

### Error: "Validación fallida"
- Verificar que materiales tengo array 'pasante'
- Verificar que cada material tiene un peso 'w' numérico
- Verificar que limites tiene formato {tamiz: [min, max]}
- Verificar que tamices es un array de strings

### No Converge
- Aumentar `max_iteraciones` en opciones
- Ajustar `E_umbral_base` en CONFIG_DECISION
- Revisar datos de entrada (limites incompatibles)

### Error Alto Persistente
- Generar tabla virtual automáticamente (sistema lo hace)
- Revisar si los límites son realizables
- Verificar que los materiales de entrada son correctos

## Contacto / Soporte

Para bugs o mejoras, revisar documentación en:
- `/NUCLEO_MATEMATICO_MINIMO.md` - Fórmulas de mezcla
- `/DEFINICION_OPERATIVA_ERROR.md` - Métrica de error
- `/CRITERIO_DECISION_OPTIMIZACION.md` - Lógica de decisión
- `/ANALISIS_OPTIMIZACION_N_TABLAS_FIJAS.md` - Optimización

---

**Versión:** 1.0.0  
**Estado:** ✅ Producción  
**Lenguaje:** Python 3.7+  
**Dependencias:** numpy (opcional, no requerido)
