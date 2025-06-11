document.getElementById("crud-link-mix").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    const entidad_id = localStorage.getItem("entidad_id");
    
    if (!userId) {
        alert("Nessun utente ha effettuato l'accesso.");
        return;
    }
    if (!entidad_id) {
        alert("Nessuna entità selezionata.");
        return;
    }

    // REDIRECCIÓN NORMAL CON GET, pasando ambos parámetros
    window.location.href = `/mixFamiliari_crud_agregado_agregados_listar/?user_id=${userId}&entidad_id=${entidad_id}`;
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

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-agregar-mix");
  if (!form) return;

  // Submit para agregar o editar
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const userId = localStorage.getItem("user_id");
    const entidad_id = localStorage.getItem("entidad_id");

    if (!userId || !entidad_id) {
      alert("⚠️ Usuario o Entidad no válidos.");
      return;
    }

    const formData = new FormData(form);
    const pais = getCookie("pais") || "Desconocido";

    const data = {
      nombre: formData.get("nome"),
      descripcion: formData.get("descrizione"),
      estado: formData.get("estado"),
      usuario_id: userId,
      entidad_id: entidad_id,
      pais: pais
    };

    const editingId = form.dataset.editingId;
    const url = editingId
      ? `/mixFamiliari_modificar_agregado/${editingId}`
      : "/mixFamiliari_crear_agregado_agregados/";
    const method = editingId ? "PUT" : "POST";

    fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
    .then(res => {
      if (!res.ok) throw new Error("❌ Errore nella richiesta");
      return res.json();
    })
    .then(response => {
      alert(editingId ? "✅ Aggregato modificato!" : "✅ Aggregato salvato con successo!");
      if (editingId) {
        actualizarFilaTabla(response);
        delete form.dataset.editingId;
      } else {
        agregarFilaTabla(response);
      }
      form.reset();
      document.getElementById('modal-agregar-mix').style.display = "none";
    })
    .catch(err => {
      console.error(err);
      alert("❌ Errore nel salvataggio: " + err.message);
    });
  });

  // Delegación para eliminar y editar
  document.querySelector("table").addEventListener("click", function(e) {
    // Eliminar
    if (e.target.classList.contains("btn-eliminar-agregado")) {
      const id = e.target.getAttribute("data-id");
      if (confirm("¿Seguro que deseas eliminar este agregado?")) {
        fetch(`/mixFamiliari_eliminar_agregado/${id}`, {
          method: "DELETE"
        })
        .then(res => {
          if (!res.ok) throw new Error("Error al eliminar");
          e.target.closest("tr").remove();
        })
        .catch(err => alert("❌ Error al eliminar: " + err.message));
      }
    }

    // Editar
    if (e.target.classList.contains("btn-editar-agregado")) {
      const id = e.target.getAttribute("data-id");
      const fila = e.target.closest("tr");
      const nombre = fila.children[1].textContent;
      const descripcion = fila.children[2].textContent;

      document.getElementById("nome").value = nombre;
      document.getElementById("descrizione").value = descripcion;

      form.dataset.editingId = id;

      // Abre el modal
      const modal = document.getElementById('modal-agregar-mix');
      modal.classList.add('show');
      modal.style.display = 'block';
      modal.removeAttribute('aria-hidden');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('role', 'dialog');
    }
  });
});





document.querySelector("table").addEventListener("click", function(e) {
  if (e.target.classList.contains("btn-editar-agregado")) {
    const id = e.target.getAttribute("data-id");
    const fila = e.target.closest("tr");
    const nombre = fila.children[1].textContent;
    const descripcion = fila.children[2].textContent;
    const estado = fila.children[4].textContent; // <-- aquí
  
    document.getElementById("nome").value = nombre;
    document.getElementById("descrizione").value = descripcion;
    document.getElementById("select-estado").value = estado; // <-- aquí
  
    form.dataset.editingId = id;
  
    // Abre el modal
    const modal = document.getElementById('modal-agregar-mix');
    modal.classList.add('show');
    modal.style.display = 'block';
    modal.removeAttribute('aria-hidden');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('role', 'dialog');
  }



  
});









function agregarFilaTabla(agregado) {
  const tabla = document.querySelector("table tbody");
  if (!tabla) return;

  const fila = document.createElement("tr");
  fila.innerHTML = `
    <td>${agregado.id}</td>
    <td>${agregado.nombre}</td>
    <td>${agregado.descripcion}</td>
    <td>${agregado.entidad_nombre || agregado.entidad_id || ''}</td>
    <td>${agregado.estado}</td>
    <td>
      <button class="btn btn-sm btn-warning btn-componente-quimico-agregado" data-id="${agregado.id}">🧱</button>
      <button class="btn btn-sm btn-warning btn-editar-agregado" data-id="${agregado.id}">✏️</button>
      <button class="btn btn-sm btn-danger btn-eliminar-agregado" data-id="${agregado.id}">🗑️</button>
    </td>
  `;
  tabla.appendChild(fila);
}



function actualizarFilaTabla(agregado) {
  const fila = document.querySelector(`button.btn-editar-agregado[data-id="${agregado.id}"]`).closest("tr");
  fila.children[1].textContent = agregado.nombre;
  fila.children[2].textContent = agregado.descripcion;
  fila.children[3].textContent = agregado.entidad_nombre || agregado.entidad_id || '';
  fila.children[4].textContent = agregado.estado;
}


















function setCookie(name, value, days = 7) {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match ? match[2] : null;
}

// Detectar país por IP solo si no está ya en cookie
async function detectarYGuardarPais() {
  if (getCookie("pais")) return;

  try {
    const response = await fetch("https://ipapi.co/json/");
    const data = await response.json();
    if (data && data.country_name) {
      setCookie("pais", data.country_name);
      console.log("🌍 País detectado y guardado en cookies:", data.country_name);
    }
  } catch (error) {
    console.warn("❌ No se pudo detectar el país", error);
  }
}

// Ejecutar al cargar
document.addEventListener("DOMContentLoaded", detectarYGuardarPais);

















 document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", function (e) {
      if (e.target.classList.contains("btn-componente-quimico-agregado")) {
        const agregadoId = e.target.getAttribute("data-id");
        if (agregadoId) {
          window.location.href = `/mixFamiliari_crud_agregado_agregados/${agregadoId}/detalle`;
        }
      }
    });
  });