// Cerrar modales
function cerrarModalAgregarMateriaForma() {
  document.getElementById('modal-agregar-materia-forma').style.display = 'none';
}
function cerrarModalModificarMateriaForma() {
  document.getElementById('modal-modificar-materia-forma').style.display = 'none';
}

// Abrir modal Agregar
document.getElementById("btn-abrir-modal-materia-forma").addEventListener("click", () => {
 
  document.getElementById('modal-agregar-materia-forma').style.display = "block";
});

// Abrir modal Modificar
document.addEventListener("click", e => {
  if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-materia-forma")) {
    const btn = e.target;
    // Poblar campos
    document.getElementById("mod-id").value          = btn.dataset.id;
    document.getElementById("mod-origen").value      = btn.dataset.origen;
    document.getElementById("mod-forma").value       = btn.dataset.forma;
    document.getElementById("mod-descripcion").value = btn.dataset.descripcion;
    document.getElementById("mod-estado").checked    = btn.dataset.estado === "true";

    // Guardar fila original para actualizar después
    document.getElementById("form-modificar-materia-forma")
            .dataset.filaId = btn.closest("tr").dataset.filaId;

    document.getElementById('modal-modificar-materia-forma').style.display = "block";
  }
});

// Submit Modificar
document.getElementById("form-modificar-materia-forma").addEventListener("submit", async function(e) {
  e.preventDefault();
  const form = this;
  const data = {
    id:          document.getElementById("mod-id").value,
    origen:      document.getElementById("mod-origen").value,
    forma:       document.getElementById("mod-forma").value,
    descripcion: document.getElementById("mod-descripcion").value,
    estado:      document.getElementById("mod-estado").checked
  };
  const filaId = form.dataset.filaId;

  try {
    const res = await fetch(`/mixFamiliari_crud_materia_forma_pantalla_modificar/${data.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Materia/Forma modificada correctamente.");

      const fila = document.querySelector(`tr[data-fila-id="${filaId}"]`);
      if (fila) {
        fila.innerHTML = `
          <td>${data.id}</td>
          <td>${data.origen}</td>
          <td>${data.forma || '-'}</td>
          <td>${data.descripcion || '-'}</td>
          <td>
            ${data.estado
              ? '<span class="badge bg-success">Activo</span>'
              : '<span class="badge bg-secondary">Inactivo</span>'
            }
          </td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button"
                      class="btn btn-warning btn-sm btn-abrir-modal-modificar-materia-forma"
                      data-id="${data.id}"
                      data-origen="${data.origen}"
                      data-forma="${data.forma}"
                      data-descripcion="${data.descripcion}"
                      data-estado="${data.estado}">
                Modificar
              </button>
              <button type="button"
                      class="btn btn-danger btn-sm btn-abrir-modal-eliminar-materia-forma"
                      data-id="${data.id}">
                Eliminar
              </button>
            </div>
          </td>
        `;
      }
      cerrarModalModificarMateriaForma();
    } else {
      alert("⚠️ Error: " + (respuesta.error || "No se pudo modificar la materia/forma."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Error en la solicitud: " + err.message);
  }
});

// DOMContentLoaded: agregar y eliminar
document.addEventListener('DOMContentLoaded', () => {
  // Agregar
  document.getElementById('form-agregar-materia-forma').addEventListener('submit', async function(e) {
    e.preventDefault();
    const data = {
      origen:      document.getElementById('add-origen').value,
      forma:       document.getElementById('add-forma').value,
      descripcion: document.getElementById('add-descripcion').value,
      estado:      document.getElementById('add-estado').checked
    };

    try {
      const res = await fetch('/mixFamiliari_crud_materia_forma_pantalla_agregar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const respuesta = await res.json();

      if (res.ok && respuesta.success && respuesta.tipo) {
        const t = respuesta.tipo;
        const tr = document.createElement('tr');
        tr.setAttribute('data-fila-id', t.id);
        tr.innerHTML = `
          <td>${t.id}</td>
          <td>${t.origen}</td>
          <td>${t.forma || '-'}</td>
          <td>${t.descripcion || '-'}</td>
          <td>
            ${t.estado
              ? '<span class="badge bg-success">Activo</span>'
              : '<span class="badge bg-secondary">Inactivo</span>'
            }
          </td>
          <td>
            <div class="d-flex align-items-center gap-2">
              <button type="button"
                      class="btn btn-warning btn-sm btn-abrir-modal-modificar-materia-forma"
                      data-id="${t.id}"
                      data-origen="${t.origen}"
                      data-forma="${t.forma}"
                      data-descripcion="${t.descripcion}"
                      data-estado="${t.estado}">
                Modificar
              </button>
              <button type="button"
                      class="btn btn-danger btn-sm btn-abrir-modal-eliminar-materia-forma"
                      data-id="${t.id}">
                Eliminar
              </button>
            </div>
          </td>
        `;
        document.getElementById('tabla-materia-forma').appendChild(tr);
        this.reset();
        cerrarModalAgregarMateriaForma();
      } else {
        alert('❌ Error al agregar materia/forma.');
      }
    } catch (err) {
      console.error(err);
      alert('💥 Error al enviar solicitud: ' + err.message);
    }
  });

  // Eliminar
  document.addEventListener("click", async e => {
    if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-materia-forma")) {
      const id = e.target.dataset.id;
      if (confirm("¿Seguro que querés eliminar esta materia/forma?")) {
        try {
          const res = await fetch(`/mixFamiliari_crud_materia_forma_pantalla_eliminar/${id}`, {
            method: "DELETE"
          });
          const data = await res.json();
          if (res.ok && data.success) {
            const fila = document.querySelector(`tr[data-fila-id="${id}"]`);
            if (fila) fila.remove();
          } else {
            alert("❌ No se pudo eliminar la materia/forma.");
          }
        } catch (err) {
          console.error(err);
          alert("💥 Error al eliminar: " + err.message);
        }
      }
    }
  });
});
