#!/usr/bin/env python3
import time
import struct
import math
from pymodbus.client import ModbusTcpClient
from math import sqrt
import socket
from pymodbus.exceptions import ModbusIOException, ConnectionException
# ===== CONFIG =====
IPS = [
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103",  # Fronius Primo GEN24 4.6
    "192.168.1.106",  # Fronius
    "192.168.1.109",
    "192.168.1.110",
    "192.168.1.111",
    "192.168.1.112",
    # añadir más IPs si hace falta
]
# IPs de inversores Fronius (SunSpec float, modelos 111/113 — unit ID=1)
# Se leen directamente con read_ip_fronius sin probar modelo 101 primero.
FRONIUS_IPS = {
    "192.168.1.103",  # Fronius Primo GEN24 4.6
    "192.168.1.106",  # Fronius
}
PORT = 502
UNIT_ID = 126
BASE_ADDR = 40001  # SunSpec 1-based
INTERVAL = 5  # segundos entre ciclos
DEBUG_MODBUS = False  # True para imprimir detalles de lectura por IP

# === OFFSETS CONFIRMADOS PARA SMA (model 101) ===
OFF_V = 8
OFF_VSF = 9
OFF_HZ = 14
OFF_HZSF = 15
OFF_W = 12
OFF_WSF = 13
# ==================================================

def is_na_signed16(v):  return v == -32768         # SunSpec NA (int16)
def is_na_unsigned16(v): return v == 0xFFFF        # SunSpec NA (uint16)
def is_na_signed32(v):  return v == -2147483648
def is_na_unsigned32(v): return v == 0xFFFFFFFF

def safe_scale(raw, sf):
    if raw is None or sf is None: return None
    return raw * (10 ** sf)

def find_voltage_in_regs_heur_v2(regs, window=16):
    """
    Busca V plausible en un payload SunSpec.
    Acepta 180–270 V (L-N) o 380–420 V (L-L). Devuelve (V, idx_raw, idx_sf) o (None, None, None).
    """
    if not regs:
        return None, None, None

    def plausible(v):
        return (180.0 <= v <= 270.0) or (380.0 <= v <= 420.0)

    # índices candidatos a SF
    sf_idxs = [(j, regs[j]) for j, w in enumerate(regs) if -3 <= s16(w) <= 1]
    for j, sf in sf_idxs:
        start = max(0, j - window)
        end   = min(len(regs)-1, j + window)
        for i in range(start, end):
            raw = regs[i]
            if raw in (0x8000, 0x7FFF):
                continue
            try:
                v = sunssf(raw, sf)
            except Exception:
                v = None
            if isinstance(v, (int, float)) and plausible(v):
                return round(v, 2), i, j
    return None, None, None
def fill_voltage_generic_if_missing(result, client, unit):
    """
    Completa el voltaje 'V_AC' de forma genérica:
    1) Si el 101 no lo trae, intenta 103/111/113 (live).
    2) Si no hay live, cae a nominal desde 120 (L-L) y deriva L-N.
    No lanza excepciones ni rompe tu flujo.
    """
    try:
        # Si ya tenés V en vivo, nada que hacer
        if result.get("V_AC") != "—":
            return

        # 1) Modelos que suelen contener V en vivo
        for mid in (103, 111, 113):
            regs = read_model_regs(client, unit, mid)
            v, i_raw, i_sf = find_voltage_in_regs_heur_v2(regs, window=16)
            if v is not None:
                # Si es L-L (alto), derivamos L-N; si ya parece L-N, lo usamos directo
                if v > 300.0:
                    result["V_AC"] = round(v / sqrt(3), 1)  # ≈ L-N
                    result["V_from"] = f"MID {mid} (L-L→L-N)"
                else:
                    result["V_AC"] = v
                    result["V_from"] = f"MID {mid}"
                return

        # 2) Nominal desde 120 (L-L) si no hay V en vivo
        regs120 = read_model_regs(client, unit, 120)
        v_ll, i_raw, i_sf = find_voltage_in_regs_heur_v2(regs120, window=16)
        if v_ll is not None and v_ll > 300.0:
            result["V_nominal_LL_V"] = round(v_ll, 1)
            result["V_nominal_LN_V"] = round(v_ll / sqrt(3), 1)
            # No forzamos V_AC (seguirá "—"); sólo contexto nominal
            if not result.get("status_text"):
                result["status_text"] = "Ok (sin V en vivo; nominal L-L disponible)"
            result["V_from"] = "MID 120 (nominal)"
    except Exception:
        # silencioso por diseño
        pass
