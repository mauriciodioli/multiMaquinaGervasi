#!/usr/bin/env python3
# dlx_rpc_monitor.py — Lee datos de varios DLX vía HTTP RPC GeteNexusData
# y maneja robustamente los valores 'na' / no numéricos.

import time
import hashlib
from datetime import datetime
from pprint import pprint

import requests

# ========= CONFIG =========

DLX_IPS = [
    "192.168.1.104",
    "192.168.1.105",    
    "192.168.1.108",
]

# Usuario/password del web de los DLX
DLX_USER = "admin"
DLX_PASS = "admin"

INTERVAL = 5  # segundos entre ciclos

# ========= BLOQUE RPC DANFOSS (HTTP) =========

def rpc(session, ip, method, params, **kwargs):
    url = f"http://{ip}/rpc/{method}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"http://{ip}/INDEX.HTM",
    }
    body = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    return session.post(url, json=body, headers=headers, timeout=8, **kwargs)


def try_login(session, ip, user, pwd):
    # 1) intento simple
    try:
        r = rpc(session, ip, "LogIn", [user, pwd])
    except Exception as e:
        return False, f"req-error: {e}"

    if not r.ok:
        return False, f"HTTP {r.status_code} {r.reason}"

    txt = r.text or ""
    ok = ("result" in txt and '"Error"' not in txt)
    if ok:
        return True, "plain"

    # 2) intento con MD5 del password
    md5pwd = hashlib.md5(pwd.encode("utf-8")).hexdigest()
    try:
        r = rpc(session, ip, "LogIn", [user, md5pwd])
    except Exception as e:
        return False, f"req-error: {e}"

    if not r.ok:
        return False, f"HTTP {r.status_code} {r.reason}"

    txt = r.text or ""
    ok = ("result" in txt and '"Error"' not in txt)
    return (ok, "md5" if ok else "none")


# ========= MAPEO eNEXUS =========
# AHORA usando exactamente lo que viste en el HTML (s:<system>,t:<systemType>)

ENEXUS_ITEMS = [
    # ---- Estado general / alarms ----
    ("status_id",      "eNEXUS_0001[s:<system>,t:<systemType>]", "INT8U"),
    ("mode_id",        "eNEXUS_0002[s:<system>,t:<systemType>]", "INT8U"),
    ("alarm_raw",      "eNEXUS_0003[s:<system>,t:<systemType>]", "INT32U"),
    ("warning_raw",    "eNEXUS_0004[s:<system>,t:<systemType>]", "INT32U"),

    # ---- Estado instantáneo DC/AC (bloque state_values) ----
    ("dc_current_in",  "eNEXUS_0005[s:<system>,t:<systemType>]", "INT16U"),  # /1000 A
    ("dc_voltage_in",  "eNEXUS_0006[s:<system>,t:<systemType>]", "INT16U"),  # /10 V
    ("dc_power_in",    "eNEXUS_0007[s:<system>,t:<systemType>]", "INT16U"),  # W

    ("ac_current_out", "eNEXUS_0008[s:<system>,t:<systemType>]", "INT16U"),  # /1000 A
    ("ac_voltage_out", "eNEXUS_0009[s:<system>,t:<systemType>]", "INT16U"),  # /10 V
    ("ac_power_out",   "eNEXUS_0010[s:<system>,t:<systemType>]", "INT16U"),  # W

    ("oper_hours",     "eNEXUS_0011[s:<system>,t:<systemType>]", "INT32U"),  # h

    # ---- Energías (bloque inverter_main_values / plant_main_values) ----
    ("energy_today_Wh", "eNEXUS_0013[s:<system>,t:<systemType>]", "INT32S"),  # Wh
    ("energy_month_Wh", "eNEXUS_0014[s:<system>,t:<systemType>]", "INT32S"),  # /1000 → kWh
    ("energy_year_Wh",  "eNEXUS_0015[s:<system>,t:<systemType>]", "INT32S"),  # /1000 → kWh

    # ---- Potencia planta (grafico "Produzione attuale energia") ----
    ("plant_power_W",  "eNEXUS_0064[s:<system>,t:<systemType>]", "INT32U"),

    # ---- Info sitio / fecha/hora (opcional) ----
    ("date_raw",       "eNEXUS_0016", "Date"),
    ("time_raw",       "eNEXUS_0017", "Time"),
    ("site_name",      "eNEXUS_0018", "STRING32"),
]


