function cerrarModalAgregarTipoMezcla() {
  document.getElementById('modal-agregar-tipo-mezcla').style.display = 'none';
}
function cerrarModalModificarTipoMezcla() {
  document.getElementById('modal-modificar-tipo-mezcla').style.display = 'none';
}


document.getElementById("btn-abrir-modal-tipo-mezcla").addEventListener("click", function () {
  document.getElementById('modal-agregar-tipo-mezcla').style.display = "block";
});

document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-tipo-mezcla")) {
    const btn = e.target;

    document.getElementById("mod-id").value = btn.dataset.id;
    document.getElementById("mod-nombre").value = btn.dataset.nombre;
    document.getElementById("mod-descripcion").value = btn.dataset.descripcion;

    document.getElementById("form-modificar-tipo-mezcla").dataset.filaOrigen = btn.closest("tr").dataset.filaId;

    document.getElementById('modal-modificar-tipo-mezcla').style.display = "block";
  }
});

document.getElementById("form-modificar-tipo-mezcla").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);
  const filaId = this.dataset.filaOrigen;

  try {
    const res = await fetch(`/mixFamiliari_crud_tipo_mezcla_pantalla_modificar/${data.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Tipo de mezcla modificado correctamente.");

      const fila = document.querySelector(`tr[data-fila-id="${filaId}"]`);
      if (fila) {
        fila.innerHTML = `
          <td>${data.id}</td>
          <td>${data.nombre}</td>
          <td>${data.descripcion}</td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-tipo-mezcla"
                data-id="${data.id}"
                data-nombre="${data.nombre}"
                data-descripcion="${data.descripcion}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-tipo-mezcla"
                data-id="${data.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;
      }

      document.getElementById('modal-modificar-tipo-mezcla').style.display = "none";

    } else {
      alert("⚠️ Error: " + (respuesta.error || "No se pudo modificar el tipo de mezcla."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Error en la solicitud: " + err.message);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('form-agregar-tipo-mezcla').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
      nombre: document.getElementById('nombre').value,
      descripcion: document.getElementById('descripcion').value
    };

    try {
      const res = await fetch('/mixFamiliari_crud_tipo_mezcla_pantalla_agregar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const respuesta = await res.json();

      if (res.ok && respuesta.success && respuesta.tipo_mezcla) {
        const t = respuesta.tipo_mezcla;
        const tr = document.createElement('tr');
        tr.setAttribute('data-fila-id', t.id);
        tr.innerHTML = `
          <td>${t.id}</td>
          <td>${t.nombre}</td>
          <td>${t.descripcion}</td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-tipo-mezcla"
                data-id="${t.id}"
                data-nombre="${t.nombre}"
                data-descripcion="${t.descripcion}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-tipo-mezcla"
                data-id="${t.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;

        document.getElementById('tabla-tipo-mezcla').appendChild(tr);
        document.getElementById('form-agregar-tipo-mezcla').reset();
        document.getElementById('modal-agregar-tipo-mezcla').style.display = "none";
      } else {
        alert('❌ Error al agregar tipo de mezcla.');
      }
    } catch (err) {
      console.error(err);
      alert('💥 Error al enviar solicitud: ' + err.message);
    }
  });

  // Eliminar
  document.addEventListener("click", async function (e) {
    if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-tipo-mezcla")) {
      const id = e.target.dataset.id;

      if (confirm("¿Seguro que querés eliminar este tipo de mezcla?")) {
        try {
          const res = await fetch(`/mixFamiliari_crud_tipo_mezcla_pantalla_eliminar/${id}`, {
            method: "DELETE"
          });
          const data = await res.json();
          if (res.ok && data.success) {
            const fila = document.querySelector(`tr[data-fila-id="${id}"]`);
            if (fila) fila.remove();
          } else {
            alert("❌ No se pudo eliminar el tipo de mezcla.");
          }
        } catch (err) {
          console.error(err);
          alert("💥 Error al eliminar: " + err.message);
        }
      }
    }
  });
});
