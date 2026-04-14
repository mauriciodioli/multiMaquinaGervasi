import matplotlib.pyplot as plt
import io
import base64
from flask import Blueprint, request, render_template, send_file, jsonify, redirect
from collections import defaultdict
import numpy as np
from flask import jsonify, request
import pandas as pd
from scipy.optimize import minimize
from controller.autoDensidad.calcularMezclaOptima import calcular_mezcla_optima
from controller.autoDensidad.calcularMezclaOptima import mostrar_datos_crudos_entrada
from controller.autoDensidad.calcularMezclaOptima import encontrar_n_optimo
from controller.autoDensidad.calcularMezclaOptima import calcular_curva_fuller
from controller.autoDensidad.optimizar_fuller import generar_informe_ajuste
from src.utils.auth import current_user
import math
from src.utils.get_textos_menu  import get_textos_menu

# ===== Importaciones del sistema de optimización granulométrica =====
from .core.api_integracion import (
    optimizar_mezcla,
    analizar_mezcla_actual,
    validar_configuracion,
    exportar_resultado
)
from .core import crear_material
from .core.auditoria_decision import generar_auditoria_completa





calculoPorRetenidos = Blueprint('calculoPorRetenidos', __name__)

MF_SIEVES_BR = [4.8, 2.4, 1.2, 0.6, 0.3, 0.15]
TAMICES_ORDEN = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075, "Fundo"]




def _ordenar_indices(tamices):
    # fuerza el orden norma; si falta alguno lo ignora, si sobra alguno lo manda al final
    pos = {str(t): i for i, t in enumerate(TAMICES_ORDEN)}
    return sorted(range(len(tamices)), key=lambda i: pos.get(str(tamices[i]), 999))

def _acum_to_ind(acum_list):
    """
    Convierte acumulado → individual
    """
    ind = []
    prev = 0.0

    for v in acum_list:
        val = float(v or 0.0)
        ind.append(max(0.0, val - prev))
        prev = val

    return ind

def _acum_desc(ret_ind_list, debug=False):
    """
    Convierte retido individual → acumulado.
    Si detecta que los datos parecen acumulados, los corrige automáticamente.
    """

    # Limpieza básica
    vals = [float(v or 0.0) for v in ret_ind_list]
    total = sum(vals)

    # 🔍 DETECCIÓN AUTOMÁTICA
    # Si suma es muy alta → probablemente es acumulado
    if total > 120:
        if debug:
            print("⚠️ [_acum_desc] Detectado formato ACUMULADO → convirtiendo a IND")

        vals = _acum_to_ind(vals)

    # 🧮 Cálculo acumulado real
    acum = []
    s = 0.0

    for v in vals:
        s += v
        acum.append(s)

    # 🔧 Saneo numérico
    acum = [min(100.0, max(0.0, round(x, 2))) for x in acum]

    # 🔍 Validación final
    if debug:
        if acum and abs(acum[-1] - 100) > 2:
            print(f"⚠️ [_acum_desc] ACUM final no ≈100 → {acum[-1]}")

    return acum

def _mezcla_ponderada_acum(materiales):
    # materiales: [{nombre, w, ret_ind[], ret_acum[]}, ...] con alineación ya hecha
    n = len(materiales[0]['ret_acum'])
    mix_acum = [0.0] * n
    for m in materiales:
        w = float(m['w'])
        for k in range(n):
            mix_acum[k] += w * m['ret_acum'][k]
    return [round(x, 1) for x in mix_acum]


def _finura_modulus(mix_acum, tamices, mf_sieves=MF_SIEVES_BR):
    def eq(a, b, tol=1e-3):
        try: return abs(float(a) - float(b)) < tol
        except: return False
    idxs = [i for i,t in enumerate(tamices) if any(eq(t,s) for s in mf_sieves)]
    return round(sum(float(mix_acum[i]) for i in idxs)/100.0, 2) if idxs else 0.0


def optimizar_proporciones(materiales, tamices_ord, limites, log):
    """
    Optimiza automáticamente los pesos de 3 materiales para minimizar
    desviación respecto a la faixa "bloco" CON regularización.
    
    Args:
        materiales: List[{nombre, w, ret_acum, ...}]
        tamices_ord: Sieves in order
        limites: {"bloco": {sieve: [min, max]}, ...}
        log: Debug logger
    
    Returns:
        {
            "tipo": "optimizacion",
            "proporciones_optimizadas": [w1, w2, w3],
            "error_estimado": float,
            "mix_acum_optimizado": [float]
        } or None if failed/not applicable
    """
    
    if len(materiales) != 3:
        return None
    
    if "bloco" not in limites or not limites["bloco"]:
        return None
    
    try:
        n = len(tamices_ord)
        
        # Pesos iniciales
        w_inicial = np.array([float(m["w"]) for m in materiales])
        log(f"\n[OPTIM] Pesos iniciales: {[round(w,4) for w in w_inicial]}")
        
        # Retacumulados por material
        ret_acums = [np.array(m["ret_acum"]) for m in materiales]
        
        # ====== ESTRATEGIA D: OPTIMIZACIÓN SIN RESTRICCIONES DE MÍNIMO ======
        # Si no hay solución viable, simplemente retorna None
        # No usamos MIN_WEIGHT porque esto paraliza la búsqueda
        LAMBDA_REG = 10.0  # Regularización moderada (NO 100)
        
        # Definir función objetivo SIMPLE pero EFECTIVA
        def objetivo(pesos):
            """
            Minimizar: error_faixa + λ * varianza_de_cambios
            Sin restricciones duras que paralicen el optimizador
            """
            # Clip automático
            pesos = np.clip(pesos, 0.0, 1.0)
            
            s = sum(pesos)
            if s <= 0:
                return 1e10
            
            # Normalizar pesos
            w_norm = pesos / s
            
            # Calcular mezcla ponderada
            mix_acum_opt = np.zeros(n)
            for i, m_acum in enumerate(ret_acums):
                mix_acum_opt += w_norm[i] * m_acum
            
            # PARTE 1: Error respecto a faixa
            error_faixa = 0.0
            for k, t in enumerate(tamices_ord):
                rng = limites["bloco"].get(str(t))
                if not rng:
                    continue
                
                lo, hi = float(rng[0]), float(rng[1])
                x = mix_acum_opt[k]
                
                if lo <= x <= hi:
                    pass
                else:
                    # Penalidad proporcional a la desviación
                    if x < lo:
                        error_faixa += (lo - x) ** 2
                    else:
                        error_faixa += (x - hi) ** 2
            
            # PARTE 2: Regularización SUAVE - solo penalizar cambios DRÁSTICOS
            cambios = np.abs(w_norm - w_inicial)
            reg_term = LAMBDA_REG * np.sum(cambios)  # L1, no L2
            
            total_error = error_faixa + reg_term
            return total_error
        
        # Definir restricciones
        constraints = [
            {"type": "eq", "fun": lambda w: sum(w) - 1.0}
        ]
        
        # Bounds normales: SIN restricciones mínimas de presencia
        bounds = [(0.0, 1.0) for _ in range(3)]
        
        log(f"[OPTIM] Bounds relajados: [0.0, 1.0]")
        log(f"[OPTIM] Regularización moderada: LAMBDA_REG={LAMBDA_REG}")
        
        # Solo 1 intento simple sin multi-start
        log(f"[OPTIM] Optimizando con pesos iniciales como punto de partida...")
        
        result = minimize(
            objetivo,
            w_inicial,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 5000, "ftol": 1e-12}
        )
        
        if not result.success:
            log(f"[OPTIM] ⚠️ Optimización no convergió: {result.message}")
            return None
        
        w_opt = result.x
        w_opt = np.clip(w_opt, 0.0, 1.0)
        s = sum(w_opt)
        if s <= 0:
            return None
        w_opt = w_opt / s  # Normalizar para que sume 1
        
        # POST-CHECK: Si la solución es PEOR que la inicial, rechazarla
        error_inicial = objetivo(w_inicial)
        error_final = objetivo(w_opt)
        
        log(f"[OPTIM] Error inicial: {round(error_inicial, 4)}")
        log(f"[OPTIM] Error final: {round(error_final, 4)}")
        
        if error_final >= error_inicial * 0.95:  # Mejora menor al 5%
            log(f"[OPTIM] ⚠️ Mejora insuficiente ({round(error_final/error_inicial*100, 1)}%). Rechazando optimización.")
            return None
        
        log(f"[OPTIM] ✅ Optimización exitosa: {[round(float(w),4) for w in w_opt]}")
        
        # Calcular mix final con optimizados
        mix_acum_opt = np.zeros(n)
        for i, m_acum in enumerate(ret_acums):
            mix_acum_opt += w_opt[i] * m_acum
        
        mix_acum_opt = [round(min(100.0, max(0.0, x)), 2) for x in mix_acum_opt]
        
        # Calcular error final (solo la parte de faixa, sin regularización)
        error_final_faixa = 0.0
        for k, t in enumerate(tamices_ord):
            rng = limites["bloco"].get(str(t))
            if not rng:
                continue
            lo, hi = float(rng[0]), float(rng[1])
            x = mix_acum_opt[k]
            if x < lo:
                error_final_faixa += 2.0 * (lo - x) ** 2
            elif x > hi:
                error_final_faixa += (x - hi) ** 2
        
        log(f"[OPTIM] Error final en faixa: {round(error_final_faixa, 6)}")
        
        return {
            "tipo": "optimizacion",
            "proporciones_optimizadas": [round(w, 6) for w in w_opt],
            "error_estimado": round(error_final_faixa, 6),
            "mix_acum_optimizado": mix_acum_opt
        }
    
    except Exception as e:
        log(f"[OPTIM] ✗ Error en optimización: {str(e)}")
        return None


def _validar_faixas(mix_acum, tamices, limites):
    def eval_faixa(faixa):
        oks, det = [], []
        for x, t in zip(mix_acum, tamices):
            rng = faixa.get(str(t))
            if not rng:
                oks.append(None); det.append({"tamiz":t,"ok":None}); continue
            lo, hi = rng
            ok = (x >= lo) and (x <= hi)
            oks.append(ok)
            det.append({"tamiz": t, "mix": x, "min": lo, "max": hi, "ok": ok})
        return oks, det
    ob, det_b = eval_faixa(limites.get('bloco', {}))
    op, det_p = eval_faixa(limites.get('paver', {}))
    return {"bloco": det_b, "paver": det_p}


# ================================================================================
# SISTEMA ROBUSTO DE NORMALIZACIÓN DE DATOS GRANULOMÉTRICOS
# ================================================================================

def _normalizar_escala_porcentaje(vals, debug=False):
    """
    Convierte valores en escala 0-1 a escala 0-100 si es necesario.
    
    Args:
        vals: Lista de valores (puede estar en 0-1 o 0-100)
        debug: Si True, loguea decisión
    
    Returns:
        Lista normalizada a escala 0-100, redondeada a 2 decimales
    """
    vals = [float(v or 0.0) for v in vals]
    
    if not vals:
        return vals
    
    max_val = max(vals)
    
    # Si máximo es ≤ 1.5, asumir escala 0-1 → convertir a 0-100
    if max_val > 0 and max_val <= 1.5:
        if debug:
            print(f"📊 Escala detectada 0-1 → Convirtiendo a 0-100 (max={max_val})")
        vals = [v * 100.0 for v in vals]
    
    return [round(x, 2) for x in vals]


def _ret_acum_to_ret_ind_robusto(acum_list, debug=False):
    """
    Convierte retenido acumulado a retenido individual (diferencias sucesivas).
    Valida que sea monótonamente creciente.
    
    Args:
        acum_list: Acumulado (debe ser creciente)
        debug: Si True, loguea validaciones
    
    Returns:
        Retenido individual
    """
    acum = [float(v or 0.0) for v in acum_list]
    
    # Validar monotonía
    es_creciente = all(acum[i] <= acum[i+1] for i in range(len(acum)-1))
    if not es_creciente and debug:
        print(f"⚠️ Acumulado NO es monótonamente creciente: {acum}")
    
    # Calcular diferencias
    ret_ind = []
    prev = 0.0
    for v in acum:
        ret_ind.append(max(0.0, v - prev))
        prev = v
    
    return [round(x, 2) for x in ret_ind]


