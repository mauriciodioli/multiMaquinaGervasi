from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from typing import Optional, Dict, Any, List
import re

from src.utils.db_session import get_db_session
from src.model.mixFamiliari.analisis_granulometrico import AnalisisGranulometrico
from src.model.mixFamiliari.resultado_tamiz import ResultadoTamiz
from src.model.mixFamiliari.proporcionOptima import ProporcionOptima
from src.model.mixFamiliari.diagnosticoAnalisis import DiagnosticoAnalisis
from src.model.mixFamiliari.recomendacionMejora import RecomendacionMejora
from src.model.mixFamiliari.pesoZonaMezcla import PesoZonaMezcla

analisisGranulometrico = Blueprint('analisisGranulometrico', __name__)

# ---------- Helpers ----------
_num_re = re.compile(r'-?\d+(?:\.\d+)?')




_tamiz_text_re = re.compile(r'Tamiz\s+([0-9]+(?:\.[0-9]+)?)\s*mm', re.IGNORECASE)
_html_tag_re   = re.compile(r'<[^>]+>')

def _strip_tags(html: str) -> str:
    return _html_tag_re.sub('', html or '').strip()

def _fit_sugerencia_for_column(sug_html: str, sug_text: str, max_len: int = 500) -> str:
    """
    Intenta guardar el HTML tal cual. Si excede el límite de la columna (500),
    guarda texto plano truncado para no romper el INSERT.
    """
    if sug_html and len(sug_html) <= max_len:
        return sug_html
    # fallback: texto plano (truncado si hace falta)
    plain = _strip_tags(sug_html) or (sug_text or '')
    return (plain[:max_len - 1] + '…') if len(plain) > max_len else plain





