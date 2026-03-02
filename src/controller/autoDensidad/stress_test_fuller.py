# controller/autoDensidad/stress_test_fuller.py

from __future__ import annotations

import math
import json
import csv
import time
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

# ✅ Importá tus funciones reales
from controller.autoDensidad.calcularMezclaOptima import (
    calcular_mezcla_optima,
    calcular_curva_fuller,
)
from controller.autoDensidad.densidadFuller import (
    alinear_mezclas_por_tamices,
    evaluar_mezcla_promedio,
)

# Master de tamices (tu convención)
TAMICES_DEFAULT = [12.5, 9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074]


# =========================
# Helpers matemáticos
# =========================

def _is_finite_list(xs: List[float]) -> bool:
    for x in xs:
        if x is None or not math.isfinite(float(x)):
            return False
    return True

def _force_monotone_increasing(curva: List[float]) -> List[float]:
    """Fuerza monotonicidad acumulada creciente (curva % pasante)."""
    out = list(curva)
    for i in range(1, len(out)):
        if out[i] < out[i - 1]:
            out[i] = out[i - 1]
    return out

def _clip_0_100(curva: List[float]) -> List[float]:
    return [float(np.clip(v, 0.0, 100.0)) for v in curva]

def _finalize_curve(curva: List[float], force_last_100: bool = True) -> List[float]:
    out = _clip_0_100(curva)
    out = _force_monotone_increasing(out)
    if force_last_100 and out:
        out[-1] = 100.0
    return out

def _rand_n(rng: random.Random, lo=0.30, hi=0.70) -> float:
    return rng.uniform(lo, hi)

def _pick_dmax(tamices: List[float]) -> float:
    return float(max(tamices)) if tamices else 25.0


# =========================
# Generación de curvas coherentes
# =========================

def generar_curva_coherente(
    tamices: List[float],
    d_max: float,
    rng: random.Random,
    ruido_sigma: float = 5.0,
    modo: str = "fuller_ruido",
) -> List[float]:
    """
    Genera una curva % pasante físicamente coherente.
    modo:
      - fuller_ruido: base Fuller(n_random) + ruido normal
      - casi_todo_fino: curva sube tarde (mucho fino)
      - casi_todo_grueso: curva sube rápido (mucho grueso)
      - plana: casi constante (edge case)
    """
    tam = list(tamices)

    if modo == "plana":
        base = [rng.uniform(0, 30) for _ in tam]  # casi plana baja
        return _finalize_curve(base, force_last_100=True)

    if modo == "casi_todo_fino":
        # Sube tarde: tomamos n alto + penalizamos puntos gruesos
        n = rng.uniform(0.60, 0.75)
        fuller = calcular_curva_fuller(tam, d_max=d_max, n=n)
        arr = np.array(fuller, dtype=float)
        # empujar gruesos hacia abajo
        for i, t in enumerate(tam):
            if t > 4.75:
                arr[i] -= rng.uniform(10, 25)
        arr += rng.normalvariate(0, ruido_sigma)
        return _finalize_curve(arr.tolist(), force_last_100=True)

    if modo == "casi_todo_grueso":
        # Sube rápido: n bajo + empujar gruesos hacia arriba
        n = rng.uniform(0.25, 0.40)
        fuller = calcular_curva_fuller(tam, d_max=d_max, n=n)
        arr = np.array(fuller, dtype=float)
        for i, t in enumerate(tam):
            if t > 4.75:
                arr[i] += rng.uniform(5, 20)
        return _finalize_curve((arr + np.random.normal(0, ruido_sigma, len(arr))).tolist(), True)

    # default: fuller_ruido
    base = np.linspace(100, 5, 9)
    ruido = np.random.normal(0, ruido_sigma, 9)
    curva = base + ruido
    curva = np.maximum.accumulate(curva[::-1])[::-1]
    return _finalize_curve(curva.tolist(), force_last_100=True)


