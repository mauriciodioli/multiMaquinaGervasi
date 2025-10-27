#!/usr/bin/env python3
import time
from pymodbus.client import ModbusTcpClient
from math import sqrt
# ===== CONFIG =====
IPS = [
    "192.168.1.101",
    "192.168.1.102",
   # "192.168.1.103",
   # "192.168.1.104",
   # "192.168.1.105",
   # "192.168.1.106",
   # "192.168.1.107",
   # "192.168.1.108",
   # "192.168.1.109",
   # "192.168.1.110",
    # añadir más IPs si hace falta
]
PORT = 502
UNIT_ID = 126
BASE_ADDR = 40001  # SunSpec 1-based
INTERVAL = 5  # segundos entre ciclos

# === OFFSETS CONFIRMADOS PARA SMA (model 101) ===
OFF_V = 8
OFF_VSF = 9
OFF_HZ = 14
OFF_HZSF = 15
OFF_W = 12
OFF_WSF = 13
# ==================================================


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
    sf_idxs = [(j, s16(w)) for j, w in enumerate(regs) if -3 <= s16(w) <= 1]
    for j, sf in sf_idxs:
        start = max(0, j - window)
        end   = min(len(regs)-1, j + window)
        for i in range(start, end):
            raw = s16(regs[i])
            if raw in (0x8000, 0x7FFF, -32768):
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
            sf_idxs.append((j, sf))

    def plausible(v):
        return (180.0 <= v <= 270.0) or (380.0 <= v <= 420.0)

    for j, sf in sf_idxs:
        start = max(0, j - window)
        end   = min(len(regs)-1, j + window)
        for i in range(start, end):
            raw = s16(regs[i])
            if raw in (0x8000, 0x7FFF, -32768):
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
    devolvemos 'Ok (heurístico)'. Mantiene el texto original si ya es conocido.
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

    # si el código cae en 200..299, asumimos fallo
    if isinstance(code, int) and 200 <= code < 300:
        return f"falla (código {code})"

    # si potencia > 0 y V/Hz razonables → Ok
    if W_ok and W > 0 and (V_ok or V == "—") and Hz_ok:
        return "Ok (heurístico)"

    # si potencia 0 pero V/Hz ok → standby
    if W_ok and W == 0 and (V_ok or V == "—") and Hz_ok:
        return "standby (heurístico)"

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
                    101: "iniciando",
                    102: "apagado",
                    104: "esperando",
                    201: "falla",
                    202: "fallo de red",
                }
                if code in mapping:
                    return f"{mapping[code]} (código {code})", code, mid, idx
                if 200 <= code < 300:
                    return f"fallo menor (código {code})", code, mid, idx
                if 300 <= code < 400:
                    return f"operando (código {code})", code, mid, idx
                if 400 <= code < 500:
                    return f"standby/operación (código {code})", code, mid, idx
                return f"estado desconocido ({code})", code, mid, idx

    return "sin datos", None, None, None


def sunssf(val, sf):
    """Aplica factor de escala SunSpec; seguro y conservador."""
    if val in (0x8000, 0x7FFF):  # sentinel SunSpec
        return None
    if sf is None or sf == -32768:
        return None
    # filtrar sf absurdos
    if sf < -10 or sf > 10:
        return None
    try:
        return val * (10 ** sf)
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

def read_common(client):
    hdr_addr0 = (BASE_ADDR + 2) - 1  # 40003 (0-based)
    hdr = read_u16s(client, UNIT_ID, hdr_addr0, 2)
    if not hdr:
        return None
    mid, mlen = hdr
    regs = read_u16s(client, UNIT_ID, hdr_addr0 + 2, mlen)
    if not regs:
        return None
    mn = regs_to_str(regs[0:16])
    md = regs_to_str(regs[16:32])
    sn = regs_to_str(regs[48:66])
    return {"manufacturer": mn, "model": md, "serial": sn, "first_model_id": mid}

def find_model_header(client, target_mid):
    """Busca el header de target_mid; devuelve (addr0, mlen) o (None, None)."""
    addr0 = (BASE_ADDR + 2) - 1
    while True:
        hdr = read_u16s(client, UNIT_ID, addr0, 2)
        if not hdr:
            return None, None
        mid, mlen = hdr
        if mid == 0xFFFF:
            return None, None
        if mid == target_mid:
            return addr0, mlen
        addr0 = addr0 + 2 + mlen

def read_first_model_payload(client):
    """Lee el primer header (el que sea) y devuelve (mid, regs) o (None, None)."""
    addr0 = (BASE_ADDR + 2) - 1
    hdr = read_u16s(client, UNIT_ID, addr0, 2)
    if not hdr:
        return None, None
    mid, mlen = hdr
    regs = read_u16s(client, UNIT_ID, addr0 + 2, mlen)
    if not regs:
        return None, None
    return mid, regs