def read_model_regs(client, unit, target_mid):
    """
    Lee el payload (LEN words) del modelo SunSpec `target_mid` para `unit`.
    Devuelve lista de registros (ints) o None si no está/no responde.
    """
    base = (BASE_ADDR + 2) - 1  # 40003 en 0-based
    addr0 = base
    for _ in range(80):  # límite de seguridad
        hdr = read_u16s(client, unit, addr0, 2)  # [ID, LEN]
        if not hdr:
            return None
        mid, mlen = hdr
        if mid == 0xFFFF:  # fin de tabla SunSpec
            return None
        if mid == target_mid:
            return read_u16s(client, unit, addr0 + 2, mlen) or []
        addr0 = addr0 + 2 + mlen  # saltar al próximo modelo
    return None



def find_voltage_in_regs_heur_v2(regs, window=12):
    """
    Busca un V plausible en un payload SunSpec (ej. modelo 103/otros).
    El SF puede estar lejos del valor; probamos una ventana alrededor.
    Acepta 180–270 V (monofásico) o 380–420 V (trifásico L-L).
    Retorna (valor_V, idx_raw, idx_sf) o (None, None, None).
    """
    if not regs:
        return None, None, None

    # índices candidatos a SF
    sf_idxs = []
    for j, w in enumerate(regs):
        sf = s16(w)
        if -3 <= sf <= 1:
            sf_idxs.append((j, w))

    def plausible(v):
        return (180.0 <= v <= 270.0) or (380.0 <= v <= 420.0)

    for j, sf in sf_idxs:
        start = max(0, j - window)
        end   = min(len(regs)-1, j + window)
        for i in range(start, end):
            raw = regs[i]
            if raw in (0x8000, 0x7FFF):
                continue
            try:
                v = sunssf(raw, sf)
            except Exception:
                v = None
            if isinstance(v, (int, float)) and plausible(v):
                return round(v, 2), i, j
    return None, None, None

def scan_all_models_for_voltage(client, unit, window=12):
    """
    Recorre todos los modelos SunSpec y loguea si encuentra un V plausible.
    SOLO PRINTS. No modifica tu flujo.
    """
    base = (BASE_ADDR + 2) - 1  # 40003 (0-based)
    addr0 = base
    seen = 0
    while seen < 120:
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr:
            print(f"unit {unit}: sin header en {addr0}")
            break
        mid, mlen = hdr
        if mid == 0xFFFF:
            print(f"unit {unit}: fin de tabla en {addr0}")
            break

        regs = read_u16s(client, unit, addr0 + 2, mlen) or []
        print(f"unit {unit}: MID {mid} mlen={mlen} len={len(regs)} head={regs[:12]}")

        v, i_raw, i_sf = find_voltage_in_regs_heur_v2(regs, window=window)
        if v is not None:
            print(f"  ↳ V candidato en MID {mid}: {v} V (raw_idx={i_raw}, sf_idx={i_sf})")

        addr0 = addr0 + 2 + mlen
        seen += 1



def s16(x):
    return x - 0x10000 if x & 0x8000 else x
def derive_ok_from_metrics(ac_dict, code, status_text):
    """
    Si no tenemos mapeo de estado pero las métricas están sanas,
    devolvemos 'Ok ()'. Mantiene el texto original si ya es conocido.
    """
    if status_text and ("operando" in status_text or "marcha" in status_text or "standby" in status_text or "falla" in status_text):
        return status_text  # ya tenemos algo útil

    V = ac_dict.get("V_AC")
    Hz = ac_dict.get("freq_Hz")
    W = ac_dict.get("P_AC_W")

    # normalizamos tipos (por si vienen como "—")
    V_ok  = (isinstance(V, (int, float))  and 180 <= V <= 260)
    Hz_ok = (isinstance(Hz, (int, float)) and 49.0 <= Hz <= 51.0)
    W_ok  = (isinstance(W, (int, float))  and W >= 0)

    # si el código cae en 200..299, asumimos fallo — pero preservamos el texto mapeado
    if isinstance(code, int) and 200 <= code < 300:
        return status_text if status_text else f"fail (code {code})"

    # si potencia > 0 y V/Hz razonables → Ok
    if W_ok and W > 0 and (V_ok or V == "—") and Hz_ok:
        return "Ok (heurstic)"

    # si potencia 0 pero V/Hz ok → standby
    if W_ok and W == 0 and (V_ok or V == "—") and Hz_ok:
        return "standby (heurstic)"

    # si no hay nada mejor, dejamos lo que había
    return status_text or "sin datos"

