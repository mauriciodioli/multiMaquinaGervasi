let mezclaSeleccionada = null;

function agregarAgredadosPreCardados(boton) {
    mezclaSeleccionada = boton.closest(".mezcla");
    fetch("/crud_agregados_mixFamiliari_lista_agregados_json/")  // 🔁 Este endpoint lo creamos abajo
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
}

function usarAgregadoSeleccionado() {
    const id = document.getElementById("selectAgregado").value;

    fetch(`/api/crud_agregados_mixFamiliari/obtener_curva_agregado/${id}`)
        .then(res => res.json())
        .then(tamices => {
            const tbody = mezclaSeleccionada.querySelector("tbody");
            tbody.innerHTML = "";  // Limpia filas anteriores

            tamices.forEach(t => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td contenteditable="true">${t.tamiz}</td>
                    <td contenteditable="true">${t.porcentaje || ""}</td>
                    <td><button class="btn btn-danger mb-3" onclick="this.closest('tr').remove()">Eliminar</button></td>
                `;
                tbody.appendChild(fila);
            });

            mezclaSeleccionada.querySelector(".nombreProducto").value = tamices[0].nombre_agregado || "Agregado";

            // 👉 Oculta el botón "Aggiungi riga"
            const btnAgregar = mezclaSeleccionada.querySelector('button[onclick*="agregarFilaMultiple"]');
            if (btnAgregar) {
                btnAgregar.style.display = "none";
            }

            cerrarModalAgregados();
        });
}

