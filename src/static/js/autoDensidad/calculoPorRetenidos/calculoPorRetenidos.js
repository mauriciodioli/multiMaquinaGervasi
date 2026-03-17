// === Config ===
const TAMICES_ORDEN = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075, "Fundo"];

const LIMITES_BR = {
  bloco: {"12.5":[0,0],"9.5":[0,0],"6.3":[0,15],"4.8":[0,33],"2.4":[19,51],"1.2":[37,66],"0.6":[54,78],"0.3":[68,90],"0.15":[80,97],"0.075":[90,100],"Fundo":[100,100]},
  paver: {"12.5":[0,0],"9.5":[0,0],"6.3":[0,10],"4.8":[0,22],"2.4":[19,40],"1.2":[37,61],"0.6":[54,78],"0.3":[72,92],"0.15":[85,100],"0.075":[95,100],"Fundo":[100,100]}
};





const LS_TABLAS = 'tablasCargadas';
const LS_PROP   = 'proporcionesRetido'; // mapa { nombre -> porcentaje }

function leerTablasCargadas(){
  try { return JSON.parse(localStorage.getItem(LS_TABLAS) || '[]'); }
  catch{ return []; }
}

function leerProporciones(){
  try { return JSON.parse(localStorage.getItem(LS_PROP) || '{}'); }
  catch{ return {}; }
}

function guardarProporciones(map){
  localStorage.setItem(LS_PROP, JSON.stringify(map || {}));
}

function abrirModalProporciones(onOk){
  const tablas = leerTablasCargadas();
  if (!Array.isArray(tablas) || !tablas.length){
    alert('No hay tablas cargadas en localStorage.');
    return;
  }

  const form = document.getElementById('formProporciones');
  const btn  = document.getElementById('btnGuardarProporciones');
  const spanTotal = document.getElementById('propTotal');
  const msg  = document.getElementById('propMsg');

  const prev = leerProporciones();
  form.innerHTML = '';

  // materiales únicos según tu JSON
  const materiales = tablas.map(m => m?.nombre).filter(Boolean);

  materiales.forEach((nombre, i) => {
    const val = (typeof prev[nombre] === 'number') ? prev[nombre] : (tablas[i]?.proporcion_pct ?? '');
    const row = document.createElement('div');
    row.className = 'prop-row';
    row.innerHTML = `
      <label class="prop-label">${nombre}</label>
      <input class="prop-input" type="number" inputmode="decimal" step="0.01" min="0" max="100"
             name="${nombre}" value="${val !== undefined ? val : ''}" placeholder="0">
      <span class="prop-suf">%</span>
    `;
    form.appendChild(row);
  });

  function recalcular(){
    const inputs = form.querySelectorAll('.prop-input');
    let total = 0;
    const map = {};
    inputs.forEach(inp => {
      const n = parseFloat(inp.value);
      const ok = !isNaN(n) && n >= 0;
      if (ok) { total += n; map[inp.name] = +n; }
    });
    spanTotal.textContent = total.toFixed(2);

    msg.textContent = '';
    btn.disabled = true;

    if (Math.abs(total - 100) < 0.01){
      btn.disabled = false;
    } else {
      msg.textContent = 'La suma debe ser exactamente 100%.';
    }
    // guardado en caliente (opcional)
    guardarProporciones(map);
  }

  form.addEventListener('input', recalcular, { passive:true });
  recalcular();

  btn.onclick = (e) => {
    e.preventDefault();
    if (btn.disabled) return;
    cerrarModal('modalProporciones');
    if (typeof onOk === 'function') onOk();
  };

  abrirModal('modalProporciones');
}



function abrirProporcionesYCalcular(){
  // sanity check: debe existir tablasCargadas en localStorage
  const tablas = leerTablasCargadas?.() || [];
  if (!Array.isArray(tablas) || !tablas.length){
    alert('No hay tablas cargadas en localStorage (tablasCargadas).');
    return;
  }

  // Abre el modal de proporciones. Cuando el usuario presiona “Usar valores”
  // el modal llama a este callback y recién ahí disparamos el cálculo.
  abrirModalProporciones(() => {
    try {
      calcularRetenidoBR();  // tu flujo actual (fetch + gráfico + modal resultado)
    } catch (e){
      console.error(e);
      alert('Error al calcular retenidos: ' + e.message);
    }
  });
}






















