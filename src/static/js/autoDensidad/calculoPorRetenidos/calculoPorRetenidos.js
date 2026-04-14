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
    const msg = typeof I18N !== 'undefined' ? I18N.t('sim.error_sin_tablas') : 'No hay tablas cargadas en localStorage.';
    showToast(msg);
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

  // Helper para traducción segura
  const t = (key, fallback) => typeof I18N !== 'undefined' ? I18N.t(key) : fallback;

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
      msg.textContent = t('sim.prop_error_suma_100', 'Las proporciones deben sumar 100%');
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
  // Traducir el modal con el idioma actual
  setTimeout(() => {
    const modal = document.getElementById('modalProporciones');
    if (modal && typeof I18N !== 'undefined') {
      I18N.applyTranslations(modal);
    }
  }, 50);
}



function abrirProporcionesYCalcular(){
  // sanity check: debe existir tablasCargadas en localStorage
  const tablas = leerTablasCargadas?.() || [];
  if (!Array.isArray(tablas) || !tablas.length){
    const msg = typeof I18N !== 'undefined' ? I18N.t('sim.error_sin_tablas') : 'No hay tablas cargadas en localStorage.';
    showToast(msg);
    return;
  }

  // Abre el modal de proporciones. Cuando el usuario presiona “Usar valores”
  // el modal llama a este callback y recién ahí disparamos el cálculo.
  abrirModalProporciones(() => {
    try {
      // 🔍 VALIDACIONES ANTES DE CALCULAR
      const errores = validarDatosCompletos();
      if (errores.length > 0) {
        mostrarErroresValidacion(errores);
        return;  // No continuar si hay errores
      }
      
      calcularRetenidoBR();  // tu flujo actual (fetch + gráfico + modal resultado)
    } catch (e){
      console.error(e);
      alert('Error al calcular retenidos: ' + e.message);
    }
  });
}

/**
 * 🔍 VALIDAR INTEGRIDAD DE DATOS
 * Verifica:
 * 1. Que cada tabla tenga retidos que sumen 100%
 * 2. Que los tamices sean consistentes (sin duplicados, valores correctos)
 */
