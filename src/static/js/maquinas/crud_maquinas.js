document.getElementById("confirmar-agregar").addEventListener("click", () => {
    const form = document.getElementById("form-agregar-maquina");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch("/maquinas_crud/agregar", {
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
        alert("Error al conectar con el servidor");
        console.error(err);
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
