/**
 * dashboard_effects.js
 * Capa de efectos visuales sci-fi para el dashboard de inversores.
 *
 * TOGGLE RÁPIDO: cambiar EFFECTS_ENABLED = false para desactivar todo.
 * No modifica datos, endpoints ni lógica de polling existente.
 * Solo lee las tarjetas .pv-card que renderiza solo_pannelli.js
 * y agrega/quita clases CSS de efectos.
 */

/* ============================================================
   CONFIGURACIÓN
   ============================================================ */
const GALAXY_MODE        = true;   // false → desactiva tema galaxia/sci-fi
const EFFECTS_ENABLED    = GALAXY_MODE;
const ENERGY_THRESHOLD_W   = 500;    // W mínimos para la línea de energía animada
const TOP_POWER_THRESHOLD_W = 2800;  // W: toda tarjeta por encima recibe badge TOP POWER
const FADE_IN_ONCE       = true;   // true = fade-in sólo en la primera carga

/* Clases de estado visual → clase de glow */
const GLOW_MAP = {
  // status_text / status strings que mapean a cada glow
  ok:       'card-glow-ok',
  mppt:     'card-glow-mppt',    // Fronius MPPT
  throttled:'card-glow-mppt',    // throttled también va cyan
  operando: 'card-glow-ok',
  running:  'card-glow-ok',
  online:   'card-glow-ok',
  standby:  'card-glow-standby',
  sleeping: 'card-glow-standby',
  idle:     'card-glow-standby',
  error:    'card-glow-error',
  fault:    'card-glow-error',
  falla:    'card-glow-error',
  fail:     'card-glow-error',
  offline:  'card-glow-offline',
  'no conect': 'card-glow-offline',
};

/* Todos los nombres de clases glow (para hacer remove antes de add) */
const ALL_GLOW_CLASSES = [
  'card-glow-ok', 'card-glow-mppt', 'card-glow-rpc',
  'card-glow-error', 'card-glow-standby', 'card-glow-offline',
];

/* ============================================================
   UTILIDADES
   ============================================================ */

/** Deriva la clase glow a partir del objeto inversor */
function glowClassFor(inv) {
  const manufacturer = (inv.manufacturer || '').toLowerCase();
  const statusText   = (inv.status_text   || inv.status || '').toLowerCase();
  const deviceStatus = (inv.device_status || '').toLowerCase();

  // Danfoss DLX → violeta RPC
  if (manufacturer.includes('danfoss') || manufacturer.includes('dlx')) {
    if (!/error|fault|fail|offline/.test(statusText)) return 'card-glow-rpc';
  }

  // Fronius MPPT → cyan
  if (statusText.includes('mppt') || statusText.includes('throttled') || statusText.includes('limitado')) {
    return 'card-glow-mppt';
  }

  // Offline / sin conexión
  if (
    statusText.includes('offline') ||
    statusText.includes('no conect') ||
    /refused|timeout|timed out|dns|modbus/.test(statusText)
  ) return 'card-glow-offline';

  // Error
  if (/error|fault|falla|fail|failure|alarm/.test(statusText) ||
      /error|fault|falla|fail/.test(deviceStatus)) {
    return 'card-glow-error';
  }

  // Standby
  if (/standby|sleeping|idle/.test(statusText)) return 'card-glow-standby';

  // OK / operando
  if (/ok|operando|running|online|mppt/.test(statusText) ||
      deviceStatus === 'ok') {
    return 'card-glow-ok';
  }

  return null;   // sin clase → quitar todos los glows
}

/** Aplica/quita clases glow en una tarjeta dada un objeto inversor */
function applyGlowToCard(cardEl, inv) {
  if (!cardEl || !EFFECTS_ENABLED) return;
  const cls = glowClassFor(inv);
  ALL_GLOW_CLASSES.forEach(c => cardEl.classList.remove(c));
  if (cls) cardEl.classList.add(cls);
}

/** Quita o añade la clase de línea de energía */
function applyEnergyLine(cardEl, powerW) {
  if (!cardEl || !EFFECTS_ENABLED) return;
  const active = typeof powerW === 'number' && isFinite(powerW) && powerW >= ENERGY_THRESHOLD_W;
  cardEl.classList.toggle('card-energy-active', active);
}

/** Añade clase card-top-power + badge a una tarjeta */
function _markTopCard(cardEl) {
  cardEl.classList.add('card-top-power');
  // Evitar badge duplicado
  if (!cardEl.querySelector('.badge-top-power')) {
    const badge = cardEl.querySelector('.badge');
    if (badge) {
      const topBadge = document.createElement('span');
      topBadge.className = 'badge-top-power';
      topBadge.textContent = 'TOP POWER';
      badge.insertAdjacentElement('afterend', topBadge);
    }
  }
}

/** Determina si un objeto inversor está en modo MPPT */
function _isMppt(inv) {
  const txt = (inv.status_text || inv.status || '').toLowerCase();
  return /mppt|throttled|limitado|operando/.test(txt);
}

