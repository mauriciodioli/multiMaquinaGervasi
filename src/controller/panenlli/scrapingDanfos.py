# danfoss_rpc_login_probe.py
import sys, hashlib, requests
from pprint import pprint

def rpc(session, ip, method, params, **kwargs):
    url = f"http://{ip}/rpc/{method}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"http://{ip}/INDEX.HTM",
    }
    body = {"jsonrpc":"2.0","method":method,"params":params,"id":1}
    r = session.post(url, json=body, headers=headers, timeout=8, **kwargs)
    return r

def try_login(session, ip, user, pwd):
    # 1) intento simple
    r = rpc(session, ip, "LogIn", [user, pwd])
    ok = r.ok and ("result" in r.text or '"Error"' not in r.text)
    if ok:
        return True, "plain"
    # 2) intento con MD5 del password
    md5pwd = hashlib.md5(pwd.encode("utf-8")).hexdigest()
    r = rpc(session, ip, "LogIn", [user, md5pwd])
    ok = r.ok and ("result" in r.text or '"Error"' not in r.text)
    return ok, "md5" if ok else "none"

def main(ip, user, pwd):
    s = requests.Session()

    ok, how = try_login(s, ip, user, pwd)
    print(f"[LogIn] método: {how} -> {'OK' if ok else 'FALLÓ'}")
    if not ok:
        print("No pudimos iniciar sesión vía RPC. Revisa user/pass o mira el archivo logon.js para confirmar si requiere hash distinto.")
        sys.exit(1)

    # Paths vistos en el HTML (s:1,t:17)
    items = [
        {"path": "eNEXUS_0009[s:1,t:17]", "datatype": "INT16U"},  # AC V (bindOutVoltage) -> /10 V
        {"path": "eNEXUS_0008[s:1,t:17]", "datatype": "INT16U"},  # AC I (bindOutCurrent) -> /1000 A (formato %1.1f/1000 A)
        {"path": "eNEXUS_0010[s:1,t:17]", "datatype": "INT16U"},  # AC P (bindOutPower)  -> W
        {"path": "eNEXUS_0006[s:1,t:17]", "datatype": "INT16U"},  # DC V (bindInVoltage) -> /10 V
        {"path": "eNEXUS_0005[s:1,t:17]", "datatype": "INT16U"},  # DC I (bindCurrent)   -> /1000 A
        {"path": "eNEXUS_0007[s:1,t:17]", "datatype": "INT16U"},  # DC P (bindInPower)   -> W
        {"path": "eNEXUS_0013[s:1,t:17]", "datatype": "INT32S"},  # Energy Today         -> Wh
        {"path": "eNEXUS_0014[s:1,t:17]", "datatype": "INT32S"},  # Energy Month         -> /1000 kWh
        {"path": "eNEXUS_0015[s:1,t:17]", "datatype": "INT32S"},  # Energy Year          -> /1000 kWh
        {"path": "eNEXUS_0011[s:1,t:17]", "datatype": "INT32U"},  # Operation Hours      -> h
    ]

    r = rpc(s, ip, "GeteNexusData", items)
    print(f"[POST] http://{ip}/rpc/GeteNexusData -> {r.status_code} {r.headers.get('Content-Type')}")
    print(r.text)

    # Si quieres, decodificar rápido:
    try:
        js = r.json()
        res = js.get("result", [])
        data = {it["path"]: it.get("value") for it in res}
        print("\nValores crudos:")
        pprint(data)
    except Exception as e:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python3 danfoss_rpc_login_probe.py <ip> <user> <pass>")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