def decode_status_guess(models):
    # 1) Buscar primero en modelos "de estado" y dejar 101 para el final
    order = [160, 103] + [m for m in models.keys() if m not in (101, 103, 160)] + ([101] if 101 in models else [])

    # índices del 101 que NO deben considerarse como estado (mediciones y SF confirmados)
    skip_idx_101 = {OFF_V, OFF_VSF, OFF_HZ, OFF_HZSF, OFF_W, OFF_WSF}

    for mid in order:
        regs = models.get(mid)
        if not regs:
            continue
        for idx, v in enumerate(regs):
            # 2) si es el 101, salteá campos conocidos que no son estado
            if mid == 101 and idx in skip_idx_101:
                continue

            if 100 <= v <= 600:
                code = v
                mapping = {
                    303: "operando / inyección",
                    307: "marcha normal",
                    455: "standby",
                    400: "operando",
                    101: "starting",
                    102: "off",
                    104: "esperando",
                    201: "fail",
                    202: "Out of range",
                    203: "delay inverter",
                    207: "DC voltage too low",
                    209: "DC overvoltage",
                    210: "DC overcurrent",
                    211: "Ground fault",
                    212: "Insulation fault",
                    213: "DC string reverse polarity",
                    214: "Temperature too high",
                    216: "AC overcurrent",
                    217: "DC injection into grid",
                    218: "RCMU fault",
                    219: "Islanding detected",
                    221: "Grid voltage too high (phase)",
                    223: "Grid voltage too high",
                    224: "Grid voltage too low",
                    227: "Grid voltage phase imbalance",
                    229: "Power stage fault",
                    230: "Fan / cooling fault",
                    233: "Hardware failure",
                    241: "Grid frequency out of range",
                    205: "communication failure",
                    
                }
                if code in mapping:
                    return f"{mapping[code]} (code {code})", code, mid, idx
                if 200 <= code < 300:
                    return f"communication failure (code {code})", code, mid, idx
                if 300 <= code < 400:
                    return f"operando (code {code})", code, mid, idx
                if 400 <= code < 500:
                    return f"standby/operación (code {code})", code, mid, idx
                if 500 <= code < 600:
                    return f"fail (code {code})", code, mid, idx
                return f"unknown status ({code})", code, mid, idx

    return "no data", None, None, None

def sunssf(raw, sf):
    """Escala SunSpec con manejo correcto de NA y SF defectuosos."""
    if raw is None or sf is None:
        return None

    # 1) El valor bruto puede venir como uint16 NA (0xFFFF).
    # El scale factor 0xFFFF equivale a -1 y es valido en SunSpec.
    if raw == 0xFFFF:
        return None

    # 2) Convertir a int16
    def to_s16(u):
        return u - 0x10000 if isinstance(u, int) and u >= 0x8000 else u

    raw_s16 = to_s16(raw)
    sf_s16  = to_s16(sf)

    # 3) NA como int16 estándar SunSpec
    if raw_s16 == -32768 or sf_s16 == -32768:
        return None

    # 4) Sanity check: SF fuera de rango razonable => descartar
    # (en SunSpec típico está entre -3 y +3; seamos generosos)
    if sf_s16 < -10 or sf_s16 > 10:
        return None

    try:
        return raw_s16 * (10 ** sf_s16)
    except Exception:
        return None


def read_u16s(client, unit, addr0, count):
    r = client.read_holding_registers(addr0, count, slave=unit)
    return None if r.isError() else r.registers

def regs_to_str(regs):
    s = []
    for reg in regs:
        hi = (reg >> 8) & 0xFF
        lo = reg & 0xFF
        if hi == 0:
            break
        s.append(chr(hi))
        if lo == 0:
            break
        s.append(chr(lo))
    return "".join(s)

