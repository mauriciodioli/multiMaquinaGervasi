let mezclaSeleccionada = null;

function agregarAgredadosPreCardados(boton) {
    // 1) guardar de qué mezcla salió el modal
    mezclaSeleccionada = boton.closest(".mezcla");

    fetch("/crud_agregados_mixFamiliari_lista_agregados_json/")
        .then(res => res.json())
        .then(agregados => {
            const select = document.getElementById("selectAgregado");
            select.innerHTML = "";
            agregados.forEach(agg => {
                const option = document.createElement("option");
                option.value = agg.id;
                option.textContent = agg.nombre;
                select.appendChild(option);
            });
            document.getElementById("modalAgregados").style.display = "block";
        });
}

function cerrarModalAgregados() {
    document.getElementById("modalAgregados").style.display = "none";
    // si querés liberar la mezcla:
    // mezclaSeleccionada = null;
}

function usarAgregadoSeleccionado() {
    const id = document.getElementById("selectAgregado").value;
    debugger;

    // 🚨 CONTROL 1: ¿tenemos mezcla seleccionada?
    if (!mezclaSeleccionada) {
        console.error("❌ No hay mezclaSeleccionada. ¿Abriste el modal desde un botón de mezcla?");
        return;
    }

    fetch(`/api/crud_agregados_mixFamiliari/obtener_curva_agregado/${id}`)
        .then(res => res.json())
        .then(tamices => {
            if (!tamices || !tamices.length) {
                console.error("❌ El agregado no devolvió tamices");
                return;
            }

            const nombre = tamices[0].nombre_agregado?.trim() || "Agregado";

            // 📝 Actualizar el nombre SOLO en esa mezcla
            const inputNombre = mezclaSeleccionada.querySelector(".nombreProducto");
            if (inputNombre) {
                inputNombre.value = nombre;
                inputNombre.dataset.original = nombre;
            }

            // 🧼 Limpiar y actualizar SOLO esa tabla
            const tbody = mezclaSeleccionada.querySelector("table.tabla tbody");
            if (!tbody) {
                console.error("❌ No se encontró el tbody en la mezcla seleccionada");
                return;
            }
            tbody.innerHTML = "";

            tamices.forEach(t => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td contenteditable="true">${t.tamiz}</td>
                    <td contenteditable="true">${isNaN(t.porcentaje) ? "" : t.porcentaje}</td>
                    <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
                `;
                tbody.appendChild(fila);
            });

            // opcional
            const btnAgregar = mezclaSeleccionada.querySelector('button[onclick*="agregarFilaMultiple"]');
            if (btnAgregar) {
                btnAgregar.style.display = "inline-block"; // o "none", como quieras
            }

            cerrarModalAgregados();
            // si no querés que se reutilice:
            // mezclaSeleccionada = null;
        })
        .catch(err => {
            console.error("❌ Error al obtener curva del agregado:", err);
        });
}