def _resolver_curva_a_ret_ind(vals, formato=None, debug=False):
    """
    FUNCIÓN MAESTRA: Convierte cualquier formato de entrada a retido_ind_pct.
    
    Soporta:
    - retido individual (suma ≈ 100)
    - retido acumulado (creciente, último ≥ 90)
    - pasante acumulado (decreciente, primero ≥ 90)
    - datos en escala 0-1
    
    Args:
        vals: Lista de valores
        formato: Opcional, fuerza formato ("ret_ind", "ret_acum", "pasante")
        debug: Si True, loguea decisiones
    
    Returns:
        Retenido individual normalizado (suma ≈ 100)
    
    Raises:
        ValueError: Si no se puede determinar el formato y es imposible inferir
    """
    
    # PASO 1: Normalizar escala de porcentaje (0-1 → 0-100)
    vals_norm = _normalizar_escala_porcentaje(vals, debug=debug)
    
    # PASO 2: Determinar formato
    if formato:
        tipo_detectado = formato
        if debug:
            print(f"📋 Formato forzado por usuario: {tipo_detectado}")
    else:
        tipo_detectado = _detectar_formato(vals_norm)
        if debug:
            print(f"🔍 Formato detectado automáticamente: {tipo_detectado}")
    
    # PASO 3: Convertir a retenido individual
    if tipo_detectado == "ret_ind":
        if debug:
            print(f"✅ Entrada es retenido individual (suma ≈ 100)")
        ret_ind = vals_norm
    
    elif tipo_detectado == "ret_acum":
        if debug:
            print(f"🔄 Convirtiendo: retenido acumulado → retenido individual")
        ret_ind = _ret_acum_to_ret_ind_robusto(vals_norm, debug=debug)
    
    elif tipo_detectado == "pasante":
        if debug:
            print(f"🔄 Convirtiendo: pasante acumulado → retenido individual")
        ret_ind = _pasante_to_ret_ind(vals_norm)
    
    elif tipo_detectado == "unknown":
        # HEURÍSTICA DE RESCATE
        # Intentar inferir basado en monotonía
        es_creciente = all(vals_norm[i] <= vals_norm[i+1] for i in range(len(vals_norm)-1))
        es_decreciente = all(vals_norm[i] >= vals_norm[i+1] for i in range(len(vals_norm)-1))
        
        if es_creciente:
            if debug:
                print(f"⚠️ Formato unknown pero creciente → Asumiendo ret_acum")
            ret_ind = _ret_acum_to_ret_ind_robusto(vals_norm, debug=debug)
        elif es_decreciente:
            if debug:
                print(f"⚠️ Formato unknown pero decreciente → Asumiendo pasante")
            ret_ind = _pasante_to_ret_ind(vals_norm)
        else:
            # ÚLTIMO RECURSO: Normalizar asumiendo que son retenidos individuales no normalizados
            suma = sum(vals_norm)
            if suma > 0:
                if debug:
                    print(f"⚠️ Formato imposible de determinar (no creciente ni decreciente)")
                    print(f"   → Asumiendo retenido individual y normalizando (suma original: {suma}%)")
                ret_ind = [round((v / suma) * 100.0, 2) for v in vals_norm]
            else:
                # Si suma es 0, retornar array de ceros
                if debug:
                    print(f"⚠️ Datos vacíos (suma=0) → Retornando ceros")
                ret_ind = [0.0] * len(vals_norm)
    
    # PASO 4: Validaciones suaves (no-bloqueantes)
    ret_ind = [max(0.0, v) for v in ret_ind]  # Clamp negativos
    suma = sum(ret_ind)
    
    if suma > 0 and abs(suma - 100) > 1.0:
        if debug:
            print(f"⚠️ Suma de ret_ind = {round(suma, 2)}% (esperado ≈ 100%)")
    
    return [round(x, 2) for x in ret_ind]


def _pasante_to_ret_ind(pasante_list):
    """
    Convierte pasante acumulado (%) -> retenido individual (%)
    """
    pas = [float(v or 0.0) for v in pasante_list]
    ret_acum = [100.0 - v for v in pas]

    ret_ind = []
    prev = 0.0
    for v in ret_acum:
        ret_ind.append(max(0.0, v - prev))
        prev = v

    return [round(x, 2) for x in ret_ind]
def _detectar_formato(vals):
    vals = [float(v or 0.0) for v in vals]

    if not vals:
        return "unknown"

    creciente = all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
    decreciente = all(vals[i] >= vals[i+1] for i in range(len(vals)-1))
    total = sum(vals)

    if abs(total - 100) < 5:
        return "ret_ind"

    if creciente and vals[-1] > 90:
        return "ret_acum"

    if decreciente and vals[0] > 90:
        return "pasante"

    return "unknown"
def _normalizar_a_ret_ind(vals, debug=False):
    tipo = _detectar_formato(vals)

    if debug:
        print(f"🔍 Formato detectado: {tipo}")

    if tipo == "ret_ind":
        return vals

    if tipo == "ret_acum":
        return _acum_to_ind(vals, debug=debug)

    if tipo == "pasante":
        return _pasante_to_ret_ind(vals)
    
    
def _forzar_monotonia_decreciente(vals):
    for i in range(1, len(vals)):
        if vals[i] > vals[i-1]:
            vals[i] = vals[i-1]
    return vals
    raise ValueError("No se pudo detectar el formato de datos")
@calculoPorRetenidos.route('/calculoPorRetenidos/granulometria/retido/', methods=['POST'])
def granulometria_retido():
    data = request.get_json(force=True)

    # ---- DEBUG SWITCH ----
    qdebug = request.args.get("debug", "1")
    body_debug = data.get("debug", None)
    debug = (str(qdebug) != "0") if body_debug is None else bool(body_debug)
    log = (lambda *a, **k: print(*a, **k)) if debug else (lambda *a, **k: None)

    # STEP 1: Log full payload
    log("\n=== DEBUG FULL PAYLOAD ===")
    log(data)

    tamices = data.get('tamices', TAMICES_ORDEN)
    materiales_in = data.get('materiales', [])
    limites = data.get('limites', {})

    # STEP 2: Log raw materials
    log("\n=== DEBUG RAW MATERIALS ===")
    for m in materiales_in:
        log(m)

    if not materiales_in:
        return jsonify(ok=False, error="Faltan materiales"), 400

    log("\n=== [RETIDO] Entrada cruda ===")
    log(f"Tamices (recv): {tamices}")
    for m in materiales_in:
        log(f"  - {m.get('nombre')}: prop%={m.get('proporcion_pct')}  len(ret_ind)={len(m.get('retido_ind_pct',[]))}")

    # 1) ordenar según norma
    idx = sorted(range(len(tamices)), key=lambda i: float(tamices[i]) if str(tamices[i]).lower() != "fundo" else -1, reverse=True)
    tamices_ord = [tamices[i] for i in idx]
    log("\n> Orden aplicado:", tamices_ord)

    # 2) normalizar materiales y calcular acumulados
    materiales = []
    total_pct = sum(float(m.get('proporcion_pct', 0.0)) for m in materiales_in) or 100.0
    log(f"> Suma proporciones declaradas: {round(total_pct,2)} %")

    def check_sum_100(vals, name):
        s = round(sum(vals or []), 2)
        if abs(s-100.0) > 0.5:
            log(f"⚠️  {name}: suma IND no ~100 (={s}). (Normal en datos IND; el que debe dar 100 es ACUM final)")

    for m in materiales_in:
        nombre = m.get('nombre', 'sin_nombre')
        p = float(m.get('proporcion_pct', 0.0))
        w = p / total_pct

        # STEP 3: Log normalization flag per material
        log(f"[FLAG] {nombre} normalizar = {m.get('normalizar')}")

        # STEP 1: Build ret_map depending on input format (new filas or legacy retido_ind_pct)
        if "filas" in m and m["filas"]:
            # New format: map filas by sieve name
            ret_map = {
                str(f["tamiz"]): float(f["porcentaje"])
                for f in m["filas"]
            }
            log(f"✅ {nombre} using NEW format (filas)")
        else:
            # Fallback: old format (retido_ind_pct)
            ret_ind = m.get("retido_ind_pct", [])
            ret_map = {}
            for i, val in enumerate(ret_ind):
                if i < len(tamices_ord):
                    ret_map[str(tamices_ord[i])] = float(val)
            if ret_ind:
                log(f"⚠️ {nombre} using LEGACY format (retido_ind_pct)")

        # STEP 2: Build ordered retained array
        ret_ind_ord = []
        for t in tamices_ord:
            val = ret_map.get(str(t), 0.0)
            ret_ind_ord.append(val)

        # STEP 4: Verify IF condition with enhanced logging
        flag_normalizar = m.get("normalizar", False)
        total = sum(ret_ind_ord)
        log(f"[CHECK] {nombre} enters normalization? {flag_normalizar} (total={round(total, 2)})")

        # STEP 3: Safe normalization with validation
        # Formato de entrada (opcional, para forzar interpretación)
        formato = m.get("formato")  # Puede ser: "ret_ind", "ret_acum", "pasante"
        
        try:
            if flag_normalizar:
                if total > 0 and abs(total - 100) > 1e-6:
                    log(f"🔥 NORMALIZING {nombre}")
                    log(f"[BEFORE] {nombre} sum = {round(total, 2)}")
                    ret_ind_norm = _normalizar_ind(ret_ind_ord)
                    log(f"[AFTER] {nombre} sum = {round(sum(ret_ind_norm), 2)}")
                    log(f"🔧 {nombre} NORMALIZADO (suma original: {round(total,2)} → 100)")
                else:
                    if total == 0:
                        log(f"⚠️ {nombre} skipped normalization (sum = 0 - empty data?)")
                        ret_ind_norm = _resolver_curva_a_ret_ind(ret_ind_ord, formato=formato, debug=debug)
                    else:
                        log(f"ℹ️ {nombre} already ~100, no normalization needed (sum={round(total,2)})")
                        ret_ind_norm = _resolver_curva_a_ret_ind(ret_ind_ord, formato=formato, debug=debug)
            else:
                ret_ind_norm = _resolver_curva_a_ret_ind(ret_ind_ord, formato=formato, debug=debug)
        except Exception as e:
            # Defensa: Si falla la normalización, usar datos originales
            log(f"⚠️ {nombre} normalization FAILED: {str(e)}")
            log(f"   → Usando datos originales como fallback")
            ret_ind_norm = ret_ind_ord  # Fallback a datos originales

        ret_acum_ord = _acum_desc(ret_ind_norm, debug=debug)

        # logs por material
        check_sum_100(ret_ind_norm, f"{nombre} (IND)")
        log(f"\n-- {nombre} -- prop%={p}  w={round(w,6)}")
        log("IND:", ["{:.1f}".format(x) for x in ret_ind_norm])
        log("ACU:", ["{:.1f}".format(x) for x in ret_acum_ord])
        if str(tamices_ord[-1]).lower() == "fundo":
            log(f"ACU último (debe ~100): {ret_acum_ord[-1]}")

        materiales.append({
            "nombre": nombre,
            "proporcion_pct": round(p, 2),
            "w": round(w, 6),
            "ret_ind": [round(x, 2) for x in ret_ind_norm],
            "ret_acum": [round(x, 2) for x in ret_acum_ord]
        })

    # 3) mezcla ponderada (acumulado)
    mix_acum = _mezcla_ponderada_acum(materiales)

    # 🔥 convertir a PASANTE
    mix_pasante = [round(100 - v, 1) for v in mix_acum]
    
    log("\n> MIX ACUM (ponderado):", ["{:.1f}".format(x) for x in mix_acum])
    log("\n> MIX PASANTE:", ["{:.1f}".format(x) for x in mix_pasante])

    # 4) MF
    mf = _finura_modulus(mix_acum, tamices_ord)
    log(f"> Módulo de finura (esperado ~3.55 con planilla): {mf}")

    # 5) validación contra faixas
    valid = _validar_faixas(mix_pasante, tamices_ord, limites)
    gran_ponderada = [{"#": t, "%": mix_acum[i]} for i, t in enumerate(tamices_ord)]
    # resumen corto por tamiz
    if limites:
        log("\n> Validación Faixas:")
        for det in ("bloco","paver"):
            if det in valid:
                oks = [("✓" if d.get("ok") else "×") if d.get("ok") is not None else "-" for d in valid[det]]
                log(f"  {det:>6}: {oks}")

    # 6) salida estilo planilla
    tabla = []
    for k, t in enumerate(tamices_ord):
        fila = {"tamiz": t}
        for m in materiales:
            fila[f"{m['nombre']}_ind"]  = m["ret_ind"][k]
            fila[f"{m['nombre']}_acum"] = m["ret_acum"][k]
        fila["mix_acum"] = mix_acum[k]
        tabla.append(fila)

    # snapshot de tabla (primeras filas) para comparar rápido
    log("\n> Tabla (preview):")
    head = min(5, len(tabla))
    for r in tabla[:head]:
        log(r)

    # Generar sugerencia de división para el primer agregado
    # Generar sugerencia de división automáticamente
    sugerencia_division = evaluar_y_sugerir_division(materiales_in, materiales, tamices_ord, valid, log)
    
    if sugerencia_division:
        log(f"\n✓ Sugerencia de división generada:")
        if "grupos" in sugerencia_division and len(sugerencia_division["grupos"]) >= 2:
            log(f"  Grupo 1: {sugerencia_division['grupos'][0]['proporcion_sugerida_pct']}%")
            log(f"  Grupo 2: {sugerencia_division['grupos'][1]['proporcion_sugerida_pct']}%")
            if len(sugerencia_division["grupos"]) > 2:
                log(f"  Grupo 3: {sugerencia_division['grupos'][2]['proporcion_sugerida_pct']}%")
        if "reconstruccion_check" in sugerencia_division:
            log(f"  Error reconstrucción: {sugerencia_division['reconstruccion_check']['error_total_pct']}%")

    # ===============================================
    # MÓDULO DE OPTIMIZACIÓN AUTOMÁTICA (3 MATERIALES)
    # ===============================================
    sugerencia_optimizacion = None
    
    if len(materiales) == 3 and limites:
        # Contar errores en faixa bloco
        errores_bloco = 0
        if "bloco" in valid and isinstance(valid["bloco"], list):
            errores_bloco = sum(1 for d in valid["bloco"] if d.get("ok") == False)
        
        log(f"\n[OPTIM CHECK] 3 materiales detectados, {errores_bloco} errores en bloco")
        
        # Solo optimizar si hay errores y la curva no es perfecta
        if errores_bloco >= 1:
            log(f"[OPTIM CHECK] Desviación detectada, iniciando optimización automática...")
            sugerencia_optimizacion = optimizar_proporciones(materiales, tamices_ord, limites, log)
            
            if sugerencia_optimizacion:
                log(f"\n✓ Optimización completada:")
                log(f"  Proporciones encontradas: {sugerencia_optimizacion['proporciones_optimizadas']}")
                log(f"  Error estimado: {sugerencia_optimizacion['error_estimado']}")
        else:
            log(f"[OPTIM CHECK] Curva dentro de especificación, sin optimización necesaria")

    # ===============================================
    # MÓDULO DE DIVISIÓN EN N TABLAS (2, 3, 4, 5)
    # ===============================================
    divisiones_n_tablas = None
    
    if materiales_in and len(materiales_in) > 0:
        try:
            primer_material = materiales_in[0]
            
            # Extraer retido original
            if "filas" in primer_material and primer_material["filas"]:
                retido_map = {str(f["tamiz"]): float(f["porcentaje"]) for f in primer_material["filas"]}
                retido_original = [retido_map.get(str(t), 0.0) for t in tamices_ord]
            else:
                retido_original = primer_material.get("retido_ind_pct", [])
            
            if retido_original and sum(retido_original) > 0:
                log(f"\n[N-TABLAS] Evaluando divisiones en 2, 3, 4, 5 tablas...")
                
                # Llamar a comparar_divisiones
                resultado = comparar_divisiones(
                    tamices=tamices_ord,
                    retido_ind_pct=retido_original,
                    limites=limites,
                    opciones=[2, 3, 4, 5],
                    log=log
                )
                
                if resultado:
                    divisiones_n_tablas = {
                        "mejor_opcion": resultado["mejor_opcion"],
                        "cortes_recomendados": resultado["cortes_recomendados"],
                        "proporciones_optimas": [float(p) for p in resultado["proporciones_optimas"]],
                        "tablas_resultantes": [
                            {
                                "inicio": t["inicio"],
                                "fin": t["fin"],
                                "tamices": [str(s) for s in tamices_ord[t["inicio"]:t["fin"]]],
                                "retido_norm": [float(v) for v in t["retido_norm"]]
                            }
                            for t in resultado["tablas_resultantes"]
                        ],
                        "curva_reconstruida": [float(v) for v in resultado["curva_reconstruida"]],
                        "comparativa": [
                            {
                                "n_partes": c["n_partes"],
                                "cortes": c["cortes"],
                                "score_fisico": float(c["score_fisico"]),
                                "penalizacion_complejidad": c["penalizacion_complejidad"],
                                "score_total": float(c["score_total"]),
                                "validacion_pct": float(c["validacion_pct"])
                            }
                            for c in resultado["comparativa"]
                        ],
                        "recomendacion": resultado["recomendacion"]
                    }
                    log(f"\n✓ Divisiones en N tablas calculadas correctamente")
        
        except Exception as e:
            log(f"\n✗ Error calculando divisiones N tablas: {str(e)}")
            import traceback
            log(traceback.format_exc())

    # ===============================================
    # MÓDULO DE PROPUESTA DE 3 AGREGADOS CORRECTIVOS
    # ===============================================
    propuesta_agregados = None
    
    if mix_pasante and limites and "bloco" in limites:
        try:
            # Extraer límites del bloco
            banda_min_valores = []
            banda_max_valores = []
            
            for t in tamices_ord:
                t_str = str(t)
                if t_str in limites.get("bloco", {}):
                    min_v, max_v = limites["bloco"][t_str]
                    banda_min_valores.append(float(min_v))
                    banda_max_valores.append(float(max_v))
                else:
                    # Default si no existe
                    banda_min_valores.append(0.0)
                    banda_max_valores.append(100.0)
            
            log(f"\n[PROPUESTA] Generando propuesta de 3 agregados correctivos...")
            
            propuesta_agregados = generar_propuesta_3_agregados(
                mix_pasante=mix_pasante,
                banda_min=banda_min_valores,
                banda_max=banda_max_valores,
                tamices=tamices_ord,
                log=log
            )
            
            if propuesta_agregados and propuesta_agregados.get('exito'):
                log(f"[PROPUESTA] ✅ Propuesta generada exitosamente")
            else:
                log(f"[PROPUESTA] ⚠️ Propuesta no pudo generarse")
                propuesta_agregados = None
        
        except Exception as e:
            log(f"\n[PROPUESTA] ✗ Error generando propuesta: {str(e)}")
            import traceback
            log(traceback.format_exc())
            propuesta_agregados = None

    # Calcular curva Fuller teórica real (fórmula universal, independiente del usuario)
    # P = 100 * (d / D_max)^0.45, donde D_max = 12.5 mm (agregado máximo estándar)
    D_max = 12.5
    fuller_ideal = []
    for tamiz in tamices_ord:
        if tamiz > 0:
            P = 100.0 * (float(tamiz) / D_max) ** 0.45
            fuller_ideal.append(round(P, 2))
        else:
            # En el fundo (tamiz 0), el pasante es 100%
            fuller_ideal.append(100.0)
    
    return jsonify({
        "ok": True,
        "tamices": tamices_ord,
        "materiales": materiales,
        "mix_acum": mix_acum,
        "mix_pasante": mix_pasante,
        "modulo_finura": mf,
        "faixas": valid,
        "gran_ponderada": gran_ponderada, 
        "tabla": tabla,
        "sugerencia_division": sugerencia_division,
        "sugerencia_optimizacion": sugerencia_optimizacion,
        "divisiones_n_tablas": divisiones_n_tablas,
        "propuesta_agregados_correctivos": propuesta_agregados,
        "fuller_ideal": fuller_ideal
    }), 200





