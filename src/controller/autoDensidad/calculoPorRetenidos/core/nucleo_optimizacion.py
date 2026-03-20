"""
NUCLEO DE OPTIMIZACION (Python)

Optimiza proporciones usando descenso de gradiente + proyección
"""

import math
from .nucleo_mezcla import calcular_mezcla_pasante, normalizar_pesos


CONFIG_OPT = {
    'max_iteraciones': 1000,
    'learning_rate_inicial': 0.01,
    'tol_convergencia': 1e-6,
    'min_paso': 1e-8,
    'regularizacion_L1': 0.0,
    'verbose': False
}


def calcular_error_cuadratico(pasante_mezcla, limites, tamices):
    """
    Calcula error cuadrático (para optimización interna)
    
    J(w) = Σ_{i=1}^M e_i(w)^2
    
    Args:
        pasante_mezcla: list
        limites: dict
        tamices: list
    
    Returns:
        float - J(w)
    """
    J = 0.0
    
    for i in range(min(len(pasante_mezcla), len(tamices))):
        tamiz = tamices[i]
        pasante = pasante_mezcla[i]
        
        tamiz_str = str(tamiz)
        if tamiz_str not in limites:
            continue
        
        limite = limites[tamiz_str]
        min_pct, max_pct = float(limite[0]), float(limite[1])
        
        # Penalidad cuadrática
        if pasante < min_pct:
            delta = min_pct - pasante
            J += delta * delta
        elif pasante > max_pct:
            delta = pasante - max_pct
            J += delta * delta
    
    return J


def calcular_gradiente(w, materiales, limites, tamices, eps=1e-5):
    """
    Calcula gradiente numérico de J respecto a w
    
    ∇J(w) ≈ (J(w + eps*e_i) - J(w)) / eps
    
    Args:
        w: list - Proporciones actuales
        materiales: list - Materiales
        limites: dict
        tamices: list
        eps: float - Tamaño de paso para diferencias finitas
    
    Returns:
        list - Gradiente
    """
    N = len(w)
    grad = [0.0] * N
    
    # Evaluación en w actual
    pasante_actual = calcular_mezcla_pasante(
        [{'pasante': m['pasante'], 'w': w[i]} for i, m in enumerate(materiales)]
    )
    J_actual = calcular_error_cuadratico(pasante_actual, limites, tamices)
    
    # Aproximación por diferencias finitas
    for i in range(N):
        w_plus = w[:]
        w_plus[i] += eps
        
        # Normalizar
        suma = sum(w_plus)
        if suma > 0:
            w_plus = [x / suma for x in w_plus]
        
        pasante_plus = calcular_mezcla_pasante(
            [{'pasante': m['pasante'], 'w': w_plus[j]} for j, m in enumerate(materiales)]
        )
        J_plus = calcular_error_cuadratico(pasante_plus, limites, tamices)
        
        grad[i] = (J_plus - J_actual) / eps
    
    return grad


def normalizar_proporciones_opt(w):
    """
    Normaliza proporciones para que sumen 1
    
    Args:
        w: list
    
    Returns:
        list - Proporciones normalizadas
    """
    suma = sum(float(x) for x in w)
    
    if suma <= 0:
        return [1.0 / len(w)] * len(w)
    
    return [float(x) / suma for x in w]


def proyectar_al_dominio(w):
    """
    Proyecta w al dominio factible
    
    Restricciones:
    - w_i >= 0
    - Σ w_i = 1
    
    Args:
        w: list
    
    Returns:
        list - w proyectado
    """
    # Clip a [0, 1]
    w_proj = [max(0.0, min(1.0, float(x))) for x in w]
    
    # Normalizar para que sume 1
    w_proj = normalizar_proporciones_opt(w_proj)
    
    return w_proj


def optimizar_proporciones(materiales, limites, tamices, opciones=None):
    """
    Optimiza proporciones usando descenso de gradiente
    
    Objetivo: min J(w) = Σ e_i(w)^2
    
    Restricciones:
    - Σ w_i = 1
    - w_i >= 0
    
    Args:
        materiales: list - Materiales
        limites: dict
        tamices: list
        opciones: dict - Override de CONFIG_OPT
    
    Returns:
        dict - {w_optimizado, proporciones_pct, error_inicial, error_final, ...}
    """
    config = {**CONFIG_OPT}
    if opciones:
        config.update(opciones)
    
    # Validación
    if not materiales:
        return {
            'w_optimizado': None,
            'error': 'Sin materiales',
            'convergio': False,
            'iteraciones': 0
        }
    
    N = len(materiales)
    
    # Inicializar w con proporciones actuales
    w = [m.get('w', 1.0 / N) for m in materiales]
    w = proyectar_al_dominio(w)
    
    # Evaluar error inicial
    pasante_inicial = calcular_mezcla_pasante(
        [{'pasante': m['pasante'], 'w': w[i]} for i, m in enumerate(materiales)]
    )
    J_inicial = calcular_error_cuadratico(pasante_inicial, limites, tamices)
    
    # Descenso de gradiente
    J_actual = J_inicial
    learning_rate = config['learning_rate_inicial']
    iteracion = 0
    convergio = False
    
    for iteracion in range(config['max_iteraciones']):
        # Calcular gradiente
        grad = calcular_gradiente(w, materiales, limites, tamices)
        
        # Norma del gradiente
        grad_norm = math.sqrt(sum(g * g for g in grad))
        
        if config['verbose']:
            print(f"[OPT] Iter {iteracion}: J={J_actual:.6f}, |∇J|={grad_norm:.6f}, lr={learning_rate:.6f}")
        
        # Verificar convergencia
        if grad_norm < config['tol_convergencia']:
            convergio = True
            if config['verbose']:
                print(f"[OPT] Convergió en iteración {iteracion}")
            break
        
        # Paso de descenso
        w_nuevo = [w[i] - learning_rate * grad[i] for i in range(N)]
        w_nuevo = proyectar_al_dominio(w_nuevo)
        
        # Evaluar nuevo error
        pasante_nuevo = calcular_mezcla_pasante(
            [{'pasante': m['pasante'], 'w': w_nuevo[i]} for i, m in enumerate(materiales)]
        )
        J_nuevo = calcular_error_cuadratico(pasante_nuevo, limites, tamices)
        
        # Si mejora, continuar
        if J_nuevo < J_actual - config['min_paso']:
            w = w_nuevo
            J_actual = J_nuevo
            learning_rate = min(learning_rate * 1.1, 0.1)
        else:
            # Si no mejora, reducir learning rate
            learning_rate *= 0.5
            
            if learning_rate < config['min_paso']:
                convergio = True
                if config['verbose']:
                    print(f"[OPT] Learning rate muy pequeño, terminando")
                break
    
    # Resultado final
    return {
        'w_optimizado': [round(x, 6) for x in w],
        'proporciones_pct': [round(x * 100, 2) for x in w],
        'error_inicial': J_inicial,
        'error_final': J_actual,
        'mejora': J_inicial - J_actual,
        'mejora_relativa': (J_inicial - J_actual) / J_inicial if J_inicial > 0 else 0,
        'iteraciones': iteracion + 1,
        'convergio': convergio,
        'learning_rate_final': learning_rate
    }


