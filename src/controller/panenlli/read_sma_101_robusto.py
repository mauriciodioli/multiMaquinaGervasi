#!/usr/bin/env python3
import time
from pymodbus.client import ModbusTcpClient
import os, json, datetime
import socket
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymodbus.client import ModbusTcpClient

# Puertos “sospechosos” para DLX/SMA y web embebida
DEFAULT_PORTS = [
    80, 81, 8080, 8000, 8443,  # HTTP(S) típicos
    502, 5020, 5021, 5022, 8502,  # Modbus variantes (SMA/Danfoss)
    21, 22, 23, 161, 443          # comunes por las dudas
]

# ========= CONFIG =========
IPS = [
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103",
    "192.168.1.104",  # Danfoss DLX    
    "192.168.1.109",
    "192.168.1.110",
    "192.168.1.111",
    "192.168.1.112",
]
PORT = 502
# --- Overrides por IP (para equipos que no usan el mismo Unit/Base) ---
IP_OVERRIDES = {
    "192.168.1.104": {
        "unit_ids": [1, 3, 126],   # DLX suele ser 1; probamos 3 y 126 también
        "bases": [40000, 40001],   # algunos DLX exponen SunSpec en 40000
        "skip_signature": True,    # escanear aunque no veamos la firma "SunS"
        "timeout": 4.0             # un poco más de paciencia
    }
}

# Danfoss suele responder en unit 1; SMA en 126. Probamos ambos (+2 por si acaso)
UNIT_IDS = [126, 1, 2]

# Algunas implementaciones ponen SunSpec en 40000 en lugar de 40001
BASE_CANDIDATES = [40001, 40000]

INTERVAL = 5  # s entre ciclos
RAW_SCAN = False  # poné True cuando quieras volcar crudo
# === OFFSETS SMA (model 101) ===
OFF_V   = 8
OFF_VSF = 9
OFF_HZ  = 14
OFF_HZSF= 15
OFF_W   = 12
OFF_WSF = 13
# ============================
def check_sunspec_signature(client, unit, base):
    """Verifica firma SunSpec 'SunS' en la base dada (1-based)."""
    r = read_u16s(client, unit, base - 1, 2)
    if not r:
        return False
    return r[0] == 0x5375 and r[1] == 0x6e53  # 'Su' 'nS'

def read_common2(client, unit, base):
    """Versión parametrizada de read_common()."""
    hdr_addr0 = (base + 2) - 1
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

def find_model_header2(client, unit, base, target_mid, max_hops=64):
    """Busca header SunSpec (parametrizado)."""
    addr0 = (base + 2) - 1
    hops = 0
    while hops < max_hops:
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr:
            return None, None
        mid, mlen = hdr
        if mid == 0xFFFF:
            return None, None
        if mid == target_mid:
            return addr0, mlen
        addr0 = addr0 + 2 + mlen
        hops += 1
    return None, None

def scan_all_models2(client, unit, base, max_hops=64):
    """Escanea todos los modelos SunSpec disponibles y devuelve {mid: regs}."""
    models = {}
    addr0 = (base + 2) - 1
    hops = 0
    while hops < max_hops:
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr:
            break
        mid, mlen = hdr
        if mid == 0xFFFF:
            break
        regs = read_u16s(client, unit, addr0 + 2, mlen) or []
        models[mid] = regs
        addr0 = addr0 + 2 + mlen
        hops += 1
    return models

def s16(x): return x - 0x10000 if x & 0x8000 else x

def sunssf(val, sf):
    if val in (0x8000, 0x7FFF): return None
    if sf is None or sf == -32768: return None
    if sf < -10 or sf > 10: return None
    try: return val * (10 ** sf)
    except Exception: return None

def read_u16s(client, unit, addr0, count):
    r = client.read_holding_registers(addr0, count, slave=unit)
    return None if r.isError() else r.registers

def regs_to_str(regs):
    s=[]
    for reg in regs:
        hi=(reg>>8)&0xFF; lo=reg&0xFF
        if hi==0: break
        s.append(chr(hi))
        if lo==0: break
        s.append(chr(lo))
    return "".join(s)

def check_sunspec_signature(client, unit, base):
    """SunSpec signature 'SunS' en base (big-endian)."""
    regs = read_u16s(client, unit, base-1, 2)  # 1-based -> 0-based
    if not regs: return False
    # 'S' 'u' y 'n' 'S' en dos registros (0x5375, 0x6e53)
    return regs[0] == 0x5375 and regs[1] == 0x6e53

