function cerrarmodalAgregarComponente() {
  document.getElementById('modal-agregar-componente').style.display = 'none';
}
function cerrarmodalAgregarComponenteQuimi() {
  document.getElementById('modalAgregarComponente').style.display = 'none';
}

document.addEventListener("DOMContentLoaded", () => {
  // Toggle de sección de componentes
  const toggleComponentes = document.getElementById("toggle-componentes");
  const seccionComponentes = document.getElementById("seccion-componentes");
  if (toggleComponentes && seccionComponentes) {
    toggleComponentes.addEventListener("click", () => {
      const visible = seccionComponentes.style.display === "block";
      seccionComponentes.style.display = visible ? "none" : "block";
      toggleComponentes.innerHTML = visible ? "🔽 Mostrar" : "🔼 Ocultar";
    });
  }

  // Abrir modal para agregar componente
  document.body.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-modalAgregarComponente-agregado")) {
      document.getElementById('modalAgregarComponente').style.display = "block";
      // Limpia el form y quita modo edición
      form.reset();
      delete form.dataset.editingId;
    }
  });

  const form = document.querySelector("#modalAgregarComponente form");
  const modalElement = document.getElementById("modalAgregarComponente");
  const tablaComponentes = document.getElementById("tabla-componentes");

  // Editar componente
  tablaComponentes.addEventListener("click", function(e) {
    if (e.target.classList.contains("btn-editar-componente")) {
      const fila = e.target.closest("tr");
      const id = e.target.getAttribute("data-id");
      const porcentaje = fila.children[1].textContent;
      const orden = fila.children[2].textContent;

      document.getElementById("porcentaje").value = porcentaje;
      document.getElementById("orden").value = orden;

      // Marca el formulario como edición
      form.dataset.editingId = id;

      // Abre el modal
      modalElement.style.display = "block";
    }
  });

  // Eliminar componente
  tablaComponentes.addEventListener("click", function(e) {
    if (e.target.classList.contains("btn-eliminar-componente")) {
      const id = e.target.getAttribute("data-id");
      if (confirm("¿Seguro que deseas eliminar este componente?")) {
        fetch(`/mixFamiliari_crud_agregado_agregados_componente/${id}/eliminar`, {
          method: "DELETE"
        })
        .then(res => {
          if (!res.ok) throw new Error("Error al eliminar");
          e.target.closest("tr").remove();
        })
        .catch(err => alert("❌ Error al eliminar: " + err.message));
      }
    }
  });

  // Agregar o editar componente químico (solo un submit handler)
  if (form && tablaComponentes) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const editingId = form.dataset.editingId;
      const isEdit = Boolean(editingId);

      const data = {
        porcentaje: document.getElementById("porcentaje").value,
        orden: document.getElementById("orden").value
      };

      const url = isEdit
        ? `/mixFamiliari_crud_agregado_agregados_componente/${editingId}/modificar`
        : form.action;
      const method = isEdit ? "PUT" : "POST";
      const fetchOptions = isEdit
        ? {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
          }
        : {
            method: method,
            body: new FormData(form)
          };

      fetch(url, fetchOptions)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (isEdit) {
              // Actualiza la fila existente
              const fila = document.querySelector(`button.btn-editar-componente[data-id="${editingId}"]`).closest("tr");
              fila.children[1].textContent = data.porcentaje;
              fila.children[2].textContent = data.orden;
              delete form.dataset.editingId;
            } else {
              // Agrega nueva fila
              const row = document.createElement("tr");
              row.innerHTML = `
                <td>${data.nombre}</td>
                <td>${data.porcentaje}</td>
                <td>${data.orden}</td>
                <td>
                  <button class="btn btn-sm btn-warning btn-editar-componente" data-id="${data.id}">✏️</button>
                  <button class="btn btn-sm btn-danger btn-eliminar-componente" data-id="${data.id}">🗑️</button>
                </td>
              `;
              tablaComponentes.appendChild(row);
            }
            form.reset();
            modalElement.style.display = "none";
            seccionComponentes.style.display = "block";
          } else {
            alert("⚠️ Error: " + (data.error || "No se pudo guardar el componente"));
          }
        })
        .catch(err => {
          console.error(err);
          alert("❌ Error inesperado al guardar el componente");
        });
    });
  }
});