def decode_ac_from_101(regs):
    """Intenta decodificar V, Hz y W usando offsets fijos SMA.
       Si no puede decodificar una magnitud, la deja como "—".
       Devuelve dict o None si todo es ininterpretable.
    """
    try:
        max_needed = max(OFF_V, OFF_VSF, OFF_HZ, OFF_HZSF, OFF_W, OFF_WSF)
        if len(regs) <= max_needed + 1:
            return None

        V_raw, V_sf = s16(regs[OFF_V]), s16(regs[OFF_VSF])
        Hz_raw, Hz_sf = s16(regs[OFF_HZ]), s16(regs[OFF_HZSF])
        W_raw, W_sf = s16(regs[OFF_W]), s16(regs[OFF_WSF])

        V = sunssf(V_raw, V_sf)
        Hz = sunssf(Hz_raw, Hz_sf)
        W = sunssf(W_raw, W_sf)

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
def read_ip(ip, unit_candidates=(126, 1, 3), port=PORT):
    """
    Lee un inversor vía Modbus TCP probando múltiples unit IDs.
    Devuelve 'ok' si decodifica AC del modelo 101, 'raw' si hay datos crudos,
    y 'fail' sólo si no conectó o no pudo leer nada útil.
    """
    result = {"ip": ip, "status": "fail"}
    try:
        with ModbusTcpClient(ip, port) as client:
            if not client.connect():
                print(f"❌ No conecta {ip}")
                return result

            info = read_common(client) or {}
            result.update(info)

            # Intentar por cada unit id posible
            last_error = None
            for unit in unit_candidates:
                try:
                    # Buscar header del modelo 101 usando este unit
                    hdr_addr0, mlen = find_model_header(client, 101, unit=unit)
                except TypeError:
                    # compat: si tu find_model_header original no acepta unit
                    hdr_addr0, mlen = find_model_header(client, 101)
                if hdr_addr0 is None:
                    continue  # probar siguiente unit

                # Si hay header, leer payload del 101 con el MISMO unit
                try:
                    regs = read_u16s(client, unit, hdr_addr0 + 2, mlen)
                except Exception as e:
                    last_error = e
                    print(f"⚠️ read_u16s falló en {ip} unit {unit}: {e}")
                    continue

                if not regs:
                    print(f"⚠️ Sin regs del 101 en {ip} unit {unit}")
                    continue

                # Guardar crudos y unit usado
                result["raw_regs"] = regs
                result["unit_used"] = unit

                # Decodificar AC
                ac = decode_ac_from_101(regs)
                if ac:
                    result.update(ac)
                    result["status"] = "ok"
                    
                    
                    # Completar nominal si falta V en vivo
                    fill_voltage_generic_if_missing(result, client, unit)

                    # 🔎 Diagnóstico opcional (solo para la IP problemática)
                    #if result.get("V_AC") == "—" and ip == "192.168.1.101":
                        #try:
                           # print(f"[{ip}] 🔎 scan_all_models_for_voltage (unit={unit})")
                           # scan_all_models_for_voltage(client, unit, window=12)
                        #except Exception as e:
                         #   print(f"[{ip}] scan_all_models_for_voltage error: {e}")

                else:
                    result["status"] = "raw"
               # if result.get("raw_regs"):
                #    print(f"[{ip}] V_raw@101={result['raw_regs'][OFF_V]} "    f"V_sf@101={result['raw_regs'][OFF_VSF]} "    f"V_AC={result.get('V_AC')}")
                # Estado heurístico
                models = {101: regs}
                st_text, st_code, st_mid, st_idx = decode_status_guess(models)
                result["status_text"] = st_text
                result["status_code"] = st_code
                result["status_src"] = {"model": st_mid, "index": st_idx}

                if result["status"] == "ok":
                    result["status_text"] = derive_ok_from_metrics(
                        result, result.get("status_code"), result.get("status_text")
                    )
                    
                #print(f"[{ip}] status_guess code={st_code} src_model={st_mid} idx={st_idx} "f"val={ (models.get(st_mid)[st_idx] if st_mid in models and st_idx is not None else None) } " f"hint={'V_SF' if (st_mid==101 and st_idx in (OFF_VSF, OFF_HZSF, OFF_WSF)) else ''}")
    
                return result  # éxito con este unit

            # Si no se encontró modelo 101 con ningún unit, al menos intenta “primer modelo”
            try:
                mid, regs = read_first_model_payload(client)
            except Exception as e:
                last_error = e
                mid, regs = None, None

            if mid is None or regs is None:
                print(f"⚠️ {ip} no devolvió modelos legibles. Último error: {last_error}")
                return result  # se queda 'fail'
         
            result["raw_model_id"] = mid
            result["raw_regs"] = regs
            result["status"] = "raw"
            models = {mid: regs}
            st_text, st_code, st_mid, st_idx = decode_status_guess(models)
            result["status_text"] = st_text
            result["status_code"] = st_code
            result["status_src"] = {"model": st_mid, "index": st_idx}
            return result

    except Exception as e:
        print(f"⚠️ Error en {ip}: {e}")
        return result


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
    """
    targets = ips or IPS
    return [read_ip(ip) for ip in targets]






