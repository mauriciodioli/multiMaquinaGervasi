
function formatDuration(sec) {
  if (!sec) return '-';
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
}



(function () {

  const btnOpen = document.getElementById('btn-cargar-produccion');
  const modalEl = document.getElementById('modal-laser-produccion');

  const btnRun  = document.getElementById('btn-esegui-produzione');
  const status  = document.getElementById('laser-prod-status');

  if (!btnOpen || !modalEl) {
    console.error('[LASER MODAL] elementos no encontrados');
    return;
  }

  function openModal() {
    modalEl.classList.remove('hidden');
    modalEl.classList.add('is-open');
    modalEl.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    modalEl.classList.add('hidden');
    modalEl.classList.remove('is-open');
    modalEl.setAttribute('aria-hidden', 'true');
  }

  // ===== ABRIR MODAL =====
  btnOpen.addEventListener('click', () => {
    openModal();

    // preload cardId desde botón
    const cardId = btnOpen.dataset.cardId;
    const inputCard = document.getElementById('laser-card-id');
    if (inputCard && cardId) inputCard.value = cardId;
  });

  // ===== CERRAR (botones + overlay) =====
  modalEl.addEventListener('click', (e) => {
    if (e.target?.dataset?.close !== undefined ||
        e.target.classList.contains('dpia-modal-overlay')) {
      closeModal();
    }
  });

  // ===== CERRAR CON ESC =====
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalEl.classList.contains('is-open')) {
      closeModal();
    }
  });

// ===== ACCIÓN PRINCIPAL =====
if (btnRun) {
  btnRun.addEventListener('click', async () => {

    const cardId = document.getElementById('laser-card-id')?.value.trim();
    const start  = document.getElementById('laser-start-time')?.value;
    const end    = document.getElementById('laser-end-time')?.value;

    if (!start || !end) {
      status.textContent = '❌ Start Time e End Time sono obbligatori';
      return;
    }

    status.textContent = 'Esecuzione in corso…';

    try {
      const resp = await fetch('/laser/tasks/completed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cardId: cardId || null,
          startTime: start,
          endTime: end
        })
      });

      const data = await resp.json();

      if (!resp.ok || !data.ok) {
        status.textContent = '❌ Errore API: ' + (data.error || resp.status);
        return;
      }

      status.textContent = `✅ OK — ${data.count} tasks trovati`;

      renderLaserTable(data.tasks);

    } catch (e) {
      console.error(e);
      status.textContent = '❌ Errore di connessione';
    }
  });
}


})();




// ===============================
// RENDER TABELLA PRODUZIONE
// ===============================
function renderLaserTable(tasks) {
  const tbody = document.querySelector('#laser-prod-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';

  if (!tasks || !tasks.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; opacity:.6">
          Nessun risultato
        </td>
      </tr>
    `;
    return;
  }

  for (const t of tasks) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${t.job_name || '-'}</td>
      <td>${t.material || '-'}</td>
      <td>${t.thickness_mm ?? '-'}</td>
      <td>${t.pieces ?? '-'}</td>
      <td>${t.cut_length_mm ?? '-'}</td>
      <td>${t.speed_mm_s ?? '-'}</td>
      <td>${formatDuration(t.duration_sec)}</td>
    `;
    tbody.appendChild(tr);
  }
}
