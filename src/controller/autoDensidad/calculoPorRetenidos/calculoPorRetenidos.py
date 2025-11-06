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

    tamices = data.get('tamices', TAMICES_ORDEN)
    materiales_in = data.get('materiales', [])
    limites = data.get('limites', {})

    if not materiales_in:
        return jsonify(ok=False, error="Faltan materiales"), 400

    log("\n=== [RETIDO] Entrada cruda ===")
    log(f"Tamices (recv): {tamices}")
    for m in materiales_in:
        log(f"  - {m.get('nombre')}: prop%={m.get('proporcion_pct')}  len(ret_ind)={len(m.get('retido_ind_pct',[]))}")

    # 1) ordenar según norma
    idx = _ordenar_indices(tamices)
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
        ret_ind = m.get('retido_ind_pct', [])

        # alineación por orden de tamices
        ret_ind_ord = [float(ret_ind[i]) if i < len(ret_ind) else 0.0 for i in idx]
        ret_acum_ord = _acum_desc(ret_ind_ord)

        # logs por material
        check_sum_100(ret_ind_ord, f"{nombre} (IND)")
        log(f"\n-- {nombre} -- prop%={p}  w={round(w,6)}")
        log("IND:", ["{:.1f}".format(x) for x in ret_ind_ord])
        log("ACU:", ["{:.1f}".format(x) for x in ret_acum_ord])
        if str(tamices_ord[-1]).lower() == "fundo":
            log(f"ACU último (debe ~100): {ret_acum_ord[-1]}")

        materiales.append({
            "nombre": nombre,
            "proporcion_pct": round(p, 2),
            "w": round(w, 6),
            "ret_ind": [round(x, 2) for x in ret_ind_ord],
            "ret_acum": ret_acum_ord
        })

    # 3) mezcla ponderada (acumulado)
    mix_acum = _mezcla_ponderada_acum(materiales)
    
    log("\n> MIX ACUM (ponderado):", ["{:.1f}".format(x) for x in mix_acum])

    # 4) MF
    mf = _finura_modulus(mix_acum, tamices_ord)
    log(f"> Módulo de finura (esperado ~3.55 con planilla): {mf}")

    # 5) validación contra faixas
    valid = _validar_faixas(mix_acum, tamices_ord, limites)
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

    return jsonify({
        "ok": True,
        "tamices": tamices_ord,
        "materiales": materiales,
        "mix_acum": mix_acum,
        "modulo_finura": mf,
        "faixas": valid,
        "gran_ponderada": gran_ponderada, 
        "tabla": tabla
    }), 200