function validarDatosCompletos(){
  const errores = [];
  const t = (key, fallback) => typeof I18N !== 'undefined' ? I18N.t(key) : fallback;
  
  // Función para detectar si los valores son pasantes o retidos
  function detectarFormatoValores(valores) {
    // Si la suma es cercana a 100 y los valores decrecen: probablemente pasantes
    // Si la suma es cercana a 100 y los valores crecen: probablemente retidos
    const suma = valores.reduce((a, b) => a + b, 0);
    
    // Si suma está cercana a 100, probablemente sean valores individuales correctos
    if (Math.abs(suma - 100) < 2) {
      // Verificar si decrecen (pasantes) o crecen inconsistentemente (retidos)
      let decrece = true;
      for (let i = 1; i < valores.length; i++) {
        if (valores[i] > valores[i-1]) {
          decrece = false;
          break;
        }
      }
      return decrece ? 'pasantes' : 'retidos';
    }
    
    // Si suma es grande (como 343), son claramente pasantes
    return suma > 100 ? 'pasantes' : 'retidos';
  }
  
  // Función para convertir pasantes acumulados a retidos individuales
  function pasantesARetidos(pasantes) {
    const retidos = [];
    retidos.push(100 - pasantes[0]); // Primer retido = 100 - pasante 1
    for (let i = 1; i < pasantes.length; i++) {
      retidos.push(pasantes[i-1] - pasantes[i]);
    }
    return retidos;
  }
  
  // 1️⃣ VALIDAR RETIDOS POR TABLA
  const mezclas = document.querySelectorAll('.mezcla');
  
  mezclas.forEach((mezcla, idx) => {
    const nombre = (mezcla.querySelector('.nombreProducto')?.value || 'Sin nombre').trim();
    
    let sumaRetidos = 0;
    const tamicesDetectados = [];
    const porcentajesFueraDeRango = [];
    
    // Leer todos los valores primero para detectar formato
    const valoresLei= [];
    const filas = [];
    
    mezcla.querySelectorAll('tbody tr').forEach(tr => {
      const tRaw = tr.cells[0]?.textContent?.trim();
      const rRaw = tr.cells[1]?.textContent?.trim();
      const tNum = parseFloat(tRaw);
      const rNum = parseFloat(rRaw);
      
      if (!isNaN(tNum) && !isNaN(rNum)) {
        valoresLei.push(rNum);
        filas.push({ tRaw, rRaw, tNum, rNum });
      }
    });
    
    // Detectar si son pasantes o retidos
    const formato = detectarFormatoValores(valoresLei);
    let retidosConvertidos = valoresLei;
    
    if (formato === 'pasantes') {
      console.log(`📊 Tabla "${nombre}": Detectado formato PASANTES. Convirtiendo a retidos...`);
      retidosConvertidos = pasantesARetidos(valoresLei);
      console.log(`   Retidos convertidos: [${retidosConvertidos.map(r => r.toFixed(2)).join(', ')}]`);
    } else {
      console.log(`📊 Tabla "${nombre}": Detectado formato RETIDOS.`);
    }
    
    // Ahora validar los retidos
    filas.forEach((fila, i) => {
      let r = retidosConvertidos[i];
      const tRaw = fila.tRaw;
      const t = fila.tNum;
      
      if (!isNaN(r)) {
        // ✅ VALIDACIÓN: Rango 0-100%
        if (r < 0 || r > 100) {
          porcentajesFueraDeRango.push({
            tamiz: tRaw,
            valor: r,
            problema: r < 0 ? 'negativo' : 'mayor_100'
          });
        }
        
        if (r > 0) {
          sumaRetidos += r;
          tamicesDetectados.push({ valor: t, texto: tRaw });
        }
      }
    });
    
    // Validar que no haya porcentajes fuera de rango
    if (porcentajesFueraDeRango.length > 0) {
      errores.push({
        tabla: nombre,
        tipo: 'PORCENTAJES_FUERA_RANGO',
        valores: porcentajesFueraDeRango,
        severidad: 'CRÍTICA'
      });
    }
    
    // Validar suma de retidos
    if (Math.abs(sumaRetidos - 100) > 1.0) {
      const faltanteValue = (100 - sumaRetidos).toFixed(2);
      let sugerencia = '';
      
      // Si fue detectado como pasantes y falta poco (< 10%), probablemente sea el Fundo
      if (formato === 'pasantes' && faltanteValue < 10 && faltanteValue > 0) {
        const ultimoTamiz = filas.length > 0 ? filas[filas.length - 1].tRaw : '0.075';
        sugerencia = {
          tipo: 'fundo_missing',
          ultimoTamiz: ultimoTamiz,
          faltanteValue: faltanteValue
        };
      }
      
      errores.push({
        tabla: nombre,
        tipo: 'RETIDOS_INCOMPLETOS',
        suma: sumaRetidos.toFixed(2),
        falta: faltanteValue,
        sugerencia: sugerencia,
        severidad: 'CRÍTICA'
      });
    }
  });
  
  // 2️⃣ VALIDAR TAMICES Y DUPLICADOS POR TABLA
  const TAMICES_VALIDOS = [12.5, 9.5, 6.3, 4.8, 2.4, 1.2, 0.6, 0.3, 0.15, 0.075];
  
  mezclas.forEach((mezcla, idx) => {
    const nombre = (mezcla.querySelector('.nombreProducto')?.value || 'Sin nombre').trim();
    const tamicesDeMezcla = [];
    
    mezcla.querySelectorAll('tbody tr').forEach(tr => {
      const tRaw = tr.cells[0]?.textContent?.trim();
      const t = parseFloat(tRaw);
      
      if (!isNaN(t)) {
        tamicesDeMezcla.push({ valor: t, texto: tRaw });
        
        // Buscar valores sospechosos (e.g., 0.75 cuando debería ser 0.075)
        if (!TAMICES_VALIDOS.includes(t)) {
          const similares = TAMICES_VALIDOS.filter(v => 
            Math.abs(v - t) < 0.5  // Diferencia <= 0.5 mm
          );
          
          if (similares.length > 0) {
            errores.push({
              tipo: 'TAMIZ_INCONSISTENTE',
              tabla: nombre,
              valor: tRaw,
              sugerencia: similares[0],
              severidad: 'CRÍTICA'
            });
          }
        }
      }
    });
    
    // Detectar duplicados DENTRO de esta mezcla
    const tamicesDuplicados = tamicesDeMezcla
      .map(t => t.valor)
      .filter((v, i, arr) => arr.indexOf(v) !== i);
    
    if (tamicesDuplicados.length > 0) {
      errores.push({
        tipo: 'TAMICES_DUPLICADOS',
        tabla: nombre,
        valores: [...new Set(tamicesDuplicados)],
        severidad: 'CRÍTICA'
      });
    }
  });
  
  return errores;
}

/**
 * 📢 MOSTRAR ERRORES DE VALIDACIÓN AL USUARIO
 */
