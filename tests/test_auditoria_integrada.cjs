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
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            response = app.test_client().post(sys.argv[1], json=json.load(sys.stdin))
        funciones = re.findall(r'^FUNCION: (\w+)', salida.getvalue(), re.M)
        print(json.dumps({'status': response.status_code, 'data': response.get_json(), 'funciones': funciones}))
`;

function flask(path, body) {
  const proceso = spawnSync(process.env.GERVASI_PYTHON || 'python', ['-c', pythonDriver, ...(path ? [path] : [])], {
    input: JSON.stringify(body),
    encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: 'src:.', MPLBACKEND: 'Agg', GERVASI_METODO_FINURA: '' }
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
    removeEventListener() {},
    children: [],
    appendChild(child) { this.children.push(child); },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    focus() {},
    setAttribute(nombre, valor) { this[nombre] = valor; },
    getContext() { return this; },
    showModal() { this.open = true; },
    close() { this.open = false; },
    get valueAsNumber() { return this.value === '' || this.value == null ? NaN : Number(this.value); },
    replaceChildren(child) { this.children = child ? [child] : []; this.textContent = child?.textContent || ''; this.innerHTML = ''; }
  };
}

test('tres series recorren el motor y el informe original de Auditoría', async () => {
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
  const prepararTablas = (serie, insumos) => insumos.map(([nombre, , masas, fondo, total], indice) => {
    const filas = [...serie.map((tamiz, i) => [tamiz, masas[i]]), ['Fundo', fondo]].map(([tamiz, masa]) => ({
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
  const tablas = prepararTablas(sieves, materials);
  const elementos = new Map();
  const peticiones = [];
  const controles = [];
  const graficos = [];
  const getElementById = id => {
    if (!elementos.has(id)) elementos.set(id, Object.assign(elemento(), { id }));
    return elementos.get(id);
  };

  let simularReferenciaOmitida = false;
  let desdeBotonRetenidos = false;
  let perfilGuardado;
  const contexto = vm.createContext({
    document: {
      getElementById,
      querySelectorAll: selector => selector === '.mezcla' ? tablas : [],
      body: elemento(),
      createElement: elemento,
      addEventListener() {}
    },
    I18N: { getLang: () => 'es', applyTranslations() {} },
    localStorage: { getItem(key) {
      if (key === 'perfilGranulometricoFuller') return perfilGuardado ?? null;
      if (key === 'tablasCargadas' && desdeBotonRetenidos) {
        return JSON.stringify(Object.keys(proporciones).map(nombre => ({ nombre })));
      }
      assert.equal(key, 'proporcionesRetido', 'La auditoría intentó leer el almacenamiento');
      return JSON.stringify(proporciones);
    }, setItem(key, valor) { if (key === 'perfilGranulometricoFuller') perfilGuardado = valor; } },
    console: { log() {}, warn() {}, error() {} },
    setTimeout: callback => callback(),
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
      const recibida = simularReferenciaOmitida ? { ...entrada, metodo_finura: null } : entrada;
      const { status, data, funciones } = flask(path, recibida);
      (entrada.solo_validar_limites ? controles : peticiones).push({ path, entrada, data, funciones });
      return { ok: status === 200, status, text: async () => JSON.stringify(data), json: async () => data };
    }
  });
  contexto.window = contexto;
  const fuller = readFileSync(`${directorioJS}/densidadFuller.js`, 'utf8');
  vm.runInContext(fuller.slice(fuller.indexOf('function esFilaFondoFuller'), fuller.indexOf('function datosMezclaParaCalculo')), contexto);
  vm.runInContext(script, contexto);
  vm.runInContext(readFileSync(`${directorioJS}/calculoPorRetenidos/calculoPorRetenidos.js`, 'utf8'), contexto);
  vm.runInContext('renderSugerenciaDivision = () => {}; notify = window.notificarPrueba;', contexto);

  const dialogo = getElementById('modalAuditoria');
  const resultado = getElementById('auditoriaResultado');
  await vm.runInContext(boton, contexto);
  assert.equal(dialogo.open, true);
  assert.match(resultado.textContent, /retenidos/);
  assert.equal(peticiones.length, 0);
  dialogo.close();

  const metodo = getElementById('metodoFinuraId');
  const serie = getElementById('metodoFinuraTamices');
  const interpolar = getElementById('metodoFinuraInterpolacion');
  const modalFinura = getElementById('modalConfigurarFinura');
  const confirmar = () => getElementById('formConfigurarFinura').onsubmit({ preventDefault() {} });
  const entradaAuditoriaActual = () => JSON.parse(vm.runInContext(
    'JSON.stringify(prepararEntradaAuditoria(calculoRetenidoMostrado))', contexto
  ));
  const referenciaHistorica = {
    id: 'Referencia histórica Gervasi', tamices: [4.8, 2.4, 1.2, 0.6, 0.3, 0.15], permitir_interpolacion: true
  };
  assert.match(principal, /id="metodoFinuraTamices"/);
  assert.equal(vm.runInContext('construirPayloadRetido().payload.metodo_finura', contexto), undefined);
  metodo.value = 'historico';
  assert.equal(vm.runInContext('construirPayloadRetido().payload.metodo_finura', contexto), 'historico');
  metodo.value = '';
  await vm.runInContext('calcularRetenidoBR(true)', contexto);
  assert.equal(controles[0].data.compatible, true);
  assert.notEqual(getElementById('modalLimitesGranulometricos')['aria-hidden'], 'false');
  const curva = peticiones[0];
  assert.equal(curva.path, rutaRetenidos);
  assert.equal(curva.data.finura.motivo, 'sin_referencia');
  assert.equal(modalFinura['aria-hidden'], 'false');
  assert.equal(getElementById('finuraTamicesDetectados').textContent, sieves.join(' · '));
  assert.equal(curva.data.tamices.length, expectedPassing.length);
  curva.data.mix_pasante.forEach((valor, i) => assert.ok(Math.abs(valor - expectedPassing[i]) < 0.1));
  const curvaVisible = graficos[0].data.datasets.find(serie => serie.label === 'Pasante');
  assert.deepEqual(Array.from(curvaVisible.data, punto => punto.y).reverse(), curva.data.mix_pasante.slice(0, -1));

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
  getElementById('reintentoFinuraId').value = referenciaHistorica.id;
  getElementById('reintentoFinuraTamices').value = '4,8; 2,4; 1,2; 600 µm; 0,3; 0,15';
  getElementById('reintentoFinuraInterpolacion').checked = true;
  const reintentoHistorico = confirmar();
  await vm.runInContext(boton, contexto);
  assert.equal(resultado.innerHTML, informe, 'Auditoría disponible durante el reintento de MF');
  await reintentoHistorico;
  assert.equal(peticiones.length, 3);
  assert.deepEqual(peticiones[2].entrada, { ...curva.entrada, metodo_finura: referenciaHistorica });
  assert.equal(peticiones[2].data.modulo_finura, 4.37);
  assert.equal(peticiones[2].data.finura.estado, 'calculado');
  assert.equal(peticiones[2].data.finura.metodo, referenciaHistorica.id);
  assert.equal(modalFinura['aria-hidden'], 'true');
  assert.deepEqual(entradaAuditoriaActual(), auditoria.entrada);
  dialogo.close();
  await vm.runInContext(boton, contexto);
  assert.equal(peticiones.length, 3);
  assert.equal(resultado.innerHTML, informe);

  dialogo.close();
  metodo.value = referenciaHistorica.id;
  serie.value = referenciaHistorica.tamices.join('; ');
  interpolar.checked = true;
  await vm.runInContext('calcularRetenidoBR()', contexto);
  await vm.runInContext(boton, contexto);
  const auditoriaActualizada = peticiones[4];
  assert.equal(auditoriaActualizada.data.exito, true);
  assert.equal(auditoriaActualizada.entrada.materiales[0].proporcion_pct, proporciones[materials[0][0]]);
  assert.notDeepEqual(auditoriaActualizada.entrada.pasante_real, auditoria.entrada.pasante_real);

  const tamicesMoreno = [10, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.063];
  const moreno = [
    ['F2', 56, [10, 13, 726, 252, 14, 1.2, 1.1, 1, 1.5], 0.2, 1020],
    ['BARILE', 44, [11, 3.1, 12.7, 39, 264.6, 260.4, 201.5, 175.5, 46.5], 11.3, 1025.6]
  ];
  const etiquetas = [10, 8, 4, 2, 1, '500 mic', '250 µm', '0,125', '63 μm'];
  tablas.splice(0, tablas.length, ...prepararTablas(etiquetas, moreno));
  for (const nombre of Object.keys(proporciones)) delete proporciones[nombre];
  for (const [nombre, prop] of moreno) proporciones[nombre] = prop;
  dialogo.close();
  const nombreMetodo = 'Serie medida completa';
  metodo.value = serie.value = '';
  getElementById('formProporciones').querySelectorAll = () =>
    Object.entries(proporciones).map(([name, value]) => ({ name, value }));
  desdeBotonRetenidos = true;
  const botonRetenidos = principal.match(/onclick="(abrirProporcionesYCalcular\(\))"/)[1];
  vm.runInContext(botonRetenidos, contexto);
  const estadoMF = getElementById('estadoFinuraAutomatica');
  const botonProporciones = getElementById('btnGuardarProporciones');
  const formularioProporciones = getElementById('formProporciones');
  assert.equal(estadoMF.className, 'text-success');
  assert.match(estadoMF.textContent, /experimental/);
  assert.match(metodo.value, /^FM_AUTO_\d{8}_\d{6}_/);
  assert.equal(serie.value, tamicesMoreno.join('; '));
  assert.equal(interpolar.checked, false);
  assert.equal(getElementById('finuraAvanzada').open, false);
  const barile = tablas[1];
  const filasBarile = barile.querySelectorAll;
  barile.querySelectorAll = () => filasBarile().filter((_, i) => i !== 8);
  formularioProporciones.oninput();
  assert.match(estadoMF.textContent, /BARILE: 0\.063 mm/);
  assert.equal(botonProporciones.disabled, true);
  barile.querySelectorAll = filasBarile;
  formularioProporciones.oninput();
  assert.equal(botonProporciones.disabled, false);
  estadoMF.dataset.metodoServidor = 'true';
  formularioProporciones.oninput();
  assert.equal(serie.value, '');
  assert.equal(vm.runInContext('construirPayloadRetido().payload.metodo_finura_automatico', contexto), undefined);
  estadoMF.dataset.metodoServidor = 'false';
  getElementById('btnGuardarProporciones').onclick({ preventDefault() {} });
  desdeBotonRetenidos = false;
  await new Promise(setImmediate);

  assert.equal(controles.at(-1).data.compatible, false);
  const modalLimites = getElementById('modalLimitesGranulometricos');
  assert.equal(modalLimites['aria-hidden'], 'false');
  assert.match(getElementById('perfilNombre').value, /^BLOCK_AUTO_\d{8}_\d{6}_/);
  assert.equal(getElementById('perfilProducto').value, 'bloco');
  assert.match(getElementById('perfilFuente').value, /LIMITES_BR.*Interpolación logarítmica/);
  assert.equal(getElementById('perfilInterpolar').checked, true);
  assert.equal(peticiones.length, 5, 'La comprobación no ejecuta el cálculo');
  const filasPerfil = getElementById('perfilFilas').children;
  assert.equal(filasPerfil.length, 9);
  assert.equal(filasPerfil.filter(f => f.children[3].className === 'text-warning').length, 8);
  assert.match(filasPerfil[1].children[2].children[0].value, /^\d+\.\d{2}$/);
  assert.equal(filasPerfil[8].children[0].textContent, 0.063);
  assert.equal(filasPerfil[8].children[3].className, 'text-danger');
  assert.equal(filasPerfil[8].children[1].children[0].value, '');
  assert.match(filasPerfil[8].children[2].children[0].className, /is-invalid/);
  vm.runInContext("cerrarModal('modalLimitesGranulometricos')", contexto);
  // Mantener también la regresión del informe con banda incompleta para clientes directos.
  metodo.value = serie.value = '';
  await vm.runInContext('calcularRetenidoBR()', contexto);

  const inicialMoreno = peticiones[5];
  assert.equal(inicialMoreno.data.finura.motivo, 'sin_referencia');
  assert.equal(inicialMoreno.data.modulo_finura, null);
  assert.equal(inicialMoreno.entrada.metodo_finura, undefined);
  assert.match(principal, /id="modalConfigurarFinura" class="dpia-modal" aria-hidden="true"/);
  assert.equal(modalFinura['aria-hidden'], 'false');
  assert.equal(getElementById('finuraTamicesDetectados').textContent, tamicesMoreno.join(' · '));
  await vm.runInContext(boton, contexto);
  const auditoriaMoreno = peticiones[6];
  const informeMoreno = resultado.innerHTML;
  dialogo.close();
  await confirmar();
  assert.equal(peticiones.length, 7);
  assert.match(getElementById('finuraConfiguracionError').textContent, /Ingresá un método/);
  getElementById('reintentoFinuraId').value = nombreMetodo;
  getElementById('reintentoFinuraTamices').value = tamicesMoreno.join('; ');
  getElementById('reintentoFinuraInterpolacion').checked = false;
  proporciones.F2 = 50;
  proporciones.BARILE = 50;
  simularReferenciaOmitida = true;
  await confirmar();
  assert.equal(peticiones.length, 8);
  assert.equal(modalFinura['aria-hidden'], 'false');
  assert.match(getElementById('finuraConfiguracionError').textContent, /sigue sin reconocer la referencia/);
  simularReferenciaOmitida = false;
  await confirmar();
  assert.equal(peticiones.length, 9);
  assert.equal(modalFinura['aria-hidden'], 'true');
  const curvaMoreno = peticiones[8];
  assert.deepEqual(curvaMoreno.entrada, { ...inicialMoreno.entrada, metodo_finura: {
    id: nombreMetodo, tamices: tamicesMoreno, permitir_interpolacion: false
  }});
  assert.deepEqual(curvaMoreno.data.mix_pasante, inicialMoreno.data.mix_pasante);
  assert.equal(curvaMoreno.data.modulo_finura, 5.41);
  assert.equal(curvaMoreno.data.finura.estado, 'calculado');
  assert.equal(curvaMoreno.data.finura.metodo, nombreMetodo);
  assert.match(getElementById('retidoFinura').textContent, /MF calculado.*5,41.*Serie medida completa/);
  assert.deepEqual(curvaMoreno.data.tamices, [...tamicesMoreno, 'Fundo']);
  const tabla = getElementById('retidoTables').innerHTML;
  assert.match(tabla, /≈ [0-9]+\.[0-9]{2}/);
  assert.match(tabla, /title="Fuera del dominio de referencia\.">N\/D/);
  const acumulados = tamicesMoreno.map((_, i) => moreno.reduce((suma, [, prop, masas, , total]) =>
    suma + prop * masas.slice(0, i + 1).reduce((a, b) => a + b, 0) / total, 0));
  curvaMoreno.data.mix_acum.slice(0, -1).forEach((valor, i) => {
    assert.ok(Math.abs(valor - acumulados[i]) < 0.1);
    assert.equal(curvaMoreno.data.mix_pasante[i], 100 - valor);
  });
  assert.equal(curvaMoreno.data.mix_pasante.at(-1), 0);
  assert.ok(curvaMoreno.data.mix_acum.every((valor, i, serie) => i === 0 || serie[i - 1] <= valor));
  assert.ok(curvaMoreno.data.mix_pasante.every((valor, i, serie) => i === 0 || serie[i - 1] >= valor));
  await vm.runInContext(boton, contexto);
  assert.equal(peticiones.length, 9);
  assert.equal(resultado.innerHTML, informeMoreno);
  assert.deepEqual(entradaAuditoriaActual(), auditoriaMoreno.entrada);
  assert.equal(auditoriaMoreno.path, rutaAuditoria);
  assert.equal(auditoriaMoreno.data.exito, true, auditoriaMoreno.data.error);
  assert.equal(auditoriaMoreno.data.data.validacion_bandas.completa, false);
  assert.equal(auditoriaMoreno.data.data.validacion_bandas.liberacion_produccion, false);
  assert.ok(auditoriaMoreno.data.data.validacion_bandas.no_evaluadas.includes('agregados_correctivos'));
  assert.equal(auditoriaMoreno.data.data.fase_1.error_total, null);
  assert.equal(auditoriaMoreno.data.data.fase_5_virtual.generada, false);
  assert.equal(auditoriaMoreno.data.data.auditoria_industrial.decision_final.estado, 'NO LIBERAR');
  assert.equal(auditoriaMoreno.data.data.orden_operativa_real, undefined);
  assert.deepEqual(auditoriaMoreno.entrada.bandas.paver.map(limite => limite.origen),
    [...Array(8).fill('interpolated'), 'unavailable']);
  assert.equal(auditoriaMoreno.entrada.banda_min.at(-1), null);
  assert.equal(auditoriaMoreno.entrada.banda_max.at(-1), null);
  assert.equal(auditoriaMoreno.entrada.materiales.reduce((suma, m) => suma + m.proporcion_pct, 0), 100);
  auditoriaMoreno.entrada.materiales.forEach((material, i) => {
    const [nombre, prop, masas, fondo, total] = moreno[i];
    assert.equal(material.nombre, nombre);
    assert.equal(material.proporcion_pct, prop);
    assert.equal(material.peso_fondo_g, fondo);
    assert.deepEqual(material.pesos_retenidos_g, masas);
    assert.ok(Math.abs(material.peso_total_recuperado_g - total) < 1e-9);
    assert.ok(Math.abs(material.pesos_retenidos_g.reduce((a, b) => a + b, fondo) - total) < 1e-9);
  });
  assert.match(resultado.innerHTML, /Liberación para producción deshabilitada/);
  assert.match(resultado.innerHTML, /graficoComparacion/);
  assert.match(resultado.innerHTML, /N\/D/);
  assert.doesNotMatch(resultado.innerHTML, /100 % compliance/);

  const terceraSerie = [7, 2.4, 0.82, 0.064];
  const terceraMezcla = [
    ['X', 40, [3, 12, 20, 55], 10, 100],
    ['Y', 60, [4, 23, 21, 45], 7, 100]
  ];
  delete proporciones.F2;
  delete proporciones.BARILE;
  for (const [nombre, proporcion] of terceraMezcla) proporciones[nombre] = proporcion;
  tablas.splice(0, tablas.length, ...prepararTablas(terceraSerie, terceraMezcla));
  dialogo.close();
  await vm.runInContext('calcularRetenidoBR()', contexto);
  const terceraCurva = peticiones.at(-1);
  assert.deepEqual(terceraCurva.entrada.metodo_finura, curvaMoreno.entrada.metodo_finura);
  await vm.runInContext(boton, contexto);
  const terceraAuditoria = peticiones.at(-1);
  assert.equal(terceraAuditoria.data.exito, true);
  assert.deepEqual(terceraAuditoria.entrada.tamices, terceraSerie);
  assert.equal(terceraAuditoria.data.data.fase_1.cumplimiento_pct, null);
  assert.doesNotMatch(principal, /function mostrarAuditoriaParcial/);
  for (const informeCompleto of [informe, informeMoreno, resultado.innerHTML]) {
    assert.match(informeCompleto, /class="operator-panel"/);
    assert.match(informeCompleto, /Evaluación Inicial/);
    assert.match(informeCompleto, /Criterios de Decisión/);
    assert.match(informeCompleto, /Materiales originales priorizados/);
    assert.match(informeCompleto, /id="graficoComparacion"/);
  }
  for (const [nombre, retenidos, audit] of [
    ['A', curva, auditoria], ['B', curvaMoreno, auditoriaMoreno], ['C', terceraCurva, terceraAuditoria]
  ]) {
    const pasos = ['api_auditoria', 'generar_auditoria_completa', '_construir_auditoria_industrial'];
    assert.ok(retenidos.funciones.includes('granulometria_retido'));
    assert.deepEqual([...new Set(audit.funciones)].filter(f => pasos.includes(f)), pasos);
    assert.equal(audit.data.data.auditoria_industrial.validacion_materiales.materiales_originales.length,
      audit.entrada.materiales.length);
    console.log(`Serie ${nombre}: granulometria_retido → ${pasos.join(' → ')}`);
  }

  delete proporciones.X;
  delete proporciones.Y;
  for (const [nombre, proporcion] of moreno) proporciones[nombre] = proporcion;
  tablas.splice(0, tablas.length, ...prepararTablas(etiquetas, moreno));
  dialogo.close();
  metodo.value = serie.value = '';
  vm.runInContext('actualizarReferenciaFinura()', contexto);
  await vm.runInContext('calcularRetenidoBR(true)', contexto);
  const antesDeGuardar = peticiones.length;
  const filaFaltante = getElementById('perfilFilas').children.at(-1);
  const minimo = filaFaltante.children[1].children[0];
  const maximo = filaFaltante.children[2].children[0];
  const guardar = () => getElementById('formLimitesGranulometricos').onsubmit({ preventDefault() {} });
  getElementById('perfilNombre').value = 'Block de prueba';
  getElementById('perfilFuente').value = 'Fixture sintético, no usar en producción';
  getElementById('perfilFuenteManual').value = 'Referencia manual de la prueba';
  minimo.value = '89';
  maximo.value = '100';
  maximo.oninput();
  assert.equal(filaFaltante.children[3].textContent, 'Manual');
  assert.doesNotMatch(minimo.className, /is-invalid/);
  assert.equal(getElementById('perfilFuenteManualGrupo').hidden, false);
  vm.runInContext("cerrarModal('modalLimitesGranulometricos')", contexto);
  await vm.runInContext('calcularRetenidoBR(true)', contexto);
  assert.equal(getElementById('perfilFilas').children.at(-1).children[1].children[0].value, '89');
  assert.equal(getElementById('perfilNombre').value, 'Block de prueba');
  assert.equal(getElementById('perfilFuenteManual').value, 'Referencia manual de la prueba');
  getElementById('perfilInterpolar').checked = true;
  await guardar();
  assert.equal(controles.at(-1).data.error, 'profile_monotonic');
  assert.equal(peticiones.length, antesDeGuardar);
  minimo.value = '96';
  getElementById('perfilInterpolar').checked = false;
  await guardar();
  assert.equal(controles.at(-1).data.compatible, false);
  assert.equal(peticiones.length, antesDeGuardar);
  getElementById('perfilInterpolar').checked = true;
  await guardar();
  assert.equal(peticiones.length, antesDeGuardar + 1);
  assert.equal(modalLimites['aria-hidden'], 'true');
  const retenidosPerfil = peticiones.at(-1);
  assert.equal(retenidosPerfil.data.finura.tipo_metodo, 'experimental');
  assert.equal(retenidosPerfil.data.modulo_finura, 5.41);
  assert.ok(Math.abs(retenidosPerfil.data.finura.valor_exacto - 5.4075162) < 5e-8);
  assert.deepEqual(retenidosPerfil.entrada.metodo_finura_automatico.tamices, tamicesMoreno);
  assert.equal(retenidosPerfil.entrada.metodo_finura, undefined);
  assert.deepEqual(retenidosPerfil.entrada.perfil_granulometrico, JSON.parse(perfilGuardado));
  assert.equal(retenidosPerfil.data.faixas.bloco.find(f => f.tamiz === 0.063).origen, 'manual');
  assert.deepEqual(retenidosPerfil.entrada.materiales, inicialMoreno.entrada.materiales);
  await vm.runInContext(boton, contexto);
  const auditoriaPerfil = peticiones.at(-1);
  assert.equal(auditoriaPerfil.data.exito, true, auditoriaPerfil.data.error);
  assert.equal(auditoriaPerfil.data.data.validacion_bandas.completa, true);
  assert.equal(auditoriaPerfil.data.data.validacion_bandas.liberacion_produccion, false);
  assert.equal(auditoriaPerfil.data.data.validacion_bandas.motivo_liberacion, 'band_interpolated');
  assert.equal(auditoriaPerfil.data.data.orden_operativa_real, undefined);
  assert.equal(auditoriaPerfil.data.data.producto_banda, 'bloco');
  assert.deepEqual(auditoriaPerfil.data.data.perfil_granulometrico, JSON.parse(perfilGuardado));
  assert.equal(auditoriaPerfil.entrada.banda_min.at(-1), 0);
  assert.equal(auditoriaPerfil.entrada.banda_max.at(-1), 4);
  assert.match(resultado.innerHTML, /≈ \[62\.27–95\.00\]%/);
  assert.doesNotMatch(resultado.innerHTML, /La mezcla cumple banda|The mix meets the band/);
  const resultadoPerfil = auditoriaPerfil.data.data;
  const esperadoMoreno = [98.9790615, 98.1323407, 57.7286654, 42.2202043, 30.0997828,
    18.8622936, 10.1572057, 2.5730525, 0.4957698];
  auditoriaPerfil.entrada.pasante_real.forEach((p, i) => assert.ok(Math.abs(p - esperadoMoreno[i]) < 5e-8));
  assert.equal(resultadoPerfil.bandas.bloco.at(-1).origen, 'manual');
  assert.equal(resultadoPerfil.perfil_granulometrico.fuente_manual, 'Referencia manual de la prueba');
  const desviacion = auditoriaPerfil.entrada.pasante_real.reduce((total, valor, i) =>
    total + Math.abs(valor - (auditoriaPerfil.entrada.banda_min[i] + auditoriaPerfil.entrada.banda_max[i]) / 2), 0) / 9;
  const residual = auditoriaPerfil.entrada.pasante_real.reduce((total, valor, i) =>
    total + Math.max(0, auditoriaPerfil.entrada.banda_min[i] - valor, valor - auditoriaPerfil.entrada.banda_max[i]), 0);
  assert.ok(Math.abs(resultadoPerfil.fase_2_4_criterios.desviacion_media_centro - desviacion) < 1e-9);
  assert.ok(Math.abs(resultadoPerfil.fase_1.error_total - residual) < 1e-9);
  assert.equal((100 - desviacion).toFixed(2), '90.55');
  assert.equal(residual.toFixed(2), '9.14');
  assert.equal(resultadoPerfil.auditoria_industrial.validacion_tabla_virtual.mezcla_materiales.estado, 'no_viable');
  assert.ok(auditoriaPerfil.funciones.includes('generar_auditoria_completa'));
});
