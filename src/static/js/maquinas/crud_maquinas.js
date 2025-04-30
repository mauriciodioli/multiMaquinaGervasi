document.getElementById("crud-link").addEventListener("click", (e) => {
    e.preventDefault();
    const userId = localStorage.getItem("user_id");
    
    if (!userId) {
        alert("No hay usuario en sesión");
        return;
    }

    fetch("/maquinas_crud_consulta/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(res => res.text())
    .then(html => {
        // Reemplazá todo el contenido del body o redirect manual
        document.open();
        document.write(html);
        document.close();
    })
    .catch(err => {
        console.error("Error al cargar máquinas:", err);
        alert("Fallo la carga del CRUD");
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







document.getElementById("confirmar-modificar").addEventListener("click", () => {
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
        form.accountCuenta.value = button.dataset.accountCuenta || '';
        form.nombre.value = button.dataset.nombre || '';
        form.ruta.value = button.dataset.ruta || '';
        form.nombreDb.value = button.dataset.nombreDb || '';
        form.selector.value = button.dataset.selector || '';
        form.sector.value = button.dataset.sector || '';
        form.estado.value = button.dataset.estado || '';
        form.setting.value = button.dataset.setting || '';
        form.passwordCuenta.value = ''; // nunca prellenar contraseñas
        document.getElementById("maquina-id-modificar").value = button.dataset.maquinaId;
    });
});





document.getElementById("confirmar-eliminar").addEventListener("click", () => {
    const id = document.getElementById("maquina-id-eliminar").value;

    fetch(`/maquinas_crud/eliminar/${id}`, {
        method: "DELETE"
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            alert("Máquina eliminada correctamente");
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


document.querySelectorAll('[data-bs-target="#modal-eliminar"]').forEach(button => {
    button.addEventListener('click', () => {
        document.getElementById("maquina-id-eliminar").value = button.dataset.maquinaId;
    });
});
