document.getElementById("crud-link-mix").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        alert("Nessun utente ha effettuato l'accesso.");
        return;
    }

    // REDIRECCIÓN NORMAL CON GET
    window.location.href = `/pantalla_agregado/?user_id=${userId}`;
});



document.addEventListener("DOMContentLoaded", () => {
  const btnAbrir = document.getElementById('btn-abrir-modal-agregar');

  if (!btnAbrir) {
    console.warn('⚠️ No se encontró el botón #btn-abrir-modal-agregar');
    return;
  }

  btnAbrir.addEventListener('click', function () {
    const modal = document.getElementById('modal-agregar-mix');
    modal.classList.add('show');
    modal.style.display = 'block';
    modal.removeAttribute('aria-hidden');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('role', 'dialog');

    inicializarModulosSelect(); // 👈 Ejecutás tu lógica cuando abrís el modal
  });

  // Cierre de modales
  document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = btn.closest('.modal');
      modal.classList.remove('show');
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      modal.removeAttribute('aria-modal');
    });
  });
});


 function seleccionarIdioma(idioma) {
    document.getElementById('input-idioma').value = idioma;
    alert('Lingua selezionata: ' + idioma);  // opcional
  }