// === MOCK proporciones planilla BR ===
const PROPORCIONES_MOCK = {
  "areia": 35,
  "brita": 10,
  "granilha": 15,
  "areia ind.": 40,
  "po brita": 0
};

// --- helper para tomar proporción: mock > input > reparto igual ---
function resolverProporcion(nombre, fallbackIgual, inputVal) {
  if (Object.prototype.hasOwnProperty.call(PROPORCIONES_MOCK, nombre)) return PROPORCIONES_MOCK[nombre];
  if (typeof inputVal === "number" && !isNaN(inputVal) && inputVal > 0) return inputVal;
  return fallbackIgual;
}
// === construir payload % retenido (usando MOCK de proporciones) ===

function construirPayloadRetido(){
  const proporciones = leerProporciones();  // <- fuente de verdad
  const materiales = [];
  const tamicesSet = new Set();

  const mezclas = document.querySelectorAll('.mezcla');
  mezclas.forEach(mezcla => {
    const nombre = (mezcla.querySelector('.nombreProducto')?.value || 'Sin nombre').trim();

    const retidosLoc = [];
    const tamicesLoc = [];

    mezcla.querySelectorAll('tbody tr').forEach(tr => {
      const tRaw = tr.cells[0]?.textContent?.trim();
      const pRaw = tr.cells[1]?.textContent?.trim();
      const t = (tRaw?.toLowerCase() === 'fundo') ? 'Fundo' : parseFloat(tRaw);
      const r = parseFloat(pRaw);
      if ((t === 'Fundo' || !isNaN(t)) && !isNaN(r)){
        tamicesLoc.push(t);
        retidosLoc.push(r);
        tamicesSet.add(t);
      }
    });

    if (retidosLoc.length){
      const pct = Number(proporciones[nombre] || 0);
      materiales.push({
        nombre,
        proporcion_pct: pct,      // ya no hay mock
        retido_ind_pct: retidosLoc
      });
    }
  });

  if (!materiales.length) throw new Error('No hay materiales con datos de % retenido.');

  const tamices = Array.from(tamicesSet);

  // Control rápido
  const suma = materiales.reduce((s,m)=>s+(+m.proporcion_pct||0), 0);
  if (Math.abs(suma-100) > 0.01){
    console.warn('[retido] Proporciones ≠ 100:', suma);
  }
  return { tamices, materiales, limites: LIMITES_BR, debug: true };
}

// === Acción principal: enviar a backend y manejar respuesta ===
async function calcularRetenidoBR() {
  let payload;
  try { payload = construirPayloadRetido(); }
  catch (e) { alert(e.message); return; }

  console.log("→ Payload BR", payload);

  try {
    const resp = await fetch("/calculoPorRetenidos/granulometria/retido/?debug=1", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include"
    });

    const text = await resp.text();
    let data; try { data = JSON.parse(text); } catch { data = { ok:false, error:text }; }

    if (!resp.ok || !data?.ok) {
      console.warn("[retido] error:", data?.error || text);
      notify('error', 'Error', data?.error || 'Fallo el cálculo de retenidos.');
      return;
    }

    window.granRetidoResultado = data;

    renderRetidoGrafico(
      data.tamices,
      data.mix_pasante,
      data.faixas,
      { faixa: 'bloco' } // o 'paver'
    );
    renderRetidoTablitas(data.tamices, data.mix_acum, data.faixas);
    abrirModal('modalRetidoBR');

    console.log("✅ MIX ACUM:", data.mix_acum);
    console.log("✅ MF:", data.modulo_finura);
    notify('success', 'Listo', `MF: ${data.modulo_finura}`);

  } catch (err) {
    console.error(err);
    notify('error', 'Error de red', String(err));
  }
}

let retidoChart;

