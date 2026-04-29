#!/usr/bin/env python3
"""
Test de conexión y lectura Modbus para Fronius 192.168.1.106
Prueba unit IDs, modelos SunSpec y decodificación de datos.

Ejecutar:
    python test_fronius_106.py
"""
import struct
import math
from pymodbus.client import ModbusTcpClient

IP   = "192.168.1.106"
PORT = 502
# Fronius Datamanager suele estar en unit 1; también probamos 3 y 126
UNITS = [1, 2, 3, 4, 126]

# SunSpec: la tabla empieza en 40001 (1-based) → 40000 (0-based)
# El primer modelo real está en 40003 (0-based: 40002)
BASE_SUNSPEC_HEADER = 40000  # contiene "SunS" (0x5375, 0x6e53)
FIRST_MODEL_ADDR    = 40002  # primer header [ID, LEN]


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def regs_to_float32(r1, r2):
    try:
        v = struct.unpack('>f', struct.pack('>HH', r1, r2))[0]
        return None if (math.isnan(v) or math.isinf(v)) else round(v, 3)
    except Exception:
        return None

def s16(x):
    return x - 0x10000 if x & 0x8000 else x

def regs_to_str(regs):
    s = []
    for reg in regs:
        hi = (reg >> 8) & 0xFF
        lo = reg & 0xFF
        if hi == 0: break
        s.append(chr(hi))
        if lo == 0: break
        s.append(chr(lo))
    return "".join(s).strip()

# Offsets Fronius float (0 = primer registro tras el header del modelo)
# SunSpec float 111/113 layout:
#   0=A, 2=AphA, 4=AphB, 6=AphC, 8=PPVphAB, 10=PPVphBC, 12=PPVphCA,
#  14=PhVphA(V), 16=PhVphB, 18=PhVphC, 20=W, 22=Hz, 46=St(uint16), 47=StVnd
_FRONIUS = {
    111: {"V": 14, "W": 20, "Hz": 22, "St": 46, "name": "AC monofásico"},
    113: {"V": 14, "W": 20, "Hz": 22, "St": 46, "name": "AC trifásico"},
    1:   {"name": "Common (fabricante/modelo/SN)"},
}

_FRONIUS_STATUS = {
    1: "Off",
    2: "Sleeping",
    3: "Starting",
    4: "MPPT (operando)",
    5: "Throttled",
    6: "Shutting down",
    7: "Fault",
    8: "Standby",
}

SMA_OFFSETS = {"V": 8, "VSF": 9, "Hz": 14, "HZSF": 15, "W": 12, "WSF": 13}


# ──────────────────────────────────────────────
# Secciones del test
# ──────────────────────────────────────────────

def section(title):
    print(f"\n{'─'*55}")
    print(f" {title}")
    print(f"{'─'*55}")


def test_tcp_connect():
    section(f"1. Conexión TCP  {IP}:{PORT}")
    client = ModbusTcpClient(IP, PORT, timeout=3)
    ok = client.connect()
    print(f" {'✅ Conectado' if ok else '❌ Sin conexión TCP'}")
    return client if ok else None


def test_sunspec_magic(client, unit):
    """Verifica la firma 'SunS' en 40000."""
    r = client.read_holding_registers(BASE_SUNSPEC_HEADER, 2, slave=unit)
    if r.isError():
        return False
    magic = (r.registers[0] << 16) | r.registers[1]
    ok = (magic == 0x53756e53)  # 'SunS'
    print(f"   unit={unit:3d} | SunSpec magic: 0x{magic:08X}  {'✅ SunS' if ok else '⚠️  no es SunS'}")
    return ok


def test_units(client):
    section("2. Detección de unit ID")
    found = []
    for unit in UNITS:
        r = client.read_holding_registers(FIRST_MODEL_ADDR, 2, slave=unit)
        if not r.isError():
            mid, mlen = r.registers
            print(f"   unit={unit:3d} → responde  [MID={mid}, LEN={mlen}]  ✅")
            test_sunspec_magic(client, unit)
            found.append(unit)
        else:
            print(f"   unit={unit:3d} → error (sin respuesta)")
    return found


def scan_models(client, unit):
    section(f"3. Tabla de modelos SunSpec  (unit={unit})")
    addr = FIRST_MODEL_ADDR
    models = {}
    for _ in range(80):
        hdr = client.read_holding_registers(addr, 2, slave=unit)
        if hdr.isError():
            print(f"   addr={addr}: error leyendo header")
            break
        mid, mlen = hdr.registers
        if mid == 0xFFFF:
            print(f"   addr={addr}: fin de tabla SunSpec")
            break
        label = _FRONIUS.get(mid, {}).get("name", "")
        print(f"   MID={mid:4d}  LEN={mlen:3d}  addr={addr}  {label}")
        models[mid] = (addr, mlen)
        addr += 2 + mlen
    return models


