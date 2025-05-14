document.getElementById("crud-link").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        alert("Nessun utente ha effettuato l'accesso.");
        return;
    }

    // REDIRECCIÓN NORMAL CON GET
    window.location.href = `/maquinas_crud_consulta/?user_id=${userId}`;
});














document.getElementById('btn-abrir-modal').addEventListener('click', function () {
  const modal = document.getElementById('crud-modal-agregar');
  modal.classList.add('show');
  modal.style.display = 'block';
  modal.removeAttribute('aria-hidden');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('role', 'dialog');

  inicializarModulosSelect(); // 👈 Ejecutás tu lógica cuando abrís el modal
});

// Cerrar el modal manualmente
document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
  btn.addEventListener('click', function () {
    const modal = btn.closest('.modal');
    modal.classList.remove('show');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    modal.removeAttribute('aria-modal');
  });
});












 document.querySelectorAll('.btn-abrir-modal-modificar').forEach(btn => {
    btn.addEventListener('click', function () {

      // Mostrar modal manualmente
      const modal = document.getElementById('crud-modal-modificar');
      modal.classList.add('show');
      modal.style.display = 'block';
      modal.removeAttribute('aria-hidden');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('role', 'dialog');

      // Cargar datos en el formulario
      document.getElementById('maquina-id-modificar').value = btn.getAttribute('data-maquina-id');
      document.querySelector('#form-modificar-maquina [name="userCuenta"]').value = btn.getAttribute('data-user-cuenta');
      document.querySelector('#form-modificar-maquina [name="nombre"]').value = btn.getAttribute('data-nombre');
      document.querySelector('#form-modificar-maquina [name="ruta"]').value = btn.getAttribute('data-ruta');
      document.querySelector('#form-modificar-maquina [name="nombreDb"]').value = btn.getAttribute('data-nombre-db');
      document.querySelector('#form-modificar-maquina [name="sector"]').value = btn.getAttribute('data-sector');
      document.querySelector('#form-modificar-maquina [name="estado"]').value = btn.getAttribute('data-estado');
      document.querySelector('#form-modificar-maquina [name="potencia"]').value = btn.getAttribute('data-potencia');

      // Settings (JSON prettify)
      const setting = btn.getAttribute('data-setting');
      try {
        const obj = JSON.parse(setting);
        document.querySelector('#form-modificar-maquina [name="setting"]').value = JSON.stringify(obj, null, 2);
      } catch (e) {
        document.querySelector('#form-modificar-maquina [name="setting"]').value = setting;
      }
    });
  });

  // Cerrar el modal manualmente
  document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = btn.closest('.modal');
      modal.classList.remove('show');
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      modal.removeAttribute('aria-modal');
    });
  });




































document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("confirmar-agregar");
    const form = document.getElementById("form-agregar-maquina");

    // ✅ Clonamos el botón para evitar listeners duplicados
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);

    newBtn.addEventListener("click", event => {
        event.preventDefault();  // ⚠️ CRÍTICO

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.modulos = Array.from(form.elements["modulos"].selectedOptions).map(opt => opt.value);
        
        data.user_id = localStorage.getItem("user_id");
        debugger;
        fetch("/maquinas_crud/agregar/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                alert("Macchina aggiunta correttamente");
                location.reload();
            } else {
                alert("Error: " + res.message);
            }
        })
        .catch(err => {
            alert("Error inesperado:\n" + err.message);
            console.error(err);
        });
    });
});







original = document.getElementById("confirmar-modificar");
nuevo = original.cloneNode(true);
original.parentNode.replaceChild(nuevo, original);