/** Marca la tarjeta con máxima potencia y todas las MPPT con el badge dorado */
function applyTopPower(cards, inverters) {
  if (!EFFECTS_ENABLED) return;

  // Quitar de todas primero
  cards.forEach(c => {
    c.classList.remove('card-top-power');
    c.querySelector('.badge-top-power')?.remove();
  });

  if (!inverters || inverters.length === 0) return;

  // Filtrar inversores con potencia válida
  const withPower = inverters.filter(i =>
    typeof i.power_W === 'number' && isFinite(i.power_W) && i.power_W > 0
  );
  if (withPower.length === 0) return;

  // Mapa IP → tarjeta
  const cardByIp = {};
  [...cards].forEach(c => {
    const ipEl = c.querySelector('.pv-card-head > div:first-child');
    if (ipEl) cardByIp[ipEl.textContent.trim()] = c;
  });

  // Solo el umbral de potencia otorga el badge TOP POWER
  withPower.forEach(i => {
    if (i.power_W >= TOP_POWER_THRESHOLD_W && i.ip && cardByIp[i.ip]) {
      _markTopCard(cardByIp[i.ip]);
    }
  });
}

/** Aplica borde rojo al KPI de voltaje si el voltaje es inválido
 *  (= "—" o 0) mientras la potencia es > 0 */
function applyVoltWarning(cardEl, inv) {
  if (!cardEl || !EFFECTS_ENABLED) return;
  const voltKpi = cardEl.querySelectorAll('.pv-kpi')[1]; // segundo KPI = Volt
  if (!voltKpi) return;
  const voltInvalid =
    (!inv.voltage_V || inv.voltage_V === 0) &&
    typeof inv.power_W === 'number' && inv.power_W > 0;
  voltKpi.classList.toggle('volt-invalid', voltInvalid);
}

/** Aplica fade-in escalonado en la primera carga */
let _firstRender = true;
function applyFadeIn(cardEl, index) {
  if (!EFFECTS_ENABLED) return;
  if (FADE_IN_ONCE && !_firstRender) return;
  cardEl.style.setProperty('--card-index', index);
  cardEl.classList.add('card-animated');
  // Quitar la clase tras la animación para que el rerender no la reanime
  cardEl.addEventListener('animationend', () => {
    cardEl.classList.remove('card-animated');
    cardEl.style.removeProperty('--card-index');
  }, { once: true });
}


/* ============================================================
   PUNTO DE ENTRADA PRINCIPAL
   Llamar después de que solo_pannelli.js termine de renderizar.
   ============================================================ */

/**
 * applyEffects(inverters)
 * @param {Array} inverters  — el array data.inverters del JSON de la API
 *
 * Busca todas las .pv-card en #sp-cards y aplica los efectos
 * en el mismo orden en que fueron renderizadas.
 */
function applyEffects(inverters) {
  if (!EFFECTS_ENABLED) return;

  const container = document.getElementById('sp-cards');
  if (!container) return;

  const cards = container.querySelectorAll('.pv-card');
  if (cards.length === 0) return;

  // Construir mapa IP → inversor para lookup rápido
  const invByIp = {};
  (inverters || []).forEach(i => { if (i.ip) invByIp[i.ip] = i; });

  cards.forEach((card, idx) => {
    // Obtener IP de la primera columna del head
    const ipEl = card.querySelector('.pv-card-head > div:first-child');
    const ip   = ipEl ? ipEl.textContent.trim() : null;
    const inv  = (ip && invByIp[ip]) ? invByIp[ip] : null;

    if (inv) {
      applyGlowToCard(card, inv);
      applyEnergyLine(card, inv.power_W);
      applyVoltWarning(card, inv);
    } else {
      // Tarjeta sin datos conocidos → offline
      ALL_GLOW_CLASSES.forEach(c => card.classList.remove(c));
      card.classList.add('card-glow-offline');
    }

    applyFadeIn(card, idx);
  });

  // TOP POWER (requiere ver todas las tarjetas)
  applyTopPower(cards, inverters);

  // Primera carga procesada
  _firstRender = false;
}


/* ============================================================
   HOOK EN solo_pannelli.js (no-invasivo)
   Esperamos a que el DOM exista e interceptamos renderCards
   sin modificar el archivo original.
   ============================================================ */
