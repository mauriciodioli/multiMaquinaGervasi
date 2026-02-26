import time
import hashlib
import requests

BASE_URL = "https://mcs-gateway.fscut.com"
APP_ID = "op19ae985631c54d49"
APP_SECRET = "1e02ed5180cf24ebcbdd0551d0ba1031d9430145d0942f4f01f127bdc06fb7fd"
ORG_CODE = ""  # opcional; si soporte te lo da, lo pegás acá

def build_headers():
    ts = int(time.time() * 1000)
    sign = hashlib.md5(f"{APP_ID}{APP_SECRET}{ts}".encode("utf-8")).hexdigest()

    h = {
        "app-id": APP_ID,
        "time-stamp": str(ts),
        "app-sign": sign,
        "Content-Type": "application/json",
    }
    if ORG_CODE:
        h["X-FS-Orgcode"] = ORG_CODE
    return h

url = f"{BASE_URL}/api/user_devices"
r = requests.post(url, json={}, headers=build_headers(), timeout=15)

print("HTTP:", r.status_code)
print("BODY:", r.text[:2000])

