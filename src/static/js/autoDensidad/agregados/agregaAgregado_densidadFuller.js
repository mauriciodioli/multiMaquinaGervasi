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

            // nombre en esa mezcla
            const inputNombre = mezclaSeleccionada.querySelector(".nombreProducto");
            if (inputNombre) {
                inputNombre.value = nombre;
                inputNombre.dataset.original = nombre;
            }

            // tabla de esa mezcla
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
                btnAgregar.style.display = "inline-block";
            }

            cerrarModalAgregados();
debugger;
            // 👇 acá sí guardamos
            guardarTablaEnLocalStorage(mezclaSeleccionada, nombre, tamices);
        })
        .catch(err => {
            console.error("❌ Error al obtener curva del agregado:", err);
        });
}


function guardarTablaEnLocalStorage(mezclaEl, nombreAgregado, tamices) {
    // 1) identificar la mezcla
    // puede ser un data-id en el contenedor .mezcla
    const mezclaId = mezclaEl.getAttribute("data-mezcla-id") || mezclaEl.id || null;
    if (!mezclaId) {
        console.warn("⚠️ No puedo identificar la mezcla, no guardo en localStorage");
        return;
    }

    // 2) leemos lo que ya hay
    const raw = localStorage.getItem("tablasCargadas");
    let tablas = [];
    if (raw) {
        try {
            tablas = JSON.parse(raw);
        } catch (e) {
            console.warn("⚠️ tablasCargadas tenía un JSON roto, lo reinicio");
            tablas = [];
        }
    }

    // 3) armamos el objeto de esta mezcla
    const tablaActual = {
        mezclaId: mezclaId,
        nombre: nombreAgregado,
        filas: tamices.map(t => ({
            tamiz: t.tamiz,
            porcentaje: isNaN(t.porcentaje) ? "" : t.porcentaje
        }))
    };

    // 4) si ya había una entrada de esta mezcla, la reemplazo
    const idx = tablas.findIndex(t => t.mezclaId === mezclaId);
    if (idx >= 0) {
        tablas[idx] = tablaActual;
    } else {
        tablas.push(tablaActual);
    }

    // 5) guardo
    localStorage.setItem("tablasCargadas", JSON.stringify(tablas));
}


document.addEventListener("DOMContentLoaded", function() {
    debugger;
    restaurarTablasDesdeLocalStorage();
});

document.addEventListener("DOMContentLoaded", function() {
    restaurarTablasDesdeLocalStorage();
});

function restaurarTablasDesdeLocalStorage() {
    const raw = localStorage.getItem("tablasCargadas");
    if (!raw) return;

    let tablas;
    try {
        tablas = JSON.parse(raw);
    } catch (e) {
        console.error("❌ No pude parsear tablasCargadas:", e);
        return;
    }

    // referencia al contenedor
    const container = document.getElementById("mezclasContainer");
    if (!container) return;

    tablas.forEach((tab, idx) => {
        // 1) crear mezcla si no existe
        let mezclaEl = document.querySelector(`.mezcla[data-mezcla-id="${tab.mezclaId}"]`);
        if (!mezclaEl) {
            // crear una mezcla nueva igual que en agregarMezcla()
            mezclaEl = document.createElement("div");
            mezclaEl.className = "mezcla";
            mezclaEl.setAttribute("data-mezcla-id", tab.mezclaId || `mezcla-${idx}`);

            mezclaEl.innerHTML = `
                <div class="contenedor-producto">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Aggregato</h3>
                        <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Rimuovere il aggregato</button>
                    </div>
                    <h3>Nuevo Producto</h3>
                    <input type="text" value="" class="nombreProducto" data-original="">
                    <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Aggiungi Riga</button>
                    <button class="btn btn-danger" onclick="agregarAgredadosPreCardados(this)">select precargados</button>
                    <button class="btn btn-danger" onclick="agregarTablaAlocalStorage(this)">save</button>
                    <table class="tabla">
                        <thead>
                            <tr><th>Tamiz</th><th>% Real</th><th>Acción</th></tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                    <hr>
                </div>
            `;
            container.appendChild(mezclaEl);
        }

        // 2) setear nombre
        const inputNombre = mezclaEl.querySelector(".nombreProducto");
        if (inputNombre && tab.nombre) {
            inputNombre.value = tab.nombre;
            inputNombre.dataset.original = tab.nombre;
        }

        // 3) setear tabla
        const tbody = mezclaEl.querySelector("table.tabla tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        (tab.filas || []).forEach(f => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td contenteditable="true">${f.tamiz || ""}</td>
                <td contenteditable="true">${f.porcentaje || ""}</td>
                <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
            `;
            tbody.appendChild(fila);
        });
    });

    // MUY IMPORTANTE: actualizar mezclaId global
    // para que las nuevas mezclas no pisen las que restauramos
    if (typeof mezclaId !== "undefined") {
        mezclaId = tablas.length;
    }
}
function LimpiarTodasLasTablas() {
    // 1) borrar del localStorage
    localStorage.removeItem("tablasCargadas");

    // 2) limpiar lo que haya en el DOM ahora
    const mezclas = document.querySelectorAll(".mezcla");
    mezclas.forEach(m => {
        // limpiar nombre
        const input = m.querySelector(".nombreProducto");
        if (input) {
            input.value = "";
            input.dataset.original = "";
        }

        // limpiar tabla
        const tbody = m.querySelector("table.tabla tbody");
        if (tbody) {
            tbody.innerHTML = "";
        }
    });

    // 3) (opcional) si querés borrar también las mezclas del DOM:
    // document.getElementById("mezclasContainer").innerHTML = "";

    // 4) (opcional) si usás mezclaId global y querés reiniciarlo:
    // if (typeof mezclaId !== "undefined") mezclaId = 0;

    console.log("✅ Tablas limpiadas y localStorage reseteado.");
}