function mostrarErroresValidacion(errores){
  // Read translations from global DPIA_I18N (defined in dpia_i18n.js)
  const lang = localStorage.getItem("lang") || "es";
  const T = window.DPIA_I18N?.[lang] || window.DPIA_I18N?.["es"] || {};
  
  const titulo = T.validation_title || "⚠️ Errores de Validación Detectados";
  const descripcion = T.validation_subtitle || "No se puede continuar con el cálculo. Corrija los errores indicados:";
  const lblTabla = T.tabla || "Tabla";
  const lblRetidosSuma = T.retidos_suman || "Retidos suman";
  const lblFalta = T.falta || "Falta";
  const lblDatosIncompletos = T.datos_incompletos || "Datos incompletos";
  const lblTamizIncorrecto = T.tamiz_incorrecto || "Tamiz Incorrecto";
  const lblValorIngresado = T.valor_ingresado || "Valor ingresado";
  const lblQuisoDecir = T.quiso_decir || "¿Quiso decir";
  const lblMm = T.mm || "mm?";
  const lblTamicesDuplicados = T.tamices_duplicados || "Tamices Duplicados";
  const lblValoresRepetidos = T.valores_repetidos || "Valores repetidos encontrados";
  const lblPorcentajesFueraRango = T.porcentajes_fuera_rango || "Porcentajes fuera de rango";
  const lblRangoInvalido = T.rango_invalido || "Los porcentajes deben estar entre 0% y 100%";
  const lblValorNegativo = T.valor_negativo || "valor negativo";
  const lblMayor100 = T.mayor_100 || "mayor que 100%";
  const lblSugerencia = T.fix_errors || "Corrija estos errores antes de continuar.";
  const btnEntendido = T.btn_entendido || "Entendido, voy a corregir";
  
  let html = `
    <div style="background:#ffebee; border:2px solid #c62828; border-radius:8px; padding:16px; margin:16px 0;">
      <h3 style="color:#c62828; margin-top:0;">
        ${titulo}
      </h3>
      <p style="color:#666; font-size:14px;">
        ${descripcion}
      </p>
      
      <ul style="list-style:none; padding:0;">
  `;
  
  errores.forEach(error => {
    if (error.tipo === 'PORCENTAJES_FUERA_RANGO') {
      const detalles = error.valores.map(v => 
        `${v.problema === 'negativo' 
          ? `❌ ${v.tamiz}mm: ${v.valor}% (${lblValorNegativo})` 
          : `❌ ${v.tamiz}mm: ${v.valor}% (${lblMayor100})`}`
      ).join('<br>');
      html += `
        <li style="background:#ffccbc; border-left:4px solid #d84315; padding:8px; margin:8px 0; border-radius:4px;">
          <strong>🔴 ${error.tabla}: ${lblPorcentajesFueraRango}</strong><br>
          ${detalles}<br>
          <span style="color:#d32f2f; font-weight:bold;">${lblRangoInvalido}</span>
        </li>
      `;
    } else if (error.tipo === 'RETIDOS_INCOMPLETOS') {
      let sugerenciaHtml = '';
      if (error.sugerencia) {
        // If sugerencia is an object (structured data)
        if (typeof error.sugerencia === 'object' && error.sugerencia.tipo === 'fundo_missing') {
          const fundo_alt = T.fundo_alt ? T.fundo_alt.replace('{{mm}}', error.sugerencia.ultimoTamiz) : `(o < ${error.sugerencia.ultimoTamiz})`;
          sugerenciaHtml = `<div style="margin-top:8px; padding:8px; background:#e8f5e9; border-radius:3px; border-left:3px solid #4caf50; font-size:0.9em; line-height:1.5;">
            <div><strong>${T.sugerencia_fundo || '💡 SUGERENCIA: Parece que falta la fila del "Fundo" (últimas partículas).'}</strong></div>
            <div>${T.agregar_fila || 'Agrege una fila con:'}</div>
            <div>• ${T.tamiz_label || 'Tamiz'}: "Fundo" ${fundo_alt}</div>
            <div>• ${T.porcentaje_label || 'Porcentaje'}: ${error.sugerencia.faltanteValue}%</div>
          </div>`;
        } else if (typeof error.sugerencia === 'string') {
          // Backward compatibility: if sugerencia is a string, render as before
          sugerenciaHtml = `<div style="margin-top:8px; padding:8px; background:#e8f5e9; border-radius:3px; border-left:3px solid #4caf50; font-size:0.9em; line-height:1.5;">
            ${error.sugerencia.split('\n').map(line => `<div>${line}</div>`).join('')}
          </div>`;
        }
      }
      html += `
        <li style="background:#fff9c4; border-left:4px solid #fbc02d; padding:8px; margin:8px 0; border-radius:4px;">
          <strong>📊 ${lblTabla}: ${error.tabla}</strong><br>
          ${lblRetidosSuma}: <strong>${error.suma}%</strong> (${lblFalta} ${error.falta}%)<br>
          <span style="color:#d32f2f; font-weight:bold;">${lblDatosIncompletos}</span>
          ${sugerenciaHtml}
        </li>
      `;
    } else if (error.tipo === 'TAMIZ_INCONSISTENTE') {
      html += `
        <li style="background:#ffccbc; border-left:4px solid #d84315; padding:8px; margin:8px 0; border-radius:4px;">
          <strong>🔍 ${error.tabla ? `${error.tabla} - ` : ''}${lblTamizIncorrecto}</strong><br>
          ${lblValorIngresado}: <strong>${error.valor}</strong><br>
          ${lblQuisoDecir}: <strong style="color:#1976d2;">${error.sugerencia} ${lblMm}</strong>?
        </li>
      `;
    } else if (error.tipo === 'TAMICES_DUPLICADOS') {
      html += `
        <li style="background:#f3e5f5; border-left:4px solid #7b1fa2; padding:8px; margin:8px 0; border-radius:4px;">
          <strong>🔄 ${error.tabla ? `${error.tabla} - ` : ''}${lblTamicesDuplicados}</strong><br>
          ${lblValoresRepetidos}: <strong>${error.valores.join(', ')} ${lblMm}</strong>
        </li>
      `;
    }
  });
  
  html += `
      </ul>
      
      <div style="background:#e3f2fd; padding:12px; border-radius:4px; margin-top:12px; border-left:4px solid #1976d2;">
        <p style="color:#1976d2; margin:0; font-size:13px;">
          💡 ${lblSugerencia}
        </p>
      </div>
    </div>
  `;
  
  // Mostrar modal
  const modal = document.createElement('div');
  modal.id = 'modalErroresValidacion';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 10000;
    padding: 24px;
    max-width: 500px;
    max-height: 80vh;
    overflow-y: auto;
  `;
  
  modal.innerHTML = html + `
    <div style="margin-top:16px;">
      <button onclick="document.getElementById('modalErroresValidacion').remove(); document.getElementById('modalErroresOverlay').remove();" 
              style="width:100%; padding:10px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">
        ${btnEntendido}
      </button>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Overlay
  const overlay = document.createElement('div');
  overlay.id = 'modalErroresOverlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 9999;
  `;
  document.body.appendChild(overlay);
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
        retido_ind_pct: retidosLoc,
        normalizar: false          // STEP 3: Add normalization flag (always true for now)
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

  // STEP 6: Debug BEFORE sending
  console.log("FINAL PAYLOAD:", payload);
  console.log("Materiales transformados:", payload.materiales);

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
    
    // 💾 Guardar límites en localStorage para que auditoría los pueda usar
    if (data.faixas && data.faixas.bloco) {
      try {
        const banda_min = data.faixas.bloco.map(spec => spec.min);
        const banda_max = data.faixas.bloco.map(spec => spec.max);
        localStorage.setItem('limitesGranulometria', JSON.stringify({
          banda_min: banda_min,
          banda_max: banda_max,
          tamices: data.tamices,
          timestamp: new Date().toISOString()
        }));
        console.log('💾 Límites guardados en localStorage para auditoría');
      } catch (e) {
        console.warn('No se pudieron guardar los límites:', e);
      }
    }
    
    renderRetidoGrafico(
      data.tamices,
      data.mix_acum,
      data.mix_pasante,
      data.faixas,
      data.fuller_ideal
    );
    //renderRetidoGrafico( data.tamices, data.mix_pasante, data.faixas, { faixa: 'bloco' } );
    renderRetidoTablitas(data.tamices, data.mix_acum, data.faixas);
    if (data.sugerencia_division) {
      renderSugerenciaDivision(data.sugerencia_division);
    }
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

//function renderRetidoGrafico(tamices, mix_acum, faixas, opts = { faixa: 'bloco' }) {
function renderRetidoGrafico(tamices, mix_acum, mix_pasante, faixas, fuller_ideal, opts = { faixa: 'bloco' }) {
  // Mapear a puntos X,Y en eje log y preparar etiquetas exactas (incluye FUNDO)
  const FUNDO_X = 0.01;

  // 🔨 Agregar 12.5 mm (agregado máximo estándar) si no está presente
  if (tamices.length > 0 && parseFloat(tamices[0]) !== 12.5) {
    tamices = [12.5, ...tamices];
    mix_acum = [100, ...mix_acum];  // 12.5 mm: todo pasa (100%)
    mix_pasante = [100, ...mix_pasante];  // todo pasa
    fuller_ideal = fuller_ideal ? [100, ...fuller_ideal] : [];  // Fuller(12.5) = 100%
  }

  const dataOrdenada = tamices.map((t, i) => ({
    x: String(t).toLowerCase() === 'fundo' ? FUNDO_X : parseFloat(t),
    label: String(t),
    acum: parseFloat(mix_acum[i]),
    pasante: parseFloat(mix_pasante[i]),
    idx: i
  }))
  .filter(p => !Number.isNaN(p.x))
  .sort((a,b) => a.x - b.x);

  // 👉 Prepare axes data
  const xs = dataOrdenada.map(p => p.x);
  const labels = dataOrdenada.map(p => p.label);

  // 🌍 Obtener etiquetas traducidas para el gráfico
  const getLabel = (key, fallback) => {
    if (typeof I18N === 'undefined' || !I18N || typeof I18N.t !== 'function') return fallback;
    try {
      const val = I18N.t(key);
      // Si devuelve [key], significa que no existe, retorna fallback
      return val.startsWith('[') ? fallback : val;
    } catch (e) {
      return fallback;
    }
  };
  
  const labelBlocoMin = getLabel('sim.retido_bloco_min', 'Limites para Blocos (min)');
  const labelBlocoMax = getLabel('sim.retido_bloco_max', 'Limites para Blocos (max)');
  const labelPaverMin = getLabel('sim.retido_paver_min', 'Limites para Pavers (min)');
  const labelPaverMax = getLabel('sim.retido_paver_max', 'Limites para Pavers (max)');
  const labelFullerIdeal = getLabel('sim.retido_fuller_ideal', 'Curva Fuller Ideal');
  const labelRetidoAcum = getLabel('sim.retido_acumulado', 'Retido acumulado');
  const labelPasante = getLabel('sim.retido_pasante', 'Pasante');
  const axisXTitle = getLabel('sim.retido_axis_x', 'Peneira (mm)');
  const axisYTitle = getLabel('sim.retido_axis_y', '% Retido Acumulado');
  const axisY1Title = getLabel('sim.retido_axis_y1', '% Pasante');

  // ---- Limites por tamiz: construimos 4 curvas (bloco min/max, paver min/max) ----
  const detBloco = (faixas && faixas.bloco) ? faixas.bloco : [];
  const detPaver = (faixas && faixas.paver) ? faixas.paver : [];

  // Reordenar según xs (por si hubiese desfasajes)
  const reorder = (det, pick) => dataOrdenada.map(p => {
    const key = p.label;
    const idx = tamices.findIndex(t => String(t) === key);
    const d = det[idx];
    if (!d || d.min == null || d.max == null) return null;
    return pick === 'min' ? d.min : d.max;
  });

  const blocoMin = reorder(detBloco, 'min');
  const blocoMax = reorder(detBloco, 'max');
  const paverMin = reorder(detPaver, 'min');
  const paverMax = reorder(detPaver, 'max');

  // Reordenar fuller_ideal según dataOrdenada
  const fullerIdealReordenada = !fuller_ideal ? [] : dataOrdenada.map(p => {
    const key = p.label;
    const idx = tamices.findIndex(t => String(t) === key);
    const val = fuller_ideal[idx];
    return val != null ? val : null;
  });

  // Helper to convert array of y-values to {x, y} dataset format (filter out nulls)
  const toDataset = (yArr) => dataOrdenada.map((p, i) => {
    const y = yArr[i];
    return y != null ? {x: p.x, y: y} : null;
  }).filter(v => v != null);

  // Preparar canvas
  const ctx = document.getElementById('retidoChart').getContext('2d');
  if (retidoChart) retidoChart.destroy();

  retidoChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        // === Limites para Blocos (azul sólido, dos curvas) ===
        {
          label: labelBlocoMin,
          data: toDataset(blocoMin),
          borderColor: '#1f6bff',
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },
        {
          label: labelBlocoMax,
          data: toDataset(blocoMax),
          borderColor: '#004aad',
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },

        // === Limites para Pavers (negro punteado, dos curvas) ===
        {
          label: labelPaverMin,
          data: toDataset(paverMin),
          borderColor: '#111',
          borderDash: [6, 5],
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },
        {
          label: labelPaverMax,
          data: toDataset(paverMax),
          borderColor: '#111',
          borderDash: [6, 5],
          pointRadius: 0,
          borderWidth: 2,
          fill: false
        },

        // === Curva Fuller Ideal (amarilla sólida, referencia teórica) ===
        {
          label: labelFullerIdeal,
          data: toDataset(fullerIdealReordenada),
          borderColor: '#FFD700',
          backgroundColor: '#FFD700',
          pointRadius: 2,
          tension: 0.25,
          borderWidth: 3,
          fill: false,
          yAxisID: 'y'
        },

        // === Curva en estudio (roja sólida con puntos) ===
        {
          label: labelRetidoAcum,
          data: dataOrdenada.map(p => ({x: p.x, y: p.acum})),
          borderColor: '#e74c3c',
          backgroundColor: '#e74c3c',
          pointRadius: 3,
          tension: 0.25,
          borderWidth: 2,
          fill: false,
          yAxisID: 'y'
        },
        {
          label: labelPasante,
          data: dataOrdenada.map(p => ({x: p.x, y: p.pasante})),
          borderColor: '#2ecc71',
          backgroundColor: '#2ecc71',
          pointRadius: 3,
          tension: 0.25,
          borderWidth: 2,
          borderDash: [5,5],
          fill: false,
          yAxisID: 'y1' 
        }
      ]
    },
    options: {
      parsing: false,
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
          min: Math.min(...xs) / 2,
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
          title: { display: true, text: axisXTitle }
        },
        y: {
          type: 'linear',
          position: 'left',
          min: 0,
          max: 100,
          title: {
            display: true,
            text: axisYTitle
          }
        },
        y1: {
          type: 'linear',
          position: 'right',
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false
          },
          title: {
            display: true,
            text: axisY1Title
          }
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

  // Helper para i18n seguro
  const t = (key, fallback = '') => typeof I18N !== 'undefined' ? I18N.t(key) : fallback;

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
  const tbl1Title = t('sim.retido_tabla1_titulo');
  const col1Title = t('sim.retido_tabla1_col1');
  const col2Title = t('sim.retido_tabla1_col2');
  const tbl1 = `
    <div class="mini-card">
      <div class="mini-title">${tbl1Title}</div>
      <table class="mini-table">
        <thead><tr><th>${col1Title}</th><th>${col2Title}</th></tr></thead>
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
  const tbl2Title = t('sim.retido_tabla2_titulo');
  const tbl2Nota = t('sim.retido_tabla2_nota');
  const col1 = t('sim.retido_tabla2_col1');
  const col2 = t('sim.retido_tabla2_col2');
  const col3 = t('sim.retido_tabla2_col3');
  const col4 = t('sim.retido_tabla2_col4');
  const col5 = t('sim.retido_tabla2_col5');
  const tbl2 = `
    <div class="mini-card">
      <div class="mini-title">${tbl2Title}</div>
      <table class="mini-table">
        <thead>
          <tr>
            <th rowspan="2">${col1}</th>
            <th colspan="2">${col2}</th>
            <th colspan="2">${col3}</th>
          </tr>
          <tr>
            <th>${col4}</th><th>${col5}</th>
            <th>${col4}</th><th>${col5}</th>
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
      <div class="muted" style="margin-top:6px">${tbl2Nota}</div>
    </div>`;

  host.innerHTML = tbl1 + tbl2;
}

