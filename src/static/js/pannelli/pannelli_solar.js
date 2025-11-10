/******************************
 * GERVASI · Pannelli Front JS
 ******************************/
/* ==== util: badge de estado global/elemento ==== */
function setBadge(el, txt) {
  const t = String(txt ?? '').toLowerCase().trim();
  let cls = 'unknown';
  let label = txt || 'Unknown';

  // 1) Desconexión / errores de red
  if (
    t.includes('no conect') ||
    t.includes('offline') ||
    /refused|timeout|timed out|dns|modbus/.test(t)
  ) {
    cls = 'error'; label = 'Sin conexión';

  // 2) OK / operando
  } else if (t.includes('ok') || /operando|running|online/.test(t)) {
    cls = 'ok'; label = 'OK';

  // 3) Standby/idle
  } else if (t.includes('standby') || /idle/.test(t)) {
    cls = 'standby'; label = 'Standby';

  // 4) Fallas (no repetir offline)
  } else if (/falla|fail|failure|fault|alarm|error/.test(t)) {
    cls = 'error'; label = 'Fail';

  // 5) Datos crudos / sin datos
  } else if (t.includes('raw')) {
    cls = 'unknown'; label = 'Datos crudos';

  } else if (t.includes('sin datos')) {
    cls = 'unknown'; label = 'No data';
  }

  // Actualiza badge global si existe (opcional)
  const globalEl = document.getElementById('sp-status');
  if (globalEl) {
    globalEl.classList.remove('ok','error','standby','unknown');
    globalEl.classList.add('badge', cls);
    globalEl.textContent = label;
  }

  // Actualiza el badge recibido si existe
  if (el) {
    el.classList.remove('ok','error','standby','unknown');
    el.classList.add('badge', cls);
    el.textContent = label;
  }

  // Por si querés usar el resultado programáticamente
  return { cls, label };
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
   
    if (states.some(s=> /falla|fail|failure|fault|alarm|error/.test(s))) {
      global='Fail';
    } else if (states.length && states.every(s=> s.includes('standby') || /idle/.test(s))) {
      global='Standby';
    } else if (states.some(s=> s.includes('ok') || /operando|running|online/.test(s))) {
      global='Ok';
    }
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
          <td><span class="badge">${i.status_text || '—'}</span></td>
          <td class="mono power-cell">${fmt(i.power_W,' W')}</td>
          <td class="mono volt-cell">${fmt(i.voltage_V,' V')}</td>
          <td class="mono freq-cell">${fmt(i.frequency_Hz,' Hz')}</td>
          <td class="muted">${(i.manufacturer||'')+' '+(i.model||'')}</td>`;

        // ⬅️ colorear el badge por código/grupo
        const statusBadge = tr.querySelector('td .badge');
        setStatusBadgeByCode(statusBadge, i.status_code, i.status_text, i.status_group, i.status);

        statusBadge.textContent = formatStatusLabel(i);
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
    if (statusEl) setBadge(statusEl, 'Fail'); // antes decía "Falla"
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


function setStatusBadgeByCode(el, code, text, group, status){
  // Clase por código
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
    // sin código ni grupo → deja que setBadge por texto se encargue
    setBadge(el, text);
    return;
  }

  // Texto por defecto
  let label = text || (typeof code === 'number' ? `Código ${code}` : '—');

  // Si el estado corto es "fail", forzamos “Fail (código N)” si hay N
  if (String(status || '').toLowerCase() === 'fail') {
    label = (typeof code === 'number') ? `Fail (código ${code})` : 'Fail';
    cls = 'error';
  }

  el.className = `badge ${cls}`;
  el.textContent = label;
}




// === helpers de status ===
function _extractStatusCode(i){
  if (typeof i?.status_code === 'number') return i.status_code;

  const pool = [i?.status_text, i?.error].filter(Boolean).join(' ');
  const m = pool.match(/\b(?:código|code|Errno)[:\s]*(-?\d+)\b/i);
  return m ? Number(m[1]) : null;
}

/**
 * Devuelve el label a mostrar en el badge de estado.
 * - Si status === "fail": "Fail (código N)" cuando haya N; si no, "Fail".
 * - En otros casos: usa status_text si existe; si no hay, y hay código, "Código N"; si no, "—".
 */
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









