function renderRetidoGrafico(tamices, mix_acum, faixas, opts = { faixa: 'bloco' }) {
  // Mapear a puntos X,Y en eje log y preparar etiquetas exactas (incluye FUNDO)
  const FUNDO_X = 0.01; // ancla para "Fundo" en eje log
  const pts = tamices.map((t, i) => ({
    x: String(t).toLowerCase() === 'fundo' ? FUNDO_X : parseFloat(t),
    y: parseFloat(mix_acum[i]),
    label: String(t)
  })).filter(p => !Number.isNaN(p.x));

  // Ordenar por X (log)
  pts.sort((a,b) => a.x - b.x);

  // Arrays finales X/Y (sin "Fundo" para el eje visible)
  const xs = pts.map(p => p.x);
  const ys = pts.map(p => p.y);
  const labels = pts.map(p => p.label);

  // ---- Limites por tamiz: construimos 4 curvas (bloco min/max, paver min/max) ----
  const detBloco = (faixas && faixas.bloco) ? faixas.bloco : [];
  const detPaver = (faixas && faixas.paver) ? faixas.paver : [];

  const byLabel = Object.fromEntries(tamices.map((t,i)=>[String(t), i]));
  const toAligned = (det, pick) => tamices.map((t,i) => {
    const d = det[i];
    if (!d || d.min == null || d.max == null) return null;
    return pick === 'min' ? d.min : d.max;
  });

  let blocoMin = toAligned(detBloco, 'min');
  let blocoMax = toAligned(detBloco, 'max');
  let paverMin = toAligned(detPaver, 'min');
  let paverMax = toAligned(detPaver, 'max');

  // Reordenar según xs (por si hubiese desfasajes)
  const reorder = arr => {
    if (!arr || !arr.length) return [];
    return tamices.map((_,i)=>arr[i]) // ya paralelos
      .map((v, i) => ({ x: String(tamices[i]).toLowerCase()==='fundo'?FUNDO_X:parseFloat(tamices[i]), v }))
      .filter(o => !Number.isNaN(o.x))
      .sort((a,b)=>a.x-b.x)
      .map(o => o.v);
  };
  blocoMin = reorder(blocoMin);
  blocoMax = reorder(blocoMax);
  paverMin = reorder(paverMin);
  paverMax = reorder(paverMax);

  // Preparar canvas
  const ctx = document.getElementById('retidoChart').getContext('2d');
  if (retidoChart) retidoChart.destroy();

  retidoChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: xs,
      datasets: [
        // === Limites para Blocos (azul sólido, dos curvas) ===
        {
          label: 'Limites para Blocos (min)',
          data: blocoMin,
          borderColor: '#1f6bff',
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },
        {
          label: 'Limites para Blocos (max)',
          data: blocoMax,
          borderColor: '#1f6bff',
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },

        // === Limites para Pavers (negro punteado, dos curvas) ===
        {
          label: 'Limites para Pavers (min)',
          data: paverMin,
          borderColor: '#111',
          borderDash: [6, 5],
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },
        {
          label: 'Limites para Pavers (max)',
          data: paverMax,
          borderColor: '#111',
          borderDash: [6, 5],
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },

        // === Curva en estudio (roja sólida con puntos) ===
        {
          label: 'curva em estudo',
          data: ys,
          borderColor: '#e74c3c',
          backgroundColor: '#e74c3c',
          pointRadius: 3,
          tension: 0.25,
          borderWidth: 2,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'nearest', intersect: false },
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            title: (items) => {
              const i = items[0].dataIndex;
              return `Peneira ${labels[i]} mm`;
            },
            label: (ctx) => `${ctx.dataset.label}: ${ctx.formattedValue}%`
          }
        }
      },
      scales: {
        x: {
          type: 'logarithmic',
          min: FUNDO_X,
          max: Math.max(...xs),
          ticks: {
            callback: (value) => {
              const i = xs.indexOf(value);
              return i >= 0 ? labels[i] : '';
            },
            values: xs
          },
          afterBuildTicks: (axis) => {
            axis.ticks = xs.map(v => ({ value: v }));
          },
          title: { display: true, text: 'Peneira (mm)' }
        },
        y: {
          min: 0, max: 100,
          title: { display: true, text: '% Retido Acumulado' }
        }
      }
    }
  });



  // Abrir modal custom (no Bootstrap)
  abrirModal('modalRetidoBR');
}