def build_items_payload():
    """Convierte ENEXUS_ITEMS al formato que espera GeteNexusData."""
    return [
        {"path": path, "datatype": dt}
        for (_name, path, dt) in ENEXUS_ITEMS
    ]


def decode_enexus(raw):
    """
    raw: dict {path_str: value} tal como lo devuelve GeteNexusData
    Devuelve un dict con valores ya escalados (A, V, W, kWh, h, etc.).
    """

    def num(path, scale=1.0, default=0.0):
        v = raw.get(path)
        # Valores no aplicables / vacíos
        if v in (None, "", "-", "na", "NA", "Na", "NaN"):
            return default
        try:
            return float(v) * scale
        except Exception:
            return default

    out = {}

    # Corrientes / tensiones / potencias (state_values)
    out["dc_current_A"]  = num("eNEXUS_0005[s:<system>,t:<systemType>]", 1/1000.0)
    out["dc_voltage_V"]  = num("eNEXUS_0006[s:<system>,t:<systemType>]", 1/10.0)
    out["dc_power_W"]    = num("eNEXUS_0007[s:<system>,t:<systemType>]", 1.0)

    out["ac_current_A"]  = num("eNEXUS_0008[s:<system>,t:<systemType>]", 1/1000.0)
    out["ac_voltage_V"]  = num("eNEXUS_0009[s:<system>,t:<systemType>]", 1/10.0)
    out["ac_power_W"]    = num("eNEXUS_0010[s:<system>,t:<systemType>]", 1.0)

    # Horas de operación

    out["oper_hours"] = num("eNEXUS_0011[s:<system>,t:<systemType>]", 1/3600.0)


    # Energías (en Wh, las pasamos a kWh)
    et = num("eNEXUS_0013[s:<system>,t:<systemType>]", 1.0)  # Wh
    em = num("eNEXUS_0014[s:<system>,t:<systemType>]", 1.0)  # Wh-equivalente
    ey = num("eNEXUS_0015[s:<system>,t:<systemType>]", 1.0)

    out["energy_today_kWh"] = et / 1000.0
    out["energy_month_kWh"] = em / 1000.0
    out["energy_year_kWh"]  = ey / 1000.0

    # Potencia planta total
    out["plant_power_W"] = num("eNEXUS_0064[s:<system>,t:<systemType>]", 1.0)

    # Status / mode / alarms crudos (sin mapear aún)
    out["status_id"]   = raw.get("eNEXUS_0001[s:<system>,t:<systemType>]")
    out["mode_id"]     = raw.get("eNEXUS_0002[s:<system>,t:<systemType>]")
    out["alarm_raw"]   = raw.get("eNEXUS_0003[s:<system>,t:<systemType>]")
    out["warning_raw"] = raw.get("eNEXUS_0004[s:<system>,t:<systemType>]")

    # Info de sitio (por si la querés usar)
    out["site_name"]   = raw.get("eNEXUS_0018")

    return out


def fetch_dlx_data(ip, debug_raw=False):
    s = requests.Session()

    ok, how = try_login(s, ip, DLX_USER, DLX_PASS)
    if not ok:
        return {"ok": False, "error": f"login failed ({how})"}

    items_payload = build_items_payload()

    try:
        r = rpc(s, ip, "GeteNexusData", items_payload)
    except Exception as e:
        return {"ok": False, "error": f"req-error: {e}"}

    if not r.ok:
        return {"ok": False, "error": f"HTTP {r.status_code} {r.reason}"}

    try:
        js = r.json()
    except Exception as e:
        return {"ok": False, "error": f"JSON error: {e}", "raw": r.text}

    res = js.get("result", [])
    raw = {it["path"]: it.get("value") for it in res}

    # Pequeño log para ver si viene vacío
    print(f"    [{ip}] GeteNexusData devolvió {len(res)} items")

    if debug_raw:
        print(f"🔎 RAW {ip}:")
        pprint(raw)

    decoded = decode_enexus(raw)

    return {
        "ok": True,
        **decoded,
        "raw": raw,
    }


