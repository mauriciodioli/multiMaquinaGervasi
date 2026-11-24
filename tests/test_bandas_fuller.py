"""Ejecutar con PYTHONPATH=src:. MPLBACKEND=Agg python tests/test_bandas_fuller.py."""
import contextlib
import io
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from flask import Flask

from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    calculoPorRetenidos,
    optimizar_proporciones_materiales,
)
from controller.autoDensidad.densidadFuller import densidadFuller
from controller.autoDensidad.tamices import (
    LIMITES_BR, convertir_limites, ordenar_tamices, resolver_limites,
)


class BandasFullerTest(unittest.TestCase):
    def test_normalizacion_y_duplicados(self):
        eje, indices = ordenar_tamices(["Pan", "63 μm", "0,5", 10, "250 mic", "8 mm"])
        self.assertEqual(eje, [10, 8, 0.5, 0.25, 0.063, "Fundo"])
        self.assertEqual(indices, [3, 5, 2, 4, 1, 0])
        for entradas in [["0,5", "500 µm"], [0], [-1], ["8 cm"], [float("nan")], ["Pan", "Fundo"]]:
            with self.subTest(entradas=entradas), self.assertRaises(ValueError):
                ordenar_tamices(entradas)

    def test_limites_originales_y_conversion(self):
        serie = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15]
        originales = {
            "bloco": [(0, 0), (0, 15), (0, 33), (19, 51), (37, 66), (54, 78), (68, 90), (80, 97)],
            "paver": [(0, 0), (0, 10), (0, 22), (19, 40), (37, 61), (54, 78), (72, 92), (85, 100)],
        }
        for nombre, valores in originales.items():
            retenido = resolver_limites(serie, LIMITES_BR[nombre])
            pasante = resolver_limites(serie, LIMITES_BR[nombre], "pasante")
            self.assertEqual([(f["min"], f["max"]) for f in retenido], valores)
            self.assertTrue(all(f["origen"] == "exact" and f["apto_validacion"] for f in retenido))
            self.assertEqual([(f["min"], f["max"]) for f in pasante],
                             [(100 - hi, 100 - lo) for lo, hi in valores])
        self.assertEqual(convertir_limites(*convertir_limites(19, 40)), (19, 40))

    def test_interpolacion_logaritmica_y_dominio(self):
        filas = resolver_limites([math.sqrt(2 * 8), 9, 1, "Fundo"], {"2": [20, 40], "8": [0, 10]})
        self.assertEqual((filas[0]["min"], filas[0]["max"]), (10, 25))
        self.assertEqual(filas[0]["origen"], "interpolated")
        self.assertFalse(filas[0]["apto_validacion"])
        for fila in filas[1:]:
            self.assertEqual((fila["min"], fila["max"], fila["origen"]), (None, None, "unavailable"))
            self.assertFalse(fila["apto_validacion"])
        self.assertEqual(filas[-1]["motivo"], "pan_without_reference")
        self.assertEqual(resolver_limites([4], {})[0]["motivo"], "outside_domain")

    def test_intervalos_excluidos_y_representacion_pasante_de_origen(self):
        excluida = resolver_limites([4], {2: (60, 80), 8: (90, 100)},
                                   intervalos_excluidos=[(3, 5)])[0]
        self.assertEqual(excluida["motivo"], "excluded_interval")
        interrumpida = resolver_limites([4], {2: (60, 80), 6: None, 8: (90, 100)})[0]
        self.assertIsNone(interrumpida["max"])
        invertida = resolver_limites([2], {2: (60, 80)}, representacion_original="pasante")[0]
        self.assertEqual((invertida["min"], invertida["max"]), (20, 40))

    def test_receta_optima_reconstruye_la_curva_publicada(self):
        materiales = [
            {"nombre": "A", "pasantes": [90, 10]},
            {"nombre": "B", "pasantes": [65, 5]},
            {"nombre": "C", "pasantes": [80, 0]},
        ]
        with patch("scipy.optimize.minimize", return_value=SimpleNamespace(
            success=True, x=np.array([1 / 3] * 3),
        )), contextlib.redirect_stdout(io.StringIO()):
            curva, receta = optimizar_proporciones_materiales(materiales, [0, 0], [100, 100], [2, 1])
        self.assertAlmostEqual(sum(receta[m["nombre"]] for m in materiales), 100)
        for i, valor in enumerate(curva):
            self.assertAlmostEqual(valor, sum(
                receta[m["nombre"]] / 100 * m["pasantes"][i] for m in materiales
            ))

    def test_retenidos_desordenados_y_banda_ausente(self):
        app = Flask(__name__)
        app.register_blueprint(calculoPorRetenidos)
        payload = {
            "tamices": ["600 mic", "16 mm", "Pan", "2,4"],
            "materiales": [{"nombre": "A", "proporcion_pct": 100, "retido_ind_pct": [65, 10, 5, 20]}],
            "debug": False,
        }
        with app.test_client() as cliente:
            url = "/calculoPorRetenidos/granulometria/retido/"
            respuesta = cliente.post(url, json=payload)
            self.assertEqual(respuesta.status_code, 200)
            datos = respuesta.get_json()
            self.assertEqual(datos["tamices"], [16, 2.4, 0.6, "Fundo"])
            self.assertEqual(datos["mix_acum"], [10, 30, 95, 100])
            self.assertEqual(datos["fuller_ideal"][0], 100)
            self.assertIsNone(datos["faixas"]["paver"][0]["ok"])
            self.assertTrue(datos["faixas"]["paver"][1]["ok"])
            self.assertEqual(datos["faixas"]["paver"][1]["mix"], 30)
            sin_banda = cliente.post(url, json={**payload, "limites": {}}).get_json()
            self.assertEqual(sin_banda["mix_acum"], datos["mix_acum"])
            self.assertTrue(all(fila["min"] is None for fila in sin_banda["faixas"]["paver"]))
            self.assertIsNone(sin_banda["sugerencia_optimizacion"])


