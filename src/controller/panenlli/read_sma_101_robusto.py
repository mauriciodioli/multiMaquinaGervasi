#!/usr/bin/env python3
import time
from pymodbus.client import ModbusTcpClient

# ===== CONFIG =====
IPS = [
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103",
    "192.168.1.104",
    "192.168.1.105",
    "192.168.1.106",
    "192.168.1.107",
    "192.168.1.108",
    "192.168.1.109",
    "192.168.1.110",

    
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
    """
    Busca un código de estado plausible (100..600) en los modelos presentes.
    Devuelve (status_text, code, src_model, src_index).
    """
    # Prioridad: primero en 101, después 103, 160, y luego cualquier otro
    order = [101, 103, 160] + [m for m in models.keys() if m not in (101, 103, 160)]
    for mid in order:
        regs = models.get(mid)
        if not regs:
            continue
        for idx, v in enumerate(regs):
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

def read_ip(ip):
    """Lee un inversor en ip; si no entiende devuelve regs crudos bajo 'raw_regs'."""
    result = {"ip": ip, "status": "fail"}
    try:
        with ModbusTcpClient(ip, PORT) as client:
            if not client.connect():
                print(f"❌ No conecta {ip}")
                return result

            info = read_common(client)
            if info:
                result.update(info)

            # Intentar localizar model 101
            hdr_addr0, mlen = find_model_header(client, 101)
            if hdr_addr0 is None:
                # sin 101: devolvemos payload crudo del primer modelo para análisis
                mid, regs = read_first_model_payload(client)
                if mid is None or regs is None:
                    print(f"⚠️ {ip} no devolvió modelos legibles")
                    return result
                result["raw_model_id"] = mid
                result["raw_regs"] = regs
                result["status"] = "raw"
                # también definimos models para que decode_status_guess pueda mirar algo
                models = {mid: regs}
                st_text, st_code, st_mid, st_idx = decode_status_guess(models)
                result["status_text"] = st_text
                result["status_code"] = st_code
                result["status_src"] = {"model": st_mid, "index": st_idx}
                return result

            # Si encontré 101, leer payload completo
            regs = read_u16s(client, UNIT_ID, hdr_addr0 + 2, mlen)
            if not regs:
                print(f"⚠️ No pude leer registros del modelo 101 en {ip}")
                return result

                     # Guardar crudos
            result["raw_regs"] = regs

            # Decodificar AC del 101 (igual que antes)
            ac = decode_ac_from_101(regs)
            if ac:
                result.update(ac)
                result["status"] = "ok"
            else:
                result["status"] = "raw"

            # Estado: buscar en los modelos que tenemos (mínimo el 101)
            models = {101: regs}
            st_text, st_code, st_mid, st_idx = decode_status_guess(models)
            result["status_text"] = st_text
            result["status_code"] = st_code
            result["status_src"] = {"model": st_mid, "index": st_idx}

            # Ajuste mínimo: si el estado no es reconocible pero todo está sano, mostrar Ok (heurístico)
            if result.get("status") == "ok":
                result["status_text"] = derive_ok_from_metrics(
                    result, result.get("status_code"), result.get("status_text")
                )

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