def generar_mezclas_random(
    rng: random.Random,
    num_mezclas: int,
    tamices_master: Optional[List[float]] = None,
    allow_missing_tamices: bool = True,
    ruido_sigma: float = 5.0,
) -> List[Dict[str, Any]]:
    """
    Genera N mezclas con posibles tamices incompletos para testear alineación.
    """
    master = list(tamices_master or TAMICES_DEFAULT)
    d_max = _pick_dmax(master)

    modos = ["fuller_ruido", "casi_todo_fino", "casi_todo_grueso", "plana"]

    mezclas = []
    for i in range(num_mezclas):
        tamices = list(master)

        # opcional: quitar algunos tamices para simular datos incompletos
        if allow_missing_tamices and rng.random() < 0.35:
            k = rng.randint(1, 3)  # quita 1..3 tamices
            drop = set(rng.sample(tamices[1:-1], k=k))  # no tocar extremos
            tamices = [t for t in tamices if t not in drop]

        modo = rng.choice(modos)
        curva = generar_curva_coherente(tamices, d_max=d_max, rng=rng, ruido_sigma=ruido_sigma, modo=modo)

        mezclas.append({
            "nombre": f"Mix_{i+1}",
            "tamices": tamices,
            "porcentajes_reales": curva,
            "modo": modo,
        })

    return mezclas


# =========================
# Métricas y reporte
# =========================

@dataclass
class CasoFallido:
    seed: int
    motivo: str
    payload: Dict[str, Any]


@dataclass
class ResultadoStress:
    iteraciones: int
    ok: int
    fail: int
    fail_rate: float
    error_mean: float
    error_std: float
    error_p50: float
    error_p95: float
    error_max: float
    error_min: float
    error_list: List[float]
    duracion_s: float
    fails: List[CasoFallido]


def _percentile(xs: List[float], p: float) -> float:
    if not xs:
        return float("nan")
    arr = np.array(xs, dtype=float)
    return float(np.percentile(arr, p))


