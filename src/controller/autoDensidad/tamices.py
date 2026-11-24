"""Aberturas en mm y bandas históricas de retenido acumulado de Gervasi."""

import math
import re

FONDO = "Fundo"
ETIQUETAS_FONDO = {"fundo", "pan", "piatto di fondo", "bandeja de fondo"}
ESCALA_MM = 1_000_000_000
ABERTURA = re.compile(r"([0-9]+(?:[.,][0-9]+)?|[.,][0-9]+)\s*(mm|mic|µm|μm|um)?", re.I)

LIMITES_BR = {
    "bloco": {
        "12.5": [0, 0], "9.5": [0, 0], "6.3": [0, 15], "4.8": [0, 33],
        "2.4": [19, 51], "1.2": [37, 66], "0.6": [54, 78], "0.3": [68, 90],
        "0.15": [80, 97], "0.075": [90, 100], FONDO: [100, 100],
    },
    "paver": {
        "12.5": [0, 0], "9.5": [0, 0], "6.3": [0, 10], "4.8": [0, 22],
        "2.4": [19, 40], "1.2": [37, 61], "0.6": [54, 78], "0.3": [72, 92],
        "0.15": [85, 100], "0.075": [95, 100], FONDO: [100, 100],
    },
}


def normalizar_tamiz(valor):
    if isinstance(valor, str) and valor.strip().lower() in ETIQUETAS_FONDO:
        return FONDO

    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        mm = valor
    else:
        coincidencia = ABERTURA.fullmatch(str(valor).strip())
        if not coincidencia:
            raise ValueError(f"Tamiz inválido: {valor}")
        numero, unidad = coincidencia.groups()
        mm = float(numero.replace(",", "."))
        if unidad and unidad.lower() != "mm":
            mm /= 1000

    if not math.isfinite(mm) or mm <= 0:
        raise ValueError(f"Tamiz inválido: {valor}")
    if mm < 1_000_000:
        mm = math.floor(mm * ESCALA_MM + 0.5) / ESCALA_MM
    if mm == 0:
        raise ValueError(f"Tamiz inválido: {valor}")
    return int(mm) if float(mm).is_integer() else mm


def ordenar_tamices(tamices):
    normalizados = [normalizar_tamiz(tamiz) for tamiz in tamices]
    if len(set(normalizados)) != len(normalizados):
        raise ValueError("La serie contiene tamices o bandejas de fondo duplicados.")
    indices = sorted(range(len(normalizados)),
                     key=lambda i: -1 if normalizados[i] == FONDO else normalizados[i],
                     reverse=True)
    return [normalizados[i] for i in indices], indices


def convertir_limites(minimo, maximo):
    """Complementar e invertir los extremos entre pasante y retenido acumulado."""
    return 100 - maximo, 100 - minimo


