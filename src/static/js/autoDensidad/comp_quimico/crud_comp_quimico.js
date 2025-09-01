function cerrarmodalAgregarComponente() {
  document.getElementById('modal-agregar-componente').style.display = 'none';
}

function cerrarmodalModificarComponente() {
  document.getElementById('modal-modificar-componente').style.display = 'none';
}

document.getElementById("btn-abrir-modal-componente").addEventListener("click", function () {
  document.getElementById('modal-agregar-componente').style.display = "block";
});

document.addEventListener("click", function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-modificar-componente")) {
    const btn = e.target;
    
    document.getElementById("mod-id").value = btn.dataset.id;
    document.getElementById("mod-nombre").value = btn.dataset.nombre;
    document.getElementById("mod-pais").value = btn.dataset.pais;
    document.getElementById("mod-descripcion").value = btn.dataset.descripcion;
    document.getElementById("mod-tipo_mezcla_id").value = btn.dataset.tipo_mezcla_id;       
    document.getElementById("mod-tipo_mezcla_nome").value = btn.dataset.tipo_mezcla_nome;
       
    document.getElementById("form-modificar-componente").dataset.filaOrigen = btn.closest("tr").dataset.filaId;

    document.getElementById('modal-modificar-componente').style.display = "block";
  }
});

document.getElementById("form-modificar-componente").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);
  const filaId = this.dataset.filaOrigen;

  try {
    const res = await fetch(`/mixFamiliari_crud_componente_quimico_pantalla_modificar/${data.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
      alert("✅ Componente químico modificado correctamente.");

      const fila = document.querySelector(`tr[data-fila-id="${filaId}"]`);
      if (fila) {
             fila.innerHTML = `
          <td>${data.id}</td>
          <td>${data.nombre}</td>
          <td>${data.pais}</td>
          <td>${data.descripcion}</td>
          <td>${data.tipo_mezcla_nome}</td>
          <td>
            <button type="button"
                          class="btn btn-danger btn-sm btn-abrir-modal-tipoMezcla-componente"
                           data-id="${ data.id }">
                    Agregar Tipo Mezcla
                  </button>
            <button type="button"
                          class="btn btn-danger btn-sm btn-abrir-modal-materia-forma"
                           data-id="${ data.id }">
                    Agregar Materia ssFormas
            </button>      
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-componente"
                data-id="${data.id}"
                data-nombre="${data.nombre}"
                data-pais="${data.pais}"
                data-descripcion="${data.descripcion}"
                data-tipo_mezcla_id="${data.tipo_mezcla_id}"
                data-tipo_mezcla_nome="${data.tipo_mezcla_nome}">
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-componente"
                data-id="${data.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;
      }

      document.getElementById('modal-modificar-componente').style.display = "none";

    } else {
      alert("⚠️ Error: " + (respuesta.error || "No se pudo modificar el componente."));
    }
  } catch (err) {
    console.error(err);
    alert("💥 Error en la solicitud: " + err.message);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('form-agregar-componente').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
      nombre: document.getElementById('nombre').value,
      pais: document.getElementById('pais').value,
      descripcion: document.getElementById('descripcion').value,   

    };

    try {
      const res = await fetch('/mixFamiliari_crud_componente_quimico_pantalla_agregar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const respuesta = await res.json();

      if (res.ok && respuesta.success && respuesta.componente_quimico) {
        const c = respuesta.componente_quimico;
        const tr = document.createElement('tr');
        tr.setAttribute('data-fila-id', c.id);
        tr.innerHTML = `
          <td>${c.id}</td>
          <td>${c.nombre}</td>
          <td>${c.pais}</td>
          <td>${c.descripcion}</td>
          <td>${c.tipo_mezcla_id}</td>
          <td>
                  <button type="button"
                          class="btn btn-danger btn-sm btn-abrir-modal-tipoMezcla-componente"
                           data-id="${ c.id }">
                    Agregar Tipo Mezcla
                  </button>
            <div class="d-flex align-items-center gap-2">
              <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-componente"
                data-id="${c.id}"
                data-nombre="${c.nombre}"
                data-pais="${c.pais}"
                data-descripcion="${c.descripcion}"
                data-tipo_mezcla_id="${c.tipo_mezcla_id}">              
                Modificare
              </button>
              <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-componente"
                data-id="${c.id}">
                Eliminare
              </button>
            </div>
          </td>
        `;

        document.getElementById('tabla-componentes').appendChild(tr);
        document.getElementById('form-agregar-componente').reset();
        document.getElementById('modal-agregar-componente').style.display = "none";
      } else {
        alert('❌ Error al agregar componente.');
      }
    } catch (err) {
      console.error(err);
      alert('💥 Error al enviar solicitud: ' + err.message);
    }
  });

  // Eliminar
  document.addEventListener("click", async function (e) {
    if (e.target && e.target.classList.contains("btn-abrir-modal-eliminar-componente")) {
      const id = e.target.dataset.id;

      if (confirm("¿Seguro que querés eliminar este componente químico?")) {
        try {
          const res = await fetch(`/mixFamiliari_crud_componente_quimico_pantalla_eliminar/${id}`, {
            method: "DELETE"
          });
          const data = await res.json();
          if (res.ok && data.success) {
            const fila = document.querySelector(`tr[data-fila-id="${id}"]`);
            if (fila) fila.remove();
          } else {
            alert("❌ No se pudo eliminar el componente.");
          }
        } catch (err) {
          console.error(err);
          alert("💥 Error al eliminar: " + err.message);
        }
      }
    }
  });
});



