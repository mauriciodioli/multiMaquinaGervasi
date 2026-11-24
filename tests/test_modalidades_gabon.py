"""Regresión Fuller en Chromium y Flask.

Ejecutar con PYTHONPATH=src:. y GERVASI_CHROME apuntando a Chromium.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from flask import Flask

from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import calculoPorRetenidos


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src/static/js"
FIXTURES = ("gabon.js", "gabon_mezcla_2.js", "gabon3.js")
TOLERANCE = 1e-6


class ModalidadesGabonTest(unittest.TestCase):
    def test_modal_persistencia_y_equivalencia(self):
        app = Flask(__name__, template_folder=str(ROOT / "src/templates"))
        app.register_blueprint(calculoPorRetenidos)
        with app.test_request_context():
            html = app.jinja_env.get_template("autoDensidad/densidadFullerMultiple.html").render(
                usuario={"id": 1, "nombre": "Prueba"}, t_menu={},
                url_for=lambda endpoint, **kw: (STATIC.parent / kw["filename"]).as_uri() if endpoint == "static" else "/",
            )
        markup = html[html.index('<div id="modalTipoAgregado"'):html.index("<!-- Modal para seleccionar tipo de curva objetivo -->")]
        stylesheet = re.search(r'<link[^>]+calculoPorRetenidos\.css[^>]*>', html)[0]
        sources = [
            "i18n.js",
            "autoDensidad/agregados/agregaAgregado_densidadFuller.js",
            "autoDensidad/densidadFuller.js",
            "autoDensidad/calculoPorRetenidos/calculoPorRetenidos.js",
        ]
        scripts = "".join("<script>" + (STATIC / source).read_text() + "</script>" for source in sources)
        fixtures = []
        for name in FIXTURES:
            source = (ROOT / "tests" / name).read_text()
            definitions = source[source.index("const tamices"):source.index("const contenedor")]
            fixtures.append("(() => {" + definitions + "return {tamices, materiales};})()")
        checks = r"""