def _to_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Acepta float/int/str/np.float64('...') y strings con coma.
    Devuelve float o default.
    """
    try:
        if v is None or v == "":
            return default
        s = str(v).replace(",", ".")
        m = _num_re.search(s)
        return float(m.group(0)) if m else default
    except Exception:
        return default

def _build_dif_map(tabla: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    """
    Mapa 'tamiz(mm as str)' -> diferencia(float) para usar en recomendaciones.
    """
    out = {}
    for r in tabla or []:
        t = str(r.get("tamiz"))
        out[t] = _to_float(r.get("diferencia"))
    return out

# ---------- Altas por modelo ----------
def create_analisis_granulometrico(session, agregado_id: int, usuario_id: int,
                                   descripcion: Optional[str],
                                   d_max: Optional[float],
                                   n: Optional[float]) -> AnalisisGranulometrico:
    analisis = AnalisisGranulometrico(
        fecha       = datetime.utcnow(),
        descripcion = descripcion,
        d_max       = d_max,
        n           = n,
        agregado_id = int(agregado_id),
        usuario_id  = int(usuario_id),
    )
    session.add(analisis)
    session.flush()  # obtener analisis.id
    return analisis

def create_resultados_tamiz(session, analisis_id: int,
                            tabla: List[Dict[str, Any]],
                            curva: Dict[str, List[Any]]) -> int:
    """
    Preferimos 'tabla' (trae zona/d_max/n). Si no hay, caemos a 'curva'.
    """
    inserted = 0
    if tabla:
        for r in tabla:
            session.add(ResultadoTamiz(
                analisis_id = analisis_id,
                tamiz       = str(r.get("tamiz")),
                porcentaje  = _to_float(r.get("resultante")),
                ideal       = _to_float(r.get("ideal")),
                diferencia  = _to_float(r.get("diferencia")),
                retenido    = _to_float(r.get("retenido")),
                acumulado   = _to_float(r.get("acumulado")),
                pasante     = _to_float(r.get("pasante")),
                zona        = (r.get("zona") or None),
            ))
            inserted += 1
        return inserted

    # fallback desde curva
    tamices = (curva.get("tamices") or [])
    res     = (curva.get("resultante") or [])
    ideal   = (curva.get("ideal") or [])
    difs    = (curva.get("diferencias") or [])
    for i, t in enumerate(tamices):
        session.add(ResultadoTamiz(
            analisis_id = analisis_id,
            tamiz       = str(t),
            porcentaje  = _to_float(res[i] if i < len(res) else None),
            ideal       = _to_float(ideal[i] if i < len(ideal) else None),
            diferencia  = _to_float(difs[i] if i < len(difs) else None),
        ))
        inserted += 1
    return inserted

def create_proporciones_optimas(session, analisis_id: int,
                                nombres: List[Any],
                                porcentajes: List[Any]) -> int:
    inserted = 0
    for nom, pct in zip(nombres or [], porcentajes or []):
        session.add(ProporcionOptima(
            analisis_id   = analisis_id,
            nombre_mezcla = str(nom),
            porcentaje    = _to_float(pct, 0.0)
        ))
        inserted += 1
    return inserted

def create_diagnostico_analisis(session, analisis_id: int,
                                evaluacion: Optional[str],
                                error_promedio: Optional[Any],
                                mensaje_html: Optional[str]) -> DiagnosticoAnalisis:
    diag = DiagnosticoAnalisis(
        analisis_id    = analisis_id,
        error_promedio = _to_float(error_promedio, 0.0),
        evalucion      = (evaluacion or None),   # campo en modelo es 'evalucion'
        mensaje        = (mensaje_html or None)
    )
    session.add(diag)
    return diag

_tamiz_text_re = re.compile(r'Tamiz\s+([0-9]+(?:\.[0-9]+)?)\s*mm', re.IGNORECASE)

def create_recomendaciones_desde_dom(
    session,
    analisis_id: int,
    recomendaciones_texto: List[str],
    dif_por_tamiz: Dict[str, Optional[float]],
    recomendaciones_html: Optional[List[str]] = None
) -> int:
    """
    Guarda RecomendacionMejora usando el HTML del DOM en 'sugerencia'.
    - Extrae 'tamiz' del texto (o del HTML limpiado) con regex.
    - 'valor' (Δ) lo toma del mapa 'dif_por_tamiz' si existe.
    - 'sugerencia' prioriza el HTML; si excede 500 chars, cae a texto plano truncado.
    """
    inserted = 0
    recomendaciones_html = recomendaciones_html or []

    for idx, s_text in enumerate(recomendaciones_texto or []):
        s_text = (s_text or '').strip()
        s_html = (recomendaciones_html[idx] if idx < len(recomendaciones_html) else '') or ''

        # Determinar tamiz desde texto (o desde html sin etiquetas)
        base_for_regex = s_text or _strip_tags(s_html)
        m = _tamiz_text_re.search(base_for_regex)
        if m:
            tval = m.group(1)  # '9.5'
            dif  = dif_por_tamiz.get(tval)
            sugerencia_final = _fit_sugerencia_for_column(s_html, s_text, max_len=500)

            session.add(RecomendacionMejora(
                analisis_id = analisis_id,
                tamiz       = tval,
                valor       = _to_float(dif, 0.0),
                sugerencia  = sugerencia_final
            ))
        else:
            sugerencia_final = _fit_sugerencia_for_column(s_html, s_text, max_len=500)
            session.add(RecomendacionMejora(
                analisis_id = analisis_id,
                tamiz       = "general",
                valor       = 0.0,
                sugerencia  = sugerencia_final
            ))
        inserted += 1

    return inserted

def create_pesos_zona(session, analisis_id: int,
                      zonas: List[Dict[str, Any]]) -> int:
    """
    Espera lista de dicts: {nombre_mezcla, zona, porcentaje}
    """
    inserted = 0
    for z in (zonas or []):
        session.add(PesoZonaMezcla(
            analisis_id   = analisis_id,
            nombre_mezcla = z.get("nombre_mezcla"),
            zona          = (z.get("zona") or "N/A"),
            porcentaje    = _to_float(z.get("porcentaje"), 0.0)
        ))
        inserted += 1
    return inserted

# ---------- Endpoint que usa las funciones ----------
@analisisGranulometrico.route(
    "/autoDensidad_analisisGranulometrico_guardar_analisis_granulometrico_db/",
    methods=["POST"]
)
def autoDensidad_analisis_granulometrico_guardar():
    try:
        p = request.get_json(silent=True) or {}

        agregado_id = p.get("agregado_id")
        usuario_id  = p.get("usuario_id")
        if not agregado_id or not usuario_id:
            return jsonify({"ok": False, "error": "agregado_id y usuario_id son obligatorios"}), 400

        descripcion = p.get("descripcion")
        d_max = _to_float(p.get("d_max"))
        n     = _to_float(p.get("n"))

        curva   = p.get("curva", {})
        resumen = p.get("resumen", {})
        mezcla  = p.get("mezcla", {})
        tabla   = p.get("tabla_dom", [])
        recs    = p.get("recomendaciones_dom", [])
        zonas   = p.get("pesos_zona", [])   # opcional
      
        # Si no vino d_max/n, intenta inferir de la primera fila de la tabla
        if d_max is None and tabla:
            d_max = _to_float(tabla[0].get("d_max"))
        if n is None and tabla:
            n = _to_float(tabla[0].get("n"))

        dif_por_tamiz = _build_dif_map(tabla)

        with get_db_session() as session:
            # 1) Alta Análisis
            analisis = create_analisis_granulometrico(
                session,
                agregado_id=int(agregado_id),
                usuario_id=int(usuario_id),
                descripcion=descripcion,
                d_max=d_max,
                n=n
            )
            analisis_id = analisis.id  # ← tomalo mientras la sesión sigue viva

            # 2) Resultados Tamiz
            create_resultados_tamiz(session, analisis_id, tabla, curva)

            # 3) Proporciones óptimas
            nombres = mezcla.get("nombres") or []
            props   = mezcla.get("proporciones_pct") or []
            create_proporciones_optimas(session, analisis_id, nombres, props)

            # 4) Diagnóstico
            create_diagnostico_analisis(
                session,
                analisis_id,
                evaluacion=resumen.get("evaluacion"),
                error_promedio=resumen.get("error_promedio"),
                mensaje_html='html.get("diagnostico")'
            )

            # 5) Recomendaciones
            # Construí el mapa de deltas (si tenés tabla_dom, mejor)
            dif_por_tamiz = _build_dif_map(tabla)  # tabla ya tiene diferencia

            # Lee lo que envía el front
            recs_text = p.get("recomendaciones_dom", [])           # lista de strings (texto)
            recs_html = p.get("recomendaciones_dom_html", [])      # lista de strings (HTML)

            create_recomendaciones_desde_dom(
                session,
                analisis_id,
                recomendaciones_texto=recs_text,
                dif_por_tamiz=dif_por_tamiz,
                recomendaciones_html=recs
            )


            # 6) Pesos por zona (opcional)
            create_pesos_zona(session, analisis_id, zonas)

        # commit lo hace get_db_session()
        return jsonify({"ok": True, "id": analisis_id}), 200

    except Exception as e:
        current_app.logger.exception("Error guardando análisis granulométrico")
        return jsonify({"ok": False, "error": str(e)}), 500