class CalculateAllTest(unittest.TestCase):
    def test_series_anterior_y_moreno(self):
        app = Flask(__name__)
        app.register_blueprint(densidadFuller)
        casos = [
            ([9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15],
             [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15],
             [([0, 2, 7, 38, 73, 233, 215, 65], 9),
              ([0, 0, 19, 263, 165, 112, 61, 10], 2),
              ([42, 303, 243, 142, 0, 0, 0, 0], 10),
              ([0, 8, 168, 570, 34, 6, 0, 0], 7),
              ([0, 0, 13, 227, 150, 91, 65, 56], 120)]),
            ([10, 8, 4, 2, 1, "500 mic", "250 µm", "0,125", "63 μm"],
             [10, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.063],
             [([10, 13, 726, 252, 14, 1.2, 1.1, 1, 1.5], 0.2),
              ([11, 3.1, 12.7, 39, 264.6, 260.4, 201.5, 175.5, 46.5], 11.3)]),
        ]
        for etiquetas, eje, materiales in casos:
            with self.subTest(eje=eje), contextlib.redirect_stdout(io.StringIO()):
                mezclas = [
                    {
                        "nombre": f"Material {i + 1}",
                        "tamices": etiquetas,
                        "porcentajes_reales": [
                            100 * (1 - sum(ret[:j + 1]) / (sum(ret) + fondo)) for j in range(len(ret))
                        ],
                    }
                    for i, (ret, fondo) in enumerate(materiales)
                ]
                response = app.test_client().post("/densidadFullerMultiple/", json={"mezclas": mezclas})
                self.assertEqual(response.status_code, 200)
                datos = response.get_json()
                self.assertEqual(datos["tamices_res"], eje)
                for material in datos["resultados"]:
                    self.assertEqual(material["tamices"], eje)
                    self.assertEqual(len(material["curva_ideal"]), len(eje))


if __name__ == "__main__":
    unittest.main()