def read_common(client, unit=UNIT_ID):
    hdr_addr0 = (BASE_ADDR + 2) - 1  # 40003 (0-based)
    hdr = read_u16s(client, unit, hdr_addr0, 2)
    if not hdr:
        return None
    mid, mlen = hdr
    regs = read_u16s(client, unit, hdr_addr0 + 2, mlen)
    if not regs:
        return None
    mn = regs_to_str(regs[0:16])
    md = regs_to_str(regs[16:32])
    sn = regs_to_str(regs[48:66])
    return {"manufacturer": mn, "model": md, "serial": sn, "first_model_id": mid}


def diagnose_ip(ip, port=PORT):
    """
    Diagnóstico completo para encontrar el unit ID y configuración Modbus
    correcta de un inversor. Imprime resultados detallados.
    Útil cuando un dispositivo conecta pero no devuelve datos.
    """
    UNIT_CANDIDATES = list(range(1, 11)) + [126, 3]
    BASE_CANDIDATES = [
        (BASE_ADDR + 2) - 1,  # SunSpec estándar 40003 (0-based)
        1,                    # offset 0 (algunos SMA)
        (40000 + 2) - 1,      # 40002 (0-based)
    ]
    print(f"\n{'='*55}")
    print(f" DIAGNÓSTICO MODBUS: {ip}:{port}")
    print(f"{'='*55}")

    try:
        with ModbusTcpClient(ip, port, timeout=2.0, retries=1) as client:
            if not client.connect():
                print(f" ❌ Sin conexión TCP")
                return
            print(f" ✅ TCP conectado")

            for unit in UNIT_CANDIDATES:
                for addr in BASE_CANDIDATES:
                    # FC03 holding registers
                    r = client.read_holding_registers(addr, 2, slave=unit)
                    if not r.isError():
                        regs = r.registers
                        print(f" ✅ FC03 unit={unit} addr={addr} → {regs}")
                        continue
                    # FC04 input registers
                    r2 = client.read_input_registers(addr, 2, slave=unit)
                    if not r2.isError():
                        regs = r2.registers
                        print(f" ✅ FC04 unit={unit} addr={addr} → {regs}  ← USA INPUT REGISTERS")

    except Exception as e:
        print(f" ⚠️ Error: {e}")
    print(f"{'='*55}\n")

def find_model_header(client, target_mid, unit=UNIT_ID):
    """Busca el header de target_mid; devuelve (addr0, mlen) o (None, None)."""
    addr0 = (BASE_ADDR + 2) - 1
    for _ in range(80):  # límite de seguridad
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr:
            return None, None
        mid, mlen = hdr
        if mid == 0xFFFF:
            return None, None
        if mid == target_mid:
            return addr0, mlen
        addr0 = addr0 + 2 + mlen
    return None, None

def read_first_model_payload(client, unit=UNIT_ID):
    """Lee el primer header (el que sea) y devuelve (mid, regs) o (None, None)."""
    addr0 = (BASE_ADDR + 2) - 1
    hdr = read_u16s(client, unit, addr0, 2)
    if not hdr:
        return None, None
    mid, mlen = hdr
    regs = read_u16s(client, unit, addr0 + 2, mlen)
    if not regs:
        return None, None
    return mid, regs

def decode_ac_from_101(regs):
    """Intenta decodificar V, Hz y W usando offsets fijos SMA.
       Si no puede decodificar una magnitud, la deja como "—".
       Devuelve dict o None si todo es ininterpretable.
    """
    try:
        max_needed = max(OFF_V, OFF_VSF, OFF_HZ, OFF_HZSF, OFF_W, OFF_WSF, 10, 11)
        if len(regs) <= max_needed + 1:
            return None

        def _decode_metric(raw_idx, sf_idx):
            return sunssf(regs[raw_idx], regs[sf_idx])

        def _plausible_voltage(value):
            return isinstance(value, (int, float)) and (180.0 <= value <= 270.0 or 380.0 <= value <= 420.0)

        V = None
        for raw_idx, sf_idx in ((OFF_V, OFF_VSF), (10, 11)):
            candidate = _decode_metric(raw_idx, sf_idx)
            if _plausible_voltage(candidate):
                V = candidate
                break

        Hz = _decode_metric(OFF_HZ, OFF_HZSF)
        W = _decode_metric(OFF_W, OFF_WSF)

        if V is None and Hz is None and W is None:
            return None

        return {
            "V_AC": round(V, 2) if V is not None else "—",
            "freq_Hz": round(Hz, 2) if Hz is not None else "—",
            "P_AC_W": round(W, 1) if W is not None else "—",
            "P_AC_kW": round(W / 1000.0, 3) if W is not None else "—"
        }
    except Exception:
        return None
