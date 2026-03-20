"""
NUCLEO DE ITERACION (Python)

Control del loop principal de optimización
Mantiene historial, genera tablas virtuales, evalúa parada
"""

from datetime import datetime
from .nucleo_mezcla import calcular_mezcla_pasante
from .nucleo_error import crear_reporte_error
from .nucleo_decision import crear_reporte_decision
from .nucleo_optimizacion import optimizar_proporciones, generar_tabla_virtual


class EstadoIteracion:
    """Captura estado en una iteración"""
    
    def __init__(self, numero=0):
        self.numero = numero
        self.timestamp = datetime.now().isoformat()
        self.pasante_mezcla = []
        self.reporte_error = None
        self.reporte_decision = None
        self.proporciones = []
        self.error_total = 0.0
        self.cumplimiento = 0.0
        self.mejora_vs_anterior = 0.0
    
    def __str__(self):
        return f"Iter {self.numero}: E={self.error_total:.3f}, Cumpl={self.cumplimiento*100:.1f}%"
    
    def __repr__(self):
        return self.__str__()


class HistorialIteraciones:
    """Mantiene historial de iteraciones"""
    
    def __init__(self, max_iteraciones=10):
        self.iteraciones = []
        self.max_iteraciones = max_iteraciones
        self.tablas_virtuales = []
        self.tablas_virtuales_usadas = 0
    
    def agregar_iteracion(self, estado):
        """Agrega una iteración al historial"""
        self.iteraciones.append(estado)
    
    def obtener_ultima(self):
        """Obtiene la última iteración"""
        return self.iteraciones[-1] if self.iteraciones else None
    
    def obtener_anterior(self, offset=1):
        """Obtiene iteración anterior"""
        idx = len(self.iteraciones) - 1 - offset
        return self.iteraciones[idx] if idx >= 0 else None
    
    def obtener_trayectoria(self):
        """Obtiene trayectoria de error y cumplimiento"""
        return [
            {
                'num': it.numero,
                'error': it.error_total,
                'cumpl': it.cumplimiento
            }
            for it in self.iteraciones
        ]
    
    def esta_estancada(self):
        """Verifica si hay estancamiento"""
        if len(self.iteraciones) < 3:
            return False
        
        ultimas = self.iteraciones[-3:]
        mejora1 = ultimas[1].error_total - ultimas[0].error_total
        mejora2 = ultimas[2].error_total - ultimas[1].error_total
        
        # Estancada si última 2 mejoras < 0.3
        return abs(mejora1) < 0.3 and abs(mejora2) < 0.3
    
    def obtener_resumen(self):
        """Obtiene resumen del historial"""
        if not self.iteraciones:
            return {'error': 'Historial vacío'}
        
        primera = self.iteraciones[0]
        ultima = self.iteraciones[-1]
        minimo = min(self.iteraciones, key=lambda it: it.error_total)
        
        errores = [it.error_total for it in self.iteraciones]
        media = sum(errores) / len(errores)
        
        return {
            'iteraciones_totales': len(self.iteraciones),
            'error_inicial': primera.error_total,
            'error_final': ultima.error_total,
            'error_minimo': minimo.error_total,
            'error_promedio': media,
            'mejora_total': primera.error_total - ultima.error_total,
            'mejora_total_relativa': (primera.error_total - ultima.error_total) / primera.error_total 
                                      if primera.error_total > 0 else 0,
            'iteracion_mejor': minimo.numero,
            'tablas_virtuales_usadas': self.tablas_virtuales_usadas
        }


