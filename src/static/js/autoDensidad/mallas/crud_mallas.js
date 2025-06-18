document.getElementById("btn-abrir-modal-malla").addEventListener("click", function () {
  document.getElementById('modal-agregar-malla').style.display = "block";
});


document.querySelectorAll(".btn-abrir-modal-modificar-malla").forEach(boton => {
  boton.addEventListener("click", function () {

    const user_id = this.getAttribute("data-id");
 
  });
});


function cerrarModalAgregarMallas() {
  document.getElementById('modal-agregar-malla').style.display = 'none';
}
function cerrarModalModificarMallas() {
  document.getElementById('modal-modificar-malla').style.display = 'none';
}








document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-malla")) {
    const btn = e.target;

    // Precargar los datos en el modal
    document.getElementById("mod-id").value = btn.dataset.id;
    document.getElementById("mod-nombre_comercial").value = btn.dataset.nombre_comercial;
    document.getElementById("mod-diametro_mm").value = btn.dataset.diametro_mm;

    // Guardar la fila original para actualizarla después
    document.getElementById("form-modificar-malla").dataset.filaOrigen = btn.closest("tr").dataset.filaId;

    // Mostrar modal
    document.getElementById("modal-modificar-malla").style.display = "block";
  }
});
document.getElementById("form-modificar-malla").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);
  const filaId = this.dataset.filaOrigen;

  try {
    const res = await fetch(`/mixFamiliari_crud_mallas_pantalla_mallas_modificar/${data.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Malla modificada correctamente.");
      document.getElementById("modal-modificar-malla").style.display = "none";

      const fila = document.querySelector(`tr[data-fila-id="${filaId}"]`);
      if (fila) {
        fila.innerHTML = `
          <td>${data.id}</td>
          <td>${data.nombre_comercial}</td>
          <td>${data.diametro_mm}</td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-malla"
                data-id="${data.id}"
                data-nombre_comercial="${data.nombre_comercial}"
                data-diametro_mm="${data.diametro_mm}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-malla"
                data-id="${data.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;
      }

    } else {
      alert("⚠️ Error: " + (respuesta.message || "No se pudo modificar la malla."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Error en la solicitud: " + err.message);
  }
});
















document.addEventListener('DOMContentLoaded', () => {
  // Agregar Malla
  document.getElementById('form-agregar-malla').addEventListener('submit', function (e) {
    e.preventDefault();

    const data = {
      nombre_comercial: document.getElementById('nombre_comercial').value,
      diametro_mm: parseFloat(document.getElementById('diametro_mm').value)
    };

    fetch('/mixFamiliari_crud_mallas_pantalla_mallas_agregar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
      if (data.success && data.malla) {
        const tbody = document.getElementById('tabla-mallas');
        const m = data.malla;

        const tr = document.createElement('tr');
        tr.setAttribute('data-fila-id', m.id);
        tr.innerHTML = `
          <td>${m.id}</td>
          <td>${m.nombre_comercial}</td>
          <td>${m.diametro_mm}</td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-malla"
                data-id="${m.id}"
                data-nombre_comercial="${m.nombre_comercial}"
                data-diametro_mm="${m.diametro_mm}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-malla"
                data-id="${m.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;

        tbody.appendChild(tr);
        document.getElementById('form-agregar-malla').reset();
        document.getElementById('modal-agregar-malla').style.display = 'none';
      } else {
        alert('Error al agregar malla.');
      }
    });
  });

  // Delegación: Abrir modal de modificar
  document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-malla")) {
      const btn = e.target;
      document.getElementById('mod-id').value = btn.dataset.id;
      document.getElementById('mod-nombre_comercial').value = btn.dataset.nombre_comercial;
      document.getElementById('mod-diametro_mm').value = btn.dataset.diametro_mm;
      document.getElementById("form-modificar-malla").dataset.filaOrigen = btn.closest("tr").dataset.filaId;
      document.getElementById('modal-modificar-malla').style.display = "block";
    }
  });

  // Delegación: Eliminar fila
  document.addEventListener("click", async function (e) {
    if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-malla")) {
      const id = e.target.dataset.id;

      if (confirm("¿Seguro que querés eliminar esta malla?")) {
        try {
          const res = await fetch(`/mixFamiliari_crud_mallas_pantalla_mallas_eliminar/${id}`, {
            method: "DELETE"
          });
          const data = await res.json();
          if (res.ok && data.success) {
            const fila = document.querySelector(`tr[data-fila-id="${id}"]`);
            if (fila) fila.remove();
          } else {
            alert("❌ No se pudo eliminar la malla.");
          }
        } catch (err) {
          console.error(err);
          alert("💥 Error al eliminar: " + err.message);
        }
      }
    }
  });
});





