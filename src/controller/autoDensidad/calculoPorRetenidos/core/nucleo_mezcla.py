"""
NUCLEO DE MEZCLA (Python)

Calcula mezclas ponderadas en representación PASANTE
Nunca mezcla representaciones (siempre PASANTE o siempre retenido_acumulado)
"""

import math


def calcular_ret_acum(ret_ind):
    """
    Convierte retenidos individuales a retenido acumulado
    
    Args:
        ret_ind: list of float - Retenidos individuales por tamiz
    
    Returns:
        list - Retenido acumulado
    """
    acum = []
    suma = 0.0
    for v in ret_ind:
        suma += float(v or 0.0)
        acum.append(suma)
    # Saneo numérico: limitar entre 0 y 100
    return [min(100.0, max(0.0, round(x, 2))) for x in acum]


def calcular_pasante(ret_acum):
    """
    Convierte retenido acumulado a PASANTE
    
    PASANTE = 100 - retenido_acumulado
    
    Args:
        ret_acum: list or float - Retenido acumulado
    
    Returns:
        list or float - PASANTE
    """
    if isinstance(ret_acum, (list, tuple)):
        return [100.0 - float(x) for x in ret_acum]
    else:
        return 100.0 - float(ret_acum)


def calcular_mezcla_pasante(materiales):
    """
    Calcula mezcla ponderada en representación PASANTE
    
    Formula: mix[j] = Σ w_i * PASANTE_i[j]
    
    Args:
        materiales: list - [{nombre, pasante: [], w: float}, ...]
    
    Returns:
        list - PASANTE de la mezcla
    """
    if not materiales:
        return []
    
    n = len(materiales[0]['pasante'])
    mezcla = [0.0] * n
    
    for material in materiales:
        w = float(material.get('w', 0.0))
        pasante = material.get('pasante', [])
        
        for j in range(min(n, len(pasante))):
            mezcla[j] += w * float(pasante[j])
    
    # Sanear y redondear
    return [round(min(100.0, max(0.0, x)), 2) for x in mezcla]


def validar_monotonia_pasante(pasante):
    """
    Verifica que PASANTE sea monótonamente decreciente
    
    Args:
        pasante: list of float
    
    Returns:
        dict - {valido: bool, razon: str}
    """
    if not pasante or len(pasante) < 2:
        return {'valido': True, 'razon': 'Array muy corto'}
    
    for i in range(len(pasante) - 1):
        if pasante[i] < pasante[i + 1]:
            return {
                'valido': False,
                'razon': f'No monotónico en índice {i}: {pasante[i]} > {pasante[i+1]}'
            }
    
    return {'valido': True, 'razon': 'Monotonía verificada'}


def normalizar_pesos(w):
    """
    Normaliza pesos para que sumen 1.0
    
    Args:
        w: list of float
    
    Returns:
        list - Pesos normalizados
    """
    suma = sum(float(x) for x in w)
    
    if suma <= 0:
        # Distribución igual
        return [1.0 / len(w)] * len(w)
    
    return [float(x) / suma for x in w]


def crear_material(nombre, ret_ind, w):
    """
    Crea un objeto material con todas las representaciones
    
    Args:
        nombre: str
        ret_ind: list - Retenidos individuales
        w: float - Peso/proporción
    
    Returns:
        dict - Material con ret_ind, ret_acum, pasante, w
    """
    ret_acum = calcular_ret_acum(ret_ind)
    pasante = calcular_pasante(ret_acum)
    
    return {
        'nombre': nombre,
        'ret_ind': ret_ind,
        'ret_acum': ret_acum,
        'pasante': pasante,
        'w': float(w)
    }


def validar_mezcla(resultado):
    """
    Valida coherencia de mezcla
    
    Args:
        resultado: dict - {pasante, error, etc}
    
    Returns:
        dict - {valido: bool, errores: []}
    """
    errores = []
    
    if 'pasante' not in resultado:
        errores.append("Falta campo 'pasante'")
    else:
        pasante = resultado['pasante']
        
        # Verificar monotonía
        for i in range(len(pasante) - 1):
            if pasante[i] < pasante[i + 1]:
                errores.append(f"No monotónico en índice {i}")
                break
        
        # Verificar rango [0, 100]
        for i, p in enumerate(pasante):
            if not (0 <= p <= 100):
                errores.append(f"PASANTE[{i}] = {p} fuera de [0, 100]")
                break
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }


if __name__ == '__main__':
    # Test
    mat1 = crear_material("Arena", [0, 5, 15, 25, 35, 40, 45, 50, 55, 60, 40], 0.35)
    mat2 = crear_material("Grava", [0, 2, 8, 15, 20, 25, 30, 35, 40, 45, 55], 0.65)
    
    print("Material 1:", mat1['pasante'])
    print("Material 2:", mat2['pasante'])
    
    mezcla = calcular_mezcla_pasante([mat1, mat2])
    print("Mezcla:", mezcla)
    
    print("Validación:", validar_mezcla({'pasante': mezcla}))