def ejecutar_iteracion(config, historial):
    """
    Ejecuta una iteración completa
    
    Args:
        config: dict - {materiales, limites, tamices, ...}
        historial: HistorialIteraciones
    
    Returns:
        dict - {iteracion, estado, reporte_error, reporte_decision, debe_continuar, razon}
    """
    numero_iter = len(historial.iteraciones)
    
    # Paso 1: Calcular mezcla actual
    pasante_mezcla = calcular_mezcla_pasante(config['materiales'])
    
    # Paso 2: Evaluar error
    reporte_error = crear_reporte_error(
        pasante_mezcla,
        config['limites'],
        config['tamices']
    )
    
    # Paso 3: Crear decisión
    reporte_decision = crear_reporte_decision(
        reporte_error,
        historial,
        len(config['tamices'])
    )
    
    # Paso 4: Crear estado
    estado = EstadoIteracion(numero_iter)
    estado.pasante_mezcla = pasante_mezcla
    estado.reporte_error = reporte_error
    estado.reporte_decision = reporte_decision
    estado.proporciones = [m.get('w', 0) for m in config['materiales']]
    estado.error_total = reporte_error['error_total']
    estado.cumplimiento = reporte_error['cumplimiento_total_pct'] / 100.0
    
    # Mejora vs anterior
    anterior = historial.obtener_ultima()
    if anterior:
        estado.mejora_vs_anterior = anterior.error_total - estado.error_total
    
    # Paso 5: Agregar al historial
    historial.agregar_iteracion(estado)
    
    # Paso 6: Evaluar parada
    parada = reporte_decision['parada']
    
    debe_continuar = parada['razon'] == 'continuar'
    razon_parada = {
        'perfección': 'Solución perfecta alcanzada',
        'aceptable': 'Solución aceptable alcanzada',
        'estancamiento': 'Error estancado, no hay mejora',
        'límite_iters': 'Límite de iteraciones alcanzado',
        'continuar': 'Continuando optimización'
    }.get(parada['razon'], 'Desconocida')
    
    return {
        'iteracion': numero_iter,
        'estado': estado,
        'reporte_error': reporte_error,
        'reporte_decision': reporte_decision,
        'debe_continuar': debe_continuar,
        'razon_parada': razon_parada
    }


def ejecutar_optimizacion_completa(config_inicial, callback_progreso=None):
    """
    Ejecuta loop completo de optimización
    
    Args:
        config_inicial: dict - {materiales, limites, tamices, max_iteraciones, max_tablas_virtuales}
        callback_progreso: function - Llamada cada iteración
    
    Returns:
        dict - {exito, resultado_final, historial, mensaje, ...}
    """
    if not config_inicial or 'materiales' not in config_inicial:
        return {
            'exito': False,
            'mensaje': 'Configuración inválida',
            'historial': None
        }
    
    max_iters = config_inicial.get('max_iteraciones', 5)
    max_tablas = config_inicial.get('max_tablas_virtuales', 3)
    
    historial = HistorialIteraciones(max_iters)
    config = dict(config_inicial)
    continuar = True
    iter_count = 0
    
    # Loop principal
    while continuar and iter_count < max_iters:
        # Ejecutar iteración
        resultado_iter = ejecutar_iteracion(config, historial)
        
        if callback_progreso:
            callback_progreso({
                'iteracion': resultado_iter['iteracion'],
                'error': resultado_iter['estado'].error_total,
                'cumplimiento': resultado_iter['estado'].cumplimiento,
                'mensaje': resultado_iter['razon_parada']
            })
        
        # Evaluar parada
        continuar = resultado_iter['debe_continuar']
        
        # Si debe continuar y no alcanzó suficiencia, optimizar
        if continuar and resultado_iter['reporte_decision']['estado_suficiencia']['nivel'] != 'perfecto':
            # Paso 1: Optimizar proporciones
            resultado_opt = optimizar_proporciones(
                config['materiales'],
                config['limites'],
                config['tamices'],
                {'max_iteraciones': 100, 'verbose': False}
            )
            
            if resultado_opt.get('w_optimizado'):
                # Actualizar proporciones
                config['materiales'] = [
                    {**m, 'w': resultado_opt['w_optimizado'][i]}
                    for i, m in enumerate(config['materiales'])
                ]
            
            # Paso 2: Si no hay mejora significativa, generar tabla virtual
            if not resultado_iter['reporte_decision']['mejora']['mejora_significativa'] and \
               historial.tablas_virtuales_usadas < max_tablas:
                
                tabla_virtual = generar_tabla_virtual(
                    config['materiales'],
                    resultado_iter['reporte_error'],
                    config['tamices']
                )
                
                # Agregar tabla virtual
                config['materiales'].append({
                    'nombre': tabla_virtual['nombre'],
                    'pasante': tabla_virtual['pasante'],
                    'w': 0.1,
                    'es_virtual': True,
                    'ret_ind': [],  # Se calcula si es necesario
                    'ret_acum': []
                })
                
                historial.tablas_virtuales.append(tabla_virtual)
                historial.tablas_virtuales_usadas += 1
                
                # Renormalizar pesos
                suma_w = sum(m.get('w', 0) for m in config['materiales'])
                config['materiales'] = [
                    {**m, 'w': m.get('w', 0) / suma_w if suma_w > 0 else 1/len(config['materiales'])}
                    for m in config['materiales']
                ]
        
        iter_count += 1
    
    # Resultado final
    ultima_iteracion = historial.obtener_ultima()
    resumen = historial.obtener_resumen()
    
    return {
        'exito': not ultima_iteracion.reporte_decision['parada'].get('debe_parar', True) 
                 if ultima_iteracion.reporte_decision else False,
        'iteracion_final': iter_count,
        'error_final': ultima_iteracion.error_total if ultima_iteracion else float('inf'),
        'cumplimiento_final': ultima_iteracion.cumplimiento if ultima_iteracion else 0,
        'proporciones_finales': ultima_iteracion.proporciones if ultima_iteracion else [],
        'historial': historial,
        'resumen': resumen,
        'razon_parada': ultima_iteracion.reporte_decision['parada'].get('razon', 'Desconocida') 
                        if ultima_iteracion and ultima_iteracion.reporte_decision else 'Desconocida',
        'reporte_decision_final': ultima_iteracion.reporte_decision if ultima_iteracion else None,
        'reporte_error_final': ultima_iteracion.reporte_error if ultima_iteracion else None,
        'mensaje': f'Optimización completada en {iter_count} iteraciones'
    }