def resolver_limites(tamices, referencia, representacion="retenido", *,
                     representacion_original="retenido", intervalos_excluidos=(),
                     permitir_interpolacion=False):
    """Resolver por abertura. Un intervalo excluido se expresa como (menor, mayor)."""
    if {representacion, representacion_original} - {"retenido", "pasante"}:
        raise ValueError("Representación de banda inválida.")
    puntos = {}
    for tamiz, extremos in referencia.items():
        tamiz = normalizar_tamiz(tamiz)
        if tamiz in puntos:
            raise ValueError(f"Tamiz de referencia duplicado: {tamiz}.")
        if extremos is None:
            # Un extremo de referencia sin datos interrumpe la banda.
            puntos[tamiz] = None
            continue
        minimo, maximo = extremos
        if not 0 <= minimo <= maximo <= 100:
            raise ValueError(f"Límites inválidos para {tamiz}.")
        puntos[tamiz] = (minimo, maximo)
    eje = sorted(t for t in puntos if t != FONDO)

    resultado = []
    for valor in tamices:
        tamiz = normalizar_tamiz(valor)
        limites = puntos.get(tamiz)
        origen = "exact" if limites is not None else "unavailable"
        motivo = None
        if origen == "unavailable":
            motivo = "outside_domain"
            if tamiz == FONDO:
                motivo = "pan_without_reference"
            elif tamiz in puntos:
                motivo = "excluded_interval"
            else:
                for menor, mayor in zip(eje, eje[1:]):
                    if menor < tamiz < mayor:
                        a, b = puntos[menor], puntos[mayor]
                        excluido = any(lo < mayor and hi > menor for lo, hi in intervalos_excluidos)
                        if a is None or b is None or excluido:
                            motivo = "excluded_interval"
                        else:
                            peso = math.log(tamiz / menor) / math.log(mayor / menor)
                            limites = tuple(x + (y - x) * peso for x, y in zip(a, b))
                            origen, motivo = "interpolated", None
                        break
        minimo, maximo = limites if limites is not None else (None, None)
        if limites is not None and representacion != representacion_original:
            minimo, maximo = convertir_limites(minimo, maximo)
        resultado.append({
            "tamiz": tamiz, "min": minimo, "max": maximo, "origen": origen,
            "apto_validacion": tamiz != FONDO and (
                origen == "exact" or origen == "interpolated" and permitir_interpolacion
            ), "motivo": motivo,
        })
    return resultado


def referencias_perfil(perfil):
    """Validar un perfil explícito y extender la referencia histórica de su producto."""
    if perfil is None:
        return LIMITES_BR, None
    if not isinstance(perfil, dict):
        raise ValueError("profile_metadata")
    producto = perfil.get("producto")
    nombre, fuente = perfil.get("nombre"), perfil.get("fuente")
    if producto not in ("bloco", "paver") or not all(
        isinstance(texto, str) and texto.strip() for texto in (nombre, fuente)
    ):
        raise ValueError("profile_metadata")
    puntos = perfil.get("puntos", {})
    if not isinstance(puntos, dict):
        raise ValueError("profile_values")
    referencias = {**LIMITES_BR, producto: dict(LIMITES_BR[producto])}
    canonicos = {}
    for abertura, extremos in puntos.items():
        tamiz = normalizar_tamiz(abertura)
        if tamiz == FONDO or str(tamiz) in canonicos:
            raise ValueError("profile_values")
        if not isinstance(extremos, (tuple, list)) or len(extremos) != 2 or not all(
            type(valor) in (int, float) and 0 <= valor <= 100 for valor in extremos
        ) or extremos[0] > extremos[1]:
            raise ValueError("profile_values")
        canonicos[str(tamiz)] = list(extremos)
    referencias[producto].update(canonicos)
    eje, _ = ordenar_tamices(referencias[producto])
    filas = [referencias[producto][str(t)] for t in eje]
    if any(lo1 > lo2 or hi1 > hi2 for (lo1, hi1), (lo2, hi2) in zip(filas, filas[1:])):
        raise ValueError("profile_monotonic")
    fuente_manual = perfil.get("fuente_manual", fuente)
    if canonicos and (not isinstance(fuente_manual, str) or not fuente_manual.strip()):
        raise ValueError("profile_manual_source")
    return referencias, {
        "nombre": nombre.strip(), "fuente": fuente.strip(), "producto": producto,
        "puntos": canonicos, "permitir_interpolacion": perfil.get("permitir_interpolacion") is True,
        **({"fuente_manual": fuente_manual.strip()} if canonicos else {}),
    }


def resolver_bandas(tamices, referencias, perfil=None, representacion="retenido"):
    bandas = {
        producto: resolver_limites(
            tamices, referencias.get(producto, {}), representacion,
            permitir_interpolacion=bool(perfil and perfil["producto"] == producto and perfil["permitir_interpolacion"]),
        )
        for producto in LIMITES_BR
    }
    if perfil:
        for fila in bandas[perfil["producto"]]:
            if str(fila["tamiz"]) in perfil["puntos"]:
                fila["origen"] = "manual"
    return bandas