# ===== FRONIUS FLOAT MODELS (111=monofásico, 113=trifásico) =====
# SunSpec float: cada valor ocupa 2 registros uint16 (big-endian float32)
# Offsets en el payload (0 = primer registro tras el header del modelo)
# SunSpec float 111/113 layout:
#   0=A, 2=AphA, 4=AphB, 6=AphC, 8=PPVphAB, 10=PPVphBC, 12=PPVphCA,
#  14=PhVphA(V), 16=PhVphB, 18=PhVphC, 20=W, 22=Hz, 24=VA, 26=VAr, 28=PF,
#  30=WH(energy), 32=DCA, 34=DCV, 36=DCW, 38=TmpCab, 40=TmpSnk,
#  42=TmpTrns, 44=TmpOt, 46=St(status uint16), 47=StVnd
_FRONIUS_OFFSETS = {
    111: {"V": 14, "W": 20, "Hz": 22, "St": 46},  # monofásico
    113: {"V": 14, "W": 20, "Hz": 22, "St": 46},  # trifásico
}

# Códigos de estado Fronius (distintos de SMA)
_FRONIUS_STATUS = {
    1: "Off",
    2: "Sleeping",
    3: "Starting",
    4: "MPPT (operando)",
    5: "Throttled (limitado)",
    6: "Shutting down",
    7: "Fault",
    8: "Standby",
}


def _regs_to_float32(r1, r2):
    """Convierte dos registros uint16 a float32 big-endian (SunSpec float)."""
    try:
        v = struct.unpack('>f', struct.pack('>HH', r1, r2))[0]
        return None if (math.isnan(v) or math.isinf(v)) else v
    except Exception:
        return None


def decode_ac_from_float_model(regs, model_id):
    """
    Decodifica V, Hz, W de un modelo SunSpec float (Fronius 111/113).
    Retorna dict con V_AC, freq_Hz, P_AC_W/kW o None si no puede.
    """
    offsets = _FRONIUS_OFFSETS.get(model_id)
    if not offsets:
        return None
    min_needed = max(offsets["V"], offsets["W"], offsets["Hz"]) + 2
    if len(regs) < min_needed:
        return None
    try:
        V  = _regs_to_float32(regs[offsets["V"]],  regs[offsets["V"]  + 1])
        W  = _regs_to_float32(regs[offsets["W"]],  regs[offsets["W"]  + 1])
        Hz = _regs_to_float32(regs[offsets["Hz"]], regs[offsets["Hz"] + 1])
        if V is None and W is None and Hz is None:
            return None
        return {
            "V_AC":    round(V,  2)      if V  is not None else "—",
            "freq_Hz": round(Hz, 2)      if Hz is not None else "—",
            "P_AC_W":  round(W,  1)      if W  is not None else "—",
            "P_AC_kW": round(W / 1000.0, 3) if W is not None else "—",
        }
    except Exception:
        return None


def decode_fronius_status(regs, model_id):
    """Lee el registro de estado St (uint16 simple) de un modelo float Fronius."""
    offsets = _FRONIUS_OFFSETS.get(model_id)
    if not offsets or len(regs) <= offsets["St"]:
        return "sin datos", None, model_id, None
    code = regs[offsets["St"]]
    text = _FRONIUS_STATUS.get(code, f"unknown ({code})")
    return text, code, model_id, offsets["St"]


# ===== HELPERS DE NORMALIZACIÓN Y LIMPIEZA =====

def detect_inverter_type(result: dict) -> str:
    """
    Devuelve: 'fronius', 'sma', 'danfoss' o 'unknown'
    usando manufacturer y model del result dict.
    """
    haystack = " ".join([
        str(result.get("manufacturer") or ""),
        str(result.get("model") or ""),
        str(result.get("vendor") or ""),
    ]).lower()
    if "fronius" in haystack:
        return "fronius"
    if "sma" in haystack or "sunny" in haystack:
        return "sma"
    if "danfoss" in haystack or "dlx" in haystack:
        return "danfoss"
    return "unknown"


