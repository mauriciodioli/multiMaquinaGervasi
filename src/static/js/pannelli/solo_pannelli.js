

/**************** SOLO PANNELLI – desde botón ****************/
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btnSoloPannelli');
  if (!btn) return;
  btn.addEventListener('click', initSoloPannelli);
});

function initSoloPannelli(){
  // 1) Ocultar tablas/zona vieja
  document.querySelectorAll('#pv-root, #pv-table, .tabla-container .table, .tabla-container table')
    .forEach(el => el && (el.style.display = 'none'));

  // 2) Montar contenedor de tarjetas si no existe
  let root = document.getElementById('sp-root');
  if (!root){
    const host = document.querySelector('.tabla-container') || document.body;
    host.insertAdjacentHTML('beforeend', `
      <div class="grid grid-2" id="sp-root" style="margin-top:12px;">
        <div class="card">
          <div id="sp-status-wrap">
            <span class="status-label">Device status</span>
            <span id="sp-status" class="badge">—</span>
          </div>
        </div>
        <div class="card">
          <div class="muted">Current power</div>
          <div id="sp-power" class="big mono">— W</div>
        </div>
        <section id="sp-cards-section" style="overflow:auto; grid-column:1 / -1;">
          <div class="muted" style="margin-bottom:.5rem">Inverters</div>
          <div id="sp-cards" class="pv-grid"></div>
        </section>
      </div>
    `);
  }

  // 3) Arrancar ciclo (fetch inmediato + polling)
  SoloPannelliRunner.start();
}

/************** Runner aislado **************/
const SoloPannelliRunner = (() => {
  let timer = null, inflight = false, started = false;

  const els = {
    cards:   () => document.getElementById('sp-cards'),
    power:   () => document.getElementById('sp-power'),
    status:  () => document.getElementById('sp-status'),
  };

  function fmt(n, suf=''){
    return (typeof n==='number' && isFinite(n)) ? n.toLocaleString('es-AR') + suf : '—';
  }

function setBadge(el, txt){
  const t = (txt ?? '').toLowerCase().trim();
  let cls = 'unknown', label = txt || 'Unknown';
 
  // ↓ Primero: casos de desconexión (tu "no conect")
  if (
    t.includes('no conect') ||
    t.includes('offline') || t.includes('offline') ||
    /refused|timeout|timed out|dns|modbus/.test(t)
  ) {
    cls = 'error'; label = 'Non in Linea';

  } else if (t.includes('ok') || /operando|running|online/.test(t)) {
    cls = 'ok'; label = 'OK';

  } else if (t.includes('standby') || /idle/.test(t)) {
    cls = 'standby'; label = 'Standby';

  } else if (/falla|fail|failure|fault|alarm|error|offline/.test(t)) {
    cls = 'error'; label = 'Fail';

  } else if (t.includes('raw')) {
    cls = 'unknown'; label = 'Datos crudos';

  } else if (t.includes('sin datos')) {
    cls = 'unknown'; label = 'no data';
  }

  el.className = `badge ${cls}`;
  el.textContent = label;
}

async function loadOnce(){
  if (inflight) return;
  inflight = true;
  try{
    // document.getElementById('spinner')?.style.display = ''; // si lo usás acá
    const res = await fetch('/api/pannelli/status', { cache:'no-store' });
    if (!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    renderCards(data.inverters || []);
    updateTop(data);
  } catch(e){
    console.warn('[solo_pannelli] ', e);
    debugger;
    setBadge(els.status(), 'Fail');
  } finally {
    hideSpinner();   // << siempre lo apagás
    inflight = false;
  }
}


  function schedule(){
    clearTimeout(timer);
    timer = setTimeout(() => loadOnce().then(schedule), 3000);
  }

function updateTop(data){
  const p = els.power();
  if (p){
    const newTotal = (typeof data.total_power_W==='number' && isFinite(data.total_power_W))
      ? data.total_power_W : null;

    if (newTotal != null){
      const oldTotal = prevSnapshot.total_power_W;
      p.textContent = newTotal.toLocaleString('es-AR') + ' W';
      p.classList.remove('total-up','total-down','total-flat');

      if (typeof oldTotal === 'number' && isFinite(oldTotal) && oldTotal > 0){
        const pct = (newTotal - oldTotal) / oldTotal * 100;
        if (pct >= 5)       p.classList.add('total-up');
        else if (pct <= -5) p.classList.add('total-down');
        else                p.classList.add('total-flat');
        setTimeout(()=> p.classList.remove('total-up','total-down','total-flat'), 1500);
      }
      prevSnapshot.total_power_W = newTotal;
    } else {
      p.textContent = '— W';
    }
  }

  // Badge global, mismo criterio que tu tabla
  const statuses = (data.inverters||[]).map(i => (i.status_text||i.status||'').toLowerCase());
  let global = 'Unknown';
  if (statuses.some(s=>/falla|fail|failure|fault|alarm|error|offline/.test(s))) global='Fail';
  else if (statuses.length && statuses.every(s=>/standby|idle/.test(s)))      global='Standby';
  else if (statuses.some(s=>/ok|running|online|operando/.test(s)))            global='Ok';
  setBadge(els.status(), global);
}


function renderCards(items){
  const container = els.cards();
  if (!container) return;
  container.innerHTML = '';

  items.forEach(i=>{
    const ip  = i.ip || '—';
    const old = prevSnapshot.inv[ip] || {};

    // Tarjeta
    const card = document.createElement('div');
    card.className = 'pv-card';

    // Head: IP + badge con tus reglas por código/grupo/texto
    const head = document.createElement('div');
    head.className = 'pv-card-head';

    const ipEl = document.createElement('div');
    ipEl.textContent = ip;

    const badge = document.createElement('span');
    badge.className = 'badge';
    setStatusBadgeByCode(badge, i.status_code, i.status_text, i.status_group, i.status);
    badge.textContent = formatStatusLabel(i);

    head.append(ipEl, badge);

    // KPIs: agrego clases para flashDelta
    const kpis = document.createElement('div');
    kpis.className = 'pv-kpis';
    kpis.innerHTML = `
          <div class="pv-kpi">
            <span class="lbl">Power</span>
            <span class="val">
              <span class="num sp-power">${fmtPow(i.power_W)}</span>
              <span class="trend" aria-hidden="true"></span>
            </span>
          </div>
          <div class="pv-kpi">
            <span class="lbl">Volt</span>
            <span class="val">
              <span class="num sp-volt">${fmtVol(i.voltage_V)}</span>
              <span class="trend" aria-hidden="true"></span>
            </span>
          </div>
          <div class="pv-kpi">
            <span class="lbl">Freq</span>
            <span class="val">
              <span class="num sp-freq">${fmtFrq(i.frequency_Hz)}</span>
              <span class="trend" aria-hidden="true"></span>
            </span>
          </div>
        `;




    const meta = document.createElement('div');
    meta.className = 'pv-card-meta';
    meta.textContent = `${i.manufacturer||''} ${i.model||''}`.trim() || '—';

    card.append(head, kpis, meta);
    container.appendChild(card);

    // === EFECTOS DINÁMICOS (verde/rojo/azul) ===
    const pEl = card.querySelector('.sp-power');
    const vEl = card.querySelector('.sp-volt');
    const fEl = card.querySelector('.sp-freq');

    // azul neutral si no cambió (true)
    applyDelta(card.querySelector('.sp-power'), old.power_W,      i.power_W,      'power');
    applyDelta(card.querySelector('.sp-volt'),  old.voltage_V,    i.voltage_V,    'volt');
    applyDelta(card.querySelector('.sp-freq'),  old.frequency_Hz, i.frequency_Hz, 'freq');

    // snapshot por IP para la próxima comparación
    prevSnapshot.inv[ip] = {
      power_W: i.power_W,
      voltage_V: i.voltage_V,
      frequency_Hz: i.frequency_Hz
    };
  });
}


  function start(){
    if (started) return;
    started = true;
    loadOnce().then(schedule);
  }
  function stop(){
    clearTimeout(timer);
    started = false;
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop();
    else if (started) loadOnce().then(schedule);
  });

  return { start, stop };
})();




