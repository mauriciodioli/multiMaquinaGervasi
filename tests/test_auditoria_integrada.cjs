// Ejecutar desde la raíz con node --test tests/test_auditoria_integrada.cjs.
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { readFileSync } = require('node:fs');
const { test } = require('node:test');
const vm = require('node:vm');

const plantilla = 'autoDensidad/calculoPorRetenidos/auditoria.html';
const directorioJS = 'src/static/js/autoDensidad';
const rutaRetenidos = '/calculoPorRetenidos/granulometria/retido/?debug=1';
const rutaAuditoria = '/calculoPorRetenidos/auditoria';

const pythonDriver = String.raw`
import contextlib, io, json, re, sys
from pathlib import Path
from flask import Flask
sys.path.insert(0, 'src')
from controller.autoDensidad.calculoPorRetenidos.calculoPorRetenidos import calculoPorRetenidos

app = Flask(__name__, template_folder=str(Path('src/templates').resolve()))
app.register_blueprint(calculoPorRetenidos)
with app.test_request_context():
    if len(sys.argv) == 1:
        html = app.jinja_env.get_template('${plantilla}').render(auditoria_integrada=True)
        principal = app.jinja_env.get_template('autoDensidad/densidadFullerMultiple.html').render(
            usuario={'id': 1, 'nombre': 'Prueba'}, t_menu={}, url_for=lambda endpoint, **kw: '/' + endpoint)
        print(json.dumps({
            'html': html, 'principal': principal, 'script': re.search(r'<script>(.*?)</script>', html, re.S)[1],
        }))
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            response = app.test_client().post(sys.argv[1], json=json.load(sys.stdin))
        print(json.dumps({'status': response.status_code, 'data': response.get_json()}))
`;

function flask(path, body) {
  const proceso = spawnSync(process.env.GERVASI_PYTHON || 'python', ['-c', pythonDriver, ...(path ? [path] : [])], {
    input: JSON.stringify(body),
    encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: 'src:.', MPLBACKEND: 'Agg' }
  });
  assert.equal(proceso.status, 0, proceso.stderr);
  return JSON.parse(proceso.stdout);
}

function elemento() {
  return {
    open: false,
    dataset: {},
    style: {},
    classList: { add() {}, remove() {} },
    addEventListener() {},
    setAttribute() {},
    getContext() { return this; },
    showModal() { this.open = true; },
    close() { this.open = false; },
    replaceChildren(child) { this.textContent = child.textContent; this.innerHTML = ''; }
  };
}

