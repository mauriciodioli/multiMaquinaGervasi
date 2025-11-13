#!/usr/bin/env python3
import requests, hashlib, time
from pprint import pprint

IP   = "192.168.1.104"
USER = "admin"
PASS = "admin"

MAX_IDX = 300      # podés subir a 600/800 si va bien
DELAY   = 0.05     # pausa entre lecturas para no matar al DLX

def rpc(session, ip, method, params, timeout=5):
    return session.post(
        f"http://{ip}/rpc/{method}",
        json={"jsonrpc":"2.0","method":method,"params":params,"id":1},
        timeout=timeout,
        headers={"Content-Type":"application/json",
                 "Accept":"application/json"}
    )

def login(session, ip):
    print(f"→ Login a {ip} ...", end="", flush=True)
    r = rpc(session, ip, "LogIn", [USER, PASS])
    txt = r.text or ""
    if '"Error"' in txt:
        md5pwd = hashlib.md5(PASS.encode()).hexdigest()
        r = rpc(session, ip, "LogIn", [USER, md5pwd])
        txt = r.text or ""
    ok = '"Error"' not in txt
    print(" OK" if ok else " FAIL")
    return ok

def scan(ip):
    s = requests.Session()
    if not login(s, ip):
        print("❌ login failed")
        return

    found = []

    print(f"\n=== Escaneo eNEXUS (0..{MAX_IDX}) en {ip} ===")
    idx = 0
    while idx <= MAX_IDX:
        path = f"eNEXUS_{idx:04d}[s:<system>,t:<systemType>]"
        payload = [{"path": path, "datatype": "INT32U"}]

        try:
            r = rpc(s, ip, "GeteNexusData", payload)
            js = r.json()
        except Exception as e:
            print(f"\n⚠ Error en idx={idx}: {e}")
            # intentar re-login y seguir
            try:
                s.close()
            except:
                pass
            s = requests.Session()
            if not login(s, ip):
                print("❌ No se pudo reloguear, corto scan.")
                break
            # NO incrementamos idx todavía, reintenta la misma posición
            time.sleep(0.5)
            continue

        res = js.get("result") or []
        if res:
            val = res[0].get("value")
            if val not in ("na", None):
                found.append((idx, path, val))
                print(f"✔ idx={idx:03d} {path} = {val}")

        idx += 1
        time.sleep(DELAY)

    print("\n--- RESULTADOS NO 'na' ---")
    pprint(found)

if __name__ == "__main__":
    scan(IP)