function initSoloPannelli(){
  // 1) Ocultar todo lo de la vista “tabla”
  [
    '#pv-root',                    // header tabla
    '#pv-table',                   // tabla principal
    '.tabla-container .table',     // cualquier tabla dentro del container
    '.tabla-container table',      // fallback
    '#sidebar',                    // <-- tu sidebar
    '#resizer',                    // separador lateral (si lo tenés)
    '#spinner'                     // overlay de carga, por las dudas
  ].forEach(sel => {
    document.querySelectorAll(sel).forEach(el => { el.style.display = 'none'; });
  });

  // 2) Montar / mostrar las tarjetas (lo que ya tenías)
  let root = document.getElementById('sp-root');
  if (!root){
    const host = document.querySelector('.tabla-container') || document.body;
    host.insertAdjacentHTML('beforeend', `
      <div class="grid grid-2" id="sp-root" style="margin-top:12px;">
        <div class="card">
          <div id="sp-status-wrap">
            <span class="status-label">Device status</span>
            <span id="sp-status" class="badge">—</span>
          </div>
        </div>
        <div class="card">
          <div class="muted">Current power</div>
          <div id="sp-power" class="big mono">— W</div>
        </div>
        <section id="sp-cards-section" style="overflow:auto; grid-column:1 / -1;">
          <div class="muted" style="margin-bottom:.5rem">Inverters</div>
          <div id="sp-cards" class="pv-grid"></div>
        </section>
      </div>
    `);
  }

  SoloPannelliRunner.start();
}







// ==== UMBRALES por KPI (ajustá a gusto)
const DELTA_THRESH = {
  power: { abs: 50, pct: 0.5 },     // ≥50 W o ≥0.5%
  volt:  { abs: 0.5, pct: 0.2 },    // ≥0.5 V o ≥0.2%
  freq:  { abs: 0.05, pct: 0.1 }    // ≥0.05 Hz o ≥0.1%
};