// Guardá proporciones del último cálculo para reusarlas en el modal de consumo
function cachearProporcionesDesdeRetido(){
  try{
    const data = window.granRetidoResultado;
    if (!data?.materiales?.length) return;

    // { "areia":35, "brita":10, ... }
    const props = {};
    data.materiales.forEach(m => props[m.nombre] = Number(m.proporcion_pct) || 0);
    localStorage.setItem('proporcionesRetido', JSON.stringify(props));
  }catch(e){ console.warn('No se pudo cachear proporciones:', e); }
}

// Hook del botón “Curva de consumo”
document.getElementById('btnIrConsumo')?.addEventListener('click', () => {
  cachearProporcionesDesdeRetido();
  // Podés apilar modales; si preferís, cerrá el de Retido antes:
  cerrarModal('modalRetidoBR');
  abrirModalEnsayos();
});











function renderRetidoTablitas(tamices, mix_acum, faixas){
  // Destino
  const host = document.getElementById('retidoTables');
  if (!host) return;

  // Normalizamos filas (ignoramos valores sin banda si no existen)
  const rows = tamices.map((t, i) => {
    const label = String(t); // puede ser "Fundo"
    const mix = Number(mix_acum[i] ?? 0);

    const b = (faixas?.bloco?.[i]) || {};
    const p = (faixas?.paver?.[i]) || {};
    return {
      label,
      mix: isFinite(mix) ? mix.toFixed(1) : '-',
      bmin: (b.min ?? null) != null ? Number(b.min).toFixed(0) : '-',
      bmax: (b.max ?? null) != null ? Number(b.max).toFixed(0) : '-',
      pmin: (p.min ?? null) != null ? Number(p.min).toFixed(0) : '-',
      pmax: (p.max ?? null) != null ? Number(p.max).toFixed(0) : '-',
    };
  });

  // Tabla 1: Granulometría ponderada
  const tbl1 = `
    <div class="mini-card">
      <div class="mini-title">Granulometría ponderada dos agregados</div>
      <table class="mini-table">
        <thead><tr><th>#</th><th>%</th></tr></thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.label}</td>
              <td>${r.mix}</td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>`;

  // Tabla 2: Faixas recomendadas (Bloco / Paver)
  const tbl2 = `
    <div class="mini-card">
      <div class="mini-title">Faixas granulométricas recomendadas</div>
      <table class="mini-table">
        <thead>
          <tr>
            <th rowspan="2">Peneira</th>
            <th colspan="2">Bloco</th>
            <th colspan="2">Paver</th>
          </tr>
          <tr>
            <th>Lim. Inf.</th><th>Lim. Sup.</th>
            <th>Lim. Inf.</th><th>Lim. Sup.</th>
          </tr>
        </thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.label}</td>
              <td>${r.bmin}</td><td>${r.bmax}</td>
              <td>${r.pmin}</td><td>${r.pmax}</td>
            </tr>`).join('')}
        </tbody>
      </table>
      <div class="muted" style="margin-top:6px">Valores en % de retido acumulado.</div>
    </div>`;

  host.innerHTML = tbl1 + tbl2;
}




(function () {
  const openModals = new Set();
  let lastActive = null;

  function focusTrap(modal) {
    const sel = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const fEls = Array.from(modal.querySelectorAll(sel)).filter(el => !el.disabled && el.offsetParent !== null);
    const first = fEls[0], last = fEls[fEls.length - 1];

    function onKey(e) {
      if (e.key === 'Escape') { cerrarModal(modal.id); return; }
      if (e.key !== 'Tab' || !fEls.length) return;
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    modal.__trapHandler = onKey;
    modal.addEventListener('keydown', onKey, true);
    (first || modal.querySelector('.dpia-modal__dialog') || modal).focus();
  }

  function removeTrap(modal) {
    if (modal.__trapHandler) {
      modal.removeEventListener('keydown', modal.__trapHandler, true);
      modal.__trapHandler = null;
    }
  }

  function abrirModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;

  if (openModals.size === 0) {
    document.body.classList.add('body--modal-open');
    lastActive = document.activeElement;
  }

  modal.setAttribute('aria-hidden', 'false');
  openModals.add(modal);

  // ⬇️ ESTE ES EL HANDLER CORREGIDO
  modal.__clickHandler = (e) => {
    const btn = e.target.closest('[data-close]');
    if (btn) {
      // Si data-close tiene un id real, lo usamos; si es "1" o vacío, cerramos el modal actual
      const val = btn.getAttribute('data-close');
      const targetId = (val && val !== '1') ? val : modal.id;
      cerrarModal(targetId);
      return;
    }
    // backdrop: click exactamente sobre el contenedor (fuera del dialog)
    if (e.target === modal) cerrarModal(modal.id);
  };
  modal.addEventListener('click', modal.__clickHandler);

  focusTrap(modal);
}


  function cerrarModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.setAttribute('aria-hidden', 'true');
    removeTrap(modal);
    if (modal.__clickHandler) {
      modal.removeEventListener('click', modal.__clickHandler);
      modal.__clickHandler = null;
    }
    openModals.delete(modal);
    if (openModals.size === 0) {
      document.body.classList.remove('body--modal-open');
      if (lastActive && typeof lastActive.focus === 'function') { try { lastActive.focus(); } catch {} }
      lastActive = null;
    }
  }

  // Exponer helpers
  window.abrirModal = abrirModal;
  window.cerrarModal = cerrarModal;

  // Atajo que pediste
  //window.cerrarModalAgregados = () => cerrarModal('modalAgregados');
})();




// --- notifier seguro: usa SweetAlert si existe, si no => alert()
function notify(type, title, text){
  if (window.Swal && typeof Swal.fire === 'function') {
    Swal.fire(title || '', text || '', type || 'info');
  } else {
    alert(`${title ? title + ': ' : ''}${text || ''}`);
  }
}







window.cerrarTodosLosModales = function(){
  if (typeof window.cerrarModal !== 'function') return;
  document.querySelectorAll('.dpia-modal[aria-hidden="false"]').forEach(m => window.cerrarModal(m.id));
};
























































let chartConsumo;

function agregarFilaEnsayo(ac = '', mpa = ''){
  const tb = document.querySelector('#tablaEnsayos tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><input type="number" step="0.01" class="dpia-input ens-ac" value="${ac}"></td>
    <td><input type="number" step="0.1"  class="dpia-input ens-mpa" value="${mpa}"></td>
    <td><button class="dpia-btn dpia-btn--tiny" data-del="1">×</button></td>`;
  tr.querySelector('[data-del]').onclick = ()=> tr.remove();
  tb.appendChild(tr);
}