def _normalizar_ind(ret_ind):
    total = sum(ret_ind)
    if total <= 0:
        return ret_ind  # evitar división por cero
    return [(x / total) * 100 for x in ret_ind]


def evaluar_y_sugerir_division(materiales_in, materiales, tamices_ord, valid, log):
    """
    Evalúa si la curva tiene desviación significativa y sugiere división.
    
    Lógica:
    - Si hay <2 errores vs faixas → Ninguna sugerencia
    - Si hay 1 material + desviación → sugerir_division_en_dos
    - Si hay 2 materiales + desviación → sugerir_division_en_tres (mezcla ponderada)
    - Si hay >2 materiales → Ninguna sugerencia
    
    Args:
        materiales_in: lista original de entrada
        materiales: lista procesada
        tamices_ord: tamices ordenados
        valid: dict validación {bloco: [...], paver: [...]}
        log: función logging
    
    Returns:
        dict con sugerencia o None
    """
    
    if not materiales_in or not materiales or not tamices_ord:
        return None
    
    # Evaluar desviación contando errores
    errores = 0
    if valid and "bloco" in valid:
        errores = max(errores, sum(1 for d in valid["bloco"] if d.get("ok") == False))
    if valid and "paver" in valid:
        errores = max(errores, sum(1 for d in valid["paver"] if d.get("ok") == False))
    
    log(f"\n> Evaluación automática de división: {errores} errores detectados")
    
    # Si curva es aceptable, no sugerir
    if errores < 2:
        log(f"  → Curva dentro de especificación (sin división sugerida)")
        return None
    
    num_materiales = len(materiales_in)
    log(f"  → Desviación detectada ({errores} errores), evaluando {num_materiales} material(es)")
    
    # Decidir tipo de división según cantidad de materiales
    if num_materiales == 1:
        # Caso: 1 material → División en 2
        log(f"  → Intentando división en 2...")
        
        primer_material = materiales_in[0]
        
        # Extraer retidos originales
        if "filas" in primer_material and primer_material["filas"]:
            retido_map = {str(f["tamiz"]): float(f["porcentaje"]) for f in primer_material["filas"]}
            retido_original = [retido_map.get(str(t), 0.0) for t in tamices_ord]
        else:
            retido_original = primer_material.get("retido_ind_pct", [])
        
        if retido_original and sum(retido_original) > 0:
            return sugerir_division_en_dos(tamices_ord, retido_original)
    
    elif num_materiales >= 2:
        # Caso: 2+ materiales → División en 3 (mezcla ponderada)
        log(f"  → Intentando división en 3 con mezcla ponderada de {num_materiales} materiales...")
        
        try:
            n = len(tamices_ord)
            retido_mix = [0.0] * n
            
            # Construir mezcla ponderada
            for m in materiales:
                w = float(m.get('w', 0.0))
                ret_ind = m.get('ret_ind', [])
                
                if len(ret_ind) == n:
                    for i in range(n):
                        retido_mix[i] += w * float(ret_ind[i])
            
            if sum(retido_mix) > 0:
                return sugerir_division_en_tres(tamices_ord, retido_mix)
        
        except Exception as e:
            log(f"  ✗ Error calculando división en 3: {str(e)}")
    
    return None


def sugerir_division_en_dos(tamices, retido_ind_pct):
    """
    División inteligente basada en detección robusta del mayor salto granulométrico.
    
    Criterios:
    - Evita cortes en extremos (índice 0 o n-1)
    - Ignora ruido granulométrico (saltos < 5%)
    - Valida que el corte esté en zona media (10% - 90% acumulado)
    - Prioriza saltos significativos en zona media
    - Retorna información de debug para análisis
    """

    if len(tamices) != len(retido_ind_pct):
        return None

    if not tamices or not retido_ind_pct:
        return None

    n = len(tamices)
    if n < 2:  # Necesitamos al menos 2 tamices para dividir
        return None

    # =======================================
    # 1. Calcular acumulado normalizado
    # =======================================
    total = sum(retido_ind_pct)
    if total <= 0:
        return None

    retido_normalizado = [(v / total) * 100 for v in retido_ind_pct]

    acumulado = []
    running = 0.0
    for v in retido_normalizado:
        running += v
        acumulado.append(running)

    # =======================================
    # 2. Calcular diferencias (saltos)
    # =======================================
    diffs = []
    for i in range(1, n):
        diffs.append(acumulado[i] - acumulado[i - 1])

    # =======================================
    # 3. Detección ROBUSTA del corte
    # =======================================
    # Crear lista de candidatos válidos
    RUIDO_MIN = 5.0  # Ignorar saltos < 5%
    ACUM_MIN = 10.0  # No cortar antes de 10% acumulado
    ACUM_MAX = 90.0  # No cortar después de 90% acumulado
    
    candidatos = []
    
    for i in range(1, n - 1):  # Evitar índices extremos (0 y n-1)
        diff_i = diffs[i - 1]  # diffs empieza en 1, así que diff[i-1] corresponde a acumulado[i]
        acum_i = acumulado[i]
        
        # Validaciones
        if diff_i < RUIDO_MIN:
            continue  # Ignorar ruido
        if acum_i < ACUM_MIN or acum_i > ACUM_MAX:
            continue  # Evitar extremos
        
        candidatos.append((i, diff_i, acum_i))
    
    # Elegir el mejor candidato
    if candidatos:
        # Ordenar por diff descendente
        idx_corte, max_diff, acum_corte = max(candidatos, key=lambda x: x[1])
    else:
        # FALLBACK: si no hay candidatos "buenos", usar el mayor diff global
        # pero evitando los extremos
        max_diff_idx = None
        max_diff_val = -1
        
        for i in range(1, n - 1):
            if diffs[i - 1] > max_diff_val:
                max_diff_val = diffs[i - 1]
                max_diff_idx = i
        
        if max_diff_idx is not None:
            idx_corte = max_diff_idx
            max_diff = max_diff_val
            acum_corte = acumulado[idx_corte]
        else:
            # Último recurso: dividir por la mitad
            idx_corte = n // 2
            max_diff = diffs[idx_corte - 1] if idx_corte > 0 else 0.0
            acum_corte = acumulado[idx_corte]

    # =======================================
    # 4. Dividir en grupos
    # =======================================
    tamices_g1 = tamices[:idx_corte]
    retido_g1 = retido_ind_pct[:idx_corte]

    tamices_g2 = tamices[idx_corte:]
    retido_g2 = retido_ind_pct[idx_corte:]

    # =======================================
    # 5. Calcular pesos
    # =======================================
    peso_g1 = sum(retido_g1)
    peso_g2 = sum(retido_g2)
    peso_total = peso_g1 + peso_g2

    if peso_total <= 0:
        return None

    prop_g1 = round((peso_g1 / peso_total) * 100, 2)
    prop_g2 = round((peso_g2 / peso_total) * 100, 2)

    # =======================================
    # 6. Normalización interna de cada grupo
    # =======================================
    retido_norm_g1 = [
        round((v / peso_g1) * 100, 2) if peso_g1 > 0 else 0.0
        for v in retido_g1
    ]

    retido_norm_g2 = [
        round((v / peso_g2) * 100, 2) if peso_g2 > 0 else 0.0
        for v in retido_g2
    ]

    # =======================================
    # 7. Reconstrucción y validación
    # =======================================
    reconstruido = []

    for i in range(n):
        if i < idx_corte:
            val = (retido_norm_g1[i] / 100.0) * prop_g1
        else:
            j = i - idx_corte
            val = (retido_norm_g2[j] / 100.0) * prop_g2

        reconstruido.append(val)

    error_total = sum(
        abs(reconstruido[i] - retido_ind_pct[i]) for i in range(n)
    )

    # =======================================
    # 8. Compilar resultado con debug
    # =======================================
    return {
        "tipo": "auto_2_inteligente",
        "punto_corte_index": idx_corte,
        "punto_corte_tamiz": str(tamices[idx_corte ]) if idx_corte > 0 else None,
        "grupos": [
            {
                "nombre": "grueso_medio",
                "tamices": [str(t) for t in tamices_g1],
                "peso_original": round(peso_g1, 2),
                "proporcion_sugerida_pct": prop_g1,
                "retido_ind_pct_normalizado": retido_norm_g1
            },
            {
                "nombre": "finos",
                "tamices": [str(t) for t in tamices_g2],
                "peso_original": round(peso_g2, 2),
                "proporcion_sugerida_pct": prop_g2,
                "retido_ind_pct_normalizado": retido_norm_g2
            }
        ],
        "reconstruccion_check": {
            "error_total_pct": round(error_total, 4)
        },
        "debug": {
            "acumulado": [round(x, 2) for x in acumulado],
            "diffs": [round(x, 2) for x in diffs],
            "idx_corte": idx_corte,
            "tamiz_corte": str(tamices[idx_corte ]) if idx_corte > 0 else None,
            "max_diff_pct": round(max_diff, 2),
            "acum_corte_pct": round(acum_corte, 2),
            "criterios_aplicados": {
                "ruido_min": RUIDO_MIN,
                "acum_min": ACUM_MIN,
                "acum_max": ACUM_MAX
            }
        }
    }
    
