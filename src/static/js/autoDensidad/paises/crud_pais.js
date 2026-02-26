document.getElementById("btn-abrir-modal-pais").addEventListener("click", function () {
  document.getElementById('modal-agregar-pais').style.display = "block";
});


document.getElementById("form-agregar-pais").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);

  try {
    const res = await fetch("/administracion_crud_pais_crear_pais/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Paese aggiunto correttamente.");
      this.reset();
      document.getElementById('modal-agregar-pais').style.display = "none";

      const nuevaFila = document.createElement("tr");
      nuevaFila.setAttribute("data-fila-id", respuesta.pais.id);
      nuevaFila.innerHTML = `
        <td data-label="ID">${respuesta.pais.id}</td>
        <td data-label="Nome">${respuesta.pais.nombre}</td>
        <td data-label="Codice">${respuesta.pais.codigo}</td>
        <td data-label="Descrizione">${respuesta.pais.descripcion || ''}</td>
        <td data-label="Stato">${respuesta.pais.estado}</td>
        <td data-label="Azioni">
          <div class="d-flex align-items-center gap-2">
            <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-pais"
              data-pais-id="${respuesta.pais.id}"
              data-nombre="${respuesta.pais.nombre}"
              data-codigo="${respuesta.pais.codigo}"
              data-descripcion="${respuesta.pais.descripcion || ''}"
              data-estado="${respuesta.pais.estado}">
              Modificare
            </button>
            <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-pais"
              data-pais-id="${respuesta.pais.id}">
              Eliminare
            </button>
          </div>
        </td>
      `;

      document.getElementById("tabla-paises").appendChild(nuevaFila);
    } else {
      alert("⚠️ Errore: " + (respuesta.message || "Non è stato possibile aggiungere il paese."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Errore nella richiesta: " + err.message);
  }
});


document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-pais")) {
    const paisId = e.target.dataset.paisId;
    if (confirm(`Sei sicuro di voler eliminare il paese ID ${paisId}?`)) {
      eliminarPais(paisId, e.target);
    }
  }
});

function eliminarPais(id, boton) {
  fetch(`/administracion_crud_pais_eliminar_pais/${id}`, {
    method: "DELETE"
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        alert("✅ Eliminato correttamente.");
        const fila = boton.closest("tr");
        if (fila) fila.remove();
      } else {
        alert("⚠️ Errore nell'eliminazione: " + (data.message || "sconosciuto"));
      }
    })
    .catch(err => {
      alert("💥 Errore di connessione: " + err.message);
    });
}


document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-pais")) {
    const btn = e.target;

    document.getElementById("mod-id").value = btn.dataset.paisId;
    document.getElementById("mod-nombre").value = btn.dataset.nombre;
    document.getElementById("mod-codigo").value = btn.dataset.codigo;
    document.getElementById("mod-descripcion").value = btn.dataset.descripcion;
    document.getElementById("mod-estado").value = btn.dataset.estado;

    document.getElementById("form-modificar-pais").dataset.filaOrigen = btn.closest("tr").dataset.filaId;
    document.getElementById('modal-modificar-pais').style.display = "block";
  }
});


document.getElementById("form-modificar-pais").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);
  const filaId = this.dataset.filaOrigen;

  try {
    const res = await fetch("/administracion_crud_pais_modifica_pais/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Paese modificato correttamente.");
      document.getElementById('modal-modificar-pais').style.display = "none";

      const fila = document.querySelector(`tr[data-fila-id="${filaId}"]`);
      if (fila) {
        fila.innerHTML = `
          <td data-label="ID">${respuesta.pais.id}</td>
          <td data-label="Nome">${respuesta.pais.nombre}</td>
          <td data-label="Codice">${respuesta.pais.codigo}</td>
          <td data-label="Descrizione">${respuesta.pais.descripcion || ''}</td>
          <td data-label="Stato">${respuesta.pais.estado}</td>
          <td data-label="Azioni">
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-pais"
                data-pais-id="${respuesta.pais.id}"
                data-nombre="${respuesta.pais.nombre}"
                data-codigo="${respuesta.pais.codigo}"
                data-descripcion="${respuesta.pais.descripcion || ''}"
                data-estado="${respuesta.pais.estado}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-pais"
                data-pais-id="${respuesta.pais.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;
      }
    } else {
      alert("⚠️ Errore: " + (respuesta.message || "Non è stato possibile modificare il paese."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Errore nella richiesta: " + err.message);
  }
});