def decode_common(client, unit, addr, mlen):
    section(f"4. Datos Common (MID 1) - fabricante / modelo / SN")
    regs = client.read_holding_registers(addr + 2, mlen, slave=unit)
    if regs.isError():
        print("   ❌ No se pudo leer el modelo Common")
        return
    r = regs.registers
    print(f"   Fabricante : {regs_to_str(r[0:16])}")
    print(f"   Modelo     : {regs_to_str(r[16:32])}")
    print(f"   SN         : {regs_to_str(r[48:66])}")


def decode_float_model(client, unit, mid, addr, mlen):
    section(f"5. Decodificación float  MID={mid}  ({_FRONIUS.get(mid,{}).get('name','')})")
    regs = client.read_holding_registers(addr + 2, mlen, slave=unit)
    if regs.isError():
        print("   ❌ No se pudo leer el payload")
        return
    r = regs.registers
    print(f"   Total registros: {len(r)}")
    print(f"   Primeros 24:     {r[:24]}")

    offsets = _FRONIUS.get(mid, {})
    if not offsets or "V" not in offsets:
        print("   ⚠️  No hay offsets definidos para este MID")
        return

    V  = regs_to_float32(r[offsets["V"]],  r[offsets["V"]  + 1])
    W  = regs_to_float32(r[offsets["W"]],  r[offsets["W"]  + 1])
    Hz = regs_to_float32(r[offsets["Hz"]], r[offsets["Hz"] + 1])
    St = r[offsets["St"]] if len(r) > offsets["St"] else None
    st_text = _FRONIUS_STATUS.get(St, f"desconocido ({St})")

    print(f"\n   {'Campo':<12} {'Raw regs':<20} {'Valor'}")
    print(f"   {'─'*50}")
    print(f"   {'V_AC':<12} {str(r[offsets['V']:offsets['V']+2]):<20} {V} V")
    print(f"   {'freq_Hz':<12} {str(r[offsets['Hz']:offsets['Hz']+2]):<20} {Hz} Hz")
    print(f"   {'P_AC_W':<12} {str(r[offsets['W']:offsets['W']+2]):<20} {W} W")
    print(f"   {'Estado':<12} {St:<20} {st_text}")

    if V and W and Hz:
        print(f"\n   ✅  DATOS VÁLIDOS  →  {V} V  |  {Hz} Hz  |  {W} W ({round(W/1000,3)} kW)  |  {st_text}")
    else:
        print(f"\n   ⚠️  Algunos valores son None — revisar offsets o estado del inversor")


def decode_sma_model101(client, unit, addr, mlen):
    section(f"5b. Decodificación SMA int+SF  MID=101")
    regs = client.read_holding_registers(addr + 2, mlen, slave=unit)
    if regs.isError():
        print("   ❌ No se pudo leer el payload")
        return
    r = regs.registers
    o = SMA_OFFSETS
    max_idx = max(o.values())
    if len(r) <= max_idx:
        print(f"   ⚠️  Payload demasiado corto: {len(r)} regs, necesita {max_idx+1}")
        return

    V   = s16(r[o["V"]])  * (10 ** s16(r[o["VSF"]]))
    Hz  = s16(r[o["Hz"]]) * (10 ** s16(r[o["HZSF"]]))
    W   = s16(r[o["W"]])  * (10 ** s16(r[o["WSF"]]))
    print(f"   V_AC    = {round(V, 2)} V")
    print(f"   freq_Hz = {round(Hz, 2)} Hz")
    print(f"   P_AC_W  = {round(W, 1)} W")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print(f"\n{'═'*55}")
    print(f"  TEST MODBUS  →  {IP}:{PORT}")
    print(f"{'═'*55}")

    client = test_tcp_connect()
    if client is None:
        print("\n❌ No hay conexión. Verificar que el Fronius tenga Modbus TCP habilitado.")
        return

    try:
        found_units = test_units(client)
        if not found_units:
            print("\n❌ Ningún unit ID respondió. Revisar configuración del Fronius.")
            return

        # Usar el primer unit que respondió
        unit = found_units[0]
        print(f"\n → Usando unit={unit} para los tests siguientes")

        models = scan_models(client, unit)
        if not models:
            print("❌ No se encontraron modelos SunSpec en este unit.")
            return

        # Common
        if 1 in models:
            decode_common(client, unit, *models[1])

        # Fronius float
        decoded = False
        for mid in (111, 113):
            if mid in models:
                decode_float_model(client, unit, mid, *models[mid])
                decoded = True
                break

        # SMA int+SF
        if not decoded and 101 in models:
            decode_sma_model101(client, unit, *models[101])
        elif not decoded:
            print("\n⚠️  No se encontró MID 101, 111 ni 113. Modelos disponibles:", list(models.keys()))

    finally:
        client.close()

    print(f"\n{'═'*55}\n")


if __name__ == "__main__":
    main()
