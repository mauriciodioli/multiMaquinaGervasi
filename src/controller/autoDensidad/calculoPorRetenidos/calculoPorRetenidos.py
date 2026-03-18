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





calculoPorRetenidos = Blueprint('calculoPorRetenidos', __name__)

MF_SIEVES_BR = [4.8, 2.4, 1.2, 0.6, 0.3, 0.15]
TAMICES_ORDEN = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075, "Fundo"]




def _ordenar_indices(tamices):
    # fuerza el orden norma; si falta alguno lo ignora, si sobra alguno lo manda al final
    pos = {str(t): i for i, t in enumerate(TAMICES_ORDEN)}
    return sorted(range(len(tamices)), key=lambda i: pos.get(str(tamices[i]), 999))

def _acum_desc(ret_ind_list):
    acum = []
    s = 0.0
    for v in ret_ind_list:
        s += float(v or 0.0)
        acum.append(s)
    # saneo numérico
    return [min(100.0, max(0.0, round(x, 2))) for x in acum]

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
                    ret_ind_norm = ret_ind_ord
                else:
                    log(f"ℹ️ {nombre} already ~100, no normalization needed (sum={round(total,2)})")
                    ret_ind_norm = ret_ind_ord
        else:
            ret_ind_norm = ret_ind_ord

        ret_acum_ord = _acum_desc(ret_ind_norm)

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
            "ret_acum": ret_acum_ord
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
    sugerencia_division = None
    if materiales_in:
        primer_material = materiales_in[0]
        
        # Extraer retidos originales (antes de cualquier normalización)
        if "filas" in primer_material and primer_material["filas"]:
            # Nuevo formato: mapear filas a retidos en orden de tamices
            retido_map = {
                str(f["tamiz"]): float(f["porcentaje"])
                for f in primer_material["filas"]
            }
            retido_original = [retido_map.get(str(t), 0.0) for t in tamices_ord]
        else:
            # Formato antiguo
            retido_original = primer_material.get("retido_ind_pct", [])
        
        # Generar sugerencia
        if retido_original:
            log("\n> Generando sugerencia de división para:", primer_material.get('nombre', 'Agregado 1'))
            sugerencia_division = sugerir_division_en_dos(tamices_ord, retido_original)
            if sugerencia_division:
                log(f"  Grupo 1: {sugerencia_division['grupos'][0]['proporcion_sugerida_pct']}%")
                log(f"  Grupo 2: {sugerencia_division['grupos'][1]['proporcion_sugerida_pct']}%")
                log(f"  Error reconstrucción: {sugerencia_division['reconstruccion_check']['error_total_pct']}%")

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
        "sugerencia_division": sugerencia_division
    }), 200




def _normalizar_ind(ret_ind):
    total = sum(ret_ind)
    if total <= 0:
        return ret_ind  # evitar división por cero
    return [(x / total) * 100 for x in ret_ind]


def sugerir_division_en_dos(tamices, retido_ind_pct):
    """
    División inteligente basada en el mayor salto granulométrico.
    """

    if len(tamices) != len(retido_ind_pct):
        return None

    if not tamices or not retido_ind_pct:
        return None

    n = len(tamices)

    # -------------------------------
    # 1. Calcular acumulado
    # -------------------------------
    # usar los valores NORMALIZADOS (los mismos que usás en IND)
    total = sum(retido_ind_pct)
    if total == 0:
        return None

    retido_normalizado = [(v / total) * 100 for v in retido_ind_pct]

    acumulado = []
    running = 0.0
    for v in retido_normalizado:
        running += v
        acumulado.append(running)

    if total <= 0:
        return None

    # -------------------------------
    # 2. Detectar mayor salto
    # -------------------------------
    diffs = []
    for i in range(1, n):
        diffs.append(acumulado[i] - acumulado[i - 1])

    idx_corte = diffs.index(max(diffs)) + 1  # +1 porque diff empieza en 1

    # -------------------------------
    # 3. Dividir en grupos
    # -------------------------------
    tamices_g1 = tamices[:idx_corte]
    retido_g1 = retido_ind_pct[:idx_corte]

    tamices_g2 = tamices[idx_corte:]
    retido_g2 = retido_ind_pct[idx_corte:]

    # -------------------------------
    # 4. Pesos
    # -------------------------------
    peso_g1 = sum(retido_g1)
    peso_g2 = sum(retido_g2)
    peso_total = peso_g1 + peso_g2

    if peso_total <= 0:
        return None

    prop_g1 = round((peso_g1 / peso_total) * 100, 2)
    prop_g2 = round((peso_g2 / peso_total) * 100, 2)

    # -------------------------------
    # 5. Normalización interna
    # -------------------------------
    retido_norm_g1 = [
        round((v / peso_g1) * 100, 2) if peso_g1 > 0 else 0.0
        for v in retido_g1
    ]

    retido_norm_g2 = [
        round((v / peso_g2) * 100, 2) if peso_g2 > 0 else 0.0
        for v in retido_g2
    ]

    # -------------------------------
    # 6. Reconstrucción CORRECTA
    # -------------------------------
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

    # -------------------------------
    # 7. Resultado
    # -------------------------------
    return {
        "tipo": "auto_2_inteligente",
        "punto_corte_index": idx_corte,
        "punto_corte_tamiz": str(tamices[idx_corte - 1]),
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
        }
    }