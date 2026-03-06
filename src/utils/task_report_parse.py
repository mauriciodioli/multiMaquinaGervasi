import re
from datetime import datetime


def parse_dt(v):
    """
    Convierte valores típicos de Excel a datetime.
    Acepta:
      - datetime (ya convertido por pandas/openpyxl)
      - string "YYYY-MM-DD HH:MM:SS"
      - string "YYYY/MM/DD HH:MM:SS" (por si acaso)
    Devuelve None si no se puede parsear.
    """
    if v is None or v == "":
        return None

    if isinstance(v, datetime):
        return v

    s = str(v).strip()
    if not s:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    # Si viene sin segundos: "YYYY-MM-DD HH:MM"
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    return None


def parse_duration_to_seconds(v):
    """
    Convierte el formato típico del reporte a segundos.

    Ejemplos:
      "7.0s" -> 7
      "31.0s" -> 31
      "2min 12.0s" -> 132
      "26min 37.0s" -> 1597
      "0s" / "" / None -> None
    """
    if v is None or v == "":
        return None

    s = str(v).strip().lower()
    if not s or s in ("0", "0s", "0.0s"):
        return None

    mins = 0.0
    secs = 0.0

    m = re.search(r"(\d+(?:\.\d+)?)\s*min", s)
    if m:
        mins = float(m.group(1))

    m = re.search(r"(\d+(?:\.\d+)?)\s*s", s)
    if m:
        secs = float(m.group(1))

    total = mins * 60.0 + secs
    return total if total > 0 else None


def parse_size_xy(v):
    """
    Parsea tamaños tipo:
      "904X570"
      "904×570"
      " 904 X 570 "
    Devuelve: (raw, x, y)
      raw: string original normalizada (o original si no matchea)
      x,y: ints o None
    """
    if v is None or v == "":
        return (None, None, None)

    s = str(v).strip()
    if not s:
        return (None, None, None)

    raw = s.strip().upper().replace("×", "X")
    m = re.match(r"^\s*(\d+)\s*X\s*(\d+)\s*$", raw)
    if not m:
        # guardamos raw pero sin x/y
        return (raw, None, None)

    return (raw, int(m.group(1)), int(m.group(2)))


def to_int(v):
    """
    Convierte a int desde:
      - int/float
      - string numérica
    Devuelve None si está vacío o no parsea.
    """
    try:
        if v is None or v == "":
            return None
        # Excel a veces trae 1.0 como float
        return int(float(v))
    except Exception:
        return None


def to_float(v):
    """
    Convierte a float desde:
      - int/float
      - string numérica
    Devuelve None si está vacío o no parsea.
    """
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def parse_hypcut_rtf_log(text):
    """Extrae datos básicos de cortes desde un log HypCut en formato RTF.

    Busca patrones del tipo:
      - "(03/05 14:38:48)...Start"
      - "Cutting length: 5466,00 mm, ... pierce count: 2 times"
      - "Tempo trascorso: 19,39s"

    Devuelve una lista de dicts con:
      - start: string "MM/DD HH:MM:SS" (según log)
      - time_consumed_s: float (segundos)
      - cutting_length_mm: float
      - perforation: int (pierce count)
    """

    # timestamps de inicio de corte
    starts = re.findall(r"\((\d{2}/\d{2} \d{2}:\d{2}:\d{2})\)[^\n]*Start", text)

    # tiempos reales de corte (Tempo trascorso: 19,39s)
    times = re.findall(r"Tempo trascorso:\s*([0-9,]+)s", text)

    # longitud de corte (Cutting length: 5466,00 mm, ...)
    lengths = re.findall(r"Cutting length:\s*([0-9,]+)", text)

    # número de perforaciones (pierce count: 2 times)
    pierces = re.findall(r"pierce count:\s*(\d+)", text)

    jobs = []
    n = min(len(starts), len(times), len(lengths), len(pierces))

    for i in range(n):
        try:
            duration_s = float(times[i].replace(",", "."))
        except Exception:
            duration_s = None

        try:
            cutting_len_mm = float(lengths[i].replace(",", "."))
        except Exception:
            cutting_len_mm = None

        try:
            pierce_count = int(pierces[i])
        except Exception:
            pierce_count = None

        jobs.append(
            {
                "start": starts[i],
                "time_consumed_s": duration_s,
                "cutting_length_mm": cutting_len_mm,
                "perforation": pierce_count,
            }
        )

    return jobs


def summarize_hypcut_rtf_log(text):
    """Devuelve (parts, total_time_s) a partir de un log HypCut RTF.

    parts = número de cortes detectados
    total_time_s = suma de "Tempo trascorso" en segundos
    """

    jobs = parse_hypcut_rtf_log(text)
    parts = len(jobs)
    total_time = sum(j["time_consumed_s"] or 0.0 for j in jobs)
    return parts, total_time
