"""
Core modules for granulometric mixture optimization
"""

from .nucleo_mezcla import (
    calcular_ret_acum,
    calcular_pasante,
    calcular_mezcla_pasante,
    validar_monotonia_pasante,
    normalizar_pesos,
    crear_material,
    validar_mezcla
)

from .nucleo_error import (
    calcular_error_por_tamiz,
    calcular_errores_por_tamiz,
    definir_zonas_automaticas,
    calcular_errores_por_zona,
    crear_reporte_error,
    detectar_no_correcible
)

from .nucleo_decision import (
    CONFIG_DECISION,
    clasificar_suficiencia,
    evaluar_mejora,
    predecir_mejora_tabla_virtual,
    evaluar_parada,
    crear_reporte_decision,
    generar_recomendacion,
    generar_proximos_pasos
)

from .nucleo_optimizacion import (
    CONFIG_OPT,
    calcular_error_cuadratico,
    calcular_gradiente,
    normalizar_proporciones_opt,
    proyectar_al_dominio,
    optimizar_proporciones,
    validar_optimizacion,
    generar_tabla_virtual
)

from .nucleo_iteracion import (
    EstadoIteracion,
    HistorialIteraciones,
    ejecutar_iteracion,
    ejecutar_optimizacion_completa,
    resumir_estado
)

from .api_integracion import (
    validar_configuracion,
    optimizar_mezcla,
    analizar_mezcla_actual,
    exportar_resultado,
    generar_mensaje_resultado
)

__all__ = [
    # Mezcla
    'calcular_ret_acum',
    'calcular_pasante',
    'calcular_mezcla_pasante',
    'validar_monotonia_pasante',
    'normalizar_pesos',
    'crear_material',
    'validar_mezcla',
    
    # Error
    'calcular_error_por_tamiz',
    'calcular_errores_por_tamiz',
    'definir_zonas_automaticas',
    'calcular_errores_por_zona',
    'crear_reporte_error',
    'detectar_no_correcible',
    
    # Decision
    'CONFIG_DECISION',
    'clasificar_suficiencia',
    'evaluar_mejora',
    'predecir_mejora_tabla_virtual',
    'evaluar_parada',
    'crear_reporte_decision',
    'generar_recomendacion',
    'generar_proximos_pasos',
    
    # Optimización
    'CONFIG_OPT',
    'calcular_error_cuadratico',
    'calcular_gradiente',
    'normalizar_proporciones_opt',
    'proyectar_al_dominio',
    'optimizar_proporciones',
    'validar_optimizacion',
    'generar_tabla_virtual',
    
    # Iteración
    'EstadoIteracion',
    'HistorialIteraciones',
    'ejecutar_iteracion',
    'ejecutar_optimizacion_completa',
    'resumir_estado',
    
    # API
    'validar_configuracion',
    'optimizar_mezcla',
    'analizar_mezcla_actual',
    'exportar_resultado',
    'generar_mensaje_resultado'
]