const check = (condition, detail) => { if (!condition) throw Error(detail); };
const container = document.getElementById('mezclasContainer');
const modal = document.getElementById('modalTipoAgregado');
const blank = () => {
    container.replaceChildren();
    localStorage.clear();
};
const select = () => {
    document.getElementById('addTest').click();
    check(modal.getAttribute('aria-hidden') === 'false', 'selector abierto');
    check(modal.querySelector('input[value="g"]').checked, 'gramos por defecto');
    modal.querySelector('input[value="porcentaje_retenido"]').checked = true;
    modal.querySelector('button[type="submit"]').click();
    check(modal.getAttribute('aria-hidden') === 'true', 'selector cerrado');
};
const assertions = [];
try {
for (const [lang, label, summary] of [
    ['es', 'Porcentaje (%)', 'Total retenido: 642.00 g | Peso de muestra: 642.00 g | Diferencia: 0.00 g'],
    ['en', 'Percentage (%)', 'Total retained: 642.00 g | Sample weight: 642.00 g | Difference: 0.00 g'],
    ['it', 'Percentuale (%)', 'Totale trattenuto: 642.00 g | Peso del campione: 642.00 g | Differenza: 0.00 g'],
]) {
    localStorage.setItem('lang', lang);
    abrirSelectorTipoAgregado();
    check(modal.querySelector('[data-i18n="sim.input_percentage"]').textContent === label, 'traducción '+lang);
    cerrarModal('modalTipoAgregado');
    agregarMezcla();
    const mezcla = container.lastElementChild;
    const input = mezcla.querySelector('.pesoCampione');
    check(getComputedStyle(input).paddingTop === '8px' && getComputedStyle(input).marginTop === '5px', 'estilo del peso');
    input.value = '642,0';
    const filas = [...mezcla.querySelectorAll('tbody tr')];
    filas.slice(1).forEach(fila => fila.remove());
    filas[0].querySelectorAll('td')[1].textContent = '642';
    prepararEnsayoGramos(mezcla);
    check(mezcla.querySelector('.balanceMasa').textContent === summary, 'balance '+lang);
}
for (const {tamices, materiales} of gabon) {
    const totalKg = materiales.reduce((s, m) => s + (m.kg || 1), 0);
    const props = materiales.map(m => 100 * (m.kg || 1) / totalKg);
    const payloads = [];
    for (const modo of ['g', 'porcentaje', 'mixto']) {
        blank();
        materiales.forEach((m, i) => {
            const porcentaje = modo === 'porcentaje' || (modo === 'mixto' && i % 2 === 1);
            if (porcentaje) select();
            else {
                agregarMezcla();
                check(modal.getAttribute('aria-hidden') === 'true', 'llamada directa sin modal');
            }
            const mezcla = container.lastElementChild;
            check(mezcla.dataset.unidadEntrada === (porcentaje ? 'porcentaje_retenido' : 'g'), 'modo');
            const peso = mezcla.querySelector('.pesoCampione');
            check(Boolean(peso) !== porcentaje, 'campo de peso');
            const total = m.valores.reduce((s, v) => s + v, m.fondo);
            if (peso) peso.value = String(total).replace('.', ',');
            mezcla.querySelector('.nombreProducto').value = m.nombre;
            const filasTamices = () => [...mezcla.querySelectorAll('tbody tr:not([data-fondo])')];
            if (porcentaje) {
                check(filasTamices().map(row => row.querySelector('td').textContent).join(',') ===
                    '9.5,6.3,4.8,2.4,1.2,0.6,0.3,0.15', 'serie inicial de porcentajes');
            }
            const botonTabla = mezcla.querySelector('[onclick="agregarFilaMultiple(this)"]');
            while (filasTamices().length < tamices.length) botonTabla.click();
            const rows = filasTamices();
            rows.slice(tamices.length).forEach(row => row.remove());
            const format = v => String(porcentaje ? 100 * v / total : v).replace('.', ',');
            tamices.forEach((tamiz, j) => {
                rows[j].querySelectorAll('td')[0].textContent = tamiz;
                rows[j].querySelectorAll('td')[1].textContent = format(m.valores[j]);
            });
            const fondo = mezcla.querySelector('[data-fondo] td:nth-of-type(2)');
            fondo.textContent = format(m.fondo);
            if (porcentaje) {
                fondo.textContent = '';
                let invalid = false;
                try { prepararEnsayoRetenido(mezcla, true); } catch { invalid = true; }
                check(invalid, 'fondo requerido');
                fondo.textContent = format(m.fondo);
            }
            agregarTablaAlocalStorage(mezcla);
        });
        container.replaceChildren();
        restaurarTablasDesdeLocalStorage();
        check(container.children.length === materiales.length, 'mismo número de agregados al restaurar');
        [...container.children].forEach((mezcla, i) => {
            const porcentaje = modo === 'porcentaje' || (modo === 'mixto' && i % 2 === 1);
            check(mezcla.dataset.unidadEntrada === (porcentaje ? 'porcentaje_retenido' : 'g'), 'modo restaurado');
            check(mezcla.querySelector('[data-fondo]'), 'fondo restaurado');
        });
        abrirModalProporciones(() => {});
        const inputs = [...document.querySelectorAll('#formProporciones .prop-input')];
        function setProps(values) {
            inputs.forEach((input, i) => {
                input.value = values[i];
                input.dispatchEvent(new Event('input', {bubbles: true}));
            });
        }
        if (inputs.length === 4) {
            for (const value of ['13', '13.5', '13,5']) {
                const expected = Number(value.replace(',', '.'));
                setProps([value, '20', '30', String(50 - expected)]);
                check(leerProporciones()[inputs[0].name] === expected, 'decimal de proporción '+value);
            }
        }
        setProps(props.map(p => String(p).replace('.', ',')));
        check(!document.getElementById('btnGuardarProporciones').disabled, 'proporciones válidas');
        document.getElementById('btnGuardarProporciones').click();
        const {payload} = construirPayloadRetido();
        check(payload.materiales.every((material, i) => material.proporcion_pct === props[i]), 'proporciones íntegras');
        payload.debug = false;
        payloads.push(payload);
    }
    assertions.push({tamices, materiales, props, payloads});
}
for (const value of ['13', '13.5', '13,5']) {
    check(numeroGranulometrico(value) === Number(value.replace(',', '.')), 'decimal de retenido '+value);
}
document.getElementById('testOutput').textContent = JSON.stringify(assertions);
} catch (error) {
    document.getElementById('testOutput').textContent = JSON.stringify({error: error.stack});
}
"""
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "modalidades.html"
            path.write_text(
                '<!doctype html><meta charset="utf-8">' + stylesheet
                + '<select id="selector-norma"></select>'
                '<button id="guardar-configuracion"></button><div id="mezclasContainer"></div>'
                '<button id="addTest" onclick="abrirSelectorTipoAgregado()">Add Aggregate</button>'
                '<script>const memoria = new Map(); Object.defineProperty(window,"localStorage",{value:{'
                'getItem:k=>memoria.get(k),setItem:(k,v)=>memoria.set(k,v),removeItem:k=>memoria.delete(k),'
                'clear:()=>memoria.clear()}});</script>' + markup + '<pre id="testOutput"></pre>' + scripts
                + "<script>const gabon = [" + ",".join(fixtures) + "];" + checks + "</script>"
            )
            browser = subprocess.run(
                [os.environ.get("GERVASI_CHROME", "chromium"), "--headless", "--no-sandbox", "--disable-gpu",
                 "--disable-dev-shm-usage", "--virtual-time-budget=1500", "--dump-dom", path.as_uri()],
                capture_output=True, text=True, check=True, timeout=30,
            )
        resultados = json.loads(re.search(r'<pre id="testOutput">(.*?)</pre>', browser.stdout, re.S)[1])
        self.assertIsInstance(resultados, list, resultados)
        client = app.test_client()
        for name, caso in zip(FIXTURES, resultados, strict=True):
            with self.subTest(ensayo=name):
                esperado = [0.0] * (len(caso["tamices"]) + 1)
                for material, prop in zip(caso["materiales"], caso["props"], strict=True):
                    masas = material["valores"] + [material["fondo"]]
                    total = sum(masas)
                    for i in range(len(masas)):
                        esperado[i] += prop * sum(masas[:i + 1]) / total
                curvas = []
                for payload in caso["payloads"]:
                    with contextlib.redirect_stdout(io.StringIO()):
                        resp = client.post("/calculoPorRetenidos/granulometria/retido/", json=payload)
                    self.assertEqual(resp.status_code, 200, resp.get_json())
                    data = resp.get_json()
                    self.assertEqual([m["proporcion_pct"] for m in data["materiales"]], caso["props"])
                    for actual, target in zip(data["mix_acum"], esperado, strict=True):
                        self.assertAlmostEqual(actual, target, delta=TOLERANCE)
                    curvas.append(data["mix_pasante"])
                error = max(abs(a - b) for curva in curvas[1:] for a, b in zip(curvas[0], curva, strict=True))
                self.assertLessEqual(error, TOLERANCE)
                print(f"{name}: {len(caso['materiales'])} agregado(s), diferencia máxima {error:.3g} puntos")
                invalido = caso["payloads"][1]
                invalido["materiales"][0]["retido_ind_pct"][-1] += 2 * TOLERANCE
                with contextlib.redirect_stdout(io.StringIO()):
                    resp = client.post("/calculoPorRetenidos/granulometria/retido/", json=invalido)
                self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