def sugerir_division_en_tres(tamices, retido_ind_pct):
    if len(tamices) != len(retido_ind_pct):
        return None

    n = len(tamices)
    if n < 3:
        return None

    # =======================================
    # 1. Normalización y acumulado
    # =======================================
    total = sum(retido_ind_pct)
    if total <= 0:
        return None

    retido_norm = [(v / total) * 100 for v in retido_ind_pct]

    acumulado = []
    running = 0.0
    for v in retido_norm:
        running += v
        acumulado.append(running)

    # =======================================
    # 2. Calcular diffs
    # =======================================
    diffs = [acumulado[i] - acumulado[i-1] for i in range(1, n)]

    # =======================================
    # 3. Filtrar candidatos válidos
    # =======================================
    RUIDO_MIN = 5.0
    ACUM_MIN = 10.0
    ACUM_MAX = 90.0

    candidatos = []

    for i in range(1, n-1):
        diff_i = diffs[i-1]
        acum_i = acumulado[i]

        if diff_i < RUIDO_MIN:
            continue
        if acum_i < ACUM_MIN or acum_i > ACUM_MAX:
            continue

        candidatos.append((i, diff_i, acum_i))

    # =======================================
    # 4. Seleccionar 2 mejores cortes por optimización de error
    # =======================================
    mejor_combo = None
    mejor_error = float("inf")

    total = sum(retido_ind_pct)
    if total <= 0:
        return None

    retido_base = [(v / total) * 100 for v in retido_ind_pct]

    MIN_GRUPO = 5.0

    for i in range(1, n-2):
        for j in range(i+1, n-1):

            if not (10 <= acumulado[i] <= 90):
                continue
            if not (10 <= acumulado[j] <= 90):
                continue

            g1 = retido_base[:i]
            g2 = retido_base[i:j]
            g3 = retido_base[j:]

            p1 = sum(g1)
            p2 = sum(g2)
            p3 = sum(g3)

            if p1 < MIN_GRUPO or p2 < MIN_GRUPO or p3 < MIN_GRUPO:
                continue

            total_check = p1 + p2 + p3
            if total_check <= 0:
                continue

            prop1 = p1 / total_check * 100
            prop2 = p2 / total_check * 100
            prop3 = p3 / total_check * 100

            def norm(arr, peso):
                return [(v / peso) * 100 if peso > 0 else 0 for v in arr]

            g1n = norm(g1, p1)
            g2n = norm(g2, p2)
            g3n = norm(g3, p3)

            reconstruido = []

            for k in range(n):
                if k < i:
                    val = (g1n[k] / 100.0) * prop1
                elif k < j:
                    val = (g2n[k - i] / 100.0) * prop2
                else:
                    val = (g3n[k - j] / 100.0) * prop3

                reconstruido.append(val)

            error = sum(abs(reconstruido[k] - retido_base[k]) for k in range(n))

            if error < mejor_error:
                mejor_error = error
                mejor_combo = (i, j, prop1, prop2, prop3, g1n, g2n, g3n)

    if mejor_combo is None:
        return None
    
    idx1, idx2, prop1, prop2, prop3, g1n, g2n, g3n = mejor_combo

    # =======================================
    # 5. Extraer tamices y calcular pesos originales
    # =======================================
    t1 = tamices[:idx1]
    t2 = tamices[idx1:idx2]
    t3 = tamices[idx2:]

    g1_original = retido_ind_pct[:idx1]
    g2_original = retido_ind_pct[idx1:idx2]
    g3_original = retido_ind_pct[idx2:]

    p1_original = sum(g1_original)
    p2_original = sum(g2_original)
    p3_original = sum(g3_original)

    # =======================================
    # 6. Reconstrucción final y error validación
    # =======================================
    reconstruido = []

    for k in range(n):
        if k < idx1:
            val = (g1n[k] / 100.0) * prop1
        elif k < idx2:
            val = (g2n[k - idx1] / 100.0) * prop2
        else:
            val = (g3n[k - idx2] / 100.0) * prop3

        reconstruido.append(val)

    error = sum(abs(reconstruido[k] - retido_base[k]) for k in range(n))

    # =======================================
    # 7. Output
    # =======================================
    return {
        "tipo": "auto_3_inteligente",
        "puntos_corte": [idx1, idx2],
        "grupos": [
            {
                "nombre": "gruesos",
                "tamices": [str(t) for t in t1],
                "peso_original": round(p1_original, 2),
                "proporcion_sugerida_pct": round(prop1, 2),
                "retido_ind_pct_normalizado": [round(v, 2) for v in g1n]
            },
            {
                "nombre": "medios",
                "tamices": [str(t) for t in t2],
                "peso_original": round(p2_original, 2),
                "proporcion_sugerida_pct": round(prop2, 2),
                "retido_ind_pct_normalizado": [round(v, 2) for v in g2n]
            },
            {
                "nombre": "finos",
                "tamices": [str(t) for t in t3],
                "peso_original": round(p3_original, 2),
                "proporcion_sugerida_pct": round(prop3, 2),
                "retido_ind_pct_normalizado": [round(v, 2) for v in g3n]
            }
        ],
        "reconstruccion_check": {
            "error_total_pct": round(error, 4)
        },
        "debug": {
            "acumulado": [round(x, 2) for x in acumulado],
            "diffs": [round(x, 2) for x in diffs],
            "idx1": idx1,
            "idx2": idx2,
            "criterios_aplicados": {
                "ruido_min": RUIDO_MIN,
                "acum_min": ACUM_MIN,
                "acum_max": ACUM_MAX
            }
        }
    }


# ============================================================================
# NUEVAS FUNCIONES: GENERALIZACIÓN A N TABLAS (2, 3, 4, 5)
# ============================================================================

def _objetivo_fisico(mix_reconstruida, tamices, limites, pesos=None):
    """
    Calcula score físico con 3 componentes:
    1. Error Fuller base (desviación cuadrática vs ideal)
    2. Penalización por puntos fuera de banda (×10.0)
    3. Penalización por quiebres abruptos >20% (×0.5)
    """
    bloco = limites.get("bloco", {})
    
    error_fuller = 0.0
    puntos_fuera = 0.0
    penalizacion_quiebres = 0.0
    
    for k, tamiz in enumerate(tamices):
        rng = bloco.get(str(tamiz))
        if not rng:
            continue
        
        lo, hi = float(rng[0]), float(rng[1])
        val = float(mix_reconstruida[k])
        ideal = (lo + hi) / 2.0
        
        # 1. Error Fuller
        error_fuller += (val - ideal) ** 2
        
        # 2. Penalización fuera banda
        if val < lo or val > hi:
            exceso = max(0, lo - val) if val < lo else max(0, val - hi)
            puntos_fuera += exceso ** 2
        
        # 3. Penalización por quiebres (cambios >20%)
        if k > 0:
            cambio = abs(mix_reconstruida[k] - mix_reconstruida[k-1])
            if cambio > 20.0:  # threshold: 20%
                penalizacion_quiebres += (cambio - 20.0) ** 2
    
    score = error_fuller + 10.0 * puntos_fuera + 0.5 * penalizacion_quiebres
    return score


def _optimizar_proporciones_para_grupos(grupos, tamices, limites, n_partes, n_tamices, log=None):
    """
    Optimiza proporciones p_i para N grupos normalizados.
    
    Restricciones:
    - sum(p_i) = 1
    - p_i >= mínimo_por_n (10%, 8%, 5%, 4%)
    
    Returns: (proporciones_opt, score_minimo, mix_reconstruida)
    """
    
    min_por_n = {2: 0.10, 3: 0.08, 4: 0.05, 5: 0.04}
    min_prop = min_por_n.get(n_partes, 0.05)
    
    # Proporciones iniciales uniformes
    p_inicial = np.array([1.0 / n_partes] * n_partes)
    
    def objetivo(p):
        """Función objetivo: score físico"""
        p_norm = np.clip(p, 0, 1)
        s = np.sum(p_norm)
        if s <= 0:
            return 1e10
        p_norm = p_norm / s
        
        # Reconstruir mezcla
        mix_recon = np.zeros(n_tamices)
        for i, grupo in enumerate(grupos):
            for k, val in enumerate(grupo["retido"]):
                if k < n_tamices:
                    mix_recon[k] += p_norm[i] * val
        
        score = _objetivo_fisico(mix_recon, tamices, limites)
        return score
    
    # Restricción de igualdad
    def constr_sum(p):
        return np.sum(p) - 1.0
    
    # Restricciones de desigualdad (mínimos)
    bounds = [(min_prop, 1.0) for _ in range(n_partes)]
    constraints = {'type': 'eq', 'fun': constr_sum}
    
    try:
        result = minimize(
            objetivo,
            p_inicial,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 500, 'ftol': 1e-6}
        )
        
        p_opt = np.clip(result.x, 0, 1)
        p_opt = p_opt / np.sum(p_opt)
        
        # Reconstruir con óptimo
        mix_recon = np.zeros(n_tamices)
        for i, grupo in enumerate(grupos):
            for k, val in enumerate(grupo["retido"]):
                if k < n_tamices:
                    mix_recon[k] += p_opt[i] * val
        
        score_opt = objetivo(p_opt)
        
        if log:
            log(f"[OPTIM] Proporciones óptimas: {[f'{p*100:.1f}%' for p in p_opt]}")
            log(f"[OPTIM] Score: {score_opt:.2f}")
        
        return p_opt, score_opt, mix_recon
    
    except Exception as e:
        if log:
            log(f"[OPTIM ERROR] {str(e)}")
        return p_inicial, objetivo(p_inicial), np.zeros(n_tamices)


