# controller/autoDensidad/stress_blueprint.py

from flask import Blueprint, request, jsonify, Response, send_file
import os, time
import numpy as np

from controller.autoDensidad.stress_test_fuller import correr_stress_test
from controller.autoDensidad.stress_report import build_html_report, write_pdf_report

stress_bp = Blueprint("stress_bp", __name__)

def go_no_go(metrics: dict) -> dict:
    """
    Reglas simples (ajustables).
    GO si:
      fail_rate <= 1%
      error_p95 <= 25
    """
    reasons = []
    fail_rate = metrics.get("fail_rate", 1.0)
    p95 = metrics.get("error_p95", 9999)

    ok_fail = fail_rate <= 0.01
    ok_p95  = (p95 is not None) and (not np.isnan(p95)) and (p95 <= 25)

    if ok_fail:
        reasons.append(f"Fail rate OK: {fail_rate*100:.2f}% ≤ 1.00%")
    else:
        reasons.append(f"Fail rate ALTO: {fail_rate*100:.2f}% > 1.00%")

    if ok_p95:
        reasons.append(f"Error p95 OK: {p95:.2f} ≤ 25")
    else:
        reasons.append(f"Error p95 ALTO: {p95} > 25")

    decision = "GO ✅ (apto para producción)" if (ok_fail and ok_p95) else "NO-GO ❌"
    return {"decision": decision, "reasons": reasons}

@stress_bp.route("/stress_test_fuller/", methods=["POST"])
def stress_test_fuller():

    data = request.get_json(force=True) or {}
    out_dir = data.get("out_dir", "tmp")
    os.makedirs(out_dir, exist_ok=True)

    stamp = int(time.time())
    csv_path  = os.path.join(out_dir, f"stress_{stamp}.csv")
    json_path = os.path.join(out_dir, f"stress_{stamp}.json")
    pdf_path  = os.path.join(out_dir, f"stress_{stamp}.pdf")
    html_path = os.path.join(out_dir, f"stress_{stamp}.html")

    print("\n==============================")
    print("INICIANDO STRESS TEST FULLER")
    print("==============================")

    res = correr_stress_test(
        iteraciones=int(data.get("iteraciones", 500)),
        min_mezclas=int(data.get("min_mezclas", 2)),
        max_mezclas=int(data.get("max_mezclas", 7)),
        ruido_sigma=float(data.get("ruido_sigma", 6.0)),
        allow_missing_tamices=bool(data.get("allow_missing_tamices", True)),
        n_fijo=float(data.get("n_fijo", 0.5)),
        seed=data.get("seed", None),
        guardar_csv_path=csv_path,
        guardar_json_path=json_path,
    )

    print("\n===== RESULTADOS =====")
    print(f"Iteraciones: {res.iteraciones}")
    print(f"OK: {res.ok}")
    print(f"FAIL: {res.fail}")
    print(f"Fail rate: {res.fail_rate*100:.2f}%")
    print(f"Error promedio: {res.error_mean:.4f}")
    print(f"Error p95: {res.error_p95:.4f}")
    print(f"Error máximo: {res.error_max:.4f}")
    print(f"Duración: {res.duracion_s:.2f} segundos")

    if res.fails:
        print("\nCasos fallidos detectados:")
        for f in res.fails[:10]:
            print(f" - Seed {f.seed} → {f.motivo}")

    metrics = {
        "iteraciones": res.iteraciones,
        "ok": res.ok,
        "fail": res.fail,
        "fail_rate": res.fail_rate,
        "error_mean": res.error_mean,
        "error_p95": res.error_p95,
        "error_max": res.error_max,
        "error_min": res.error_min,
        "duracion_s": res.duracion_s,
    }

    decision = "GO ✅ (apto para producción)" \
        if (res.fail_rate <= 0.01 and res.error_p95 <= 25) \
        else "NO-GO ❌"

    payload = {
        "meta": {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "metrics": metrics,
        "fails": [{"seed": f.seed, "motivo": f.motivo} for f in res.fails],
        "go_no_go": {
            "decision": decision
        },
        "raw_errors": res.error_list,
    }

    # Generar HTML
    html = build_html_report(payload)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Generar PDF
    write_pdf_report(payload, pdf_path)

    print("\nArchivos generados:")
    print("CSV:", csv_path)
    print("JSON:", json_path)
    print("HTML:", html_path)
    print("PDF:", pdf_path)
    print("==============================\n")

    return jsonify({
        "mensaje": "Stress test completado",
        "decision": decision,
        "archivos": {
            "csv": csv_path,
            "json": json_path,
            "html": html_path,
            "pdf": pdf_path,
        }
    })