"""Ejecutar con PYTHONPATH=src:. MPLBACKEND=Agg python tests/test_finura_dinamica.py."""
import contextlib
import io
import json
import math
import os
import unittest
from unittest.mock import patch

from flask import Flask

from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import (
    _finura_modulus, calculoPorRetenidos,
)


class FinuraDinamicaTest(unittest.TestCase):
    referencia = {"id": "Referencia histórica Gervasi", "tamices": [4.8, 2.4, 1.2, 0.6, 0.3, 0.15]}

    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(calculoPorRetenidos)
        self.app = app
        self.client = app.test_client()

    def calcular(self, aberturas, muestras, fondo_explicito=True, **opciones):
        materiales = []
        for nombre, proporcion, masas, fondo in muestras:
            material = {"nombre": nombre, "proporcion_pct": proporcion, "pesos_retenidos_g": masas}
            if fondo is not None:
                material["peso_fondo_g"] = fondo
            materiales.append(material)
        with contextlib.redirect_stdout(io.StringIO()):
            response = self.client.post("/calculoPorRetenidos/granulometria/retido/", json={
                "tamices": aberturas + (["Pan"] if fondo_explicito else []),
                "materiales": materiales, "debug": False, **opciones,
            })
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def validar_curvas(self, datos, muestras):
        fondo_explicito = datos["tamices"][-1] == "Fundo"
        estimados = []
        for (_, proporcion, masas, fondo), material in zip(muestras, datos["materiales"]):
            total = sum(masas) + (fondo or 0)
            self.assertEqual(material["pesos_retenidos_g"], masas)
            self.assertEqual(material["peso_fondo_g"], fondo or 0)
            self.assertAlmostEqual(material["peso_total_recuperado_g"], total)
            retenido = [100 * masa / total for masa in (masas + ([fondo or 0] if fondo_explicito else []))]
            for medido, esperado in zip(material["ret_ind"], retenido, strict=True):
                self.assertAlmostEqual(medido, esperado, delta=0.00501)
            acumulado = [sum(retenido[:i + 1]) for i in range(len(retenido))]
            estimados.append([valor * proporcion / 100 for valor in acumulado])
            for acum, pasante, esperado in zip(material["ret_acum"], material["pasante"], acumulado, strict=True):
                self.assertAlmostEqual(acum, esperado, delta=0.00501)
                self.assertAlmostEqual(acum + pasante, 100)
        acumulados = datos["mix_acum"]
        for medido, esperado in zip(acumulados, map(sum, zip(*estimados)), strict=True):
            self.assertAlmostEqual(medido, esperado, delta=0.056)
        self.assertEqual(acumulados, sorted(acumulados))
        self.assertEqual(datos["mix_pasante"], [100 - v for v in acumulados])
        self.assertEqual(acumulados[-1], 100)

    def test_a_conserva_curva_y_mf_historico_configurado(self):
        self.app.config.update(
            METODO_FINURA="historico",
            METODOS_FINURA={"historico": {**self.referencia, "permitir_interpolacion": True}},
        )
        datos = self.calcular([9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15], [
            ("Areia 1", 20, [0, 2, 7, 38, 73, 233, 215, 65], 9),
            ("Areia 2", 20, [0, 0, 19, 263, 165, 112, 61, 10], 2),
            ("Brita 1", 25, [42, 303, 243, 142, 0, 0, 0, 0], 10),
            ("Brita 2", 25, [0, 8, 168, 570, 34, 6, 0, 0], 7),
            ("Areia Ind.", 10, [0, 0, 13, 227, 150, 91, 65, 56], 120),
        ])
        self.assertEqual([round(v, 1) for v in datos["mix_pasante"]],
                         [98.6, 88.0, 73.5, 38.1, 27.5, 15.2, 5.7, 2.6, 0.0])
        self.assertEqual(datos["modulo_finura"], 4.37)
        self.assertEqual(datos["finura"]["estado"], "calculado")
        self.assertEqual({p["origen"] for p in datos["finura"]["puntos"]}, {"medido"})

    def test_b_moreno_masas_y_mf_estimado_con_permiso(self):
        metodo = {**self.referencia, "permitir_interpolacion": True}
        muestras = [
            ("F2", 56, [10, 13, 726, 252, 14, 1.2, 1.1, 1, 1.5], 0.2),
            ("BARILE", 44, [11, 3.1, 12.7, 39, 264.6, 260.4, 201.5, 175.5, 46.5], 11.3),
        ]
        with patch.dict(os.environ, {
            "GERVASI_METODO_FINURA": "historico",
            "GERVASI_METODOS_FINURA": json.dumps({"historico": metodo}),
        }):
            datos = self.calcular([10, 8, 4, 2, 1, "500 µm", 0.25, 0.125, "63 mic"], muestras)
        self.validar_curvas(datos, muestras)
        esperado = [98.9790615, 98.1323407, 57.7286654, 42.2202043, 30.0997828,
                    18.8622936, 10.1572057, 2.5730525, 0.4957698]
        for calculado, referencia in zip(datos["mix_pasante"][:-1], esperado, strict=True):
            self.assertAlmostEqual(calculado, referencia, places=7)
        self.assertAlmostEqual(sum(datos["mix_acum"][:-1]) / 100, 5.4075162, places=7)
        finura = datos["finura"]
        self.assertEqual(finura["estado"], "estimado")
        self.assertEqual(finura["valor"], 4.13)
        self.assertEqual(finura["metodo"], self.referencia["id"])
        self.assertEqual({p["origen"] for p in finura["puntos"]}, {"interpolado"})
        eje, curva = datos["tamices"][:-1], datos["mix_acum"][:-1]
        valores = []
        for d in self.referencia["tamices"]:
            i = next(i for i, x in enumerate(eje) if x < d)
            factor = math.log(d / eje[i]) / math.log(eje[i - 1] / eje[i])
            valores.append(curva[i] + (curva[i - 1] - curva[i]) * factor)
        self.assertEqual(finura["valor"], round(sum(valores) / 100, 2))

    def test_c_serie_nueva_tres_materiales_y_sin_referencia(self):
        muestras = [
            ("A", 37, [1.4, 7.1, 3.1, 2.8, 1.4], 0.5),
            ("B", 28, [0, 1.6, 7.3, 8.4, 4.3], 1.9),
            ("C", 35, [0.1, 0.7, 1.4, 7.5, 3.6], 3.1),
        ]
        indices = [3, 4, 2, 0, 1]
        desordenadas = [(nombre, p, [masas[i] for i in indices], fondo) for nombre, p, masas, fondo in muestras]
        datos = self.calcular([0.82, 0.09, 3, 14, 7.2], desordenadas, fondo_explicito=False,
                              metodo_finura=None)
        self.assertEqual(datos["tamices"], [14, 7.2, 3, 0.82, 0.09, "Fundo"])
        self.validar_curvas(datos, muestras)
        self.assertEqual(datos["finura"]["motivo"], "sin_referencia")
        self.assertIsNone(datos["modulo_finura"])
        self.assertEqual(datos["finura"]["indice_descriptivo"]["valor"],
                         round(sum(datos["mix_acum"][:-1]) / 5, 2))

    def test_sin_fondo_y_referencia_sin_identificador(self):
        datos = self.calcular([5, 2], [("A", 100, [0.1, 9.9], None)], fondo_explicito=False,
                              metodo_finura={"tamices": [5]})
        self.assertEqual(datos["tamices"], [5, 2])
        self.assertEqual(datos["finura"]["valor"], 0.01)

    def test_referencia_experimental_cede_ante_metodo_configurado(self):
        automatico = {"id": "FM_AUTO_prueba", "tamices": [5, 2], "permitir_interpolacion": False}
        argumentos = ([5, 2], [("A", 100, [20, 80], None)])
        self.app.config["METODO_FINURA"] = None
        datos = self.calcular(*argumentos, fondo_explicito=False, metodo_finura_automatico=automatico)
        self.assertEqual(datos["modulo_finura"], 1.2)
        self.assertEqual(datos["finura"]["tipo_metodo"], "experimental")
        self.app.config["METODO_FINURA"] = {"id": "Referencia configurada", "tamices": [5]}
        datos = self.calcular(*argumentos, fondo_explicito=False, metodo_finura_automatico=automatico)
        self.assertEqual(datos["modulo_finura"], 0.2)
        self.assertEqual(datos["finura"]["metodo"], "Referencia configurada")
        self.assertNotIn("tipo_metodo", datos["finura"])

    def test_seleccion_vacia_o_perfil_desconocido(self):
        muestras = [("A", 100, [20, 80], None)]
        self.app.config["METODO_FINURA"] = " "
        datos = self.calcular([5, 2], muestras, fondo_explicito=False)
        self.assertEqual(datos["finura"]["motivo"], "sin_referencia")
        datos = self.calcular([5, 2], muestras, fondo_explicito=False, metodo_finura="desconocido")
        self.assertEqual(datos["finura"]["motivo"], "referencia_invalida")
        self.assertEqual(datos["finura"]["metodo"], "desconocido")
        self.assertIsNone(datos["modulo_finura"])

    def test_datos_faltantes_sin_extrapolar_y_cero_medido(self):
        datos = _finura_modulus([0, 100], [8, 1], {"tamices": [8, 10], "permitir_interpolacion": True})
        self.assertEqual(datos["estado"], "no_calculable")
        self.assertEqual(datos["tamices_faltantes"], [10])
        self.assertIsNone(datos["valor"])
        self.assertIsNone(_finura_modulus([0, 100], [8, 1], {"tamices": [2]})["valor"])
        self.assertEqual(_finura_modulus([0, 100], [8, 1], {"tamices": [8]})["valor"], 0)
        self.assertEqual(_finura_modulus([], [8])["motivo"], "curva_invalida")
        self.assertEqual(_finura_modulus([0, 100], [8, 1], {"tamices": [8, "8000 µm"]})["motivo"],
                         "referencia_invalida")


if __name__ == "__main__":
    unittest.main()