def normalize_inverter_result(result: dict) -> dict:
    """
    Normaliza valores raros (-0, "-0", "-0 V") sin romper claves existentes.
    Mantiene compatibilidad con el frontend actual.
    """
    def _is_neg_zero(v):
        return isinstance(v, float) and v == 0.0 and math.copysign(1, v) < 0

    def _fix(v):
        if isinstance(v, str) and v.strip() in ("-0", "-0.0", "-0 V"):
            return 0
        if isinstance(v, float) and _is_neg_zero(v):
            return 0.0
        return v

    P = result.get("P_AC_W")
    has_power = isinstance(P, (int, float)) and P > 0

    # Potencia: -0 → 0
    for key in ("P_AC_W", "P_AC_kW"):
        result[key] = _fix(result.get(key, "\u2014"))

    # Voltaje: si es 0 pero hay potencia real, es inconsistente → "—"
    v_fixed = _fix(result.get("V_AC"))
    if isinstance(v_fixed, (int, float)) and v_fixed == 0 and has_power:
        result["V_AC"] = "\u2014"
    else:
        result["V_AC"] = v_fixed

    # Frecuencia: igual que voltaje
    hz_fixed = _fix(result.get("freq_Hz"))
    if isinstance(hz_fixed, (int, float)) and hz_fixed == 0 and has_power:
        result["freq_Hz"] = "\u2014"
    else:
        result["freq_Hz"] = hz_fixed

    return result


def clean_status_text(result: dict) -> dict:
    """
    Evita mostrar "unknown status" cuando las métricas indican funcionamiento.
    Asigna textos de estado coherentes por fabricante.
    """
    txt = (result.get("status_text") or "").lower()
    P   = result.get("P_AC_W")
    Hz  = result.get("freq_Hz")

    has_power = isinstance(P, (int, float)) and P > 0
    hz_ok     = (Hz == "\u2014") or (isinstance(Hz, (int, float)) and 49.0 <= Hz <= 51.0)

    inv_type = detect_inverter_type(result)

    # 1) Limpiar "unknown status (XXX)" cuando las métricas son válidas
    if "unknown status" in txt and has_power and hz_ok:
        if inv_type == "fronius":
            result["status_text"] = "MPPT (operando)"
        elif inv_type == "danfoss":
            result["status_text"] = "Ok (DLX RPC)"
        else:
            result["status_text"] = "Ok"
        return result

    # 2) Fronius con potencia pero sin estado conocido
    if inv_type == "fronius" and has_power:
        _known = ("mppt", "throttled", "starting", "fault", "standby", "sleeping", "off")
        if not any(s in txt for s in _known):
            result["status_text"] = "MPPT (operando)"
        return result

    # 3) Danfoss con potencia pero sin estado conocido
    if inv_type == "danfoss" and has_power:
        if not any(s in txt for s in ("ok", "standby", "error", "fail")):
            result["status_text"] = "Ok (DLX RPC)"
        return result

    # 4) SMA con potencia pero sin estado conocido
    if inv_type == "sma" and has_power:
        _known = ("operando", "marcha", "ok", "standby", "fail", "starting")
        if not any(s in txt for s in _known):
            result["status_text"] = "Ok"
        return result

    return result


def _finalize(result: dict) -> dict:
    """Normaliza y limpia cada result antes de devolverlo al caller."""
    result = normalize_inverter_result(result)
    result = clean_status_text(result)
    if DEBUG_MODBUS:
        inv_type = detect_inverter_type(result)
        print(
            f"[DEBUG] {result.get('ip')} | {result.get('manufacturer')} {result.get('model')}"
            f" | type={inv_type} | unit={result.get('unit_used')}"
            f" | status={result.get('status_text')}"
            f" | V={result.get('V_AC')} | Hz={result.get('freq_Hz')} | W={result.get('P_AC_W')}"
        )
    return result