function deltaClass(oldVal, newVal, {abs=0, pct=0}={}){
  if (typeof oldVal !== 'number' || !isFinite(oldVal) ||
      typeof newVal !== 'number' || !isFinite(newVal)) return 'same';

  const d = newVal - oldVal;
  const mag = Math.abs(d);
  const passAbs = mag >= abs;
  const passPct = (typeof oldVal === 'number' && Math.abs(oldVal) > 1e-9)
      ? (mag / Math.abs(oldVal) * 100) >= pct
      : passAbs;

  if (!(passAbs || passPct)) return 'flat';   // cambió, pero por debajo del umbral ⇒ neutro
  return d > 0 ? 'up' : d < 0 ? 'down' : 'flat';
}

// Aplica clase + flash + simbolito
function applyDelta(el, oldVal, newVal, kind){
  if (!el) return;
  const cls = deltaClass(oldVal, newVal, DELTA_THRESH[kind] || {});
  const kpi = el.closest('.pv-kpi');
  const trendEl = kpi?.querySelector('.trend');

  kpi?.classList.remove('delta-up','delta-down','delta-flat','delta-same');
  el.classList.remove('flash-up','flash-down','flash-neutral');

  kpi?.classList.add(`delta-${cls}`);
  if (cls === 'up')      el.classList.add('flash-up');
  else if (cls === 'down') el.classList.add('flash-down');
  else if (cls === 'flat') el.classList.add('flash-neutral');

  if (trendEl) trendEl.textContent = (cls === 'up' ? '▲' : cls === 'down' ? '▼' : '▬');
}




// --- enteros (sin decimales) ---
const fmtInt = (n, suf='') =>
  (typeof n === 'number' && isFinite(n))
    ? n.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + suf
    : '—';

const fmtPow = n => fmtInt(n, ' W');
const fmtVol = n => fmtInt(n, ' V');
const fmtFrq = n => fmtInt(n, ' Hz'); // entero también
















// === Selectores de lo que ocultás/mostrás en modo Matriz ===
const MATRIX_SEL = [
  '#pv-root',                    // header tabla
  '#pv-table',                   // tabla principal
  '.tabla-container .table',     // otras tablas dentro del container
  '.tabla-container table',      // fallback
  '#sidebar',                    // sidebar
  '#resizer'                    // separador lateral
  
];


function hideSpinner(){
  const s = document.getElementById('spinner');
  if (!s) return;
  s.style.display = 'none';
  s.classList.remove('is-active','show');
  s.setAttribute('aria-hidden','true');
}

// Helpers
function hideMany(selectors){ selectors.forEach(s => 
  document.querySelectorAll(s).forEach(el => el.style.display = 'none')
);}
function showMany(selectors){ selectors.forEach(s => 
  document.querySelectorAll(s).forEach(el => el.style.display = '')
);}

function ensureCardsContainer(){
  let root = document.getElementById('sp-root');
  if (root) return root;
  const host = document.querySelector('.tabla-container') || document.body;
  host.insertAdjacentHTML('beforeend', `
    <div class="grid grid-2" id="sp-root" style="margin-top:12px;">
      <div class="card">
        <div id="sp-status-wrap">
          <span class="status-label">Device status</span>
          <span id="sp-status" class="badge">—</span>
        </div>
      </div>
      <div class="card">
        <div class="muted">Current power</div>
        <div id="sp-power" class="big mono">— W</div>
      </div>
      <section id="sp-cards-section" style="overflow:auto; grid-column:1 / -1;">
        <div class="muted" style="margin-bottom:.5rem">Inverters</div>
        <div id="sp-cards" class="pv-grid"></div>
      </section>
    </div>
  `);
  return document.getElementById('sp-root');
}

// === Mostrar tarjetas (Cards) ===
function showCards(){
  hideMany(MATRIX_SEL);
  hideSpinner();                 // << oculta por si quedó activo
  ensureCardsContainer().style.display = '';
  SoloPannelliRunner.start?.();
  const btn = document.getElementById('btnSoloPannelli');
  if (btn){ btn.textContent = 'Matriz'; btn.dataset.mode = 'cards'; }
}

function showMatriz(){
  SoloPannelliRunner.stop?.();
  const spRoot = document.getElementById('sp-root');
  if (spRoot) spRoot.style.display = 'none';
  showMany(MATRIX_SEL);
  hideSpinner();                 // << fuerza oculto al volver a tabla
  const btn = document.getElementById('btnSoloPannelli');
  if (btn){ btn.textContent = 'Cards'; btn.dataset.mode = 'matrix'; }
}

// === Click del botón (toggle) ===
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btnSoloPannelli');
  if (!btn) return;
  // estado inicial: estás en matriz
  btn.dataset.mode = 'matrix';
  // alinear a la derecha (por si no pusiste el CSS)
  btn.style.position = 'absolute';
  btn.style.right = '0';
  btn.style.top = '50%';
  btn.style.transform = 'translateY(-50%)';

  btn.addEventListener('click', () => {
    if (btn.dataset.mode === 'matrix') showCards();
    else showMatriz();
  });
});