(function hookRenderCards() {
  // Si EFFECTS_ENABLED=false, no instalamos nada
  if (!EFFECTS_ENABLED) return;

  // Espera a que SoloPannelliRunner esté disponible (se define en solo_pannelli.js)
  const POLL_INTERVAL = 200;
  let attempts = 0;

  function tryHook() {
    attempts++;
    if (attempts > 50) return; // 10s máximo

    // Activar fondo galaxy en <body> si existe .pannelli-dash
    if (GALAXY_MODE && document.querySelector('.pannelli-dash')) {
      document.body.classList.add('galaxy-page');
    }

    // Verificamos que el runner esté listo buscando el contenedor sp-cards
    // El hook real: sobreescribimos window.renderCards si fue expuesta,
    // o usamos MutationObserver como alternativa robusta.

    const container = document.getElementById('sp-cards');
    if (!container) {
      // El botón "Cards" aún no fue presionado, instalar observer en body
      installMutationObserver();
      return;
    }
    installMutationObserver();
  }

  function installMutationObserver() {
    // Observar mutaciones en #sp-cards (se re-renderiza en cada poll)
    // Cuando detecta hijos nuevos, llama applyEffects con los últimos datos
    const observer = new MutationObserver(() => {
      // Leer los datos del último render desde el snapshot global de solo_pannelli.js
      // (prevSnapshot.inv contiene IP → {power_W, voltage_V, frequency_Hz})
      // Para el glow necesitamos status, que no está en prevSnapshot.
      // Alternativa: leer desde los propios elementos DOM.
      applyEffectsFromDOM();
    });

    function startObserver() {
      const cards = document.getElementById('sp-cards');
      if (cards) {
        observer.observe(cards, { childList: true });
      } else {
        // sp-cards todavía no existe: observar body para detectar cuándo aparece
        const bodyObs = new MutationObserver((_, obs) => {
          const c = document.getElementById('sp-cards');
          if (c) {
            obs.disconnect();
            observer.observe(c, { childList: true });
          }
        });
        bodyObs.observe(document.body, { childList: true, subtree: true });
      }
    }
    startObserver();
  }

  /**
   * Lee información de efectos directamente desde el DOM ya renderizado.
   * No necesita acceso al objeto inversor original.
   */
  function applyEffectsFromDOM() {
    const container = document.getElementById('sp-cards');
    if (!container) return;
    const cards = container.querySelectorAll('.pv-card');

    cards.forEach((card, idx) => {
      // Leer badge text para determinar estado
      const badge = card.querySelector('.badge');
      const badgeTxt = (badge ? badge.textContent : '').toLowerCase().trim();

      // Leer texto del fabricante desde meta
      const meta = card.querySelector('.pv-card-meta');
      const metaTxt = (meta ? meta.textContent : '').toLowerCase();

      // Construir objeto inv mínimo desde DOM
      const inv = {
        manufacturer: metaTxt,
        status_text:  badgeTxt,
        device_status: '',
        power_W: null,
        voltage_V: null,
      };

      // Leer potencia (primer .num en primer .pv-kpi)
      // Nota: los números usan formato es-AR donde el punto es separador
      // de miles (ej. "2.940" = 2940 W). Hay que quitar los puntos antes
      // de parsear, y sustituir la coma decimal por punto.
      const kpis = card.querySelectorAll('.pv-kpi');
      if (kpis[0]) {
        const numEl = kpis[0].querySelector('.num');
        if (numEl) {
          const raw = numEl.textContent
            .replace(/[^0-9,.]/g, '')   // quitar todo salvo dígitos, punto y coma
            .replace(/\./g, '')         // eliminar puntos (miles en es-AR)
            .replace(',', '.');         // coma decimal → punto
          const pw  = parseFloat(raw);
          if (!isNaN(pw)) inv.power_W = pw;
        }
      }
      // Leer voltaje
      if (kpis[1]) {
        const numEl = kpis[1].querySelector('.num');
        if (numEl) {
          const raw = numEl.textContent
            .replace(/[^0-9,.]/g, '')
            .replace(/\./g, '')
            .replace(',', '.');
          const vv  = parseFloat(raw);
          if (!isNaN(vv)) inv.voltage_V = vv;
        }
      }

      // IP
      const ipEl = card.querySelector('.pv-card-head > div:first-child');
      inv.ip = ipEl ? ipEl.textContent.trim() : '';

      // Aplicar efectos
      applyGlowToCard(card, inv);
      applyEnergyLine(card, inv.power_W);
      applyVoltWarning(card, inv);
      applyFadeIn(card, idx);

    });

    // Quitar badge previo de top power
    cards.forEach(c => {
      c.classList.remove('card-top-power');
      c.querySelector('.badge-top-power')?.remove();
    });

    // Solo el umbral de potencia otorga el badge TOP POWER
    cards.forEach(c => {
      const numEl = c.querySelector('.pv-kpi:first-child .num');
      if (!numEl) return;
      const raw = numEl.textContent
        .replace(/[^0-9,.]/g, '')
        .replace(/\.(?=.*\.)/g, '')  // quitar puntos de miles (conservar último si es decimal)
        .replace(/\./g, '')          // quitar el punto de miles restante
        .replace(',', '.');
      const pw  = parseFloat(raw);
      if (!isNaN(pw) && pw >= TOP_POWER_THRESHOLD_W) {
        _markTopCard(c);
      }
    });

    _firstRender = false;
  }

  // Arrancar hook
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tryHook);
  } else {
    tryHook();
  }
})();