def read_common(client, unit, base):
    hdr_addr0 = (base + 2) - 1  # 40003 0-based
    hdr = read_u16s(client, unit, hdr_addr0, 2)
    if not hdr: return None
    mid, mlen = hdr
    regs = read_u16s(client, unit, hdr_addr0 + 2, mlen)
    if not regs: return None
    mn = regs_to_str(regs[0:16])
    md = regs_to_str(regs[16:32])
    sn = regs_to_str(regs[48:66])
    return {"manufacturer": mn, "model": md, "serial": sn, "first_model_id": mid}

def iterate_model_headers(client, unit, base, max_hops=64):
    """Genera (mid, mlen, addr0) para cada header SunSpec hasta 0xFFFF."""
    addr0 = (base + 2) - 1
    hops = 0
    while hops < max_hops:
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr: break
        mid, mlen = hdr
        if mid == 0xFFFF: break
        yield mid, mlen, addr0
        addr0 = addr0 + 2 + mlen
        hops += 1

def find_model_header(client, unit, base, target_mid):
    for mid, mlen, addr0 in iterate_model_headers(client, unit, base):
        if mid == target_mid:
            return addr0, mlen
    return None, None

def scan_all_models(client, unit, base, take_payload=True):
    models = {}
    for mid, mlen, addr0 in iterate_model_headers(client, unit, base):
        regs = read_u16s(client, unit, addr0 + 2, mlen) if take_payload else []
        models[mid] = regs or []
    return models

def decode_ac_from_101(regs):
    try:
        max_needed = max(OFF_V, OFF_VSF, OFF_HZ, OFF_HZSF, OFF_W, OFF_WSF)
        if len(regs) <= max_needed + 1: return None
        V_raw, V_sf = s16(regs[OFF_V]),  s16(regs[OFF_VSF])
        Hz_raw,Hz_sf= s16(regs[OFF_HZ]), s16(regs[OFF_HZSF])
        W_raw, W_sf = s16(regs[OFF_W]),  s16(regs[OFF_WSF])

        V  = sunssf(V_raw, V_sf)
        Hz = sunssf(Hz_raw, Hz_sf)
        W  = sunssf(W_raw, W_sf)

        if V is None and Hz is None and W is None: return None
        return {
            "V_AC": round(V,2) if V is not None else "—",
            "freq_Hz": round(Hz,2) if Hz is not None else "—",
            "P_AC_W": round(W,1) if W is not None else "—",
            "P_AC_kW": round(W/1000.0,3) if W is not None else "—"
        }
    except Exception:
        return None

def decode_status_guess(models):
    order = [101, 103, 160] + [m for m in models.keys() if m not in (101,103,160)]
    mapping = {303:"operando / inyección",307:"marcha normal",455:"standby",
               400:"operando",101:"iniciando",102:"apagado",104:"esperando",
               201:"falla",202:"fallo de red"}
    for mid in order:
        regs = models.get(mid) or []
        for idx, v in enumerate(regs):
            if 100 <= v <= 600:
                if v in mapping: return f"{mapping[v]} (código {v})", v, mid, idx
                if 200 <= v < 300: return f"fallo menor (código {v})", v, mid, idx
                if 300 <= v < 400: return f"operando (código {v})", v, mid, idx
                if 400 <= v < 500: return f"standby/operación (código {v})", v, mid, idx
                return f"estado desconocido ({v})", v, mid, idx
    return "sin datos", None, None, None

def derive_ok_from_metrics(ac, code, status_text):
    if status_text and any(k in status_text for k in ("operando","marcha","standby","falla")):
        return status_text
    V = ac.get("V_AC"); Hz = ac.get("freq_Hz"); W = ac.get("P_AC_W")
    V_ok  = (isinstance(V,(int,float))  and 180<=V<=260)
    Hz_ok = (isinstance(Hz,(int,float)) and 49.0<=Hz<=51.0)
    W_ok  = (isinstance(W,(int,float))  and W>=0)
    if isinstance(code,int) and 200 <= code < 300: return f"falla (código {code})"
    if W_ok and W>0 and (V_ok or V=="—") and Hz_ok: return "Ok (heurístico)"
    if W_ok and W==0 and (V_ok or V=="—") and Hz_ok: return "standby (heurístico)"
    return status_text or "sin datos"