test('la curva y el modal comparten el cálculo real a través de las dos rutas Flask', async () => {
  const datos = flask();
  const { script, html, principal } = datos;
  const sieves = [9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15];
  const materials = [
    ['Areia 1', 20, [0, 2, 7, 38, 73, 233, 215, 65], 9, 642],
    ['Areia 2', 20, [0, 0, 19, 263, 165, 112, 61, 10], 2, 632],
    ['Brita 1', 25, [42, 303, 243, 142, 0, 0, 0, 0], 10, 740],
    ['Brita 2', 25, [0, 8, 168, 570, 34, 6, 0, 0], 7, 793],
    ['Areia Ind.', 10, [0, 0, 13, 227, 150, 91, 65, 56], 120, 722]
  ];
  const expectedPassing = [98.58108108, 88.03008249, 73.52489027, 38.10722803,
    27.46212448, 15.20971078, 5.68123471, 2.56423363, 0];
  assert.equal(principal.match(/id="modalAuditoria"/g)?.length, 1);
  assert.match(principal, /id="btnAuditoria" onclick="abrirAuditoriaDesdeModal\(\)"/);
  assert.match(html, /<form method="dialog">/);
  assert.doesNotMatch(html, /sessionStorage|window\.open|tablasCargadas/);

  const boton = principal.match(/id="btnAuditoria" onclick="([^"]+)"/)[1];
  const proporciones = Object.fromEntries(materials.map(([nombre, porcentaje]) => [nombre, porcentaje]));
  const tablas = materials.map(([nombre, , masas, fondo, total], indice) => {
    const filas = [...sieves.map((tamiz, i) => [tamiz, masas[i]]), ['Fundo', fondo]].map(([tamiz, masa]) => ({
      dataset: { fondo: String(tamiz === 'Fundo') },
      querySelectorAll: () => [{ textContent: String(tamiz) }, { textContent: String(masa) }]
    }));
    return {
      dataset: { unidadEntrada: 'g', mezclaId: `mezcla-${indice}` },
      querySelectorAll: () => filas,
      querySelector: selector => ({
        value: selector === '.nombreProducto' ? nombre : String(total)
      })
    };
  });
  const elementos = new Map();
  const peticiones = [];
  const graficos = [];
  const getElementById = id => {
    if (!elementos.has(id)) elementos.set(id, elemento());
    return elementos.get(id);
  };

  const contexto = vm.createContext({
    document: {
      getElementById,
      querySelectorAll: selector => selector === '.mezcla' ? tablas : [],
      body: { appendChild() {} },
      createElement: elemento,
      addEventListener() {}
    },
    I18N: { getLang: () => 'es' },
    localStorage: { getItem(key) {
      assert.equal(key, 'proporcionesRetido', 'La auditoría intentó leer el almacenamiento');
      return JSON.stringify(proporciones);
    } },
    console: { log() {}, warn() {}, error() {} },
    requestAnimationFrame: callback => callback(),
    Chart: class {
      constructor(canvas, config) { graficos.push(config); }
      destroy() {}
    },
    open() { assert.fail('Se abrió otra ventana'); },
    addEventListener() {},
    alert: assert.fail,
    notificarPrueba(level, title, message) { assert.notEqual(level, 'error', message); },
    async fetch(path, options) {
      const entrada = JSON.parse(options.body);
      const { status, data } = flask(path, entrada);
      peticiones.push({ path, entrada, data });
      return { ok: status === 200, status, text: async () => JSON.stringify(data), json: async () => data };
    }
  });
  contexto.window = contexto;
  const fuller = readFileSync(`${directorioJS}/densidadFuller.js`, 'utf8');
  vm.runInContext(fuller.slice(fuller.indexOf('function esFilaFondoFuller'), fuller.indexOf('function datosMezclaParaCalculo')), contexto);
  vm.runInContext(script, contexto);
  vm.runInContext(readFileSync(`${directorioJS}/calculoPorRetenidos/calculoPorRetenidos.js`, 'utf8'), contexto);
  // La prueba conserva el gráfico de retenidos y el de auditoría. Sustituye el
  // DOM auxiliar de las tablas y sugerencias de la pantalla principal.
  vm.runInContext('renderRetidoTablitas = () => {}; renderSugerenciaDivision = () => {}; abrirModal = () => {}; notify = window.notificarPrueba;', contexto);

  const dialogo = getElementById('modalAuditoria');
  const resultado = getElementById('auditoriaResultado');
  await vm.runInContext(boton, contexto);
  assert.equal(dialogo.open, true);
  assert.match(resultado.textContent, /retenidos/);
  assert.equal(peticiones.length, 0);
  dialogo.close();

  await vm.runInContext('calcularRetenidoBR()', contexto);
  const curva = peticiones[0];
  assert.equal(curva.path, rutaRetenidos);
  assert.equal(curva.data.tamices.length, expectedPassing.length);
  curva.data.mix_pasante.forEach((valor, i) => assert.ok(Math.abs(valor - expectedPassing[i]) < 0.1));
  const curvaVisible = graficos[0].data.datasets.find(serie => serie.label === 'Pasante');
  assert.deepEqual(Array.from(curvaVisible.data, punto => punto.y).reverse().slice(1), curva.data.mix_pasante);

  proporciones[materials[0][0]] += 5;
  proporciones[materials[1][0]] -= 5;
  await vm.runInContext(boton, contexto);
  const auditoria = peticiones[1];
  assert.equal(auditoria.path, rutaAuditoria);
  assert.equal(auditoria.data.exito, true, auditoria.data.error);
  assert.deepEqual(auditoria.entrada.tamices, sieves);
  assert.deepEqual(auditoria.entrada.pasante_real, curva.data.mix_pasante.slice(0, -1));
  assert.deepEqual(auditoria.entrada.banda_min, curva.data.faixas.paver.slice(0, -1).map(limite => 100 - limite.max));
  assert.deepEqual(auditoria.entrada.banda_max, curva.data.faixas.paver.slice(0, -1).map(limite => 100 - limite.min));
  assert.equal(auditoria.entrada.materiales.length, materials.length);
  auditoria.entrada.materiales.forEach((material, i) => {
    const [nombre, porcentaje, masas, fondo, total] = materials[i];
    assert.equal(material.nombre, nombre);
    assert.equal(material.mezclaId, `mezcla-${i}`);
    assert.equal(material.proporcion_pct, porcentaje);
    assert.equal(material.peso, porcentaje / 100);
    assert.deepEqual(material.pesos_retenidos_g, masas);
    assert.equal(material.peso_fondo_g, fondo);
    assert.equal(material.peso_campione_g, total);
    assert.equal(material.peso_total_recuperado_g, total);
    assert.deepEqual(material.retido_ind_pct, masas.map(masa => 100 * masa / total));
  });
  assert.deepEqual(auditoria.data.data.meta.pasante_entrada_original, auditoria.entrada.pasante_real);
  assert.deepEqual(auditoria.data.data.para_grafico.tamices, sieves);
  assert.equal(auditoria.data.data.para_grafico.pasante_real.length, sieves.length);
  assert.match(resultado.innerHTML, /graficoComparacion/);
  const informe = resultado.innerHTML;

  dialogo.close();
  await vm.runInContext(boton, contexto);
  assert.equal(dialogo.open, true);
  assert.equal(peticiones.length, 2);
  assert.equal(resultado.innerHTML, informe);

  dialogo.close();
  await vm.runInContext('calcularRetenidoBR()', contexto);
  await vm.runInContext(boton, contexto);
  const auditoriaActualizada = peticiones[3];
  assert.equal(auditoriaActualizada.data.exito, true);
  assert.equal(auditoriaActualizada.entrada.materiales[0].proporcion_pct, proporciones[materials[0][0]]);
  assert.notDeepEqual(auditoriaActualizada.entrada.pasante_real, auditoria.entrada.pasante_real);

  dialogo.close();
  await vm.runInContext('calcularRetenidoBR()', contexto);
  vm.runInContext('calculoRetenidoMostrado.resultado.faixas.paver[0].min = null', contexto);
  await vm.runInContext(boton, contexto);
  assert.equal(peticiones.length, 5);
  assert.match(resultado.textContent, /límites válidos/);
});