function leerEnsayos(){
  const rows = [...document.querySelectorAll('#tablaEnsayos tbody tr')];
  const pts = [];
  for (const r of rows){
    const x = parseFloat(r.querySelector('.ens-ac')?.value);
    const y = parseFloat(r.querySelector('.ens-mpa')?.value);
    if (!isNaN(x) && x>0 && !isNaN(y) && y>0) pts.push({x,y});
  }
  return pts;
}

// y = a ln(x) + b  (regresión lineal sobre (ln x, y))
function ajustarLog(pts){
  const X = pts.map(p => Math.log(p.x));
  const Y = pts.map(p => p.y);
  const n = pts.length;
  const sum = a => a.reduce((s,v)=>s+v,0);
  const SX = sum(X), SY = sum(Y);
  const SXX = sum(X.map(v=>v*v));
  const SXY = sum(X.map((v,i)=>v*Y[i]));
  const a = (n*SXY - SX*SY) / (n*SXX - SX*SX);
  const b = (SY - a*SX) / n;
  return {a,b};
}

function ratioParaObjetivo(a,b,MPa){
  return Math.exp((MPa - b)/a); // A/C requerido
}

// Usa proporciones del modal de proporciones (ya cargadas en tu flujo)
function obtenerProporcionesMix(){
  // 1) primero las proporciones cacheadas del retido
  const cache = localStorage.getItem('proporcionesRetido');
  if (cache){
    try{
      const obj = JSON.parse(cache);
      const total = Object.values(obj).reduce((s,v)=>s + (Number(v)||0), 0);
      if (total > 0) return obj;
    }catch{}
  }

  // 2) si no, lee tablasCargadas con proporcion_pct
  const tablas = JSON.parse(localStorage.getItem('tablasCargadas') || '[]');
  let total = 0, map = {};
  for (const m of tablas){
    const p = Number(m.proporcion_pct);
    if (!isNaN(p) && p>0){ map[m.nombre]=p; total+=p; }
  }
  if (total>0) return map;

  // 3) reparto igual como último recurso
  const eq = tablas.length>0 ? +(100/tablas.length).toFixed(2) : 0;
  for (const m of tablas) map[m.nombre]=eq;
  return map;
}