def read_ip_fronius(ip, unit_candidates=(1, 3, 126), port=PORT):
    """
    Lee un inversor Fronius (SunSpec float, modelos 111/113) vía Modbus TCP.
    Devuelve el mismo dict estándar que read_ip:
      'ok'       - datos decodificados correctamente
      'fail'     - conectó pero no encontró datos útiles
      'no conect'- sin conexión TCP
    """
    result = {
        "ip": ip,
        "status": "no conect",
        "status_text": "offline",
        "status_code": None,
        "status_src": None,
        "V_AC": "—",
        "freq_Hz": "—",
        "P_AC_W": "—",
        "P_AC_kW": "—",
        "unit_used": None,
        "vendor": "Fronius",
    }
    try:
        with ModbusTcpClient(ip, port, timeout=1.5, retries=1) as client:
            if not client.connect():
                print(f"❌ No conecta {ip}")
                return _finalize(result)

            result["status"] = "fail"
            result["status_text"] = "no data"

            # Detectar unit activo
            working_unit = None
            for u in unit_candidates:
                r = client.read_holding_registers((BASE_ADDR + 2) - 1, 2, slave=u)
                if not r.isError():
                    working_unit = u
                    break
            if working_unit is None:
                print(f"⚠️ {ip}: ningún unit ID respondió")
                return _finalize(result)

            # Leer datos comunes (fabricante, modelo, SN)
            info = read_common(client, unit=working_unit) or {}
            result.update(info)

            # Buscar modelo float 111 (monofásico) o 113 (trifásico)
            for float_mid in (111, 113):
                hdr_addr0, mlen = find_model_header(client, float_mid, unit=working_unit)
                if hdr_addr0 is None:
                    continue
                regs = read_u16s(client, working_unit, hdr_addr0 + 2, mlen)
                if not regs:
                    continue

                ac = decode_ac_from_float_model(regs, float_mid)
                if not ac:
                    print(f"⚠️ {ip}: MID {float_mid} encontrado pero no decodificable")
                    continue

                result.update(ac)
                result["status"]       = "ok"
                result["unit_used"]    = working_unit
                result["sunspec_model"] = float_mid

                st_text, st_code, st_mid, st_idx = decode_fronius_status(regs, float_mid)
                result["status_text"]  = st_text
                result["status_code"]  = st_code
                result["status_src"]   = {"model": st_mid, "index": st_idx}
                result["status_group"] = status_group_from_code(st_code)
                return _finalize(result)

            print(f"⚠️ {ip}: no se encontró MID 111 ni 113 (unit={working_unit})")
            return _finalize(result)

    except Exception as e:
        print(f"⚠️ Error en {ip}: {e}")
        result["status"]     = "no conect"
        result["status_text"] = "offline"
        result["error"]      = f"{type(e).__name__}: {e}"
        return _finalize(result)