def read_ip(ip):
    result = {"ip": ip, "status": "fail"}

    # Overrides por IP o defaults globales (SIN renombrar nada)
    ov = IP_OVERRIDES.get(ip, {})
    unit_ids       = ov.get("unit_ids", UNIT_IDS)
    base_candidates= ov.get("bases", BASE_CANDIDATES)
    skip_signature = ov.get("skip_signature", False)
    timeout        = ov.get("timeout", 2.5)

    try:
        # mismo cliente, sólo agrego timeout si vino en overrides
        client = ModbusTcpClient(ip, PORT, timeout=timeout)
        with client:
            if not client.connect():
                print(f"❌ No conecta {ip}")
                return result

            for unit in unit_ids:
                for base in base_candidates:
                    try:
                        # Respetar skip_signature para equipos como el 104
                        if not skip_signature:
                            if not check_sunspec_signature(client, unit, base):
                                continue

                        # Usamos TUS mismos helpers y nombres
                        info = read_common(client, unit, base)
                        if info:
                            result.update(info)

                        models = scan_all_models(client, unit, base)
                        if not models:
                            continue

                        hdr_addr0, mlen = find_model_header(client, unit, base, 101)
                        regs101 = read_u16s(client, unit, hdr_addr0 + 2, mlen) if hdr_addr0 else []

                        if regs101:
                            result["raw_regs"] = regs101
                            ac = decode_ac_from_101(regs101)
                            result["status"] = "ok" if ac else "raw"
                            if ac:
                                result.update(ac)
                        else:
                            first_mid = next(iter(models.keys()))
                            result["raw_model_id"] = first_mid
                            result["raw_regs"] = models[first_mid]
                            result["status"] = "raw"

                        st_text, st_code, st_mid, st_idx = decode_status_guess(models)
                        if result.get("status") == "ok":
                            st_text = derive_ok_from_metrics(result, st_code, st_text)

                        result["status_text"] = st_text
                        result["status_code"] = st_code
                        result["status_src"] = {"model": st_mid, "index": st_idx}
                        result["unit_id"] = unit
                        result["base_addr"] = base
                        return result

                    except Exception:
                        continue

            return result

    except Exception as e:
        print(f"⚠️ Error en {ip}: {e}")
        return result


# ===== Loop principal =====
# ===== Loop principal =====
if __name__ == "__main__":
    while True:
        print("\n================ CICLO DE LECTURA ================")
        for ip in IPS:
            # --- MODO CRUDO ---
            if RAW_SCAN:
                res = scan_ports(ip)  # o scan_ports(ip, ports=range(1,1025)) si querés full
                print_scan(ip, res)
                raw = read_ip_raw(ip)
                print_raw_overview(raw, max_ascii=4)
                path = save_raw_dump(raw)
                print(f"💾 Dump guardado: {path}")

                cands = guess_tracker_candidates(raw)
                if cands:
                    print("🧭 Candidatos X/Y (revisar):")
                    for mid, rows in cands.items():
                        for r in rows[:10]:
                            print(f"   MID {mid} idx {r['idx']:>3} @addr1 {r['addr1']} "
                                  f"u16={r['u16']} s16={r['s16']} sf={r['sf']} "
                                  f"→ {r['scaled_u']} / {r['scaled_s']}")
                # si querés SOLO crudo, saltá al siguiente ip:
                # continue

            # --- LECTURA NORMAL ---
            data = read_ip(ip)
            if data.get("status") == "ok":
                st = data.get("status_text", "sin datos")
                src = data.get("status_src", {})
                src_str = f"(src m{src.get('model')} idx{src.get('index')})" if src.get("model") is not None else ""
                print(
                    f"✅ {ip} | {data.get('manufacturer','?')} {data.get('model','?')} SN:{data.get('serial','?')} | "
                    f"{data['V_AC']} V | {data['freq_Hz']} Hz | {data['P_AC_W']} W ({data['P_AC_kW']} kW) | "
                    f"Estado: {st} {src_str} | unit={data.get('unit_id')} base={data.get('base_addr')}"
                )
            elif data.get("status") == "raw":
                mid = data.get("raw_model_id", "101")
                regs = data.get("raw_regs", [])
                st = data.get("status_text","sin datos")
                print(f"🟡 {ip} | MODEL {mid} CRUDO len={len(regs)} | regs[:12]={regs[:12]} | {st}")
            else:
                print(f"❌ {ip} sin datos válidos.")
        print("===================================================")
        time.sleep(INTERVAL)










# === RAW DUMPS: inspección completa por modelo ===