document.addEventListener("click", async function (e) {
  if (e.target && e.target.classList.contains("btn-abrir-modal-tipoMezcla-componente")) {
    // Setea el id del componente químico en el botón guardar
    const componenteId = e.target.dataset.id;
    document.getElementById('btn-guardar-tipo-mezcla').dataset.componenteId = componenteId;
debugger;
    try {
      const res = await fetch("/mixFamiliari_crud_tipo_mezcla_pantalla_listar_json/");
      const data = await res.json();
      if (res.ok && data.success) {
        const select = document.getElementById("select-tipo-mezcla");
        select.innerHTML = "";
        data.tipos_mezcla.forEach(tipo => {
          const option = document.createElement("option");
          option.value = tipo.id;
          option.textContent = tipo.nombre + " - " + tipo.descripcion;
          select.appendChild(option);
        });
        // Mostrar el modal (sin Bootstrap)
        document.getElementById('modal-tipo-mezla').style.display = "block";
        document.getElementById('modal-tipo-mezla').classList.add('show');
      }
    } catch (err) {
      console.error(err);
      alert("💥 Error al cargar tipos de mezcla: " + err.message);
    }
  }
});

// Para cerrar el modal al hacer clic en el botón de cerrar o fuera del modal
document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
  btn.addEventListener('click', function() {
    const modal = document.getElementById('modal-tipo-mezla');
    modal.style.display = "none";
    modal.classList.remove('show');
  });
});

// Opcional: cerrar al hacer clic fuera del contenido
window.addEventListener('click', function(event) {
  const modal = document.getElementById('modal-tipo-mezla');
  if (event.target === modal) {
    modal.style.display = "none";
    modal.classList.remove('show');
  }
});
document.getElementById('btn-guardar-tipo-mezcla').addEventListener('click', async function() {
  const tipoMezclaId = document.getElementById('select-tipo-mezcla').value;
  const componenteId = this.dataset.componenteId;
  // Obtén el nombre del tipo de mezcla seleccionado
  const tipoMezclaNombre = document.getElementById('select-tipo-mezcla').selectedOptions[0].textContent;
  
  try {
    const res = await fetch(`/mixFamiliari_crud_componente_quimico_pantalla_modificar_tipo_Mezcla/${componenteId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo_mezcla_id: tipoMezclaId })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      alert("✅ Tipo de mezcla actualizado correctamente.");
      document.getElementById('modal-tipo-mezla').style.display = "none";
      document.getElementById('modal-tipo-mezla').classList.remove('show');
      // Actualiza la celda en la tabla
      const fila = document.querySelector(`tr[data-fila-id="${componenteId}"]`);
     if (fila) {
    // Usa el nombre y el id que vienen del backend
    fila.children[4].textContent = data.componente_quimico.tipo_mezcla_nome;

    const btnModificar = fila.querySelector('.btn-abrir-modal-modificar-componente');
    if (btnModificar) {
      btnModificar.dataset.tipo_mezcla_id = data.componente_quimico.tipo_mezcla_id;
      btnModificar.dataset.tipo_mezcla_nome = data.componente_quimico.tipo_mezcla_nome;
    }
  }
    } else {
      alert("❌ Error al actualizar tipo de mezcla.");
    }
  } catch (err) {
    alert("💥 Error en la solicitud: " + err.message);
  }
});