def read_ip(ip, unit_candidates=(1, 3, 126), port=PORT):
    """
    Lee un inversor vía Modbus TCP probando múltiples unit IDs.
    Devuelve:
      - 'ok'  : si decodifica AC del modelo 101
      - 'raw' : si hay datos crudos pero no AC
      - 'fail': si conectó pero no pudo leer nada útil
      - 'no conect': si NO logró establecer conexión TCP
    """
    # POR DEFECTO: asumir que no conecta
    result = {
        "ip": ip,
        "status": "no conect",
        "status_text": "offline",
        "status_code": None,
        "status_src": None,
        "V_AC": "—",
        "freq_Hz": "—",
        "P_AC_W": "—",
        "P_AC_kW": "—",
        "unit_used": None,
    }
    try:
        with ModbusTcpClient(ip, port, timeout=1.5, retries=1) as client:
            if not client.connect():
                print(f"❌ No conecta {ip}")
                return _finalize(result)  # <- queda "no conect"

            # Conectó: si después no obtenemos nada, será "fail"
            result["status"] = "fail"
            result["status_text"] = "no data"

            # Detectar unit correcto probando lectura del header SunSpec
            working_unit = None
            for u in unit_candidates:
                r = client.read_holding_registers((BASE_ADDR + 2) - 1, 2, slave=u)
                if not r.isError():
                    working_unit = u
                    break
            if working_unit is None:
                working_unit = unit_candidates[0]

            info = read_common(client, unit=working_unit) or {}
            result.update(info)

            last_error = None
            for unit in unit_candidates:
                hdr_addr0, mlen = find_model_header(client, 101, unit=unit)
                if hdr_addr0 is None:
                    continue

                try:
                    regs = read_u16s(client, unit, hdr_addr0 + 2, mlen)
                except Exception as e:
                    last_error = e
                    print(f"⚠️ read_u16s falló en {ip} unit {unit}: {e}")
                    continue

                if not regs:
                    print(f"⚠️ Sin regs del 101 en {ip} unit {unit}")
                    continue

                result["raw_regs"] = regs
                result["unit_used"] = unit

                ac = decode_ac_from_101(regs)
                if ac:
                    result.update(ac)
                    result["status"] = "ok"
                    fill_voltage_generic_if_missing(result, client, unit)
                else:
                    result["status"] = "raw"

                # Estado heurstic
                models = {101: regs}
                st_text, st_code, st_mid, st_idx = decode_status_guess(models)
                result["status_text"] = st_text
                result["status_code"] = st_code
                result["status_src"] = {"model": st_mid, "index": st_idx}
                result["status_group"]= status_group_from_code(st_code) 

                if result["status"] == "ok":
                    result["status_text"] = derive_ok_from_metrics(
                        result, result.get("status_code"), result.get("status_text")
                    )

                return _finalize(result)  # éxito con este unit (ok/raw)

            # --- Modelo 101 no encontrado: intentar como Fronius float ---
            fronius = read_ip_fronius(ip, unit_candidates=unit_candidates, port=port)
            if fronius.get("status") == "ok":
                return fronius
            # Si no apareció 101, intentá “primer modelo” para al menos dejar "raw"
            for unit in unit_candidates:
                try:
                    mid, regs = read_first_model_payload(client, unit=unit)
                except Exception as e:
                    last_error = e
                    mid, regs = None, None
                if mid is not None and regs is not None:
                    result["unit_used"] = unit
                    break

            if mid is None or regs is None:
                print(f"⚠️ {ip} no devolvió modelos legibles. Último error: {last_error}")
                # OJO: aquí conectó pero no hay datos → 'fail'
                result["status"] = "fail"
                result["status_text"] = "no data"
                return _finalize(result)

            result["raw_model_id"] = mid
            result["raw_regs"] = regs
            result["status"] = "raw"
            st_text, st_code, st_mid, st_idx = decode_status_guess({mid: regs})
            result["status_text"] = st_text
            result["status_code"] = st_code
            result["status_src"] = {"model": st_mid, "index": st_idx}
            result["status_group"]= status_group_from_code(st_code) 
            return _finalize(result)

    except Exception as e:
        # Error duro de conexión: mantener "no conect"
        print(f"⚠️ Error en {ip}: {e}")
        result["status"] = "no conect"
        result["status_text"] = "offline"
        result["error"] = f"{type(e).__name__}: {e}"
        return _finalize(result)



def status_group_from_code(code: int) -> str:
    if code is None: return "unknown"
    if 100 <= code < 200: return "init"
    if 200 <= code < 300: return "error"
    if 300 <= code < 400: return "ok"
    if 400 <= code < 500: return "standby"
    if 500 <= code < 600: return "error"
    return "unknown"


# ===== Loop principal =====
if __name__ == "__main__":
    while True:
        print("\n================ CICLO DE LECTURA ================")
        for ip in IPS:
            data = read_ip(ip)
            if data.get("status") == "ok":
                st = data.get("status_text", "sin datos")
                src = data.get("status_src", {})
                src_str = f"(src m{src.get('model')} idx{src.get('index')})" if src.get("model") is not None else ""
                print(
                    f"✅ {ip} | {data.get('manufacturer','?')} {data.get('model','?')} SN:{data.get('serial','?')} | "
                    f"{data['V_AC']} V | {data['freq_Hz']} Hz | {data['P_AC_W']} W ({data['P_AC_kW']} kW) | "
                    f"Estado: {st} {src_str}"
                )
            elif data.get("status") == "raw":
                mid = data.get("raw_model_id", "101")
                regs = data.get("raw_regs", [])
                print(f"🟡 {ip} | MODEL {mid} CRUDO len={len(regs)} | regs[:12]={regs[:12]}")
            else:
                print(f"❌ {ip} sin datos válidos.")
        print("===================================================")
        time.sleep(INTERVAL)


def read_all(ips=None):
    """
    Lee todos los inversores y devuelve una lista de dicts (uno por IP).
    Si no se pasa 'ips', usa la lista IPS definida en este módulo.
    Las IPs en FRONIUS_IPS van directamente a read_ip_fronius (más rápido).
    """
    targets = ips or IPS
    results = []
    for ip in targets:
        if ip in FRONIUS_IPS:
            results.append(read_ip_fronius(ip))
        else:
            results.append(read_ip(ip))
    return results










