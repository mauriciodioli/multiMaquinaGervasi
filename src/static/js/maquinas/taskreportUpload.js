(function () {
  const btnOpen = document.getElementById('btn-subir-taskreport');
  const btnDo   = document.getElementById('btn-confirmar-taskreport-upload');
  const result  = document.getElementById('taskreport-upload-result');

  const inputFile  = document.getElementById('taskreport-file');
  const inputSheet = document.getElementById('taskreport-sheet');
  const selectMode = document.getElementById('taskreport-mode');

  const modalEl = document.getElementById('modalLaserTaskReportUpload');

  if (!btnOpen || !btnDo || !modalEl) return;

  const uploadUrl = btnOpen.dataset.uploadUrl;

  function openModal(){
    modalEl.classList.add('is-open');
    modalEl.setAttribute('aria-hidden', 'false');
  }
  function closeModal(){
    modalEl.classList.remove('is-open');
    modalEl.setAttribute('aria-hidden', 'true');
  }

  function setResult(html, ok = true) {
    if (!result) return;
    result.classList.remove('text-muted', 'text-danger', 'text-success');
    result.classList.add(ok ? 'text-success' : 'text-danger');
    result.innerHTML = html;
  }

  // abrir
  btnOpen.addEventListener('click', openModal);

  // cerrar por botones/backdrop
  modalEl.addEventListener('click', (e) => {
    if (e.target && e.target.dataset && e.target.dataset.close === "1") {
      closeModal();
    }
  });

  // cerrar con ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modalEl.classList.contains('is-open')) {
      closeModal();
    }
  });

  // upload
  btnDo.addEventListener('click', async () => {
    try {
      if (!uploadUrl) {
        setResult('❌ uploadUrl mancante (data-upload-url).', false);
        return;
      }

      const file = inputFile?.files?.[0];
      if (!file) {
        setResult('❌ Seleziona un file Excel.', false);
        return;
      }

      btnDo.disabled = true;
      btnDo.innerText = 'Importando...';

      const fd = new FormData();
      fd.append('file', file);
      fd.append('sheet', (inputSheet?.value || '0').trim());
      fd.append('mode', (selectMode?.value || 'upsert').trim());

      const resp = await fetch(uploadUrl, { method: 'POST', body: fd });

      const text = await resp.text();
      let data;
      try { data = JSON.parse(text); } catch { data = { status: 1, msg: text }; }

      if (!resp.ok || data.status !== 0) {
        setResult(`❌ Import fallito: ${data.msg || resp.status}`, false);
        return;
      }

      setResult(`✅ OK — inserted: <b>${data.inserted}</b>, updated: <b>${data.updated}</b>, skipped: <b>${data.skipped}</b>`, true);
      closeModal();

    } catch (e) {
      setResult(`❌ Errore: ${e}`, false);
    } finally {
      btnDo.disabled = false;
      btnDo.innerText = 'Importa';
    }
  });
})();
