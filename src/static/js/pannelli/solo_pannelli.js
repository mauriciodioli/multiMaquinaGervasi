/****************************** 
 * GERVASI · Pannelli Front JS (Grid 12)
 ******************************/
// ===== MOCK TOGGLE =====
const USE_MOCK = (new URLSearchParams(location.search).get('mock') === '1') || true; // poné false para desactivar

// ===== MOCK DATA =====
const _MOCK = {
  t: 0,
  baseIps: Array.from({length:12}, (_,k)=> `192.168.1.${101+k}`),
  models: [
    ['SMA','SunnyBoy 5.0'],
    ['Danfoss','DLX 2.0'],
    ['Fronius','Primo 6.0'],
    ['Huawei','SUN2000-5KTL'],
  ],
  stateCycle: ['ok','standby','fail','ok','ok','ok','ok','ok','ok','standby','ok','ok']
};




function _pick(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
function _jitter(val, pct=0.05){ // ±5% por defecto
  const d = val * pct;
  return val + (Math.random()*2-1)*d;
}
function _statusForIndex(i){
  const s = _MOCK.stateCycle[i % _MOCK.stateCycle.length];
  if (s === 'fail')   return {status:'fail',    status_group:'error',   status_code: 501, status_text:'Fail'};
  if (s === 'standby')return {status:'standby', status_group:'standby', status_code: 410, status_text:'Standby'};
  return {status:'ok', status_group:'ok', status_code: 320, status_text:'Ok'};
}

function buildMockResponse(){
  _MOCK.t++;
  const inverters = _MOCK.baseIps.map((ip, idx)=>{
    const [man, model] = _pick(_MOCK.models);
    // Potencias base: alternamos para que no sean todas iguales
    const baseP = 800 + (idx%4)*250; // 800,1050,1300,1550...
    const baseV = 228 + (idx%3)*3;   // 228,231,234
    const baseF = 49.8 + (idx%2)*0.2;// 49.8, 50.0

    // Le metemos un jitter suave y una onda lenta en el tiempo
    const p = Math.max(0, _jitter(baseP * (1+0.15*Math.sin((_MOCK.t+idx)/5)), 0.06));
    const v = _jitter(baseV, 0.01);
    const f = _jitter(baseF, 0.002);

    const st = _statusForIndex(idx);

    // Si está en fail, tiramos P=0 y badge de error
    const power_W = (st.status === 'fail') ? 0 : Math.round(p);
    const voltage_V = +(v.toFixed(1));
    const frequency_Hz = +(f.toFixed(2));

    return {
      ip,
      manufacturer: man,
      model,
      power_W,
      voltage_V,
      frequency_Hz,
      ...st
    };
  });

  const total = inverters.reduce((a,b)=> a + (Number.isFinite(b.power_W)? b.power_W : 0), 0);

  return {
    total_power_W: Math.round(total),
    inverters
  };
}

// Wrapper de fetch para mock
async function fetchStatus(){
  if (USE_MOCK) return buildMockResponse();
  const res = await fetch('/api/pannelli/status', { cache: 'no-store' });
  if(!res.ok) throw new Error('HTTP '+res.status);
  return res.json();
}


/* ==== util: badge de estado global ==== */
function setBadge(el, txt){
  const t = (txt ?? '').toLowerCase().trim();
  let cls = 'unknown', label = txt || 'Unknown';

  if (
    t.includes('no conect') ||
    t.includes('offline') ||
    /refused|timeout|timed out|dns|modbus/.test(t)
  ) { cls = 'error'; label = 'Sin conexión'; }
  else if (t.includes('ok') || /operando|running|online/.test(t)) { cls = 'ok'; label = 'OK'; }
  else if (t.includes('standby') || /idle/.test(t)) { cls = 'standby'; label = 'Standby'; }
  else if (/falla|fail|failure|fault|alarm|error/.test(t)) { cls = 'error'; label = 'Fail'; }
  else if (t.includes('raw')) { cls = 'unknown'; label = 'Datos crudos'; }
  else if (t.includes('sin datos')) { cls = 'unknown'; label = 'no data'; }

  el.className = `badge ${cls}`;
  el.textContent = label;
}

/* ==== estado previo para comparar difs ===== */
let prevSnapshot = {
  total_power_W: null,
  inv: {} // por IP: { power_W, voltage_V, frequency_Hz }
};

/* ==== helper: formato seguro ==== */
const fmt = (n,suf='') =>
  (typeof n==='number' && isFinite(n)) ? n.toLocaleString('es-AR')+suf : '—';

/* ==== helper: flash visual de delta (verde/rojo/azul) ==== */
function flashDelta(el, oldVal, newVal, neutralIsBlue=false){
  if (typeof oldVal !== 'number' || !isFinite(oldVal) ||
      typeof newVal !== 'number' || !isFinite(newVal)) return;

  let cls;
  if (newVal > oldVal) cls = 'flash-up';
  else if (newVal < oldVal) cls = 'flash-down';
  else if (neutralIsBlue)   cls = 'flash-neutral';
  else return;

  el.classList.remove('flash-up','flash-down','flash-neutral');
  el.classList.add(cls);
  setTimeout(()=> el.classList.remove('flash-up','flash-down','flash-neutral'), 1200);
}

/* ========= UI GRID (12 slots) ========= */
function ensureGridContainer(){
  const host = document.querySelector('.card_panelles');
  if (!host) return null;

  let grid = host.querySelector('#pv-grid');
  if (!grid){
    grid = document.createElement('div');
    grid.id = 'pv-grid';
    grid.className = 'pv-grid';
    host.appendChild(grid);
  }
  return grid;
}

/** Crea una card vacía o por IP */
function createCard(ip = null){
  const card = document.createElement('div');
  card.className = 'pv-card';
  if (ip) card.dataset.ip = ip;

  card.innerHTML = `
    <div class="pv-card-head">
      <span class="pv-ip">${ip || '—'}</span>
      <span class="badge pv-badge">—</span>
    </div>
    <div class="pv-metrics">
      <div class="pv-metric"><span class="lbl">P</span><span class="val mono power-cell">— W</span></div>
      <div class="pv-metric"><span class="lbl">V</span><span class="val mono volt-cell">— V</span></div>
      <div class="pv-metric"><span class="lbl">F</span><span class="val mono freq-cell">— Hz</span></div>
    </div>
    <div class="pv-foot muted pv-model">—</div>
  `;
  return card;
}

/** Normaliza listado a máximo 12 y conserva orden estable por IP */
function normalizeInverters(list){
  const uniq = [];
  const seen = new Set();
  for (const i of (list || [])){
    const key = i.ip || `__noip_${Math.random().toString(36).slice(2)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    uniq.push(i);
    if (uniq.length >= 12) break;
  }
  return uniq;
}

/** Renderiza/actualiza matriz de 12 */
function renderGrid(inverters){
  const grid = ensureGridContainer();
  if (!grid) return;

  const data = normalizeInverters(inverters);
  const usedIps = new Set();

  // 1) actualizar/crear cards de datos
  for (const i of data){
    const ip = i.ip || '—';
    usedIps.add(ip);

    let card = grid.querySelector(`.pv-card[data-ip="${ip}"]`);
    if (!card){
      card = createCard(ip);
      grid.appendChild(card);
    }

    // elementos
    const badge = card.querySelector('.pv-badge');
    const pEl   = card.querySelector('.power-cell');
    const vEl   = card.querySelector('.volt-cell');
    const fEl   = card.querySelector('.freq-cell');
    const mEl   = card.querySelector('.pv-model');

    // badge por código/grupo + label
    setStatusBadgeByCode(badge, i.status_code, i.status_text, i.status_group, i.status);
    badge.textContent = formatStatusLabel(i);

    // flashes y valores
    const old = prevSnapshot.inv[ip] || {};
    if (pEl){ pEl.textContent = fmt(i.power_W,' W'); flashDelta(pEl, old.power_W, i.power_W, true); }
    if (vEl){ vEl.textContent = fmt(i.voltage_V,' V'); flashDelta(vEl, old.voltage_V, i.voltage_V, true); }
    if (fEl){ fEl.textContent = fmt(i.frequency_Hz,' Hz'); flashDelta(fEl, old.frequency_Hz, i.frequency_Hz, true); }
    if (mEl){ mEl.textContent = `${i.manufacturer||''} ${i.model||''}`.trim() || '—'; }

    // snapshot
    prevSnapshot.inv[ip] = {
      power_W: i.power_W,
      voltage_V: i.voltage_V,
      frequency_Hz: i.frequency_Hz
    };

    // marca card como activa
    card.classList.remove('pv-empty');
  }

  // 2) eliminar cards sobrantes que no están en el set actual y no queremos reciclar
  const cards = Array.from(grid.querySelectorAll('.pv-card'));
  // Mantener hasta 12 en total: las que no estén en usedIps las pongo vacías para completar matriz
  let total = cards.length;

  // 2.a completa huecos hasta 12
  while (total < 12){
    grid.appendChild(createCard());
    total++;
  }

  // 2.b setear vacías (sin IP) o no usadas como “empty”
  let idx = 0;
  for (const card of Array.from(grid.children)){
    const ip = card.dataset.ip || null;
    if (!ip || !usedIps.has(ip)){
      card.dataset.ip = ''; // sin IP
      card.classList.add('pv-empty');
      card.querySelector('.pv-ip').textContent = `Slot ${idx+1}`;
      const b = card.querySelector('.pv-badge'); b.className = 'badge standby'; b.textContent = 'Libre';
      card.querySelector('.power-cell').textContent = '— W';
      card.querySelector('.volt-cell').textContent  = '— V';
      card.querySelector('.freq-cell').textContent  = '— Hz';
      card.querySelector('.pv-model').textContent   = '—';
    }
    idx++;
    if (idx >= 12) break;
  }

  // 2.c si hay más de 12, recorta extras visualmente
  while (grid.children.length > 12){
    grid.removeChild(grid.lastElementChild);
  }
}

/* ==== fetch + render (defensivo) ==== */
async function loadStatus(){
  const powerEl = document.getElementById('pv-power');
  const statusEl= document.getElementById('pv-status');

  const data = await fetchStatus();  // ← usa mock o API según toggle

  // ... el resto de tu loadStatus sigue igual (total, badge global, renderGrid)
  /* ===== TOTAL con umbral ±5% ===== */
  if (powerEl){
    const newTotal = (typeof data.total_power_W==='number' && isFinite(data.total_power_W))
      ? data.total_power_W : null;

    if (newTotal!=null){
      const oldTotal = prevSnapshot.total_power_W;
      powerEl.textContent = newTotal.toLocaleString('es-AR')+' W';
      powerEl.classList.remove('total-up','total-down','total-flat');

      if (typeof oldTotal === 'number' && isFinite(oldTotal) && oldTotal>0){
        const pct = (newTotal - oldTotal) / oldTotal * 100;
        if (pct >= 5)       powerEl.classList.add('total-up');
        else if (pct <= -5) powerEl.classList.add('total-down');
        else                powerEl.classList.add('total-flat');
        setTimeout(()=> powerEl.classList.remove('total-up','total-down','total-flat'), 1500);
      }
      prevSnapshot.total_power_W = newTotal;
    } else {
      powerEl.textContent = '— W';
    }
  }

  /* ===== BADGE global ===== */
  const states = (data.inverters||[]).map(i=> (i.status_text||'').toLowerCase());
  if (statusEl){
    let global = 'Unknown';
    if (states.some(s=> /falla|fail|failure|fault|alarm|error/.test(s))) {
      global='Fail';
    } else if (states.length && states.every(s=> s.includes('standby') || /idle/.test(s))) {
      global='Standby';
    } else if (states.some(s=> s.includes('ok') || /operando|running|online/.test(s))) {
      global='Ok';
    }
    setBadge(statusEl, global);
  }

  /* ===== GRID (matriz 12) ===== */
  renderGrid(data.inverters || []);
}


/* ==== polling 3s sin solaparse ==== */
let pollTimer = null;
let inFlight = false;

async function pollOnce(){
  if (inFlight) return;  // evita solapes si backend tarda
  inFlight = true;
  try {
    await loadStatus();
  } catch(e){
    console.warn('poll error:', e);
    const statusEl= document.getElementById('pv-status');
    if (statusEl) setBadge(statusEl, 'Fail');
  } finally {
    inFlight = false;
    pollTimer = setTimeout(pollOnce, 3000); // 3s exactos entre ciclos
  }
}

/* ==== pausa el polling cuando no está visible ==== */
document.addEventListener('visibilitychange', ()=>{
  if (document.hidden){ clearTimeout(pollTimer); }
  else { pollOnce(); }
});

/* ==== arranque ==== */
pollOnce();

/* ======= helpers de status ======= */
function setStatusBadgeByCode(el, code, text, group, status){
  let cls = 'unknown';
  if (typeof code === 'number') {
    if (code >= 300 && code < 400) cls = 'ok';
    else if (code >= 400 && code < 500) cls = 'standby';
    else if ((code >= 200 && code < 300) || (code >= 500 && code < 600)) cls = 'error';
    else if (code >= 100 && code < 200) cls = 'init';
  } else if (group) {
    const g = String(group).toLowerCase();
    cls = ({ ok:'ok', standby:'standby', error:'error', init:'init', unknown:'unknown' }[g]) || 'unknown';
  } else {
    setBadge(el, text);
    return;
  }

  let label = text || (typeof code === 'number' ? `Código ${code}` : '—');

  if (String(status || '').toLowerCase() === 'fail') {
    label = (typeof code === 'number') ? `Fail (código ${code})` : 'Fail';
    cls = 'error';
  }

  el.className = `badge ${cls}`;
  el.textContent = label;
}

function _extractStatusCode(i){
  if (typeof i?.status_code === 'number') return i.status_code;
  const pool = [i?.status_text, i?.error].filter(Boolean).join(' ');
  const m = pool.match(/\b(?:código|code|Errno)[:\s]*(-?\d+)\b/i);
  return m ? Number(m[1]) : null;
}

function formatStatusLabel(i){
  const status = String(i?.status || '').toLowerCase();
  const text   = (i?.status_text || '').trim();

  if (status === 'fail'){
    const code = _extractStatusCode(i);
    return (code != null) ? `Fail (código ${code})` : 'Fail';
  }
  if (text) return text;

  const code = _extractStatusCode(i);
  if (code != null) return `Código ${code}`;

  return '—';
}




document.addEventListener('DOMContentLoaded', () => {
  const btn  = document.getElementById('btnSoloPannelli');
  const wrap = document.getElementById('solo-pannelli-wrap');

  if (!btn || !wrap) return;

  btn.addEventListener('click', () => {
    // 1) mostrar el parcial
    wrap.style.display = 'block';

    // 2) ocultar TODO lo demás que esté al mismo nivel que wrap
    const root = wrap.parentElement;                 // el contenedor de todo el contenido
    Array.from(root.children).forEach(el => {
      if (el !== wrap) el.style.display = 'none';    // solo dejamos visible el wrap
    });

    // 3) llevar la vista al panel
    wrap.querySelector('#solo-panelli-card')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // 4) bandera opcional para que tu JS no pinte la tabla en modo SOLO
    window.MODE_SOLO = true;

    // 5) iniciar matriz o forzar una actualización
    if (window.Pannelli?.start) {
      window.Pannelli.start({
        gridHost: '#solo-panelli-card .card_panelles',
        mock: (new URLSearchParams(location.search).get('mock') === '1')
      });
    } else if (typeof window.pollOnce === 'function') {
      window.pollOnce();
    }
  });
});