def _validate_result(resultado: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida invariantes del resultado de calcular_mezcla_optima().
    """
    if not isinstance(resultado, dict):
        return False, "resultado_no_dict"

    if "error" in resultado:
        return False, f"opt_error:{resultado.get('error')}"

    err = resultado.get("error_total")
    if err is None or not math.isfinite(float(err)):
        return False, "error_total_invalido"

    pesos = resultado.get("pesos_optimos_mezcla")
    if not pesos or not isinstance(pesos, list):
        return False, "pesos_inexistentes"

    # pesos_optimos_mezcla viene en % en tu función (redondeados)
    # convertimos a fracción para checks suaves
    w = [float(p) / 100.0 for p in pesos]

    s = sum(w)
    if not (0.98 <= s <= 1.02):
        return False, f"suma_pesos_invalida:{s:.4f}"

    if any((p < -1e-6 or p > 1.000001) for p in w):
        return False, "peso_fuera_de_rango"

    curva_res = resultado.get("curva_resultante")
    curva_ideal = resultado.get("curva_ideal")
    if not (isinstance(curva_res, list) and isinstance(curva_ideal, list)):
        return False, "curvas_no_list"

    if not _is_finite_list(curva_res) or not _is_finite_list(curva_ideal):
        return False, "curvas_no_finitas"

    return True, "ok"


def correr_stress_test(
    iteraciones: int = 500,
    min_mezclas: int = 2,
    max_mezclas: int = 7,
    tamices_master: Optional[List[float]] = None,
    d_max: Optional[float] = None,
    n_fijo: float = 0.5,
    ruido_sigma: float = 6.0,
    allow_missing_tamices: bool = True,
    seed: Optional[int] = None,
    guardar_csv_path: Optional[str] = None,
    guardar_json_path: Optional[str] = None,
) -> ResultadoStress:
    """
    Monte Carlo + edge cases. Devuelve métricas y lista de fallos reproducibles.
    """
    t0 = time.time()
    master = list(tamices_master or TAMICES_DEFAULT)
    dmax = float(d_max) if d_max is not None else _pick_dmax(master)

    # Seed reproducible global para el runner
    base_seed = seed if seed is not None else random.randint(1, 2_000_000_000)
    rng_global = random.Random(base_seed)

    errores = []
    fails: List[CasoFallido] = []
    ok = 0
    fail = 0

    # CSV rows (opcional)
    csv_rows = []

    for it in range(iteraciones):
        case_seed = rng_global.randint(1, 2_000_000_000)
        rng = random.Random(case_seed)

        try:
            num_mezclas = rng.randint(min_mezclas, max_mezclas)
            mezclas = generar_mezclas_random(
                rng=rng,
                num_mezclas=num_mezclas,
                tamices_master=master,
                allow_missing_tamices=allow_missing_tamices,
                ruido_sigma=ruido_sigma,
            )

            # Alinear (tu función real) para asegurar set común
            # Devuelve master_tamices y mezclas_alineadas con 0.0 donde falte
            master_tamices, mezclas_alineadas = alinear_mezclas_por_tamices(mezclas, dec=3, tol=0.0)

            curvas_individuales = [m["porcentajes_reales"] for m in mezclas_alineadas]

            # Ejecutar optimizador real
            resultado = calcular_mezcla_optima(
                curvas_individuales,
                master_tamices,
                d_max=dmax,
                n=n_fijo,
            )

            is_ok, motivo = _validate_result(resultado)
            if not is_ok:
                fail += 1
                fails.append(CasoFallido(
                    seed=case_seed,
                    motivo=motivo,
                    payload={
                        "mezclas_original": mezclas,
                        "mezclas_alineadas": mezclas_alineadas,
                        "master_tamices": master_tamices,
                        "d_max": dmax,
                        "n": n_fijo,
                        "resultado": resultado,
                    }
                ))
                continue

            ok += 1
            err = float(resultado["error_total"])
            errores.append(err)

            # evaluación por zonas sobre curva resultante vs ideal (opcional pero útil)
            # (diferencias ya vienen como resultante - ideal en tu función)
            # Si quisieras, podés recalcular diferencias. Acá lo dejamos simple:
            dif = [r - i for r, i in zip(resultado["curva_resultante"], resultado["curva_ideal"])]
            evalz = evaluar_mezcla_promedio(master_tamices[:len(dif)], dif)

            csv_rows.append({
                "iter": it + 1,
                "case_seed": case_seed,
                "num_mezclas": num_mezclas,
                "error_total": err,
                "estado": evalz.get("estado"),
                "error_promedio_eval": evalz.get("error_promedio"),
            })

        except Exception as e:
            fail += 1
            fails.append(CasoFallido(
                seed=case_seed,
                motivo=f"exception:{type(e).__name__}:{str(e)}",
                payload={"d_max": dmax, "n": n_fijo}
            ))

    dur = time.time() - t0

    # Métricas
    if errores:
        mean = float(np.mean(errores))
        std = float(np.std(errores))
        p50 = _percentile(errores, 50)
        p95 = _percentile(errores, 95)
        mx = float(np.max(errores))
        mn = float(np.min(errores))
    else:
        mean = std = p50 = p95 = mx = mn = float("nan")

    res = ResultadoStress(
        iteraciones=iteraciones,
        ok=ok,
        fail=fail,
        fail_rate=(fail / max(1, iteraciones)),
        error_mean=mean,
        error_std=std,
        error_p50=p50,
        error_p95=p95,
        error_max=mx,
        error_min=mn,
        error_list=errores,
        duracion_s=dur,
        fails=fails[:50],  # guardamos top 50 fallos (para no explotar memoria)
    )

    # Export CSV (opcional)
    if guardar_csv_path:
        fieldnames = list(csv_rows[0].keys()) if csv_rows else ["iter", "case_seed", "num_mezclas", "error_total", "estado", "error_promedio_eval"]
        with open(guardar_csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in csv_rows:
                w.writerow(row)

    # Export JSON con métricas + fallos
    if guardar_json_path:
        payload = asdict(res)
        # serializar fails (dataclass)
        payload["fails"] = [ {"seed": f.seed, "motivo": f.motivo, "payload": f.payload} for f in res.fails ]
        payload["base_seed"] = base_seed
        payload["raw_errors"] = res.error_list
        with open(guardar_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    return res


def reproducir_fallo(caso: CasoFallido) -> Dict[str, Any]:
    """
    Te permite re-ejecutar exactamente un caso fallido (misma seed).
    """
    seed = int(caso.seed)
    rng = random.Random(seed)
    master = TAMICES_DEFAULT
    dmax = _pick_dmax(master)

    num_mezclas = rng.randint(2, 7)
    mezclas = generar_mezclas_random(rng, num_mezclas, master, True, 6.0)

    master_tamices, mezclas_alineadas = alinear_mezclas_por_tamices(mezclas, dec=3, tol=0.0)
    curvas = [m["porcentajes_reales"] for m in mezclas_alineadas]

    resultado = calcular_mezcla_optima(curvas, master_tamices, d_max=dmax, n=0.5)

    return {
        "seed": seed,
        "mezclas": mezclas,
        "mezclas_alineadas": mezclas_alineadas,
        "master_tamices": master_tamices,
        "resultado": resultado,
    }