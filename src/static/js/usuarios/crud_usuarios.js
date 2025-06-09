document.querySelectorAll(".btn-abrir-modal-modificar-usuario").forEach(boton => {
  boton.addEventListener("click", function () {
    const user_id = this.getAttribute("data-id");
    abrirModalModificar(this);
  });
});



document.querySelectorAll(".btn-abrir-modal-eliminar-usuario").forEach(boton => {
  boton.addEventListener("click", function () {
    const user_id = this.getAttribute("data-id");
    console.log("Eliminando usuario ID:", user_id);
    eliminarUsuario(user_id);
  });
});


document.querySelectorAll(".btn-abrir-modal-entidad-usuario").forEach(boton => {
  boton.addEventListener("click", function () {
    const user_id = this.getAttribute("data-id");
    
    // Lógica que quieras usar con el ID
    console.log("Abrir modal para elemento_entidad_id ID:", user_id);

    listarEntidades(user_id);
  });
});


let usuarioSeleccionadoId = null;
 
// Captura el ID del usuario al abrir el modal
function prepararSeleccionEntidad() {
  document.querySelectorAll('.btn-abrir-modal-entidad-usuario').forEach(btn => {
    btn.addEventListener('click', function () {
      usuarioSeleccionadoId = this.getAttribute('data-id');
      listarEntidades();
    });
  });
}




document.getElementById("btn-abrir-modal-usuario").addEventListener("click", () => {
    document.getElementById('modal-agregar-usuario').style.display = "block";
});

document.getElementById("form-agregar-usuario").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const data = Object.fromEntries(formData);

  try {
    const res = await fetch("/administracion_crud_usuario_crear_usuario/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const respuesta = await res.json();

    if (res.ok && respuesta.success) {
  alert("✅ Usuario agregado correctamente.");

  this.reset();
  document.getElementById('modal-agregar-usuario').style.display = "none";

  // Crear nueva fila
  const fila = document.createElement("tr");
  fila.setAttribute("data-fila-id", respuesta.usuario.id);
  fila.innerHTML = `
    <td>${respuesta.usuario.id}</td>
    <td>${respuesta.usuario.correo_electronico}</td>
    <td>${respuesta.usuario.roll}</td>
    <td>${respuesta.usuario.activo ? 'True' : 'False'}</td>
    <td><span class="text-muted">Nessuna entità</span></td>
    <td>
      <div class="d-flex gap-2">
        <button type="button" class="btn btn-info btn-sm btn-abrir-modal-entidad-usuario"
            data-id="${respuesta.usuario.id}">
            ➕ Entità
        </button>

        <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-usuario"
            data-id="${respuesta.usuario.id}">
            Eliminare
        </button>

        <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-usuario"
            data-id="${respuesta.usuario.id}"
            data-email="${respuesta.usuario.correo_electronico}"
            data-roll="${respuesta.usuario.roll}"
            data-activo="${respuesta.usuario.activo ? 1 : 0}">
            Modificare
        </button>
      </div>
    </td>
  `;

  // Reasignar eventos a los nuevos botones
  fila.querySelector(".btn-abrir-modal-entidad-usuario").addEventListener("click", function () {
    usuarioSeleccionadoId = this.getAttribute('data-id');
    listarEntidades();
  });

  fila.querySelector(".btn-abrir-modal-eliminar-usuario").addEventListener("click", function () {
    eliminarUsuario(this.getAttribute('data-id'));
  });

  fila.querySelector(".btn-abrir-modal-modificar-usuario").addEventListener("click", function () {
    abrirModalModificar(this); // Asumido que tenés esta función
  });

  document.getElementById("tabla-usuarios").appendChild(fila);
} else {
  alert("⚠️ Error al crear usuario: " + (respuesta.message || "Error desconocido"));
}

  } catch (err) {
    alert("💥 Error en la solicitud: " + err.message);
  }
});





function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

document.getElementById("form-agregar-usuario").addEventListener("submit", async function (e) {
  e.preventDefault();

  const pass = document.getElementById("password").value;
  const confirm = document.getElementById("confirmar_password").value;

  if (pass !== confirm) {
    alert("❌ Las contraseñas no coinciden.");
    return;
  }

  // ... sigue el envío al backend
});








