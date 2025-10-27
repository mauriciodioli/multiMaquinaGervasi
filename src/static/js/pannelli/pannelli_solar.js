/******************************
 * DPIA · Pannelli Front JS
 ******************************/

/* ==== util: badge de estado global ==== */
function setBadge(el, txt){
  const t = (txt||'').toLowerCase();
  let cls='unknown', label=txt||'Unknown';
  if (t.includes('ok')) cls='ok', label='Ok';
  else if (t.includes('standby')) cls='standby', label='Standby';
  else if (t.includes('falla') || t.includes('error')) cls='error', label='Falla';
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

/* ==== fetch + render (defensivo) ==== */
async function loadStatus(){
  const powerEl = document.getElementById('pv-power');          // opcional
  const statusEl= document.getElementById('pv-status');          // opcional
  const bodyEl  = document.querySelector('#pv-table tbody');     // opcional

  const res = await fetch('/api/pannelli/status', { cache: 'no-store' });
  if(!res.ok) throw new Error('HTTP '+res.status);
  const data = await res.json();

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
    if (states.some(s=>s.includes('falla'))) global='Falla';
    else if (states.length && states.every(s=>s.includes('standby'))) global='Standby';
    else if (states.some(s=>s.includes('ok')) || states.some(s=>s.includes('operando'))) global='Ok';
    setBadge(statusEl, global);
  }

  /* ===== TABLA ===== */
  if (bodyEl){
    bodyEl.innerHTML = '';
    (data.inverters||[]).forEach(i=>{
      const ip   = i.ip || '—';
      const old  = prevSnapshot.inv[ip] || {};

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${ip}</td>
        <td><span class="badge">${i.status_text||'—'}</span></td>
        <td class="mono power-cell">${fmt(i.power_W,' W')}</td>
        <td class="mono volt-cell">${fmt(i.voltage_V,' V')}</td>
        <td class="mono freq-cell">${fmt(i.frequency_Hz,' Hz')}</td>
        <td class="muted">${(i.manufacturer||'')+' '+(i.model||'')}</td>`;

      // flashes por celda (incluye neutral azul si no cambió)
      const pc = tr.querySelector('.power-cell');
      const vc = tr.querySelector('.volt-cell');
      const fc = tr.querySelector('.freq-cell');
      if (pc) flashDelta(pc, old.power_W,      i.power_W,      true);
      if (vc) flashDelta(vc, old.voltage_V,    i.voltage_V,    true);
      if (fc) flashDelta(fc, old.frequency_Hz, i.frequency_Hz, true);

      // snapshot por IP
      prevSnapshot.inv[ip] = {
        power_W: i.power_W,
        voltage_V: i.voltage_V,
        frequency_Hz: i.frequency_Hz
      };

      bodyEl.appendChild(tr);
    });
  }
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
    if (statusEl) setBadge(statusEl, 'Falla');
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