nuevo.addEventListener("click", () => {
    const form = document.getElementById("form-modificar-maquina");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const id = document.getElementById("maquina-id-modificar").value;

    fetch(`/maquinas_crud/modificar/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            alert("Macchina modificata correttamente");
            location.reload();
        } else {
            alert("Error: " + res.message);
        }
    })
    .catch(err => {
        alert("Errore durante la connessione al server");
        console.error(err);
    });
});


document.querySelectorAll('[data-bs-target="#modal-modificar"]').forEach(button => {
    button.addEventListener('click', () => {
        const form = document.getElementById("form-modificar-maquina");
        form.reset();

        form.userCuenta.value = button.dataset.userCuenta || '';
        form.nombre.value = button.dataset.nombre || '';
        form.ruta.value = button.dataset.ruta || '';
        form.nombreDb.value = button.dataset.nombreDb || '';
        form.sector.value = button.dataset.sector || '';
        form.estado.value = button.dataset.estado || '';
        form.potencia.value = button.dataset.potencia || '';

        try {
            const setting = JSON.parse(button.dataset.setting || '{}');
            form.setting.value = JSON.stringify(setting, null, 2);
        } catch (e) {
            console.warn("Error al parsear setting:", e);
            form.setting.value = button.dataset.setting || '';
        }

        document.getElementById("maquina-id-modificar").value = button.dataset.maquinaId;
    });
});








document.addEventListener("DOMContentLoaded", () => {
  // Abrir modal eliminar y pasar ID
  document.querySelectorAll('.btn-abrir-modal-eliminar').forEach(button => {
    button.addEventListener('click', function () {
      const maquinaId = this.getAttribute('data-maquina-id');
      document.getElementById('maquina-id-eliminar-crud').value = maquinaId;

      const modal = document.getElementById('modal-eliminar-crud');
      modal.classList.add('show');
      modal.style.display = 'block';
      modal.removeAttribute('aria-hidden');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('role', 'dialog');
    });
  });

  // Cerrar modal manualmente
  document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
    btn.addEventListener('click', function () {
      const modal = btn.closest('.modal');
      modal.classList.remove('show');
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      modal.removeAttribute('aria-modal');
    });
  });

  // Confirmar eliminación
  document.getElementById("confirmar-eliminar").addEventListener("click", () => {
    const maquinaId = document.getElementById("maquina-id-eliminar-crud").value;
    debugger;
    fetch(`/maquinas_crud/eliminar/${maquinaId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Eliminar la fila de la tabla
        const boton = document.querySelector(`.btn-abrir-modal-eliminar[data-maquina-id="${maquinaId}"]`);
        const fila = boton?.closest('tr');
        if (fila) fila.remove();
      } else {
        alert("❌ Errore durante l'eliminazione: " + data.message);
      }

      // Cerrar el modal manualmente
      const modal = document.getElementById('modal-eliminar-crud');
      modal.classList.remove('show');
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      modal.removeAttribute('aria-modal');
    })
    .catch(error => {
      alert("⚠️ Errore di connessione");
      console.error(error);
    });
  });
});






































function inicializarModulosSelect() {
  const select = document.getElementById("modulos-select"); // ✅ FIJATE AQUÍ
  const input = document.getElementById("nuevo-modulo");
  const btn = document.getElementById("btn-agregar-modulo");

  if (!select || !input || !btn) {
    console.error("Faltan elementos en el DOM.");
    return;
  }
 if (select.dataset.inicializado === "true") {
    return;
  }
  select.dataset.inicializado = "true";
  // Solo cargar si aún no tiene opciones
  if (select.options.length === 0) {
    const guardados = JSON.parse(localStorage.getItem("modulosPersonalizados")) || [];
    const baseModulos = ["history", "jobs", "settings", "statistics", "logs"];
    const todos = [...new Set([...baseModulos, ...guardados])];

    todos.forEach(valor => {
      const opt = new Option(valor, valor);
      select.add(opt);
    });
  }

  // Agregar módulo dinámicamente
  btn.onclick = () => {
    const valor = input.value.trim();
    if (!valor) return;

    const existe = [...select.options].some(opt => opt.value === valor);
    if (existe) {
      alert("Quel modulo esiste già.");
      return;
    }

    const nuevaOpcion = new Option(valor, valor, true, true);
    select.add(nuevaOpcion);
    input.value = "";

    const existentes = JSON.parse(localStorage.getItem("modulosPersonalizados")) || [];
    if (!existentes.includes(valor)) {
      existentes.push(valor);
      localStorage.setItem("modulosPersonalizados", JSON.stringify(existentes));
    }
  };

  // Escuchar cambios en selección
  select.addEventListener("change", () => {
    const seleccionados = Array.from(select.selectedOptions).map(opt => opt.value);
    console.log("👉 Módulos seleccionados:", seleccionados);

  });
}