function listarEntidades(usuario_id) {
  fetch('/administracion_crud_entidad_contexto_listar/')
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById('tablaEntidadesBody');
      tbody.innerHTML = '';

      if (data.entidades && data.entidades.length > 0) {
        data.entidades.forEach(entidad => {
          const fila = document.createElement('tr');
          fila.classList.add('fila-entidad');
          fila.setAttribute('data-entidad-id', entidad.id);
          fila.innerHTML = `
            <td>${entidad.id}</td>
            <td>${entidad.nombre}</td>
            <td>${entidad.tipo}</td>
            <td>${entidad.descripcion || ''}</td>
          `;
          tbody.appendChild(fila);
        });

        // Agregar evento de selección
        document.querySelectorAll('.fila-entidad').forEach(fila => {
          fila.addEventListener('click', function () {
            document.querySelectorAll('.fila-entidad').forEach(f => f.classList.remove('table-primary'));
            this.classList.add('table-primary');
            this.setAttribute('data-seleccionado', 'true');
            const id = this.children[0].textContent;
            const nombre = this.children[1].textContent;
            console.log(`👉 Seleccionaste entidad ID: ${id}, Nombre: ${nombre}`);
            // También podés marcar visualmente la fila si querés
            document.querySelectorAll('.fila-entidad').forEach(f => f.classList.remove('seleccionada'));
            this.classList.add('seleccionada');

          });
        });


      } else {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td colspan="4" class="text-center">No hay entidades registradas.</td>`;
        tbody.appendChild(fila);
      }

      document.getElementById('modalListaEntidades').style.display = "block";
    })
    .catch(error => {
      console.error('Error al cargar entidades:', error);
      alert('No se pudo cargar el listado de entidades');
    });
}







// Guardar relación usuario <-> entidad
function guardarRelacionEntidad() {
  const filaSeleccionada = document.querySelector('.fila-entidad.table-primary');
  if (!filaSeleccionada) return alert('Selecciona una entidad.');

  const entidadId = filaSeleccionada.getAttribute('data-entidad-id');

  fetch('/asignar_entidad_usuario/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario_id: usuarioSeleccionadoId, entidad_id: entidadId })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Entidad asignada correctamente');
        document.getElementById('modalListaEntidades').style.display = "none";
        // Actualizar la celda de Entidades en la fila del usuario
        const filaUsuario = document.querySelector(`tr[data-fila-id="${usuarioSeleccionadoId}"] td:nth-child(5)`); // 5 = columna 'Entità'
        if (filaUsuario) {
          filaUsuario.innerHTML = ''; // 🔥 Limpiar antes
          const nuevaEntidad = document.createElement('div');
          nuevaEntidad.innerHTML = `🏷️ ${data.entidad.nombre}`;
          filaUsuario.appendChild(nuevaEntidad);
        }

        // Cerrar modal
        document.getElementById('modalListaEntidades').style.display = "none";
        usuarioSeleccionadoId = null;


      } else {
        alert('Error al asignar entidad: ' + data.error);
      }
    })
    .catch(error => alert('Error inesperado: ' + error));
}

document.addEventListener('DOMContentLoaded', () => {
  prepararSeleccionEntidad();
  document.getElementById('btnGuardarEntidadSeleccionada').addEventListener('click', guardarRelacionEntidad);
});














function eliminarUsuario(id) {

  const confirmacion = confirm("⚠️ Sei sicuro di voler eliminare questo utente? Questa azione non può essere annullata.");

  if (!confirmacion) {
    return; // Cancelado por el usuario
  }

  fetch(`/administracion_crud_usuario_eliminar_usuario/${id}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Usuario eliminado correctamente.");

        // ✅ Borra la fila sin recargar
        const fila = document.querySelector(`tr[data-fila-id='${id}']`);
        if (fila) fila.remove();

      } else {
        alert("Error: " + data.error);
      }
    })
    .catch(err => {
      console.error("Error eliminando usuario:", err);
      alert("Error inesperado");
    });
}

















// Mostrar el modal
function abrirModalModificar(boton) {
  document.getElementById('mod-id').value = boton.dataset.id;
  document.getElementById('mod-email').value = boton.dataset.email;
  document.getElementById('mod-roll').value = boton.dataset.roll;
  document.getElementById('mod-activo').value = boton.dataset.activo;

  document.getElementById('modal-modificar-usuario').style.display = 'block';
}

// Cerrar modal manualmente
document.getElementById('btn-cerrar-modal-modificar').addEventListener('click', () => {
  document.getElementById('modal-modificar-usuario').style.display = 'none';
});
document.getElementById('btn-cancelar-modificar').addEventListener('click', () => {
  document.getElementById('modal-modificar-usuario').style.display = 'none';
});






document.getElementById('form-modificar-usuario').addEventListener('submit', function (e) {
  e.preventDefault();

  const id = document.getElementById('mod-id').value;
  const email = document.getElementById('mod-email').value;
  const roll = document.getElementById('mod-roll').value;
  const activo = document.getElementById('mod-activo').value;

  fetch(`/administracion_crud_usuario_modificar_usuario/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      correo_electronico: email,
      roll: roll,
      activo: activo
    })
  })
    .then(res => res.json())
    .then(respuesta => {
      if (respuesta.success) {
        alert('✅ Usuario actualizado correctamente.');

        // 🧠 Actualizar fila en la tabla
        const fila = document.querySelector(`tr[data-fila-id="${id}"]`);
        if (fila) {
          const celdas = fila.querySelectorAll('td');
          celdas[1].textContent = email;
          celdas[2].textContent = roll;
          celdas[3].textContent = activo === "1" ? "True" : "False";
        }

        // Cerrar el modal
        document.getElementById('modal-modificar-usuario').style.display = 'none';
      } else {
        alert('⚠️ Error al actualizar: ' + respuesta.error);
      }
    })
    .catch(err => {
      console.error('Error al actualizar usuario:', err);
      alert('Error inesperado.');
    });
});
