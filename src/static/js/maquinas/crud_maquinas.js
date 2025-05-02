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






