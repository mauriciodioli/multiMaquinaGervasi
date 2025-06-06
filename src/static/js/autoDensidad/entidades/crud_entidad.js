document.getElementById("btn-abrir-modal-entidad").addEventListener("click", function () {
  document.getElementById('modal-agregar-entidad').style.display = "block";
});







document.getElementById("form-agregar-entidad").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);

  try {
    const res = await fetch("/administracion_crud_entidad_crear_entidad/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Entidad agregada correctamente.");
    // Limpiar el formulario
      this.reset();
      document.getElementById('modal-agregar-entidad').style.display = "none";
      // Insertar fila a la tabla
      const nuevaFila = document.createElement("tr");
      nuevaFila.innerHTML = `
        <td>${respuesta.entidad.id}</td>
        <td>${respuesta.entidad.nombre}</td>
        <td>${respuesta.entidad.tipo || ''}</td>
        <td>${respuesta.entidad.descripcion || ''}</td>
        <td>${respuesta.entidad.estado}</td>
        <td>
          <div class="d-flex align-items-center gap-2">
            <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-entidad"
              data-entidad-id="${respuesta.entidad.id}"
              data-nombre="${respuesta.entidad.nombre}"
              data-tipo="${respuesta.entidad.tipo || ''}"
              data-descripcion="${respuesta.entidad.descripcion || ''}"
              data-estado="${respuesta.entidad.estado}">
              Modificare
            </button>
            <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-entidad"
              data-entidad-id="${respuesta.entidad.id}">
              Eliminare
            </button>

            
          </div>
        </td>
      `;

      document.getElementById("tabla-entidades").appendChild(nuevaFila);

    } else {
      alert("⚠️ Error: " + (respuesta.message || "No se pudo agregar la entidad."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Error en la solicitud: " + err.message);
  }
});













document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-entidad")) {
    const entidadId = e.target.dataset.entidadId;
    console.log("🗑️ Entidad a eliminar ID:", entidadId);

    if (confirm(`¿Seguro que querés eliminar la entidad ID ${entidadId}?`)) {
      eliminarEntidad(entidadId, e.target);
    }
  }
});

function eliminarEntidad(id, boton) {
  fetch(`/administracion_crud_entidad_eliminar_entidad/${id}`, {
    method: "DELETE"
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        alert("✅ Eliminada correctamente.");
        const fila = boton.closest("tr");
        if (fila) fila.remove();
      } else {
        alert("⚠️ Error al eliminar: " + (data.message || "desconocido"));
      }
    })
    .catch(err => {
      alert("💥 Error al conectarse con el servidor: " + err.message);
    });
}

