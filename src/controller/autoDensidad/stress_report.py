# controller/autoDensidad/stress_report.py

from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Any, List
import os
import time
import math
import json
import numpy as np
import matplotlib.pyplot as plt
import io
# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def _safe(v, default=""):
    return default if v is None else v

def _fmt(x, nd=3):
    try:
        if isinstance(x, (int, float)):
            if math.isnan(x) or math.isinf(x):
                return "NaN"
            return f"{x:.{nd}f}"
        return str(x)
    except Exception:
        return str(x)
def generar_histograma_errores(errors, output_path=None):
    if not errors:
        return None

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.hist(errors, bins=30, alpha=0.7)

    mean_val = np.mean(errors)
    p95 = np.percentile(errors, 95)
    max_val = np.max(errors)

    ax.axvline(mean_val, linestyle='--', linewidth=2, label=f"Mean: {mean_val:.2f}")
    ax.axvline(p95, linestyle='--', linewidth=2, label=f"P95: {p95:.2f}")
    ax.axvline(max_val, linestyle='--', linewidth=2, label=f"Max: {max_val:.2f}")

    ax.set_title("Distribución del Error Total")
    ax.set_xlabel("Error Total")
    ax.set_ylabel("Frecuencia")
    ax.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)

    buf.seek(0)
    return buf