def resumir_estado(historial):
    """
    Resume estado actual en formato legible
    
    Args:
        historial: HistorialIteraciones
    
    Returns:
        str
    """
    resumen = historial.obtener_resumen()
    trayectoria = historial.obtener_trayectoria()
    
    texto = "HISTORIAL DE OPTIMIZACIÓN\n"
    texto += "=" * 50 + "\n"
    
    # Tabla de iteraciones
    texto += "Iteración | Error    | Cumpl% | Mejora\n"
    texto += "-" * 45 + "\n"
    
    for i, punto in enumerate(trayectoria):
        mejora = "---"
        if i > 0:
            mejora = f"{(trayectoria[i-1]['error'] - punto['error']):.3f}"
        
        texto += f"{str(punto['num']).ljust(9)} | {str(punto['error'].__format__('.3f')).ljust(8)} | " \
                f"{str((punto['cumpl']*100).__format__('.1f')).ljust(5)} | {mejora}\n"
    
    texto += "\n" + "=" * 50 + "\n"
    texto += f"Error inicial: {resumen['error_inicial']:.3f}\n"
    texto += f"Error final: {resumen['error_final']:.3f}\n"
    texto += f"Mejora total: {resumen['mejora_total']:.3f} ({resumen['mejora_total_relativa']*100:.1f}%)\n"
    texto += f"Tablas virtuales usadas: {resumen['tablas_virtuales_usadas']}\n"
    
    return texto


if __name__ == '__main__':
    # Test simple
    from .nucleo_mezcla import crear_material
    
    mat1 = crear_material("Arena", [0, 5, 15, 25, 35, 40, 45, 50, 55, 60], 0.35)
    mat2 = crear_material("Grava", [0, 2, 8, 15, 20, 25, 30, 35, 40, 45], 0.65)
    
    config = {
        'materiales': [mat1, mat2],
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
        'max_iteraciones': 5,
        'max_tablas_virtuales': 3
    }
    
    resultado = ejecutar_optimizacion_completa(config)
    print("Resultado:")
    print(f"  Error final: {resultado['error_final']:.3f}")
    print(f"  Cumplimiento: {resultado['cumplimiento_final']*100:.1f}%")
    print(f"  Iteraciones: {resultado['iteracion_final']}")
    print("\n" + resumir_estado(resultado['historial']))