function dimensionarLote(kgAgregados, proporciones, acRatio){
  const kgCem = kgAgregados / acRatio;
  const desglose = Object.entries(proporciones).map(([nombre,p]) => {
    return { nombre, kg: +(kgAgregados * (p/100)).toFixed(1), pct: p };
  });
  return { kgCemento: +kgCem.toFixed(1), agregados: desglose };
}

function renderCurvaConsumo(pts, a, b){
  const ctx = document.getElementById('chartConsumo').getContext('2d');
  const xs = [];
  const ys = [];
  // rango suave alrededor de los x medidos
  const xmin = Math.min(...pts.map(p=>p.x));
  const xmax = Math.max(...pts.map(p=>p.x));
  const N = 40;
  for (let i=0;i<=N;i++){
    const x = xmin + (xmax-xmin)*i/N;
    xs.push(x);
    ys.push(a*Math.log(x) + b);
  }

  if (chartConsumo) chartConsumo.destroy();
  chartConsumo = new Chart(ctx, {
    type:'line',
    data:{
      labels: xs,
      datasets:[
        {label:'Ensayos', data: pts.map(p=>({x:p.x,y:p.y})), showLine:false, pointRadius:4, borderWidth:0},
        {label:'Ajuste y = a·ln(x) + b', data: xs.map((x,i)=>({x, y:ys[i]})), borderWidth:2, pointRadius:0, tension:0}
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      parsing:false, // usamos {x,y}
      scales:{
        x:{ type:'linear', title:{display:true, text:'Relación A/C (agregado/cemento)'} },
        y:{ title:{display:true, text:'Resistencia (MPa)'} }
      }
    }
  });
}

// Abridor del modal y defaults
function abrirModalEnsayos(){
  // si no hay filas, cargo 4–5 placeholders típicos
  const tb = document.querySelector('#tablaEnsayos tbody');
  tb.innerHTML = '';
  [[3.5,48],[4.5,40],[5.0,35],[6.0,30],[8.0,23]].forEach(([x,y])=>agregarFilaEnsayo(x,y));
  document.getElementById('mpaObjetivo').value = 35;
  document.getElementById('kgAgregados').value = 1700;
  abrirModal('modalEnsayos');
}

// Hook UI
document.getElementById('btnAddPunto')?.addEventListener('click', ()=>agregarFilaEnsayo());
document.getElementById('btnCalcularConsumo')?.addEventListener('click', ()=>{
  const pts = leerEnsayos();
  if (pts.length < 3){ alert('Ingresá al menos 3 puntos de ensayo.'); return; }
  const {a,b} = ajustarLog(pts);
  renderCurvaConsumo(pts, a, b);

  const mpa = parseFloat(document.getElementById('mpaObjetivo').value);
  const kgAgg = parseFloat(document.getElementById('kgAgregados').value);
  if (isNaN(mpa) || isNaN(kgAgg) || kgAgg<=0){ alert('Completá MPa objetivo y kg de agregados.'); return; }

  const xreq = ratioParaObjetivo(a,b,mpa); // A/C requerido
  const props = obtenerProporcionesMix();
  const lote = dimensionarLote(kgAgg, props, xreq);

  document.getElementById('resultadoTrazo').innerHTML =
    `Trazo requerido (A/C): <b>${xreq.toFixed(2)}</b>  →  Cemento: <b>${lote.kgCemento} kg</b> por ${kgAgg} kg de agregados.`;

  const rows = lote.agregados.map(r=>`${r.nombre}: ${r.kg} kg (${r.pct}%)`).join('<br>');
  document.getElementById('resultadoDesglose').innerHTML = rows;
});