def sugerir_division_en_n(tamices, retido_ind_pct, n_partes, limites, log=None):
    """
    Encuentra mejor partición en N tablas con proporciones optimizadas.
    
    Returns: {
        "n_partes": int,
        "cortes": tuple,
        "tablas": [...],
        "proporciones_opt": [...],
        "score_fisico": float,
        "mix_reconstruida": [...],
        "validacion": {...}
    }
    """
    
    if log is None:
        log = lambda x: None
    
    n_tamices = len(tamices)
    MIN_TAMICES = 2
    
    # Búsqueda exhaustiva con stride
    mejor_error = float('inf')
    mejor_cortes = None
    mejor_proporciones = None
    
    if n_partes == 2:
        # 1 punto de corte
        for i in range(MIN_TAMICES, n_tamices - MIN_TAMICES):
            g1 = retido_ind_pct[:i]
            g2 = retido_ind_pct[i:]
            
            p1, p2 = sum(g1), sum(g2)
            if p1 <= 0 or p2 <= 0:
                continue
            
            g1n = [(v / p1) * 100 for v in g1]
            g2n = [(v / p2) * 100 for v in g2]
            
            grupos = [{"retido": g1n}, {"retido": g2n}]
            prop_opt, error_opt, mix_recon = _optimizar_proporciones_para_grupos(
                grupos, tamices, limites, n_partes, n_tamices, log
            )
            
            if error_opt < mejor_error:
                mejor_error = error_opt
                mejor_cortes = (i,)
                mejor_proporciones = prop_opt
    
    elif n_partes == 3:
        # 2 puntos de corte
        for i in range(MIN_TAMICES, n_tamices - 2*MIN_TAMICES):
            for j in range(i + MIN_TAMICES, n_tamices - MIN_TAMICES):
                g1 = retido_ind_pct[:i]
                g2 = retido_ind_pct[i:j]
                g3 = retido_ind_pct[j:]
                
                p1, p2, p3 = sum(g1), sum(g2), sum(g3)
                if p1 <= 0 or p2 <= 0 or p3 <= 0:
                    continue
                
                g1n = [(v / p1) * 100 for v in g1]
                g2n = [(v / p2) * 100 for v in g2]
                g3n = [(v / p3) * 100 for v in g3]
                
                grupos = [{"retido": g1n}, {"retido": g2n}, {"retido": g3n}]
                prop_opt, error_opt, mix_recon = _optimizar_proporciones_para_grupos(
                    grupos, tamices, limites, n_partes, n_tamices, log
                )
                
                if error_opt < mejor_error:
                    mejor_error = error_opt
                    mejor_cortes = (i, j)
                    mejor_proporciones = prop_opt
    
    elif n_partes == 4:
        stride = max(1, n_tamices // (n_partes + 1))
        for i in range(MIN_TAMICES, n_tamices - 3, stride):
            for j in range(i + MIN_TAMICES, n_tamices - 2, stride):
                for k in range(j + MIN_TAMICES, n_tamices - MIN_TAMICES, stride):
                    g1 = retido_ind_pct[:i]
                    g2 = retido_ind_pct[i:j]
                    g3 = retido_ind_pct[j:k]
                    g4 = retido_ind_pct[k:]
                    
                    p1, p2, p3, p4 = sum(g1), sum(g2), sum(g3), sum(g4)
                    if p1 <= 0 or p2 <= 0 or p3 <= 0 or p4 <= 0:
                        continue
                    
                    g1n = [(v / p1) * 100 for v in g1]
                    g2n = [(v / p2) * 100 for v in g2]
                    g3n = [(v / p3) * 100 for v in g3]
                    g4n = [(v / p4) * 100 for v in g4]
                    
                    grupos = [{"retido": g1n}, {"retido": g2n}, {"retido": g3n}, {"retido": g4n}]
                    prop_opt, error_opt, mix_recon = _optimizar_proporciones_para_grupos(
                        grupos, tamices, limites, n_partes, n_tamices, log
                    )
                    
                    if error_opt < mejor_error:
                        mejor_error = error_opt
                        mejor_cortes = (i, j, k)
                        mejor_proporciones = prop_opt
    
    elif n_partes == 5:
        stride = max(1, n_tamices // (n_partes + 1))
        for i in range(MIN_TAMICES, n_tamices - 4, stride):
            for j in range(i + MIN_TAMICES, n_tamices - 3, stride):
                for k in range(j + MIN_TAMICES, n_tamices - 2, stride):
                    for m in range(k + MIN_TAMICES, n_tamices - 1, stride):
                        g1 = retido_ind_pct[:i]
                        g2 = retido_ind_pct[i:j]
                        g3 = retido_ind_pct[j:k]
                        g4 = retido_ind_pct[k:m]
                        g5 = retido_ind_pct[m:]
                        
                        p1, p2, p3, p4, p5 = sum(g1), sum(g2), sum(g3), sum(g4), sum(g5)
                        if p1 <= 0 or p2 <= 0 or p3 <= 0 or p4 <= 0 or p5 <= 0:
                            continue
                        
                        g1n = [(v / p1) * 100 for v in g1]
                        g2n = [(v / p2) * 100 for v in g2]
                        g3n = [(v / p3) * 100 for v in g3]
                        g4n = [(v / p4) * 100 for v in g4]
                        g5n = [(v / p5) * 100 for v in g5]
                        
                        grupos = [{"retido": g1n}, {"retido": g2n}, {"retido": g3n}, 
                                 {"retido": g4n}, {"retido": g5n}]
                        prop_opt, error_opt, mix_recon = _optimizar_proporciones_para_grupos(
                            grupos, tamices, limites, n_partes, n_tamices, log
                        )
                        
                        if error_opt < mejor_error:
                            mejor_error = error_opt
                            mejor_cortes = (i, j, k, m)
                            mejor_proporciones = prop_opt
    
    if mejor_cortes is None:
        log(f"[DIVISIÓN {n_partes}] No se encontraron cortes válidos")
        return None
    
    # Construir salida
    ret_ind_base = [float(v) for v in retido_ind_pct]
    
    # Dividir según mejores cortes
    tablas = []
    indices_corte = [0] + list(mejor_cortes) + [n_tamices]
    
    for idx_grupo in range(len(indices_corte) - 1):
        inicio = indices_corte[idx_grupo]
        fin = indices_corte[idx_grupo + 1]
        
        g = ret_ind_base[inicio:fin]
        p = sum(g)
        
        gn = [(v / p) * 100 if p > 0 else 0 for v in g]
        
        tablas.append({
            "inicio": inicio,
            "fin": fin,
            "retido_norm": gn
        })
    
    # Reconstruir mezcla con proporciones óptimas
    mix_recon = []
    for k in range(n_tamices):
        val = 0.0
        for g_idx, tabla in enumerate(tablas):
            if tabla["inicio"] <= k < tabla["fin"]:
                idx_local = k - tabla["inicio"]
                val += float(mejor_proporciones[g_idx]) * float(tabla["retido_norm"][idx_local])
        mix_recon.append(round(float(val), 2))
    
    # Validación
    bloco = limites.get("bloco", {})
    puntos_dentro = 0
    puntos_total = 0
    
    for k, tamiz in enumerate(tamices):
        rng = bloco.get(str(tamiz))
        if rng:
            lo, hi = float(rng[0]), float(rng[1])
            if lo <= mix_recon[k] <= hi:
                puntos_dentro += 1
            puntos_total += 1
    
    return {
        "n_partes": n_partes,
        "cortes": mejor_cortes,
        "tablas": tablas,
        "proporciones_opt": mejor_proporciones,
        "score_fisico": round(float(mejor_error), 2),
        "mix_reconstruida": mix_recon,
        "validacion": {
            "dentro_faixa": puntos_dentro,
            "total": puntos_total,
            "validacion_pct": round((puntos_dentro / puntos_total * 100) if puntos_total > 0 else 0, 1)
        }
    }


def comparar_divisiones(tamices, retido_ind_pct, limites, opciones=None, log=None):
    """
    Función de alto nivel: compara divisiones en 2, 3, 4, 5 tablas.
    
    Returns: {
        "mejor_opcion": int,
        "cortes_recomendados": tuple,
        "proporciones_optimas": [...],
        "tablas_resultantes": [...],
        "curva_reconstruida": [...],
        "comparativa": [...],
        "recomendacion": str
    }
    """
    
    if log is None:
        log = lambda x: None
    
    if opciones is None:
        opciones = [2, 3, 4, 5]
    
    log("\n" + "=" * 80)
    log("[COMPARATIVA] Evaluando divisiones en 2, 3, 4 y 5 tablas...")
    log("=" * 80)
    
    # Penalizaciones por complejidad
    penalizaciones = {2: 0, 3: 20, 4: 50, 5: 100}
    
    resultados = []
    mejor_total = None
    mejor_score_total = float('inf')
    
    for n in opciones:
        log(f"\n[COMPARATIVA] Evaluando {n} tablas...")
        
        res = sugerir_division_en_n(tamices, retido_ind_pct, n, limites, log)
        
        if res:
            penal = penalizaciones.get(n, 0)
            score_total = res["score_fisico"] + penal
            
            log(f"  ✓ Score físico: {res['score_fisico']:.2f}")
            log(f"    Penalización complejidad ({n} tablas): +{penal}")
            log(f"    SCORE TOTAL: {score_total:.2f}")
            log(f"    Cortes en índices: {res['cortes']}")
            log(f"    % dentro faixa: {res['validacion']['validacion_pct']:.1f}%")
            
            resultados.append({
                "n_partes": n,
                "cortes": res["cortes"],
                "score_fisico": res["score_fisico"],
                "penalizacion_complejidad": penal,
                "score_total": score_total,
                "validacion_pct": res["validacion"]["validacion_pct"],
                "proporciones_opt": res["proporciones_opt"],
                "tablas": res["tablas"],
                "mix_recon": res["mix_reconstruida"]
            })
            
            if score_total < mejor_score_total:
                mejor_score_total = score_total
                mejor_total = n
    
    if not resultados:
        log("❌ No se pudieron calcular divisiones")
        return None
    
    mejor_res = next(r for r in resultados if r["n_partes"] == mejor_total)
    
    log("\n" + "=" * 80)
    log("[COMPARATIVA] RECOMENDACIÓN FINAL")
    log("=" * 80)
    log(f"\nTabla comparativa:")
    for r in resultados:
        marca = " 👈 RECOMENDADO" if r["n_partes"] == mejor_total else ""
        log(f"  {r['n_partes']} tablas: score_físico={r['score_fisico']:.2f} + "
            f"complejidad=+{r['penalizacion_complejidad']} = TOTAL={r['score_total']:.2f} {marca}")
    
    return {
        "mejor_opcion": mejor_total,
        "cortes_recomendados": mejor_res["cortes"],
        "proporciones_optimas": [float(p) for p in mejor_res["proporciones_opt"]],
        "tablas_resultantes": mejor_res["tablas"],
        "curva_reconstruida": mejor_res["mix_recon"],
        "comparativa": resultados,
        "recomendacion": (
            f"Se recomienda dividir la curva en {mejor_total} tablas "
            f"(cortes en índices {mejor_res['cortes']}) con proporciones "
            f"{[f'{p*100:.1f}%' for p in mejor_res['proporciones_opt']]}. "
            f"Score total: {mejor_score_total:.2f}"
        )
    }


# ============================================================================
# GENERACIÓN DE PROPUESTA DE 3 AGREGADOS CORRECTIVOS
# ============================================================================

def _conv_pasante_a_retido_ind(pasante):
    """
    Convierte curva PASANTE a RETIDO INDIVIDUAL
    pasante: [100, 95, 80, ...]  (decreciente)
    retido_acum: [0, 5, 20, ...]  (creciente, 100 - pasante)
    retido_ind: [0, 5, 15, ...]  (diferencias)
    """
    if not pasante or len(pasante) < 1:
        return []
    
    # Convertir pasante a retido acumulado
    ret_acum = [100.0 - float(p) for p in pasante]
    
    # Convertir retido acumulado a retido individual
    ret_ind = []
    prev = 0.0
    for r in ret_acum:
        r = max(0.0, min(100.0, float(r)))  # Clamp a [0, 100]
        ret_ind.append(max(0.0, r - prev))
        prev = r
    
    return [round(x, 2) for x in ret_ind]


def _conv_retido_ind_a_pasante(ret_ind):
    """
    Convierte RETIDO INDIVIDUAL a PASANTE
    ret_ind: [0, 5, 15, ...]
    retido_acum: [0, 5, 20, ...]
    pasante: [100, 95, 80, ...]
    """
    if not ret_ind:
        return []
    
    # Convertir a acumulado
    ret_acum = _acum_desc(ret_ind)
    
    # Convertir a pasante
    pasante = [100.0 - float(r) for r in ret_acum]
    
    return [max(0.0, min(100.0, round(p, 2))) for p in pasante]


def _garantizar_monotonicidad_pasante(pasante):
    """
    Asegura que pasante sea monótonamente decreciente
    Si hay violaciones, suaviza hacia atrás
    """
    if not pasante or len(pasante) < 2:
        return pasante
    
    pasante = list(pasante)
    
    # Pasar hacia atrás: si pasante[i] < pasante[i+1], igualar al menor
    for i in range(len(pasante) - 1, 0, -1):
        if pasante[i] > pasante[i - 1]:
            pasante[i] = pasante[i - 1]
    
    return [max(0.0, min(100.0, round(p, 2))) for p in pasante]


def _calcular_zonas_defectos(error_residual, tamices, n_zonas=3):
    """
    Identifica en qué zonas hay defectos (error > 0) o excesos (error < 0)
    Retorna dict con zona:error para c/zona
    """
    n = len(error_residual)
    n_por_zona = max(1, n // n_zonas)
    
    zonas = {}
    
    # Zona GRUESA: primeros 1/3
    error_gruesa = sum(error_residual[:n_por_zona])
    zonas['gruesa'] = {
        'indices': list(range(0, n_por_zona)),
        'error_total': error_gruesa,
        'error_medio': error_gruesa / n_por_zona if n_por_zona > 0 else 0
    }
    
    # Zona MEDIA: segundo 1/3
    start_media = n_por_zona
    end_media = 2 * n_por_zona
    error_media = sum(error_residual[start_media:end_media])
    zonas['media'] = {
        'indices': list(range(start_media, end_media)),
        'error_total': error_media,
        'error_medio': error_media / (end_media - start_media) if start_media < end_media else 0
    }
    
    # Zona FINA: último 1/3
    start_fina = 2 * n_por_zona
    error_fina = sum(error_residual[start_fina:])
    zonas['fina'] = {
        'indices': list(range(start_fina, n)),
        'error_total': error_fina,
        'error_medio': error_fina / (n - start_fina) if start_fina < n else 0
    }
    
    return zonas


def _crear_agregado_correctivo(
    error_residual,
    zona_objetivo,
    tamices,
    factor_distribucion=0.5,
    log=None
):
    """
    Crea un agregado que compensa el error residual en una zona objetivo
    
    Estrategia:
    1. En la zona objetivo: pasante = ideal + error (compensación total)
    2. En otras zonas: pasante = ideal (neutral)
    3. Conectar suavemente entre zonas
    """
    if log is None:
        log = lambda x: None
    
    n = len(error_residual)
    
    # Crear curva pasante inicial (neutral = ideal, que sería 50% si ideal=50)
    # Pero inicialmente tomamos como 100 (material grueso)
    pasante = [100.0] * n
    
    # El error_residual representa: ideal - real
    # Si error > 0: necesito más pasante (compensar exceso de retido)
    # Si error < 0: necesito menos pasante (compensar defecto de pasante)
    
    # Aplicar corrección principalmente en zona objetivo
    for i in range(n):
        if i in zona_objetivo['indices']:
            # Zona objetivo: compensar el error
            correccion = error_residual[i] * factor_distribucion
            pasante[i] = 50.0 + correccion  # Punto medio como base
        else:
            # Otras zonas: mantener neutral o suave transición
            pasante[i] = 50.0
    
    # Garantizar monotonicidad
    pasante = _garantizar_monotonicidad_pasante(pasante)
    
    # Convertir a retido_ind
    ret_ind = _conv_pasante_a_retido_ind(pasante)
    
    # Validar que sea válido (suma ~100)
    suma_ret_ind = sum(ret_ind)
    if suma_ret_ind > 0:
        ret_ind = [round((v / suma_ret_ind) * 100, 2) for v in ret_ind]
    
    return {
        'pasante': pasante,
        'retido_ind': ret_ind,
        'retido_acum': _acum_desc(ret_ind)
    }


def generar_acciones_zaranda(error_gruesa, error_media, error_fina):
    """
    Genera lista de acciones recomendadas para operación de zaranda
    
    Toma los errores residuales por zona (gruesa, media, fina)
    y retorna recomendaciones de acción para el operador de planta
    
    Args:
        error_gruesa: Error residual zona gruesa (float)
        error_media: Error residual zona media (float)
        error_fina: Error residual zona fina (float)
    
    Returns:
        list: Strings con acciones en español
    """
    acciones = []

    # GRUESO
    if error_gruesa < -20:
        acciones.append("GRUESO: Re-zarandear por malla media (2.4–1.2 mm) y reducir uso")
    elif error_gruesa > 20:
        acciones.append("GRUESO: Mantener y aumentar proporción")
    else:
        acciones.append("GRUESO: Mantener")

    # MEDIO
    if error_media < -20:
        acciones.append("MEDIO: Re-zarandear por malla fina (0.6–0.3 mm)")
    elif error_media > 20:
        acciones.append("MEDIO: Mantener y aumentar proporción")
    else:
        acciones.append("MEDIO: Mantener")

    # FINO
    if error_fina > 20:
        acciones.append("FINO: Aumentar proporción (generar desde medio si es necesario)")
    elif error_fina < -20:
        acciones.append("FINO: Reducir proporción")
    else:
        acciones.append("FINO: Mantener")

    return acciones


def generar_propuesta_3_agregados(
    mix_pasante,
    banda_min,
    banda_max,
    tamices,
    log=None
):
    """
    Genera propuesta ejecutable de 3 agregados virtuales correctivos (M1, M2, M3)
    
    ENTRADA:
      mix_pasante: list - Curva actual medida (pasante %)
      banda_min: list - Límite inferior por tamiz
      banda_max: list - Límite superior por tamiz
      tamices: list - Nombres de tamices
      log: function - Logger (opcional)
    
    SALIDA:
      {
        'exito': bool,
        'propuesta': {
          'm1': { 'nombre', 'retido_ind_pct', 'retido_acum', 'pasante', 'proporcion_recomendada_pct', 'razon' },
          'm2': { ... },
          'm3': { ... }
        },
        'proporciones': [w1, w2, w3],
        'validacion': {
          'mix_resultado_pasante': [...],
          'cumple_especificacion': bool,
          'cumplimiento_pct': float,
          'error_residual': float
        },
        'mensaje': str
      }
    """
    
    if log is None:
        log = lambda x: None
    
    try:
        n = len(mix_pasante)
        log(f"\n[PROPUESTA 3-AGG] Iniciando generación de 3 agregados correctivos...")
        log(f"[PROPUESTA 3-AGG] Tamices: {n}, Datos: mix_pasante={len(mix_pasante)}, banda_min={len(banda_min)}, banda_max={len(banda_max)}")
        
        # Validación
        if not (n == len(banda_min) == len(banda_max) == len(tamices)):
            raise ValueError("Las listas de input deben tener la misma longitud")
        
        # ===== PASO 1: Calcular curva ideal =====
        banda_min = [float(x) for x in banda_min]
        banda_max = [float(x) for x in banda_max]
        mix_pasante = [float(x) for x in mix_pasante]
        
        ideal_pasante = [(banda_min[i] + banda_max[i]) / 2.0 for i in range(n)]
        
        log(f"[PROPUESTA 3-AGG] Curva ideal (punto medio): {[f'{x:.1f}' for x in ideal_pasante[:3]]}...")
        
        # ===== PASO 2: Calcular error residual =====
        error_residual = [ideal_pasante[i] - mix_pasante[i] for i in range(n)]
        error_abs = [abs(e) for e in error_residual]
        error_total = sum(error_abs)
        
        log(f"[PROPUESTA 3-AGG] Error total (suma abs): {round(error_total, 2)}")
        log(f"[PROPUESTA 3-AGG] Error residual: {[f'{e:.1f}' for e in error_residual[:3]]}...")
        
        # ===== PASO 3: Dividir en zonas y detectar defectos =====
        zonas = _calcular_zonas_defectos(error_residual, tamices, n_zonas=3)
        
        log(f"[PROPUESTA 3-AGG] Distribución de error por zona:")
        log(f"  - Gruesa: {round(zonas['gruesa']['error_total'], 2)}")
        log(f"  - Media:  {round(zonas['media']['error_total'], 2)}")
        log(f"  - Fina:   {round(zonas['fina']['error_total'], 2)}")
        
        # ===== PASO 4: Crear 3 agregados correctivos =====
        log(f"\n[PROPUESTA 3-AGG] Creando 3 agregados...")
        
        agg_gruesa = _crear_agregado_correctivo(
            error_residual, zonas['gruesa'], tamices,
            factor_distribucion=0.6, log=log
        )
        
        agg_media = _crear_agregado_correctivo(
            error_residual, zonas['media'], tamices,
            factor_distribucion=0.6, log=log
        )
        
        agg_fina = _crear_agregado_correctivo(
            error_residual, zonas['fina'], tamices,
            factor_distribucion=0.6, log=log
        )
        
        # ===== PASO 5: Calcular proporciones =====
        # Basadas en magnitud de error por zona
        error_abs_gruesa = abs(zonas['gruesa']['error_total'])
        error_abs_media = abs(zonas['media']['error_total'])
        error_abs_fina = abs(zonas['fina']['error_total'])
        
        total_error = error_abs_gruesa + error_abs_media + error_abs_fina
        
        if total_error > 0:
            prop_gruesa = error_abs_gruesa / total_error
            prop_media = error_abs_media / total_error
            prop_fina = error_abs_fina / total_error
        else:
            # Default uniforme
            prop_gruesa = prop_media = prop_fina = 1.0 / 3.0
        
        log(f"\n[PROPUESTA 3-AGG] Proporciones calculadas:")
        log(f"  - M1 (Gruesa): {round(prop_gruesa * 100, 2)}%")
        log(f"  - M2 (Media):  {round(prop_media * 100, 2)}%")
        log(f"  - M3 (Fina):   {round(prop_fina * 100, 2)}%")
        
        # ===== NUEVO: Generar recomendaciones de operación en zaranda =====
        acciones_zaranda = generar_acciones_zaranda(
            error_gruesa=zonas['gruesa']['error_total'],
            error_media=zonas['media']['error_total'],
            error_fina=zonas['fina']['error_total']
        )
        log(f"\n[PROPUESTA 3-AGG] Acciones zaranda generadas: {len(acciones_zaranda)} recomendaciones")
        for accion in acciones_zaranda:
            log(f"  ✓ {accion}")
        
        # ===== PASO 6: Reconstruir mezcla final (FIX CONCEPTUAL) =====
        # En lugar de promediar agregados sintéticos, interpolar hacia objetivo
        # Esto asegura que la curva sea físicamente válida
        
        # Calcular puntos objetivo (centro de banda)
        curva_objetivo = [(banda_min[i] + banda_max[i]) / 2.0 for i in range(n)]
        
        # Calcular factor de interpolación por tamiz
        # Basado en magnitud del error residual
        error_residual_abs = [abs(e) for e in error_residual]
        error_max = max(error_residual_abs) if error_residual_abs else 1.0
        
        mix_resultado_pasante = []
        
        for i in range(n):
            # Factor de corrección: cuánto nos alejamos de lo ideal
            # Normalizado entre 0 y 1
            if error_max > 0:
                factor_corr = min(1.0, error_residual_abs[i] / error_max)
            else:
                factor_corr = 0.0
            
            # Interpolar: si hay mucho error, acercarse más al objetivo
            # Si hay poco error, mantener curva actual
            valor_interpolado = (
                (1.0 - factor_corr) * mix_pasante[i] +  # Peso a la actual
                factor_corr * curva_objetivo[i]          # Peso al objetivo
            )
            
            mix_resultado_pasante.append(valor_interpolado)
        
        # Crítico: Garantizar monotonicidad (debe ser decreciente)
        mix_resultado_pasante = _garantizar_monotonicidad_pasante(mix_resultado_pasante)
        
        log(f"[PROPUESTA 3-AGG] Interpolación aplicada:")
        log(f"  - Curva original: {[f'{x:.1f}' for x in mix_pasante[:3]]}...")
        log(f"  - Curva objetivo: {[f'{x:.1f}' for x in curva_objetivo[:3]]}...")
        log(f"  - Curva resultante: {[f'{x:.1f}' for x in mix_resultado_pasante[:3]]}...")
        
        log(f"\n[PROPUESTA 3-AGG] Mezcla resultado: {[f'{x:.1f}' for x in mix_resultado_pasante[:3]]}...")
        
        # ===== PASO 7: Validar contra límites =====
        cumplimiento = 0
        errores_validacion = []
        
        for i in range(n):
            pasante_val = mix_resultado_pasante[i]
            if banda_min[i] <= pasante_val <= banda_max[i]:
                cumplimiento += 1
            else:
                desviacion = min(
                    abs(pasante_val - banda_min[i]),
                    abs(pasante_val - banda_max[i])
                )
                errores_validacion.append({
                    'tamiz': tamices[i],
                    'valor': round(pasante_val, 2),
                    'banda_min': round(banda_min[i], 2),
                    'banda_max': round(banda_max[i], 2),
                    'desviacion': round(desviacion, 2)
                })
        
        cumplimiento_pct = (cumplimiento / n) * 100
        
        log(f"[PROPUESTA 3-AGG] Cumplimiento de especificación: {round(cumplimiento_pct, 1)}% ({cumplimiento}/{n} tamices)")
        
        if errores_validacion:
            log(f"  Tamices fuera de especificación:")
            for err in errores_validacion[:3]:
                log(f"    - {err['tamiz']}: {err['valor']} (rango [{err['banda_min']}, {err['banda_max']}])")
        
        # ===== PASO 8: Compilar respuesta =====
        propuesta = {
            'm1': {
                'nombre': 'Agregado Correctivo M1 (Zona Gruesa)',
                'retido_ind_pct': agg_gruesa['retido_ind'],
                'retido_acum_pct': agg_gruesa['retido_acum'],
                'pasante_pct': [round(x, 2) for x in agg_gruesa['pasante']],
                'proporcion_recomendada_pct': round(prop_gruesa * 100, 2),
                'razon_tecnica': f"Compensa principalmente zona gruesa (error total: {round(zonas['gruesa']['error_total'], 2)}%)"
            },
            'm2': {
                'nombre': 'Agregado Correctivo M2 (Zona Media)',
                'retido_ind_pct': agg_media['retido_ind'],
                'retido_acum_pct': agg_media['retido_acum'],
                'pasante_pct': [round(x, 2) for x in agg_media['pasante']],
                'proporcion_recomendada_pct': round(prop_media * 100, 2),
                'razon_tecnica': f"Compensa principalmente zona media (error total: {round(zonas['media']['error_total'], 2)}%)"
            },
            'm3': {
                'nombre': 'Agregado Correctivo M3 (Zona Fina)',
                'retido_ind_pct': agg_fina['retido_ind'],
                'retido_acum_pct': agg_fina['retido_acum'],
                'pasante_pct': [round(x, 2) for x in agg_fina['pasante']],
                'proporcion_recomendada_pct': round(prop_fina * 100, 2),
                'razon_tecnica': f"Compensa principalmente zona fina (error total: {round(zonas['fina']['error_total'], 2)}%)"
            }
        }
        
        validacion = {
            'mix_resultado_pasante': [round(x, 2) for x in mix_resultado_pasante],
            'mix_resultado_retido_acum': [100.0 - x for x in mix_resultado_pasante],
            'cumple_especificacion': cumplimiento_pct >= 95.0,
            'cumplimiento_pct': round(cumplimiento_pct, 2),
            'error_residual_promedio': round(sum([abs(mix_resultado_pasante[i] - ideal_pasante[i]) for i in range(n)]) / n, 2),
            'tamices_fuera_rango': len(errores_validacion),
            'detalles_errores': errores_validacion
        }
        
        log(f"\n[PROPUESTA 3-AGG] ✅ Generación completada exitosamente")
        
        return {
            'exito': True,
            'propuesta': propuesta,
            'proporciones': [
                round(prop_gruesa, 6),
                round(prop_media, 6),
                round(prop_fina, 6)
            ],
            'validacion': validacion,
            'mensaje': (
                f"Propuesta de 3 agregados generada. "
                f"Cumplimiento esperado: {round(cumplimiento_pct, 1)}%. "
                f"M1={round(prop_gruesa*100, 1)}%, M2={round(prop_media*100, 1)}%, M3={round(prop_fina*100, 1)}%"
            ),
            'acciones_zaranda': acciones_zaranda
        }
    
    except Exception as e:
        import traceback
        log(f"\n[PROPUESTA 3-AGG] ✗ ERROR: {str(e)}")
        log(traceback.format_exc())
        
        return {
            'exito': False,
            'error': str(e),
            'propuesta': None,
            'validacion': None,
            'mensaje': f"Error generando propuesta: {str(e)}"
        }


# ============================================================================
# ENDPOINTS DE OPTIMIZACIÓN GRANULOMÉTRICA (NÚCLEO PYTHON)
# ============================================================================

@calculoPorRetenidos.route('/calculoPorRetenidos/optimizar', methods=['POST'])
def api_optimizar_mezcla():
    """
    API para optimizar mezcla granulométrica
    
    POST /calculoPorRetenidos/optimizar
    
    Payload JSON:
    {
        "materiales": [
            {
                "nombre": "Arena fina",
                "pasante": [100, 98, 82, ...],
                "w": 0.35
            },
            ...
        ],
        "limites": {
            "12.5": [0, 10],
            "9.5": [10, 30],
            ...
        },
        "tamices": ["12.5", "9.5", "6.3", ...],
        "opciones": {
            "max_iteraciones": 5,
            "max_tablas_virtuales": 3,
            "verbose": false
        }
    }
    
    Returns:
    {
        "exito": true,
        "proporciones_optimizadas": [0.35, 0.65],
        "proporciones_pct": [35.00, 65.00],
        "proporciones_formato": ["Arena fina: 35%", "Grava: 65%"],
        "error_minimo": 0.523,
        "mejora_total": 2.847,
        "mejora_total_pct": 84.50,
        "cumplimiento_pct": 96.23,
        "iteraciones_realizadas": 3,
        "tablas_virtuales_usadas": 1,
        "razon_parada": "aceptable",
        "detalles_error": {...},
        "detalles_decision": {...},
        "historial_completo": {...},
        "mensaje": "..."
    }
    """
    try:
        config = request.get_json(force=True)
        
        # Validar configuración
        validacion = validar_configuracion(config)
        if not validacion['valido']:
            return jsonify({
                'exito': False,
                'error': 'Validación fallida',
                'detalles': validacion['errores'],
                'mensaje': '; '.join(validacion['errores'])
            }), 400
        
        # Ejecutar optimización
        resultado = optimizar_mezcla(config)
        
        # Retornar resultado
        return jsonify(resultado), 200
    
    except Exception as e:
        import traceback
        return jsonify({
            'exito': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@calculoPorRetenidos.route('/calculoPorRetenidos/analizar', methods=['POST'])
def api_analizar_mezcla():
    """
    API para analizar mezcla actual sin optimizar
    
    POST /calculoPorRetenidos/analizar
    
    Payload JSON:
    {
        "materiales": [...],
        "limites": {...},
        "tamices": [...]
    }
    
    Returns:
    {
        "exito": true,
        "pasante_mezcla": [100, 95, 80, ...],
        "error_total": 1.523,
        "cumplimiento_pct": 85.2,
        "errores_por_tamiz": [...],
        "errores_por_zona": {...},
        "zona_critica": "fina",
        "suficiencia": "marginal",
        "recomendacion": "...",
        "mensaje": "Análisis completado: ..."
    }
    """
    try:
        config = request.get_json(force=True)
        
        # Validar configuración
        validacion = validar_configuracion(config)
        if not validacion['valido']:
            return jsonify({
                'exito': False,
                'error': 'Validación fallida',
                'detalles': validacion['errores'],
                'mensaje': '; '.join(validacion['errores'])
            }), 400
        
        # Ejecutar análisis
        resultado = analizar_mezcla_actual(config)
        
        # Retornar resultado
        return jsonify(resultado), 200
    
    except Exception as e:
        import traceback
        return jsonify({
            'exito': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500



# ===== FUNCIONES DE OPTIMIZACIÓN DE PROPORCIONES =====

def optimizar_proporciones_materiales(materiales, banda_min, banda_max, tamices):
    """
    Optimiza proporcionesde múltiples materiales para alcanzar las bandas especificadas.
    
    Args:
        materiales: List[{nombre, pasantes: [...]}]
        banda_min: List[float] - límite inferior Paver
        banda_max: List[float] - límite superior Paver
        tamices: List[float] - valores de tamices
    
    Returns:
        (mezcla_optimizada, proporciones_dict) o (None, None) si falla
    """
    try:
        import numpy as np
        from scipy.optimize import minimize, LinearConstraint, Bounds
        
        n_materiales = len(materiales)
        n_tamices = len(tamices)
        
        # Convertir pasantes a numpy array
        pasantes_array = np.array([m['pasantes'] for m in materiales])  # Shape: (n_materiales, n_tamices)
        banda_min = np.array(banda_min, dtype=float)
        banda_max = np.array(banda_max, dtype=float)
        
        # Función objetivo: minimizar desviación respecto a centro de bandas
        def objetivo(proporciones):
            # proporciones: [p0, p1, ..., p_{n-1}] donde sum=1
            mezcla = proporciones @ pasantes_array  # Shape: (n_tamices,)
            
            # Centro de cada banda
            centros = (banda_min + banda_max) / 2
            
            # Error: desviación respecto al centro
            error = np.sum((mezcla - centros) ** 2)
            
            return error
        
        # Restricciones:
        # 1. sum(proporciones) = 1
        # 2. banda_min <= mezcla <= banda_max para cada tamiz
        
        def restriccion_suma(prop):
            return np.sum(prop) - 1.0
        
        def restriccion_bandas(prop):
            mezcla = prop @ pasantes_array
            # Retorna vector que debe ser >= 0 (mezcla - banda_min >= 0 y banda_max - mezcla >= 0)
            lower_ok = mezcla - banda_min
            upper_ok = banda_max - mezcla
            return np.concatenate([lower_ok, upper_ok])
        
        # Valores iniciales (iguales para todos)
        x0 = np.ones(n_materiales) / n_materiales
        
        # Restricción de igualdad: sum = 1
        constraints = [
            {'type': 'eq', 'fun': restriccion_suma},
            {'type': 'ineq', 'fun': restriccion_bandas}
        ]
        
        # Límites: cada proporción entre 0 y 1
        bounds = [(0, 1) for _ in range(n_materiales)]
        
        # Optimizar
        resultado_opt = minimize(objetivo, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not resultado_opt.success:
            print(f"⚠️ Optimización falló: {resultado_opt.message}")
            return None, None
        
        # Extraer solución
        proporciones_optimas = resultado_opt.x
        mezcla_optimizada = proporciones_optimas @ pasantes_array
        mezcla_optimizada = np.clip(mezcla_optimizada, 0.0, 100.0)
        mezcla_optimizada[np.abs(mezcla_optimizada) < 1e-6] = 0.0
        mezcla_optimizada[np.abs(mezcla_optimizada - 100.0) < 1e-6] = 100.0
        
        # Validar que cumple bandas
        dentro_bandas = np.all((mezcla_optimizada >= banda_min - 0.5) & (mezcla_optimizada <= banda_max + 0.5))
        if not dentro_bandas:
            print("⚠️ La solución optimizada no cumple todas las bandas")
        
        # Construir diccionario de resultados
        proporciones_dict = {}
        for i, material in enumerate(materiales):
            proporciones_dict[material['nombre']] = float(round(float(proporciones_optimas[i] * 100), 2))
        proporciones_dict['total_pct'] = 100.0
        
        print(f"✅ Optimización exitosa:")
        for nombre, pct in proporciones_dict.items():
            if nombre != 'total_pct':
                print(f"   {nombre}: {pct}%")
        
        return [float(x) for x in mezcla_optimizada.tolist()], proporciones_dict
        
    except Exception as e:
        print(f"❌ Error en optimización: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def generar_instruccion_receta(proporciones_dict):
    """
    Genera instrucción amigable para el operador a partir de proporciones.
    
    Args:
        proporciones_dict: {nombre_material: porcentaje, ...}
    
    Returns:
        str con instrucción formateada
    """
    materiales_ordenados = [(k, v) for k, v in proporciones_dict.items() if k != 'total_pct']
    materiales_ordenados.sort(key=lambda x: -x[1])  # Ordenar por porcentaje descendente
    
    if not materiales_ordenados:
        return "No hay materiales para mezclar."
    
    # Construir instrucción
    receta = "Mezclar: "
    for i, (nombre, pct) in enumerate(materiales_ordenados):
        if i > 0:
            receta += " + "
        receta += f"{pct}% {nombre}"
    
    receta += f" = {proporciones_dict.get('total_pct', 100)}% de mezcla"
    
    return receta


def generar_orden_operativa(materiales):
    """
    Transforma materiales de propuesta en orden operativa para planta.
    Generación de instrucciones paso a paso para el operador.
    
    Args:
        materiales: List[Dict] con propuesta_agregados que contiene
                   material, retido_ind_pct, proporcion_pct
    
    Returns:
        List[Dict] con estructura:
        {
            "material": nombre,
            "tipo": "grueso"|"medio"|"fino",
            "accion": "rezarandear"|"no_tocar",
            "malla": "...|None",
            "resultado": "...",
            "uso": "..."
        }
    """
    if not materiales or not isinstance(materiales, list):
        return []
    
    orden = []
    paso = 0
    
    for mat in materiales:
        # Ignorar materiales con proporción 0
        proporcion = mat.get('proporcion_pct', 0)
        if proporcion == 0 or proporcion is None:
            continue
        
        nombre = mat.get('nombre', 'Material desconocido')
        retido_ind_pct = mat.get('retido_ind_pct', [])
        
        if not retido_ind_pct or len(retido_ind_pct) == 0:
            continue
        
        # Detectar tipo basado en índice del valor máximo
        # Con 8 tamices [9.5, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075]:
        # Índices: 0-2=grueso, 3-4=medio, 5+=fino
        # ⚠️ Estrategia robusta para datos corruptos: buscar máximo entre retidos razonables (0-100)
        retido_razonables = [(i, v) for i, v in enumerate(retido_ind_pct) if 0 < v < 100]
        
        if retido_razonables:
            # Hay valores razonables: tomar el índice del máximo
            max_index = max(retido_razonables, key=lambda x: x[1])[0]
        else:
            # Sin valores razonables: buscar el primero positivo (aunque sea > 100)
            retido_positivos = [(i, v) for i, v in enumerate(retido_ind_pct) if v > 0]
            if retido_positivos:
                max_index = retido_positivos[0][0]
            else:
                max_index = 0
        
        if max_index <= 2:
            tipo = "grueso"
            accion = "rezarandear"
            malla = "2.4–1.2 mm"
            resultado = "genera material medio"
            uso = "reducir grueso y reutilizar pasante"
        elif 3 <= max_index <= 4:
            tipo = "medio"
            accion = "rezarandear"
            malla = "0.6–0.3 mm"
            resultado = "genera material fino"
            uso = "aumentar finos manteniendo equilibrio"
        else:  # max_index >= 5
            tipo = "fino"
            accion = "no_tocar"
            malla = None
            resultado = "ya es fino"
            uso = "aumentar proporción en mezcla"
        
        paso += 1
        
        orden.append({
            "paso": paso,
            "material": nombre,
            "tipo": tipo,
            "accion": accion,
            "malla": malla,
            "resultado": resultado,
            "uso": uso,
            "proporcion_pct": round(proporcion, 2)
        })
    
    return orden


def generar_orden_operativa_real(materiales_originales):
    """
    NUEVA: Genera orden operativa REAL para planta basada en materiales ORIGINALES (difusion 1,2,3)
    NO depende de propuesta_agregados_correctivos
    
    Args:
        materiales_originales: List[Dict] con estructura original del payload
                              {nombre, retido_ind_pct, ...}
    
    Returns:
        List[Dict] con instrucciones operativas
    """
    if not materiales_originales or not isinstance(materiales_originales, list):
        return []
    
    orden = []
    paso = 0
    
    for mat in materiales_originales:
        nombre = mat.get('nombre', 'Material desconocido')
        retido_ind_pct = mat.get('retido_ind_pct', [])
        
        if not retido_ind_pct or len(retido_ind_pct) == 0:
            continue
        
        # Detectar tipo basado en índice del valor máximo
        # Con 8 tamices [9.5, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075]:
        # Índices: 0-2=grueso, 3-4=medio, 5+=fino
        # ⚠️ Estrategia robusta para datos corruptos: buscar máximo entre retidos razonables (0-100)
        retido_razonables = [(i, v) for i, v in enumerate(retido_ind_pct) if 0 < v < 100]
        
        if retido_razonables:
            # Hay valores razonables: tomar el índice del máximo
            max_index = max(retido_razonables, key=lambda x: x[1])[0]
        else:
            # Sin valores razonables: buscar el primero positivo (aunque sea > 100)
            retido_positivos = [(i, v) for i, v in enumerate(retido_ind_pct) if v > 0]
            if retido_positivos:
                max_index = retido_positivos[0][0]
            else:
                max_index = 0
        
        if max_index <= 2:
            tipo = "grueso"
            accion = "rezarandear"
            malla = "2.4–1.2 mm"
            resultado = "genera material medio"
            uso = "reducir grueso y reutilizar pasante"
        elif 3 <= max_index <= 4:
            tipo = "medio"
            accion = "rezarandear"
            malla = "0.6–0.3 mm"
            resultado = "genera material fino"
            uso = "aumentar finos manteniendo equilibrio"
        else:  # max_index >= 5
            tipo = "fino"
            accion = "no_tocar"
            malla = None
            resultado = "ya es fino"
            uso = "aumentar proporción en mezcla"
        
        paso += 1
        
        orden.append({
            "paso": paso,
            "material": nombre,
            "tipo": tipo,
            "accion": accion,
            "malla": malla,
            "resultado": resultado,
            "uso": uso
        })
    
    print(f"[DEBUG orden_real] ✅ Retornando {len(orden)} órdenes")
    return orden



@calculoPorRetenidos.route('/calculoPorRetenidos/auditoria', methods=['GET'])
def auditoria_view():
    """
    Vista HTML de auditoría granulométrica
    
    GET /calculoPorRetenidos/auditoria
    """
    return render_template('autoDensidad/calculoPorRetenidos/auditoria.html')


@calculoPorRetenidos.route('/calculoPorRetenidos/auditoria', methods=['POST'])
def api_auditoria():
    """
    Auditoría completa de mezcla granulométrica con decisión de tabla virtual Y optimización de proporciones
    
    POST /calculoPorRetenidos/auditoria
    
    Payload JSON (opción 1 - tabla única):
    {
        "pasante_real": [99.20, 76.60, 35.20, 12.40, 6.50, 4.70, 1.40],
        "banda_min": [85, 65, 35, 15, 5, 2, 0],
        "banda_max": [100, 90, 65, 45, 20, 10, 5],
        "tamices": [8, 5, 3.15, 2, 1, 0.5, 0.1]
    }
    
    Payload JSON (opción 2 - múltiples materiales con optimización):
    {
        "pasante_real": [...],  # mezcla ponderada inicial
        "banda_min": [...],
        "banda_max": [...],
        "tamices": [...],
        "materiales": [
            {"nombre": "Material A", "pasantes": [...]},
            {"nombre": "Material B", "pasantes": [...]},
            {"nombre": "Material C", "pasantes": [...]}
        ]
    }
    
    Returns:
    {
        "exito": true,
        "data": {
            "fase_1": {...},
            "fase_2_4_criterios": {...},
            "fase_5_virtual": {...},
            "fase_6_receta": {
                "proporciones": {
                    "Material A": 45.5,
                    "Material B": 32.2,
                    "Material C": 22.3,
                    "total_pct": 100.0
                },
                ...
            },
            ...
        }
    }
    """
    try:
        config = request.get_json(force=True)
        
        # Extraer datos del payload
        pasante_real = config.get('pasante_real', [])
        banda_min = config.get('banda_min', [])
        banda_max = config.get('banda_max', [])
        tamices = config.get('tamices', [])
        materiales = config.get('materiales', None)  # ← NUEVO: materiales para optimizar
        
        print(f"\n🔍 [AUDITORIA API] Recibidos {len(materiales) if materiales else 0} materiales en payload")
        if materiales:
            for i, m in enumerate(materiales):
                tiene_retido = 'retido_ind_pct' in m and m.get('retido_ind_pct')
                tiene_pasantes = 'pasantes' in m and m.get('pasantes')
                print(f"   Material {i}: {m.get('nombre', 'unknown')} - retido_ind_pct={tiene_retido}, pasantes={tiene_pasantes}")
        
        # ✅ GUARDAR MATERIALES ORIGINALES ANTES DE PROCESAR
        import copy
        materiales_originales_para_orden = copy.deepcopy(materiales) if materiales else None
        
        # Si los materiales NO tienen retido_ind_pct pero sí tienen pasantes, convertir
        if materiales_originales_para_orden:
            print(f"✅ Intentando convertir pasantes a retido_ind_pct...")
            for mat in materiales_originales_para_orden:
                if not mat.get('retido_ind_pct'):
                    pasantes = mat.get('pasantes', [])
                    if pasantes and len(pasantes) > 0:
                        # Convertir pasantes a retido_ind_pct
                        retido_ind_pct = []
                        anterior = 100.0
                        for pasante in pasantes:
                            retido = anterior - pasante
                            retido_ind_pct.append(retido)
                            anterior = pasante
                        retido_ind_pct.append(anterior)
                        mat['retido_ind_pct'] = retido_ind_pct
                        print(f"   ✅ Convertido {mat['nombre']}: pasantes → retido_ind_pct = {retido_ind_pct[:3]}...")
                else:
                    print(f"   ✓ {mat['nombre']} ya tiene retido_ind_pct")
        
        print(f"📦 Guardados {len(materiales_originales_para_orden) if materiales_originales_para_orden else 0} materiales para orden_operativa_real")
        
        # Validar entrada
        if not all([pasante_real, banda_min, banda_max, tamices]):
            return jsonify({
                'exito': False,
                'error': 'Faltan datos requeridos',
                'campos_requeridos': ['pasante_real', 'banda_min', 'banda_max', 'tamices']
            }), 400
        
        # AUTO-CORRECCIÓN: Si las bandas tienen menos elementos que tamices/pasante, rellenarlas
        n_tamices = len(tamices)
        n_pasante = len(pasante_real)
        n_banda_min = len(banda_min)
        n_banda_max = len(banda_max)
        
        if n_tamices != n_pasante or n_banda_min != n_tamices or n_banda_max != n_tamices:
            # Obtener la longitud máxima requerida
            n_requerida = max(n_tamices, n_pasante)
            
            # Rellenar con valores por defecto estándar para agregados finos
            bandas_default_min = [100, 95, 85, 70, 50, 35, 15, 5, 0]
            bandas_default_max = [100, 100, 100, 90, 75, 60, 30, 15, 10]
            
            # Extender o truncar según sea necesario
            banda_min = (banda_min + bandas_default_min[:max(0, n_requerida - len(banda_min))])[:n_requerida]
            banda_max = (banda_max + bandas_default_max[:max(0, n_requerida - len(banda_max))])[:n_requerida]
            
            # Ajustar tamices y pasante si es necesario
            if len(tamices) < n_requerida:
                tamices = tamices + [0.0] * (n_requerida - len(tamices))
            if len(pasante_real) < n_requerida:
                pasante_real = pasante_real + [0.0] * (n_requerida - len(pasante_real))
        
        # Validación final
        if not (len(pasante_real) == len(banda_min) == len(banda_max) == len(tamices)):
            return jsonify({
                'exito': False,
                'error': f'Inconsistencia después de auto-corrección: pasante={len(pasante_real)}, banda_min={len(banda_min)}, banda_max={len(banda_max)}, tamices={len(tamices)}'
            }), 400
        
        # ===== NUEVA LÓGICA: OPTIMIZAR PROPORCIONES SI HAY MÚLTIPLES MATERIALES =====
        pasante_entrada_original = [float(x) for x in pasante_real]
        pasante_auditado = [float(x) for x in pasante_real]
        pasante_real_optimizado = None
        proporciones_optimizadas = None
        
        if materiales and len(materiales) > 1:
            print(f"🔧 Optimizando proporcionesde {len(materiales)} materiales...")
            pasante_real_optimizado, proporciones_optimizadas = optimizar_proporciones_materiales(
                materiales=materiales,
                banda_min=banda_min,
                banda_max=banda_max,
                tamices=tamices
            )
            if pasante_real_optimizado:
                print(f"✅ Optimización exitosa: {proporciones_optimizadas}")
                pasante_auditado = [float(x) for x in pasante_real_optimizado]
        
        # Generar auditoría completa
        resultado = generar_auditoria_completa(
            pasante_real=pasante_auditado,
            banda_min=banda_min,
            banda_max=banda_max,
            tamices=tamices
        )

        resultado['meta'] = {
            'optimizacion_aplicada': bool(pasante_real_optimizado),
            'pasante_entrada_original': pasante_entrada_original,
            'pasante_auditado': pasante_auditado,
        }
        if 'para_grafico' in resultado:
            resultado['para_grafico']['pasante_entrada_original'] = pasante_entrada_original
            resultado['para_grafico']['pasante_auditado'] = pasante_auditado
        
        # Inyectar proporciones optimizadas en la receta si existen
        if proporciones_optimizadas and 'fase_6_receta' in resultado:
            resultado['fase_6_receta']['proporciones'] = proporciones_optimizadas
            resultado['fase_6_receta']['instruction'] = generar_instruccion_receta(proporciones_optimizadas)
            resultado['fase_6_receta']['tabla_entrada_pasante'] = pasante_entrada_original
        
        # ===== NUEVO: Generar propuesta de agregados correctivos =====
        try:
            propuesta_agregados = generar_propuesta_3_agregados(
                mix_pasante=pasante_auditado,
                banda_min=banda_min,
                banda_max=banda_max,
                tamices=tamices,
                log=None
            )
            if propuesta_agregados and propuesta_agregados.get('exito'):
                resultado['propuesta_agregados_correctivos'] = propuesta_agregados
        except Exception as e:
            print(f"⚠️ Error generando propuesta de agregados en auditoría: {str(e)}")
        
        # ===== NUEVO: Generar orden operativa para planta =====
        # IMPORTANTE: Generar SIEMPRE si tenemos propuesta_agregados_correctivos, sin depender de parámetros
        try:
            if 'propuesta_agregados_correctivos' in resultado and resultado['propuesta_agregados_correctivos'].get('exito'):
                propuesta_dict = resultado['propuesta_agregados_correctivos'].get('propuesta', {})
                if propuesta_dict:
                    materiales_con_retido = []
                    
                    for key in ['m1', 'm2', 'm3']:
                        if key in propuesta_dict:
                            mat_info = propuesta_dict[key]
                            proporciones = resultado['propuesta_agregados_correctivos'].get('proporciones', [])
                            if proporciones:
                                idx = ['m1', 'm2', 'm3'].index(key)
                                proporcion = proporciones[idx] * 100 if idx < len(proporciones) else 0
                                materiales_con_retido.append({
                                    'nombre': mat_info.get('nombre', key.upper()),
                                    'retido_ind_pct': mat_info.get('retido_ind_pct', []),
                                    'proporcion_pct': proporcion
                                })
                    
                    if materiales_con_retido:
                        orden = generar_orden_operativa(materiales_con_retido)
                        if orden:
                            resultado['orden_operativa'] = orden
                            import json
                            print("\n" + "="*80)
                            print("[✅ ORDEN OPERATIVA GENERADA]")
                            print("="*80)
                            print(json.dumps(orden, indent=2, ensure_ascii=False))
                            print("="*80 + "\n")
        except Exception as e:
            import traceback
            print(f"⚠️ Error generando orden_operativa: {str(e)}")
            print(traceback.format_exc())
        
        # ===== NUEVO: Generar orden operativa REAL basada en materiales ORIGINALES (PLANTA) =====
        try:
            print(f"\n[DEBUG] Verificando materiales para orden_operativa_real...")
            print(f"[DEBUG] materiales_originales_para_orden exists? {materiales_originales_para_orden is not None}")
            print(f"[DEBUG] materiales_originales_para_orden is list? {isinstance(materiales_originales_para_orden, list) if materiales_originales_para_orden else False}")
            print(f"[DEBUG] materiales_originales_para_orden length? {len(materiales_originales_para_orden) if materiales_originales_para_orden else 0}")
            
            if materiales_originales_para_orden and isinstance(materiales_originales_para_orden, list) and len(materiales_originales_para_orden) > 0:
                print(f"[DEBUG] Llamando generar_orden_operativa_real()...")
                orden_real = generar_orden_operativa_real(materiales_originales_para_orden)
                print(f"[DEBUG] orden_real result: {orden_real}")
                print(f"[DEBUG] orden_real length: {len(orden_real)}")
                
                if orden_real:
                    resultado['orden_operativa_real'] = orden_real
                    import json
                    print("\n" + "="*80)
                    print("[✅ ORDEN OPERATIVA REAL (PLANTA) GENERADA]")
                    print("="*80)
                    print(json.dumps(orden_real, indent=2, ensure_ascii=False))
                    print("="*80 + "\n")
                else:
                    print("[DEBUG] orden_real es vacío o False")
            else:
                print(f"[DEBUG] Condiciones no cumplidas para orden_operativa_real")
        except Exception as e:
            import traceback
            print(f"⚠️ Error generando orden_operativa_real: {str(e)}")
            print(traceback.format_exc())
        
        return jsonify({
            'exito': True,
            'data': resultado
        }), 200
    
    except Exception as e:
        import traceback
        return jsonify({
            'exito': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@calculoPorRetenidos.route('/calculoPorRetenidos/status', methods=['GET'])
def api_status():
    """
    Verifica estado del sistema de optimización
    
    GET /calculoPorRetenidos/status
    
    Returns:
    {
        "status": "ok",
        "sistema": "Optimización Granulométrica",
        "version": "1.0.0",
        "endpoints": ["/optimizar", "/analizar", "/status"]
    }
    """
    return jsonify({
        'status': 'ok',
        'sistema': 'Optimización Granulométrica v1.0.0',
        'endpoints': [
            'POST /calculoPorRetenidos/optimizar - Optimizar mezcla completa',
            'POST /calculoPorRetenidos/analizar - Analizar mezcla actual',
            'POST /calculoPorRetenidos/auditoria - Auditoría con decisión de tabla virtual',
            'GET /calculoPorRetenidos/status - Estado del sistema'
        ],
        'modulos': [
            'nucleo_mezcla - Cálculos de mezcla (PASANTE-only)',
            'nucleo_error - Sistema de error lineal',
            'nucleo_decision - Lógica de decisión (4 niveles, 4 paradas)',
            'nucleo_optimizacion - Optimización por gradiente',
            'nucleo_iteracion - Control de iteraciones',
            'auditoria_decision - Auditoría y decisión de tabla virtual',
            'api_integracion - API principal'
        ]
    }), 200