def harvest_all_models(client, unit, base, max_hops=128, take_payload=True):
    """
    Recorre todos los headers SunSpec a partir de `base` y devuelve
    una lista de dicts con meta (mid, mlen, addrs) y registros crudos.
    """
    out = []
    addr0 = (base + 2) - 1  # primer header (0-based)
    hops = 0
    while hops < max_hops:
        hdr = read_u16s(client, unit, addr0, 2)
        if not hdr:
            break
        mid, mlen = hdr
        if mid == 0xFFFF:
            break

        regs = read_u16s(client, unit, addr0 + 2, mlen) if take_payload else []
        entry = {
            "mid": mid,
            "mlen": mlen,
            "addr0": addr0,           # 0-based header address
            "addr1": addr0 + 1,       # 1-based header address (visual)
            "payload_addr0": addr0+2, # 0-based payload start
            "payload_addr1": addr0+3, # 1-based payload start
            "regs_len": len(regs),
            "regs": regs or [],
        }

        # Previews útiles
        entry["u16_preview"] = (regs[:16] if regs else [])
        entry["s16_preview"] = ([s16(x) for x in regs[:16]] if regs else [])

        # Aspiramos spans ASCII (pares de bytes no nulos)
        entry["ascii_spans"] = _extract_ascii_spans(regs)

        out.append(entry)
        addr0 = addr0 + 2 + mlen
        hops += 1
    return out

def _extract_ascii_spans(regs):
    """
    Heurística: intenta armar cadenas ASCII a partir de u16 big-endian.
    Útil para encontrar labels y strings de config.
    """
    spans = []
    cur = []
    def flush():
        if not cur: return
        s = "".join(cur)
        # Filtrar basura muy corta o con pocos caracteres visibles
        if len(s.strip()) >= 3:
            spans.append(s)
        cur.clear()

    for r in (regs or []):
        hi = (r >> 8) & 0xFF
        lo = r & 0xFF
        for b in (hi, lo):
            if 32 <= b <= 126:        # rango ASCII imprimible
                cur.append(chr(b))
            elif b == 0:              # terminador C
                flush()
            else:
                flush()
    flush()
    return spans

def read_ip_raw(ip):
    """
    Igual filosofía que read_ip(), pero devolviendo TODO lo crudo por modelo.
    """
    ov = IP_OVERRIDES.get(ip, {})
    unit_ids        = ov.get("unit_ids", UNIT_IDS)
    base_candidates = ov.get("bases", BASE_CANDIDATES)
    skip_signature  = ov.get("skip_signature", False)
    timeout         = ov.get("timeout", 2.5)

    meta = {"ip": ip, "status": "fail"}
    client = ModbusTcpClient(ip, PORT, timeout=timeout)
    with client:
        if not client.connect():
            return meta
        for unit in unit_ids:
            for base in base_candidates:
                try:
                    if not skip_signature and not check_sunspec_signature(client, unit, base):
                        continue

                    info = read_common(client, unit, base) or {}
                    models = harvest_all_models(client, unit, base, take_payload=True)
                    if not models:
                        continue

                    meta.update(info)
                    meta.update({
                        "status": "raw_ok",
                        "unit_id": unit,
                        "base_addr": base,
                        "models": models,
                    })
                    return meta
                except Exception:
                    continue
    return meta

