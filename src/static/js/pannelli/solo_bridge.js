// solo_bridge.js — NO toca pannelli.html
(function(){
  // Esperamos al botón que ya EXISTE en la página
  const btn = document.getElementById('btnSoloPannelli');
  if (!btn) return;

  // 1) crear contenedor para la vista SOLO (no requiere HTML previo)
  let solo = document.getElementById('solo-pannelli-dyn');
  if (!solo){
    solo = document.createElement('div');
    solo.id = 'solo-pannelli-dyn';
    solo.style.display = 'none';
    document.body.appendChild(solo); // lo coloco al final del body
  }

  // 2) util: esconder todo lo de la vista normal (sin envolver nada)
  function hideLegacy(){
    // Oculto bloques conocidos sin tocar la plantilla
    const blocks = document.querySelectorAll(
      '.contenedor-flex, .spinner-overlay, .titulo-maquinas, #sidebar, #resizer'
    );
    blocks.forEach(el => { if (el) el.style.display = 'none'; });
  }

  // 3) util: mostrar legacy de nuevo (por si querés volver)
  function showLegacy(){
    const blocks = document.querySelectorAll(
      '.contenedor-flex, .spinner-overlay, .titulo-maquinas, #sidebar, #resizer'
    );
    blocks.forEach(el => { if (el) el.style.display = ''; });
  }

  // 4) inyectar markup del solo_pannelli (copiado acá para no tocar la plantilla)
  function ensureSoloMarkup(){
    if (solo.firstChild) return;
    solo.innerHTML = `
      <section id="solo-panelli-card" class="tabla-container" style="overflow:auto;">
        <div class="grid grid-2">
          <div class="card_panelles" style="grid-column:1 / -1">
            <div class="muted" style="margin-bottom:.5rem">Inverters</div>
            <!-- JS crea #pv-grid -->
          </div>
        </div>
      </section>
    `;

    // cargo CSS si no está
    if (!document.querySelector('link[data-solo-css]')){
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/static/css/pannelli/solo_pannelli.css';
      link.setAttribute('data-solo-css','1');
      document.head.appendChild(link);
    }
  }

  // 5) arranque de la matriz (usa tu mismo polling)
  function startSolo(){
    window.MODE_SOLO = true;                 // bandera para que tu JS NO pinte la tabla
    if (window.prevSnapshot) {               // opcional: limpiar deltas
      window.prevSnapshot = { total_power_W:null, inv:{} };
    }
    // módulo para renderizar la grilla de 12
    if (!window.Pannelli) {
      // definimos un micro-módulo mínimo si no existe
      (function(){
        function ensureGrid(){
          const host = document.querySelector('#solo-panelli-card .card_panelles');
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
        function createCard(ip){
          const d = document.createElement('div');
          d.className = 'pv-card';
          if (ip) d.dataset.ip = ip;
          d.innerHTML = `
            <div class="pv-card-head">
              <span class="pv-ip">${ip||'—'}</span>
              <span class="badge pv-badge">—</span>
            </div>
            <div class="pv-metrics">
              <div class="pv-metric"><span class="lbl">P</span><span class="val mono power-cell">— W</span></div>
              <div class="pv-metric"><span class="lbl">V</span><span class="val mono volt-cell">— V</span></div>
              <div class="pv-metric"><span class="lbl">F</span><span class="val mono freq-cell">— Hz</span></div>
            </div>
            <div class="pv-foot muted pv-model">—</div>
          `;
          return d;
        }
        function renderGrid(inverters, prev){
          const grid = ensureGrid(); if (!grid) return;
          const used = new Set();
          (inverters||[]).slice(0,12).forEach(i=>{
            const ip = i.ip || '—';
            used.add(ip);
            let card = grid.querySelector(`.pv-card[data-ip="${ip}"]`);
            if (!card){ card = createCard(ip); grid.appendChild(card); }
            const b = card.querySelector('.pv-badge');
            if (window.setStatusBadgeByCode) {
              window.setStatusBadgeByCode(b, i.status_code, i.status_text, i.status_group, i.status);
              if (window.formatStatusLabel) b.textContent = window.formatStatusLabel(i);
            } else { b.textContent = i.status_text || '—'; }
            const old = prev?.inv?.[ip] || {};
            const fmt = (n,s='') => (typeof n==='number'&&isFinite(n)) ? n.toLocaleString('es-AR')+s : '—';
            const P = card.querySelector('.power-cell'); if (P) P.textContent = fmt(i.power_W,' W');
            const V = card.querySelector('.volt-cell');  if (V) V.textContent = fmt(i.voltage_V,' V');
            const F = card.querySelector('.freq-cell');  if (F) F.textContent = fmt(i.frequency_Hz,' Hz');
            const M = card.querySelector('.pv-model');   if (M) M.textContent = `${i.manufacturer||''} ${i.model||''}`.trim() || '—';
          });
          // completar hasta 12
          while (grid.children.length < 12) grid.appendChild(createCard());
          while (grid.children.length > 12) grid.removeChild(grid.lastElementChild);
        }
        window.Pannelli = {
          start(){ /* noop: render ocurre en onData */ },
          onData(data, prev){ renderGrid(data?.inverters || [], prev); }
        };
      })();
    }
    // forzar un fetch inmediato
    if (typeof window.pollOnce === 'function') window.pollOnce();
    // scroll
    solo.querySelector('#solo-panelli-card')?.scrollIntoView({behavior:'smooth', block:'start'});
  }

  // CLICK → oculto legacy, muestro solo, arranco
  btn.addEventListener('click', () => {
    ensureSoloMarkup();
    hideLegacy();
    solo.style.display = 'block';
    startSolo();
  });
})();