def print_row(ip, info):
    if not info.get("ok"):
        print(f"❌ {ip}: {info.get('error')}")
        return

    print(
        f"✅ {ip} | "
        f"DC={info['dc_voltage_V']:.1f} V {info['dc_current_A']:.3f} A {info['dc_power_W']:.0f} W | "
        f"AC={info['ac_voltage_V']:.1f} V {info['ac_current_A']:.3f} A {info['ac_power_W']:.0f} W | "
        f"Plant={info['plant_power_W']:.0f} W | "
        f"E_today={info['energy_today_kWh']:.2f} kWh | "
        f"E_month={info['energy_month_kWh']:.1f} kWh | "
        f"E_year={info['energy_year_kWh']:.1f} kWh | "
        f"h={info['oper_hours']:.0f}"
    )


def main():
    print("Monitor DLX vía HTTP RPC (GeteNexusData). Ctrl+C para salir.")
    if DLX_PASS == "cambia_esto":
        print("⚠ ATENCIÓN: Cambiá DLX_USER / DLX_PASS antes de usar de verdad.")

    # primer ciclo con debug_raw=True para ver qué devuelve cada uno
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n========== CICLO RPC (DEBUG RAW) {ts} ==========")
    for ip in DLX_IPS:
        info = fetch_dlx_data(ip, debug_raw=True)
        print_row(ip, info)

    # luego bucle normal
    while True:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n========== CICLO RPC {ts} ==========")
        for ip in DLX_IPS:
            info = fetch_dlx_data(ip)
            print_row(ip, info)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDetenido por el usuario.")






# === API para Flask: normalizar DLX al formato de modbus_sma.read_ip ===

def read_dlx_ip(ip: str) -> dict:
    """
    Usa fetch_dlx_data() y devuelve el MISMO formato que modbus_sma.read_ip().
    """
    base = {
        "ip": ip,
        "status": "no conect",
        "status_text": "offline",
        "status_code": None,
        "status_src": {"model": "DLX", "index": None},
        "status_group": "unknown",
        "manufacturer": "Danfoss",
        "model": "DLX",
        "V_AC": "—",
        "freq_Hz": 50.0,
        "P_AC_W": "—",
        "P_AC_kW": "—",
    }

    info = fetch_dlx_data(ip, debug_raw=False)

    if not info.get("ok"):
        # hubo error de login / request
        base["status"] = "fail"
        base["status_text"] = info.get("error", "no data")
        return base

    # Si llegamos acá, info tiene lo que arma decode_enexus()
    base["status"] = "ok"
    base["status_text"] = "Ok (DLX RPC)"
    base["status_group"] = "ok"

    # Potencia AC
    p_ac = info.get("ac_power_W")
    if isinstance(p_ac, (int, float)):
        base["P_AC_W"] = p_ac
        base["P_AC_kW"] = round(p_ac / 1000.0, 3)

    # Tensión AC
    v_ac = info.get("ac_voltage_V")
    if isinstance(v_ac, (int, float)):
        base["V_AC"] = round(v_ac, 1)

    # Frecuencia: DLX siempre 50 Hz (si algún día la leemos, se cambia)
    base["freq_Hz"] = 50.0

    # Extras opcionales si los querés usar luego
    base["E_today_kWh"] = info.get("energy_today_kWh")
    base["E_month_kWh"] = info.get("energy_month_kWh")
    base["E_year_kWh"] = info.get("energy_year_kWh")
    base["hours"] = info.get("oper_hours")

    # Si potencia 0 => standby
    if isinstance(base["P_AC_W"], (int, float)) and base["P_AC_W"] <= 0:
        base["status_text"] = "standby (DLX)"
        base["status_group"] = "standby"

    return base


def read_all_dlx(ips=None):
    """
    Igual que read_all() de SMA, pero para DLX.
    Devuelve una lista de dicts (uno por IP).
    """
    targets = ips or DLX_IPS
    return [read_dlx_ip(ip) for ip in targets]
