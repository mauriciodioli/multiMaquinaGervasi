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
