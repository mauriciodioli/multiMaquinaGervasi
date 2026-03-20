"""
calculoPorRetenidos Package

Module for granulometric mixture optimization with Python backend
All calculations (mezcla, error, decision, optimization) are in core/
"""

from .core import (
    # Mezcla
    calcular_mezcla_pasante,
    crear_material,
    
    # Error
    crear_reporte_error,
    
    # Decision
    crear_reporte_decision,
    
    # Optimization
    optimizar_proporciones,
    
    # Iteration
    ejecutar_optimizacion_completa,
    HistorialIteraciones,
    
    # API
    optimizar_mezcla,
    analizar_mezcla_actual,
    validar_configuracion,
    exportar_resultado
)

__version__ = '1.0.0'
__author__ = 'Granulometric Optimization System'

__all__ = [
    'calcular_mezcla_pasante',
    'crear_material',
    'crear_reporte_error',
    'crear_reporte_decision',
    'optimizar_proporciones',
    'ejecutar_optimizacion_completa',
    'HistorialIteraciones',
    'optimizar_mezcla',
    'analizar_mezcla_actual',
    'validar_configuracion',
    'exportar_resultado'
]
