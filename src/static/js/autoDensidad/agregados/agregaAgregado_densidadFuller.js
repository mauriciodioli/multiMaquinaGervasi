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
            actualizarTextoModalAgregados();
        });
}

function cerrarModalAgregados() {
    document.getElementById("modalAgregados").style.display = "none";
    // si querés liberar la mezcla:
    // mezclaSeleccionada = null;
}

function actualizarTextoModalAgregados() {
    const titulo = document.getElementById("modalAgregadosTitulo");
    const boton = document.getElementById("btnUsarAgregado");
    
    if (titulo && typeof I18N !== 'undefined') {
        titulo.textContent = I18N.t('sim.modal_titulo_agregados', 'Seleccionar agregado precargado');
    }
    
    if (boton && typeof I18N !== 'undefined') {
        boton.textContent = I18N.t('sim.modal_boton_usar_agregado', 'Usar agregado');
    }
}

function usarAgregadoSeleccionado() {
    const id = document.getElementById("selectAgregado").value;
    debugger;

    if (!mezclaSeleccionada) {
        const msg = typeof I18N !== 'undefined' 
            ? I18N.t('sim.error_sin_mezcla_seleccionada', 'No hay mezcla seleccionada. Abre el modal desde un botón de mezcla.')
            : '❌ No hay mezclaSeleccionada. ¿Abriste el modal desde un botón de mezcla?';
        notify('error', 'Error', msg);
        console.error(msg);
        return;
    }

    fetch(`/api/crud_agregados_mixFamiliari/obtener_curva_agregado/${id}`)
        .then(res => res.json())
        .then(tamices => {
            if (!tamices || !tamices.length) {
                const msg = typeof I18N !== 'undefined' 
                    ? I18N.t('sim.error_sin_valores', 'El agregado no tiene valores disponibles')
                    : '❌ El agregado no devolvió tamices';
                notify('error', 'Error', msg);
                console.error(msg);
                // Cerrar modal de agregados automáticamente cuando no hay datos
                if (typeof cerrarModalAgregados === 'function') {
                    setTimeout(() => cerrarModalAgregados(), 2000);
                }
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
                const msg = typeof I18N !== 'undefined' 
                    ? I18N.t('sim.error_tabla_no_encontrada', 'No se encontró la tabla en la mezcla seleccionada')
                    : '❌ No se encontró el tbody en la mezcla seleccionada';
                notify('error', 'Error', msg);
                console.error(msg);
                // Cerrar modal de agregados automáticamente cuando hay error en tabla
                if (typeof cerrarModalAgregados === 'function') {
                    setTimeout(() => cerrarModalAgregados(), 2000);
                }
                return;
            }
            tbody.innerHTML = "";

            tamices.forEach(t => {
                const fila = document.createElement("tr");
                const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
                fila.innerHTML = `
                    <td contenteditable="true">${t.tamiz}</td>
                    <td contenteditable="true">${isNaN(t.porcentaje) ? "" : t.porcentaje}</td>
                    <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
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
            const msg = typeof I18N !== 'undefined' 
                ? I18N.t('sim.error_conexion_agregado', 'Error al conectar con el servidor')
                : '❌ Error al obtener curva del agregado';
            notify('error', 'Error', `${msg}: ${err}`);
            console.error("❌ Error al obtener curva del agregado:", err);
            // Cerrar modal de agregados automáticamente cuando hay error de conexión
            if (typeof cerrarModalAgregados === 'function') {
                setTimeout(() => cerrarModalAgregados(), 2000);
            }
        });
}

// Función fallback para notificaciones (en caso de que notify no esté global)
function notify(type, title, text) {
    if (window.Swal && typeof Swal.fire === 'function') {
        Swal.fire(title || '', text || '', type || 'info');
    } else {
        alert(`${title ? title + ': ' : ''}${text || ''}`);
    }
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

            const nuevoProductoLabel = typeof I18N !== 'undefined' ? I18N.t('sim.nuevo_producto') : 'Nuevo Producto';

            mezclaEl.innerHTML = `
                <div class="contenedor-producto">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Aggregato</h3>
                        <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Rimuovere il aggregato</button>
                    </div>
                    <h3>${nuevoProductoLabel}</h3>
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
        if (!tbody) {
            console.warn(`⚠️ No tiene tbody mezcla ${tab.mezclaId}, salto`);
            return; // salir del forEach, NO de la función
        }
        tbody.innerHTML = "";

        (tab.filas || []).forEach(f => {
            const fila = document.createElement("tr");
            const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
            fila.innerHTML = `
                <td contenteditable="true">${f.tamiz || ""}</td>
                <td contenteditable="true">${f.porcentaje || ""}</td>
                <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
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
