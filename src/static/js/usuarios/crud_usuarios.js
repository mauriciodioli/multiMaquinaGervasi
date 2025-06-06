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

      // Crear fila
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
            <button type="button" class="btn btn-warning btn-sm btn-abrir-modal-modificar-usuario"
                data-id="${respuesta.usuario.id}"
                data-email="${respuesta.usuario.correo_electronico}"
                data-roll="${respuesta.usuario.roll}"
                data-activo="${respuesta.usuario.activo ? 1 : 0}">
                Modificare
            </button>
            <button type="button" class="btn btn-danger btn-sm btn-abrir-modal-eliminar-usuario"
                data-id="${respuesta.usuario.id}">
                Eliminare
            </button>
            </div>
        </td>
        `;


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
