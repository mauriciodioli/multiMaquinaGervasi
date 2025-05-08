document.getElementById("crud-link").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        alert("No hay usuario en sesión");
        return;
    }

    // REDIRECCIÓN NORMAL CON GET
    window.location.href = `/maquinas_crud_consulta/?user_id=${userId}`;
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
                alert("Máquina agregada correctamente");
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







const original = document.getElementById("confirmar-modificar");
const nuevo = original.cloneNode(true);
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
            alert("Máquina modificada correctamente");
            location.reload();
        } else {
            alert("Error: " + res.message);
        }
    })
    .catch(err => {
        alert("Error al conectar con el servidor");
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









// Capturar el clic en los botones de "Eliminar" usando el atributo data-bs-target
document.querySelectorAll('[data-bs-target="#modal-eliminar"]').forEach(button => {
    button.addEventListener('click', function() {
        // Obtener el ID de la máquina desde el atributo data-maquina-id
        const maquinaId = this.getAttribute('data-maquina-id');
        
        // Asignar el ID al campo oculto del modal
        document.getElementById('maquina-id-eliminar-crud').value = maquinaId;

        // Crear una instancia del modal de Bootstrap
        const modalElement = document.getElementById('modal-eliminar-crud');
        const modal = new bootstrap.Modal(modalElement);

        // Mostrar el modal usando la API de Bootstrap
        modal.show();  // Abre el modal correctamente
    });
});

// Capturar el clic en el botón "Confirmar eliminar"
document.getElementById("confirmar-eliminar").addEventListener("click", () => {
    const maquinaId = document.getElementById("maquina-id-eliminar-crud").value;  // Obtiene el ID desde el campo oculto
    
    console.log("ID de la máquina a eliminar:", maquinaId);

    // Realizar la solicitud DELETE al servidor
    fetch(`/maquinas_crud/eliminar/${maquinaId}`, {
        method: 'DELETE',  // Especificamos que es un método DELETE
        headers: {
            'Content-Type': 'application/json',  // El tipo de contenido es JSON
        },
    })
    .then(response => response.json())  // Procesamos la respuesta como JSON
    .then(data => {
        if (data.success) {
            console.log("Máquina eliminada con éxito");
        
            // Buscar el botón de eliminación usando el ID
            const maquinaEliminada = document.querySelector(`button[data-maquina-id="${maquinaId}"]`);
            if (maquinaEliminada) {
                // Encontrar la fila completa <tr> que contiene el botón de eliminación
                const trElement = maquinaEliminada.closest('tr'); // Encuentra el <tr> que contiene el <button>
                trElement.remove();  // Elimina la fila completa (<tr>) del DOM
            }
        } else {
            console.error("Error al eliminar la máquina:", data.message);
            alert("Error al eliminar la máquina");
        }
        
    })
    .catch(error => {
        console.error("Error al conectar con el servidor:", error);
        alert("Error al conectar con el servidor");
    });

    // Cerrar el modal después de la eliminación usando la API de Bootstrap 5
    const modalElement = document.getElementById('modal-eliminar-crud');
    const modal = bootstrap.Modal.getInstance(modalElement);  // Obtener la instancia del modal
    modal.hide();  // Cierra el modal correctamente
});



































const select = document.getElementById("modulos-select");
const input = document.getElementById("nuevo-modulo");
const btn = document.getElementById("btn-agregar-modulo");

// Cargar módulos al iniciar desde localStorage
document.addEventListener("DOMContentLoaded", () => {
    const guardados = JSON.parse(localStorage.getItem("modulosPersonalizados")) || [];

    // Opciones iniciales por defecto
    const baseModulos = ["history", "jobs", "settings", "statistics", "logs"];

    const todos = [...new Set([...baseModulos, ...guardados])]; // evita duplicados

    todos.forEach(valor => {
        const opt = new Option(valor, valor);
        select.add(opt);
    });
});

// Agregar nuevo módulo dinámicamente
btn.addEventListener("click", () => {
    const valor = input.value.trim();
    if (!valor) return;

    // Verificar si ya existe
    const existe = [...select.options].some(opt => opt.value === valor);
    if (existe) {
        alert("Ese módulo ya existe.");
        return;
    }

    // Crear y seleccionar la nueva opción
    const nuevaOpcion = new Option(valor, valor, true, true);
    select.add(nuevaOpcion);
    input.value = "";

    // Guardar en localStorage
    const existentes = JSON.parse(localStorage.getItem("modulosPersonalizados")) || [];
    if (!existentes.includes(valor)) {
        existentes.push(valor);
        localStorage.setItem("modulosPersonalizados", JSON.stringify(existentes));
    }
});