function renderSugerenciaDivision(sugerencia_division){
  if (!sugerencia_division || !sugerencia_division.grupos) return;

  const host = document.getElementById('retidoTables');
  if (!host) return;

  // Helper para i18n seguro con fallbacks en español
  const t = (key, fallback = '') => typeof I18N !== 'undefined' ? I18N.t(key) : fallback;

  const { grupos, reconstruccion_check, debug } = sugerencia_division;
  if (grupos.length < 2) return;

  // Traduciones (con fallbacks en español)
  const titulo = t('sim.division_titulo', 'División de Mezcla');
  const desc = t('sim.division_desc_base', 'Análisis de división granulométrica');
  const grupo = t('sim.division_grupo_n', 'Grupo');
  const proporcion = t('sim.division_proporcion', 'Proporción');
  const pesoOriginal = t('sim.division_peso_original', 'Peso Original');
  const debugBtn = t('sim.division_debug_btn', 'Mostrar Detalles');
  const debugBtnClose = t('sim.division_debug_btn_close', 'Ocultar Detalles');
  const debugCutpoint = t('sim.division_debug_cutpoint', 'Punto de corte seleccionado:');
  const debugIndice = t('sim.division_debug_indice', 'Índice:');
  const debugTamiz = t('sim.division_debug_tamiz', 'Tamiz:');
  const debugSalto = t('sim.division_debug_salto', 'Salto detectable:');
  const debugAcum = t('sim.division_debug_acum', 'Acumulado en corte:');
  const debugCriterios = t('sim.division_debug_criterios', 'Criterios de detección aplicados:');
  const debugFiltro = t('sim.division_debug_filtro_ruido', 'Filtro mínimo de ruido:');
  const debugZona = t('sim.division_debug_zona_valida', 'Rango válido acumulado:');
  const debugZonaEntre = t('sim.division_debug_zona_entre', '-');
  const debugAnalisis = t('sim.division_debug_analisis', 'Análisis granulométrico por tamiz:');
  const debugTablaIndice = t('sim.division_debug_tabla_indice', 'Índice');
  const debugTablaAcum = t('sim.division_debug_tabla_acum', 'Acum %');
  const debugTablaSalto = t('sim.division_debug_tabla_salto', 'Salto %');
  const debugTablaNota = t('sim.division_debug_tabla_nota', 'Amarillo = Punto de corte seleccionado');

  // Determinar grid dinámicamente basado en # de grupos
  const numGrupos = grupos.length;
  const gridCols = numGrupos === 2 ? '1fr 1fr' : numGrupos === 3 ? '1fr 1fr 1fr' : '1fr';

  // Grid DINÁMICO
  let html = `
    <div class="mini-card" style="grid-column: 1 / -1;">
      <div class="mini-title" style="color: #1a73e8; font-size: 0.95rem; margin-bottom: 8px;">${titulo}</div>
      <div style="font-size: 0.85rem; color: #666; margin-bottom: 12px;">${desc} ${reconstruccion_check.error_total_pct}%</div>
      
      <div style="display: grid; grid-template-columns: ${gridCols}; gap: 12px;">`;

  // Generar dinámicamente cada grupo
  grupos.forEach((g, idx) => {
    html += `
        <div style="border: 1px solid #e8eef7; border-radius: 6px; padding: 10px; background: #f8fafb;">
          <h4 style="margin: 0 0 8px 0; font-size: 0.9em; color: #1a73e8; font-weight: 600;">${grupo} ${idx + 1}</h4>
          <div style="font-size: 0.85rem; font-weight: 500; color: #666; margin-bottom: 8px;">
            ${proporcion} <strong>${g.proporcion_sugerida_pct}%</strong>
          </div>
          <table class="mini-table" style="font-size: 0.8rem; margin-bottom: 8px;">
            <thead>
              <tr>
                <th>Tamiz</th>
                <th>Ret. %</th>
              </tr>
            </thead>
            <tbody>
              ${(g.retido_ind_pct_normalizado || []).map((ret, i) => `
                <tr>
                  <td>${g.tamices && g.tamices[i] ? g.tamices[i] : '-'}</td>
                  <td>${typeof ret === 'number' ? ret.toFixed(2) : '0.00'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          <div style="font-size: 0.8rem; color: #888; border-top: 1px solid #e8eef7; padding-top: 6px;">
            <strong>${pesoOriginal}</strong> ${typeof g.peso_original === 'number' ? g.peso_original.toFixed(2) : '0.00'}%
          </div>
        </div>`;
  });

  html += `
      </div>`;

  // Agregar sección de debug si existe
  if (debug) {
    const debugId = 'debugSection_' + Math.random().toString(36).slice(2);
    const esDivisionDos = numGrupos === 2 && debug.idx_corte !== undefined;
    const esDivisionTres = numGrupos === 3 && debug.idx1 !== undefined;

    html += `
      <div style="margin-top: 16px; border-top: 1px solid #e8eef7; padding-top: 12px;">
        <button type="button" onclick="toggleDebugInfo('${debugId}')" 
                style="background: none; border: none; color: #1a73e8; padding: 0; cursor: pointer; font-size: 0.85rem; font-weight: 500;">
          ${debugBtn}
        </button>
        <div id="${debugId}" style="display: none; margin-top: 8px; padding: 10px; background: #f8fafb; border-radius: 4px; border-left: 3px solid #dadce0;">
          <div style="font-size: 0.8rem; line-height: 1.6; color: #555;">`;

    // DEBUG para DIVISIÓN EN 2
    if (esDivisionDos) {
      html += `
            <div style="margin-bottom: 10px;">
              <strong>${debugCutpoint}</strong><br>
              ${debugIndice} ${debug.idx_corte} | ${debugTamiz} ${debug.tamiz_corte} | ${debugSalto} ${( typeof debug.max_diff_pct === 'number' ? debug.max_diff_pct.toFixed(2) : '0.00')}%<br>
              ${debugAcum} ${(typeof debug.acum_corte_pct === 'number' ? debug.acum_corte_pct.toFixed(2) : '0.00')}%
            </div>`;

      if (debug.criterios_aplicados) {
        html += `
            <div style="margin-bottom: 10px;">
              <strong>${debugCriterios}</strong><br>
              ${debugFiltro} ${debug.criterios_aplicados.ruido_min}%<br>
              ${debugZona} ${debug.criterios_aplicados.acum_min}% ${debugZonaEntre} ${debug.criterios_aplicados.acum_max}%
            </div>`;
      }
    }

    // DEBUG para DIVISIÓN EN 3
    if (esDivisionTres) {
      html += `
            <div style="margin-bottom: 10px;">
              <strong>Puntos de Corte</strong><br>
              Índice 1: ${debug.idx1} | Índice 2: ${debug.idx2}
            </div>`;

      if (debug.criterios_aplicados) {
        html += `
            <div style="margin-bottom: 10px;">
              <strong>${debugCriterios}</strong><br>
              ${debugFiltro} ${debug.criterios_aplicados.ruido_min}%<br>
              ${debugZona} ${debug.criterios_aplicados.acum_min}% ${debugZonaEntre} ${debug.criterios_aplicados.acum_max}%
            </div>`;
      }
    }

    // Tabla de acumulado y diferencias (ambos casos)
    if (debug.acumulado && debug.diffs) {
      html += `
            <div style="margin-bottom: 10px;">
              <strong>${debugAnalisis}</strong>
              <table style="width: 100%; margin-top: 5px; border-collapse: collapse; font-size: 0.75rem;">
                <thead style="background: #e8eef7;">
                  <tr>
                    <th style="padding: 3px; text-align: left; border: 1px solid #dadce0;">${debugTablaIndice}</th>
                    <th style="padding: 3px; text-align: right; border: 1px solid #dadce0;">${debugTablaAcum}</th>
                    <th style="padding: 3px; text-align: right; border: 1px solid #dadce0;">${debugTablaSalto}</th>
                  </tr>
                </thead>
                <tbody>`;
      for (let i = 0; i < debug.acumulado.length; i++) {
        const acum = debug.acumulado[i];
        const diff = debug.diffs[i] || 0;
        
        // Destacar puntos de corte
        let bgColor = '';
        let highlight = false;
        
        if (esDivisionDos && i === debug.idx_corte - 1) {
          bgColor = '#fff3cd';
          highlight = true;
        }
        if (esDivisionTres && (i === debug.idx1 - 1 || i === debug.idx2 - 1)) {
          bgColor = '#fff3cd';
          highlight = true;
        }
        
        html += `
                  <tr style="background: ${bgColor}; ${highlight ? 'font-weight: bold;' : ''}">
                    <td style="padding: 3px; border: 1px solid #dadce0;">${i}</td>
                    <td style="padding: 3px; text-align: right; border: 1px solid #dadce0;">${(typeof acum === 'number' ? acum.toFixed(1) : '0.0')}</td>
                    <td style="padding: 3px; text-align: right; border: 1px solid #dadce0;">${(typeof diff === 'number' ? diff.toFixed(2) : '0.00')}</td>
                  </tr>`;
      }
      html += `
                </tbody>
              </table>
              <div style="font-size: 0.7rem; color: #999; margin-top: 4px;">
                ${debugTablaNota}
              </div>
            </div>`;
    }

    html += `
          </div>
        </div>
      </div>`;
  }

  html += `</div>`;

  // Agregar al final del contenido existente
  host.innerHTML += html;
}

// Helper para toggle de debug info
function toggleDebugInfo(debugId) {
  const elem = document.getElementById(debugId);
  if (elem) {
    const btn = elem.previousElementSibling;
    const isOpen = elem.style.display !== 'none';
    if (isOpen) {
      elem.style.display = 'none';
      const closedText = typeof I18N !== 'undefined' ? I18N.t('sim.division_debug_btn') : 'Mostrar Detalles';
      btn.textContent = closedText;
    } else {
      elem.style.display = 'block';
      const openText = typeof I18N !== 'undefined' ? I18N.t('sim.division_debug_btn_close') : 'Ocultar Detalles';
      btn.textContent = openText;
    }
  }
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
  const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
  tr.innerHTML = `
    <td><input type="number" step="0.01" class="dpia-input ens-ac" value="${ac}"></td>
    <td><input type="number" step="0.1"  class="dpia-input ens-mpa" value="${mpa}"></td>
    <td><button class="dpia-btn dpia-btn--tiny" data-del="1" title="${btnLabel}">×</button></td>`;
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

  // Obtener labels traducidos (con fallbacks)
  const labelEnsayos = typeof I18N !== 'undefined' ? I18N.t('sim.chart_label_ensayos') : 'Ensayos';
  const labelAjuste = typeof I18N !== 'undefined' ? I18N.t('sim.chart_label_ajuste') : 'Ajuste';
  const axisX = typeof I18N !== 'undefined' ? I18N.t('sim.chart_axis_x') : 'Tamiz (mm)';
  const axisY = typeof I18N !== 'undefined' ? I18N.t('sim.chart_axis_y') : 'Pasante %';

  if (chartConsumo) chartConsumo.destroy();
  chartConsumo = new Chart(ctx, {
    type:'line',
    data:{
      labels: xs,
      datasets:[
        {label:labelEnsayos, data: pts.map(p=>({x:p.x,y:p.y})), showLine:false, pointRadius:4, borderWidth:0},
        {label:labelAjuste, data: xs.map((x,i)=>({x, y:ys[i]})), borderWidth:2, pointRadius:0, tension:0}
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      parsing:false, // usamos {x,y}
      scales:{
        x:{ type:'linear', title:{display:true, text:axisX} },
        y:{ title:{display:true, text:axisY} }
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

  const trazoLabel = typeof I18N !== 'undefined' ? I18N.t('sim.consumo_trazo_label') : 'Trazo';
  const cementoLabel = typeof I18N !== 'undefined' ? I18N.t('sim.consumo_cemento_label') : 'Cemento';
  const porLabel = typeof I18N !== 'undefined' ? I18N.t('sim.consumo_por_label') : 'para';
  const kgAgLabel = typeof I18N !== 'undefined' ? I18N.t('sim.consumo_kg_agregados') : 'kg agregados';

  document.getElementById('resultadoTrazo').innerHTML =
    `${trazoLabel} <b>${xreq.toFixed(2)}</b>  →  ${cementoLabel} <b>${lote.kgCemento} kg</b> ${porLabel} ${kgAgg} ${kgAgLabel}.`;

  const rows = lote.agregados.map(r=>`${r.nombre}: ${r.kg} kg (${r.pct}%)`).join('<br>');
  document.getElementById('resultadoDesglose').innerHTML = rows;
});

// ============================================================================
// FUNCIÓN: Abrir Auditoría desde Modal Retido
// ============================================================================
function abrirAuditoriaDesdeModal() {
  try {
    // 1. Obtener la tabla visible en el modal
    const weightedTitles = new Set([
      typeof I18N !== 'undefined' ? I18N.t('sim.retido_tabla1_titulo') : '',
      'Weighted granulometry two aggregates',
      'Granulometría ponderada dos agregados',
      'Granulometria ponderata due aggregati',
      'Granulometria ponderada dois agregados',
      'Granulometria ważona dwa agregaty'
    ].filter(Boolean).map(text => text.trim()));

    let tituloWeighted = Array.from(document.querySelectorAll('.mini-title'))
      .find(el => weightedTitles.has((el.textContent || '').trim()));

    if (!tituloWeighted) {
      tituloWeighted = document.querySelector('.mini-card .mini-title');
    }
    
    if (!tituloWeighted) {
      alert('No se encontró la tabla de granulometría ponderada. Asegúrate de haber calculado los retenidos primero.');
      return;
    }
    
    const tablaWeighted = tituloWeighted.closest('.mini-card').querySelector('table');
    const filas = Array.from(tablaWeighted.querySelectorAll('tbody tr'));
    
    if (filas.length === 0) {
      alert('La tabla está vacía. Calcula los valores primero.');
      return;
    }
    
    // 2. Extraer tamices y pasantes (YA SON PASANTES, NO RETENIDOS)
    const tamices = [];
    const pasante_real = [];
    
    filas.forEach((fila, idx) => {
      const celdas = fila.querySelectorAll('td');
      console.log(`Fila ${idx}: ${celdas.length} celdas`);
      if (celdas.length >= 2) {
        const tVal = parseFloat(celdas[0].textContent.trim());
        const pVal = parseFloat(celdas[1].textContent.trim());
        console.log(`  Tamiz=${tVal}, Pasante=${pVal}`);
        tamices.push(tVal);
        pasante_real.push(pVal); // Ya es pasante acumulado
      }
    });
    
    if (tamices.length === 0) {
      alert('No se pudieron extraer los datos de la tabla.');
      return;
    }
    
    // 3. Definir bandas por defecto (valores estándar para agregados finos)
    // NOTA: Deben tener la MISMA longitud que tamices y pasante_real
    const banda_min = [100, 95, 85, 70, 50, 35, 15, 5].slice(0, tamices.length);
    const banda_max = [100, 100, 100, 90, 75, 60, 30, 15].slice(0, tamices.length);
    
    // 4. Preparar datos para el endpoint
    // VALIDACIÓN DEFENSIVA: Asegurar que TODOS tienen la misma longitud
    const longitud_maxima = Math.max(tamices.length, pasante_real.length, banda_min.length, banda_max.length);
    
    // Si faltan elementos, rellenarlos
    while (tamices.length < longitud_maxima) tamices.push(0);
    while (pasante_real.length < longitud_maxima) pasante_real.push(0);
    while (banda_min.length < longitud_maxima) banda_min.push(0);
    while (banda_max.length < longitud_maxima) banda_max.push(100);
    
    // Truncar si alguno tiene más
    const datos = {
      pasante_real: pasante_real.slice(0, longitud_maxima),
      banda_min: banda_min.slice(0, longitud_maxima),
      banda_max: banda_max.slice(0, longitud_maxima),
      tamices: tamices.slice(0, longitud_maxima)
    };
    
    console.log('✓ Validación defensiva completada');
    console.log(`  - Longitud final: ${longitud_maxima} elementos en cada array`);
    
    // 🛡️ NUEVA: Advertencia sobre contexto de origen
    console.warn('⚠️ ADVERTENCIA: Enviando desde Modal (SIN materiales)');
    console.warn('   - Backend NO generará orden_operativa_real');
    console.warn('   - Estructura esperada: {pasante_real, banda_min, banda_max, tamices}');
    console.log('[DEBUG] Enviando datos a auditoría:', datos);
    
    // 5. Guardar datos en sessionStorage y sessionStorage para que auditoria.html los use
    sessionStorage.setItem('datosAuditoriaRecientes', JSON.stringify({
      entrada: datos
    }));
    console.log('💾 Datos guardados en sessionStorage para auditoría');
    
    // 6. Abrir nueva ventana con la auditoría
    console.log('🔓 Abriendo ventana de auditoría...');
    const ventana = window.open('/calculoPorRetenidos/auditoria', 'auditoria');
    
    if (!ventana) {
      alert('⚠️ No se pudo abrir la ventana de auditoría. Verifica si los popups están bloqueados.');
    } else {
      console.log('✅ Ventana de auditoría abierta correctamente');
    }
    
  } catch (e) {
    alert('❌ Error: ' + e.message);
    console.error('Error en abrirAuditoriaDesdeModal:', e);
  }
}













