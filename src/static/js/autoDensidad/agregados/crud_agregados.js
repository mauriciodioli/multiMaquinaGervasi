document.getElementById("crud-link-mix").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        alert("Nessun utente ha effettuato l'accesso.");
        return;
    }

    // REDIRECCIÓN NORMAL CON GET
    window.location.href = `/pantalla_agregado/?user_id=${userId}`;
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

    inicializarModulosSelect(); // 👈 Ejecutás tu lógica cuando abrís el modal
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
  
  const btnGuardar = document.getElementById("btn-confirmar-aggiungi");
  const userId = localStorage.getItem("user_id");
  localStorage.setItem('entidad_id','17');
  const entidad_id = localStorage.getItem("entidad_id");

  if (!btnGuardar) return;

  btnGuardar.addEventListener("click", function (e) {
     e.preventDefault();  // ⬅️ Esto evita el envío automático del formulario
    if (!userId) {
      alert("⚠️ Nessun utente ha effettuato l'accesso.");
      return;
    }

    const form = document.getElementById("form-agregar-mix");
    const formData = new FormData(form);

   const pais = getCookie("pais") || "Desconocido";

   const data = {
        nombre: formData.get("nome"),
        descripcion: formData.get("descrizione"),
        idioma: formData.get("idioma"),
        estado: formData.get("estado"),
        usuario_id: userId,
        entidad_id: entidad_id,  // debe ser ID numérico
        malla_id: null,
        pais: getCookie("pais") || "Desconocido"
      };


    fetch("/mixFamiliari_crear_agregado_agregados/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    })
      .then(res => {
        if (!res.ok) throw new Error("❌ Errore nella richiesta");
        return res.json();
      })
      .then(response => {
        alert("✅ Aggregato salvato con successo!");
        location.reload(); // o podés cerrar el modal y actualizar la tabla
      })
      .catch(err => {
        console.error(err);
        alert("❌ Errore nel salvataggio: " + err.message);
      });
  });
});



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