def _percentiles_table(errors: List[float]) -> Dict[str, float]:
    if not errors:
        return {k: float("nan") for k in ["p50","p80","p90","p95","p99"]}
    arr = np.array(errors, dtype=float)
    return {
        "p50": float(np.percentile(arr, 50)),
        "p80": float(np.percentile(arr, 80)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }

def build_html_report(payload: Dict[str, Any]) -> str:
    """
    payload esperado:
      {
        "meta": {...},
        "metrics": {...},
        "distribution": {...},
        "fails": [{"seed":..,"motivo":..}, ...],
        "go_no_go": {"decision": "...", "reasons":[...]}
      }
    """
    meta = payload.get("meta", {})
    m = payload.get("metrics", {})
    dist = payload.get("distribution", {})
    fails = payload.get("fails", [])
    dec = payload.get("go_no_go", {})

    fail_rows = "\n".join(
        f"<tr><td>{_safe(f.get('seed'))}</td><td>{_safe(f.get('motivo'))}</td></tr>"
        for f in fails
    ) or "<tr><td colspan='2'>Sin fallos ✅</td></tr>"

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<title>Reporte Stress Test - Motor Fuller</title>
<style>
  body {{ font-family: Arial, Helvetica, sans-serif; margin: 24px; color: #111; }}
  h1 {{ margin: 0 0 6px 0; }}
  .sub {{ color: #444; margin-bottom: 18px; }}
  .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 14px; margin: 12px 0; }}
  .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }}
  th {{ background: #f5f5f5; }}
  .ok {{ color: #0a7; font-weight: 700; }}
  .bad {{ color: #d22; font-weight: 700; }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }}
</style>
</head>
<body>
  <h1>Reporte de Validación (Stress Test) – Motor Fuller</h1>
  <div class="sub">Generado: {meta.get("generated_at","")} · Base seed: <span class="mono">{meta.get("base_seed","")}</span></div>

    <div class="card">
    <h2>Decisión</h2>
    <div class="{ 'ok' if dec.get('decision','').startswith('GO') else 'bad' }">
      {dec.get("decision","")}
    </div>
    <ul>
      {''.join(f"<li>{r}</li>" for r in dec.get("reasons", [])) or "<li>(sin razones)</li>"}
    </ul>
    <div style="margin-top:10px; font-size:13px; color:#555;">
      {('<b>NO-GO:</b><br>Para avanzar, es fundamental realizar pruebas reales en planta y obtener datos granulométricos auténticos. Esto permitirá afinar el generador de curvas y validar el modelo en condiciones reales.' if dec.get('decision','').startswith('NO-GO') else '')}
      {('<b>GO:</b><br>El modelo ha sido validado con datos reales de planta y cumple los requisitos de precisión y plausibilidad física.' if dec.get('decision','').startswith('GO') else '')}
    </div>
  </div>

  <div class="card">
    <h2>Métricas principales</h2>
    <div class="grid">
      <div><b>Iteraciones</b>: {_fmt(m.get("iteraciones"),0)}</div>
      <div><b>Duración (s)</b>: {_fmt(m.get("duracion_s"))}</div>
      <div><b>OK</b>: {_fmt(m.get("ok"),0)}</div>
      <div><b>FAIL</b>: {_fmt(m.get("fail"),0)}</div>
      <div><b>Fail rate</b>: {_fmt(m.get("fail_rate")*100 if m.get("fail_rate") is not None else None)}%</div>
      <div><b>Error mean</b>: {_fmt(m.get("error_mean"))}</div>
      <div><b>Error p95</b>: {_fmt(m.get("error_p95"))}</div>
      <div><b>Error max</b>: {_fmt(m.get("error_max"))}</div>
    </div>
  </div>

  <div class="card">
    <h2>Distribución</h2>
    <div class="grid">
      <div><b>p50</b>: {_fmt(dist.get("p50"))}</div>
      <div><b>p80</b>: {_fmt(dist.get("p80"))}</div>
      <div><b>p90</b>: {_fmt(dist.get("p90"))}</div>
      <div><b>p95</b>: {_fmt(dist.get("p95"))}</div>
      <div><b>p99</b>: {_fmt(dist.get("p99"))}</div>
    </div>
  </div>

  <div class="card">
    <h2>Fallos (reproducibles por seed)</h2>
    <p class="sub">Usá la seed para reproducir exactamente el caso y debugear.</p>
    <table>
      <thead><tr><th>Seed</th><th>Motivo</th></tr></thead>
      <tbody>
        {fail_rows}
      </tbody>
    </table>
  </div>

</body>
</html>"""
    return html


def write_pdf_report(payload: Dict[str, Any], pdf_path: str) -> str:
    """
    Genera PDF simple y limpio con ReportLab.
    """
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    meta = payload.get("meta", {})
    m = payload.get("metrics", {})
    dist = payload.get("distribution", {})
    fails = payload.get("fails", [])
    dec = payload.get("go_no_go", {})

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 2.0*cm

    def line(txt, size=11, dy=0.7*cm, bold=False):
        nonlocal y
        if y < 2.0*cm:
            c.showPage()
            y = height - 2.0*cm
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(2.0*cm, y, txt)
        y -= dy

    line("Reporte de Validación (Stress Test) – Motor Fuller", size=16, dy=1.0*cm, bold=True)
    line(f"Generado: {meta.get('generated_at','')}", size=10)
    line(f"Base seed: {meta.get('base_seed','')}", size=10)

    line("Decisión:", bold=True)
    line(dec.get("decision",""), bold=True)
    for r in dec.get("reasons", [])[:10]:
      line(f"- {r}", size=10, dy=0.55*cm)
    # Aclaración adicional según el estado
    if dec.get("decision","").startswith("NO-GO"):
      # Línea en negrita y salto de línea para aclaración
      c.setFont("Helvetica-Bold", 9)
      if y < 2.7*cm:
        c.showPage()
        y = height - 2.0*cm
      c.drawString(2.0*cm, y, "NO-GO:")
      y -= 0.5*cm
      c.setFont("Helvetica", 9)
      for txt in [
        "Para avanzar, es fundamental realizar pruebas reales en planta y obtener datos granulométricos auténticos.",
        "Esto permitirá afinar el generador de curvas y validar el modelo en condiciones reales."
      ]:
        if y < 2.2*cm:
          c.showPage()
          y = height - 2.0*cm
        c.drawString(2.0*cm, y, txt)
        y -= 0.5*cm
    elif dec.get("decision","").startswith("GO"):
      c.setFont("Helvetica-Bold", 9)
      if y < 2.7*cm:
        c.showPage()
        y = height - 2.0*cm
      c.drawString(2.0*cm, y, "GO:")
      y -= 0.5*cm
      c.setFont("Helvetica", 9)
      txt = "El modelo ha sido validado con datos reales de planta y cumple los requisitos de precisión y plausibilidad física."
      c.drawString(2.0*cm, y, txt)
      y -= 0.5*cm

    line("Métricas principales:", bold=True)
    line(f"Iteraciones: {_fmt(m.get('iteraciones'),0)}", size=10)
    line(f"Duración (s): {_fmt(m.get('duracion_s'))}", size=10)
    line(f"OK: {_fmt(m.get('ok'),0)}  |  FAIL: {_fmt(m.get('fail'),0)}  |  Fail rate: {_fmt((m.get('fail_rate') or 0)*100)}%", size=10)
    line(f"Error mean: {_fmt(m.get('error_mean'))}  |  p95: {_fmt(m.get('error_p95'))}  |  max: {_fmt(m.get('error_max'))}  |  min: {_fmt(m.get('error_min'))}", size=10)

    line("Distribución (percentiles):", bold=True)
    line(f"p50={_fmt(dist.get('p50'))}  p80={_fmt(dist.get('p80'))}  p90={_fmt(dist.get('p90'))}  p95={_fmt(dist.get('p95'))}  p99={_fmt(dist.get('p99'))}", size=10)

    line("Fallos (seed → motivo):", bold=True)
    if not fails:
        line("Sin fallos ✅", size=10)
    else:
        for f in fails[:25]:
            line(f"{f.get('seed')} → {f.get('motivo')}", size=9, dy=0.5*cm)
    # === HISTOGRAMA ===
    errors = payload.get("raw_errors", [])
    img_buf = generar_histograma_errores(errors)

    if img_buf:
      # Reservar espacio para el título y la imagen
      img_height = 7*cm
      img_width = 16*cm
      min_y_for_img = 2*cm + img_height + 1*cm  # 1cm extra para el título
      if y < min_y_for_img:
        c.showPage()
        y = height - 2*cm

      line("Histograma de errores:", bold=True, dy=0.8*cm)

      img_buf.seek(0)  # MUY IMPORTANTE
      img = ImageReader(img_buf)

      # Ajustar la posición Y para que la imagen no se salga de la página
      img_y = max(y - img_height, 2*cm)
      c.drawImage(
        img,
        2*cm,
        img_y,
        width=img_width,
        height=img_height
      )
      y = img_y - 1*cm  # Dejar margen debajo de la imagen

    c.save()
    return pdf_path