def validar_optimizacion(resultado):
    """
    Valida si optimización fue exitosa
    
    Args:
        resultado: dict
    
    Returns:
        dict - {exitoso, razon, mejora_relativa_pct}
    """
    if not resultado.get('w_optimizado'):
        return {
            'exitoso': False,
            'razon': resultado.get('error', 'Error en optimización'),
            'mejora_relativa_pct': 0
        }
    
    mejora_rel_pct = round(resultado['mejora_relativa'] * 10000) / 100
    
    # Criterio: mejora > 1% o error final muy pequeño
    exitosa = resultado['mejora_relativa'] > 0.01 or resultado['error_final'] < 0.1
    
    return {
        'exitoso': exitosa,
        'razon': f"Mejora de {mejora_rel_pct}%" if exitosa else f"Mejora insuficiente ({mejora_rel_pct}%)",
        'mejora_relativa_pct': mejora_rel_pct,
        'error_final': resultado['error_final'],
        'iteraciones': resultado['iteraciones'],
        'convergio': resultado['convergio']
    }


def generar_tabla_virtual(materiales, reporte_error, tamices):
    """
    Genera tabla virtual estratégica en zona crítica
    
    Args:
        materiales: list
        reporte_error: dict
        tamices: list
    
    Returns:
        dict - Nueva tabla virtual
    """
    zona_critica = reporte_error['zona_critica']
    
    # Identificar índices de zona crítica
    from .nucleo_error import definir_zonas_automaticas
    zonas = definir_zonas_automaticas(tamices)
    indices_zona = zonas.get(zona_critica, [])
    
    # Crear tabla virtual como promedio ponderado
    # Enfatizando pasante en zona crítica
    pasante_virtual = []
    
    for i, t in enumerate(tamices):
        en_zona = i in indices_zona
        
        if en_zona:
            # En zona crítica: ajustar según necesidad
            error_en_idx = reporte_error['errores_por_tamiz'][i] if i < len(reporte_error['errores_por_tamiz']) else None
            
            if error_en_idx:
                if error_en_idx['tipo'] == 'debajo':
                    # Necesita más pasante
                    pasante_virtual.append(100.0 - (100.0 - error_en_idx['pasante']) * 0.5)
                elif error_en_idx['tipo'] == 'arriba':
                    # Necesita menos pasante
                    pasante_virtual.append(error_en_idx['pasante'] * 0.7)
                else:
                    pasante_virtual.append(error_en_idx['pasante'])
            else:
                pasante_virtual.append(50.0)
        else:
            # Fuera de zona crítica: interpolación suave
            idx_anterior = max(0, i - 1)
            idx_siguiente = min(len(tamices) - 1, i + 1)
            
            p_anterior = (materiales[idx_anterior]['pasante'][i] if idx_anterior < len(materiales) 
                         else 50.0)
            p_siguiente = (materiales[idx_siguiente]['pasante'][i] if idx_siguiente < len(materiales) 
                          else 50.0)
            
            pasante_virtual.append((p_anterior + p_siguiente) / 2.0)
    
    timestamp = int(__import__('time').time() * 1000) % 10000
    
    return {
        'nombre': f'tabla_virtual_{timestamp}',
        'pasante': [round(x, 2) for x in pasante_virtual],
        'es_virtual': True,
        'generada_en_zona': zona_critica
    }


if __name__ == '__main__':
    # Test simple
    from .nucleo_mezcla import crear_material
    
    mat1 = crear_material("Arena", [0, 5, 15, 25, 35, 40, 45, 50, 55, 60], 0.35)
    mat2 = crear_material("Grava", [0, 2, 8, 15, 20, 25, 30, 35, 40, 45], 0.65)
    
    limites = {
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
    }
    tamices = ['12.5', '9.5', '6.3', '4.8', '2.4', '1.2', '0.6', '0.3', '0.15', '0.075']
    
    resultado = optimizar_proporciones([mat1, mat2], limites, tamices)
    print("Resultado:", resultado)