def save_raw_dump(data, out_dir="./raw_dumps"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ip = data.get("ip","unknown").replace(".","-")
    path = os.path.join(out_dir, f"raw_{ip}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def print_raw_overview(raw_meta, max_ascii=3):
    """
    Vista rápida en consola: por cada MID muestra len y algunos spans ASCII.
    """
    if raw_meta.get("status") != "raw_ok":
        print(f"❌ {raw_meta.get('ip')} sin raw_ok")
        return
    print(f"🔎 RAW {raw_meta['ip']} unit={raw_meta['unit_id']} base={raw_meta['base_addr']} "
          f"| {raw_meta.get('manufacturer','?')} {raw_meta.get('model','?')} SN:{raw_meta.get('serial','?')}")
    for m in raw_meta.get("models", []):
        mids = m["mid"]; mlen = m["mlen"]; rlen = m["regs_len"]
        spans = (m.get("ascii_spans") or [])[:max_ascii]
        spans_str = " | ".join(spans) if spans else "—"
        print(f"  • MID {mids:<4} @{m['addr1']:<6} len={mlen:<4} regs={rlen:<4} ascii={spans_str}")

# ————————————————————————————————————————————————
# (OPCIONAL) Marcador de candidatos a posición X/Y
# ————————————————————————————————————————————————
def guess_tracker_candidates(raw_meta):
    """
    Busca pares (idx, valor) que podrían ser ángulos/posiciones.
    Estrategia:
     - Considera s16 y u16.
     - Prueba SF en [-3..+3] y marca si cae en:
         a) 0..360   (azimut)
         b) -180..180 (tilt/azimut con signo)
         c) 0..1000  (mm, décimas de grado, centideg)
    Devuelve: dict[mid] = lista de dicts {idx, u16, s16, sf, scaled, addr1}
    """
    if raw_meta.get("status") != "raw_ok":
        return {}

    out = {}
    for m in raw_meta.get("models", []):
        regs = m.get("regs") or []
        if not regs: 
            continue
        candidates = []
        for i, u in enumerate(regs):
            sv = s16(u)
            for sf in range(-3, 4):
                try:
                    scaled_u = u * (10 ** sf)
                    scaled_s = sv * (10 ** sf)
                except Exception:
                    continue
                # Rangos tentativos
                if (0 <= scaled_u <= 360) or (-180 <= scaled_s <= 180) or (0 <= scaled_u <= 1000):
                    candidates.append({
                        "idx": i,
                        "u16": u,
                        "s16": sv,
                        "sf": sf,
                        "scaled_u": scaled_u,
                        "scaled_s": scaled_s,
                        "addr1": m["payload_addr1"] + i  # 1-based real
                    })
        if candidates:
            out[m["mid"]] = candidates
    return out












def _is_open(ip, port, timeout=1.2):
    """Conexión TCP básica; devuelve True si abre."""
    try:
        with closing(socket.create_connection((ip, port), timeout=timeout)):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def _grab_banner(ip, port, timeout=1.0):
    """Sniff liviano: intenta leer/obtener algún banner (HTTP/Modbus)."""
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        s.settimeout(timeout)
        with closing(s):
            # Prueba HTTP
            try:
                s.sendall(b"GET / HTTP/1.0\r\nHost: %b\r\n\r\n" % ip.encode())
                data = s.recv(256)
                if data:
                    return data[:256].decode(errors="ignore")
            except Exception:
                pass
            # Si no hubo HTTP, devolvemos vacío
            return ""
    except Exception:
        return ""

def _looks_like_http(banner: str) -> bool:
    b = (banner or "").upper()
    return ("HTTP" in b) or ("SERVER:" in b) or ("CONTENT-" in b)

def _confirm_modbus(ip, port, timeout=2.0):
    """Intenta handshake Modbus con pymodbus. No lee nada, solo conecta."""
    try:
        client = ModbusTcpClient(ip, port=port, timeout=timeout)
        with client:
            if client.connect():
                # Conexión establecida; opcionalmente podríamos hacer un request MEI.
                return True
        return False
    except Exception:
        return False

def scan_ports(ip, ports=DEFAULT_PORTS, timeout=1.2, max_workers=32):
    """Escanea lista de puertos y devuelve dict con estado y hints."""
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_is_open, ip, p, timeout): p for p in ports}
        for fut in as_completed(futs):
            p = futs[fut]
            is_open = False
            try:
                is_open = fut.result()
            except Exception:
                is_open = False
            if not is_open:
                results[p] = {"open": False}
                continue

            # Si está open, intentamos banner y, si aplica, Modbus
            banner = _grab_banner(ip, p, timeout=timeout)
            looks_http = _looks_like_http(banner)
            is_modbus = False
            if p in (502, 5020, 5021, 5022, 8502) and not looks_http:
                is_modbus = _confirm_modbus(ip, p, timeout=timeout)

            results[p] = {
                "open": True,
                "http-ish": looks_http,
                "modbus-ish": is_modbus,
                "banner": (banner[:120] if banner else "")
            }
    return dict(sorted(results.items(), key=lambda kv: kv[0]))

def print_scan(ip, results):
    print(f"\n🔎 Scan {ip}")
    for port, info in results.items():
        if not info.get("open"):
            print(f"  {port:>5}/tcp  closed/filtered")
            continue
        tags = []
        if info.get("http-ish"): tags.append("HTTP")
        if info.get("modbus-ish"): tags.append("MODBUS")
        tag_str = f" [{'|'.join(tags)}]" if tags else ""
        banner = info.get("banner") or ""
        banner = banner.replace("\r", " ").replace("\n", " ")[:80]
        print(f"  {port:>5}/tcp  OPEN{tag_str}  {banner}")
