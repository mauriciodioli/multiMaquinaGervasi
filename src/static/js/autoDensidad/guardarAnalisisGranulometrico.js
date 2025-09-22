// CSRF helper
function getCookie(name){ const m=document.cookie.match(new RegExp('(^| )'+name+'=([^;]+)')); return m?decodeURIComponent(m[2]):null; }
// primer número del string (soporta coma)
function num(txt){ const s=(txt||'').toString().replace(',', '.'); const m=s.match(/-?\d+(\.\d+)?/); return m?Number(m[0]):NaN; }

window.guardarAnGranulometricoDb = async function () {
  try {
    const r = window.ultimaCurvaPromedio || {};        // {tamices, curva_resultante, curva_ideal, diferencias, evaluacion, error_promedio, d_max, n}
    const mezcla = window.ultimaMezclaOptima || {};    // {nombres_mezclas, proporciones|pesos_optimos_mezcla}

    // ⚠️ Ajustá estos 2: deben existir
    const usuario_id  = Number(localStorage.getItem('user_id') || 0);
    const agregado_id = 26;

    // Lee TODAS las columnas de la tabla que mostraste (7 columnas)
    const filasTabla = [...document.querySelectorAll('#tabla-comparativa tbody tr')].map(tr => {
      const c = tr.cells;
      return {
        tamiz: num(c[0]?.textContent),            // Tamiz (mm)
        resultante: num(c[1]?.textContent),       // Prom reales (%)
        ideal: num(c[2]?.textContent),            // Prom Fuller (%)
        diferencia: num(c[3]?.textContent),       // ΔProm (%)
        zona: (c[4]?.textContent || '').trim(),   // Zona (gruesos/medios/finos)
        d_max: num(c[5]?.textContent),            // d_max (fila muestra el mismo)
        n: num(c[6]?.textContent)                 // n
      };
    });

   

    const nombresMezclas = mezcla.nombres_mezclas || (window.nombreProductos || []);
    const proporciones   = (mezcla.proporciones || mezcla.pesos_optimos_mezcla || []).map(Number);
    const raw = proporciones.map(v => (v <= 1 ? v * 100 : v));
    const suma = raw.reduce((a,b)=>a+(isFinite(b)?b:0),0) || 0;
    const proporcionesPct = raw.map(v => (suma>0 ? (v/suma)*100 : 0));
    
    // 1) Tomar el <ul> y sus <li>
    const ul = document.getElementById('recomendaciones-list'); // el <ul id="recomendaciones-list">
    const lis = ul ? [...ul.querySelectorAll('li')] : [];

    // 2) Lo que normalmente vas a enviar
    const recomendaciones_ul_html  = ul ? ul.outerHTML.trim() : null;     // el <ul> completo
    const recomendacionesText      = lis.map(li => li.innerText.trim());  // sólo texto
    const recomendacionesHTML      = lis.map(li => li.outerHTML.trim());  // cada <li> con su HTML

    // 3) (Opcional) Parsear tamiz y delta desde el texto
    const reTamiz = /Tamiz\s+([0-9.]+)\s*mm/i;
    const rePct   = /([+-]?\d+(?:\.\d+)?)\s*%/;

    const parsed = lis.map(li => {
      const t = li.innerText;
      const mT = t.match(reTamiz);
      const mP = t.match(rePct);
      return {
        tamiz: mT ? parseFloat(mT[1]) : null,
        delta: mP ? parseFloat(mP[1]) : null
      };
    });


    const d_max = Number(localStorage.getItem('d_max') || NaN);
    const n     = Number(localStorage.getItem('n') || NaN);

    const payload = {
      usuario_id,
      agregado_id,
      descripcion: r.descripcion || 'Análisis granulométrico',
      d_max: Number.isFinite(d_max) ? d_max : null,
      n:   Number.isFinite(n) ? n : null,

      curva: {
        tamices: r.tamices || [],
        resultante: r.promedios || r.curva_resultante || [],
        ideal: r.curva_ideal || [],
        diferencias: r.diferencias || []
      },
      resumen: {
        evaluacion: r.evaluacion ?? null,
        error_promedio: r.error_promedio ?? null,
        ajustes: r.ajustes || []
      },
      mezcla: { nombres: nombresMezclas, proporciones_pct: proporcionesPct },
      tabla_dom: filasTabla,
      // recomendaciones
      recomendaciones_ul_html: recomendaciones_ul_html,
      recomendaciones_dom: recomendacionesText,
      recomendaciones_dom_html: recomendacionesHTML,
      
    };



    if (!usuario_id || !agregado_id) {
      alert('Faltan usuario_id o agregado_id'); return;
    }

    const res = await fetch('/autoDensidad_analisisGranulometrico_guardar_analisis_granulometrico_db/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrf_token') || '' },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.log('✅ Guardado OK:', data);
    alert('✅ Análisis guardado (ID: ' + (data.id ?? '—') + ')');
  } catch (e) {
    console.error('❌ Error al guardar:', e);
    alert('❌ Error al guardar el análisis');
  }
};
