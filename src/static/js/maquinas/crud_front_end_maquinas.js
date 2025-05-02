let maquinaSeleccionada = null; // Global temporal
let maquinaAEliminar = null;
// MODAL AGREGAR
document.querySelector('.btn-agregar').onclick = function() {
    document.getElementById('modal-agregar').style.display = "block";
    abrirModalAgregarMaquinas();
};
document.querySelector('.close').onclick = function() {
    document.getElementById('modal-agregar').style.display = "none";
};

// MODAL ELIMINAR
document.querySelector('.btn-eliminar').onclick = function() {
    document.getElementById('modal-eliminar').style.display = "block";
};
document.querySelector('.close-eliminar').onclick = function() {
    maquinaAEliminar = null;
    document.getElementById('modal-eliminar').style.display = "none";
};
document.getElementById("confirmar-eliminar").addEventListener("click", () => {
    const id = document.getElementById("maquina-id-eliminar").value;

    console.log("🧪 ID de máquina a eliminar:", id);  // 👈 LOG DE VERIFICACIÓN

    fetch(`/maquinas_crud/eliminar/${id}`, {
        method: "DELETE"
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            alert("🗑️ Máquina eliminada correctamente");
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





function abrirModalAgregarMaquinas() {
    const user_id = localStorage.getItem("user_id");

    fetch("/maquinas_online/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id })
    })
    .then(res => res.json())
    .then(data => {
        const modal = document.getElementById('modal-agregar');
        if (data.success) {
            let html = `
                <div class="modal-content">
                    <span class="close" onclick="document.getElementById('modal-agregar').style.display='none'">&times;</span>
                    <h2>Macchine disponibili</h2>
                    <ul id="lista-maquinas">
            `;

            data.maquinas.forEach(maquina => {
                html += `<li class="item-maquina" data-id="${maquina.id}" data-nombre="${maquina.nombre}" style="cursor:pointer;">${maquina.nombre}</li>`;
            });

            html += `
                </ul>
                <input type="hidden" id="maquina-id-eliminar"> <!-- 👈 aquí -->
                <hr>
                <button id="confirmar-agregar">Agregar</button>
            </div>
            `;


            modal.innerHTML = html;
            modal.style.display = "block";

            // Agregar eventos
            const items = modal.querySelectorAll('.item-maquina');
            items.forEach(li => {
                li.addEventListener('click', () => {
                    items.forEach(el => el.style.color = 'black'); // Limpiar selección visual
                    li.style.color = 'red'; // Pintar la seleccionada
            
                    const idSeleccionado = li.dataset.id;
                    const maquina = data.maquinas.find(m => m.id.toString() === idSeleccionado);
            
                    if (maquina) {
                        maquinaSeleccionada = {
                            id: maquina.id,
                            nombre: maquina.nombre,
                            modulos: maquina.modulos || []
                        };
            
                        // 👇 Setear en el input hidden
                        const input = document.getElementById("maquina-id-eliminar");
                        if (input) input.value = idSeleccionado;
                    }
                });
            });
            
            // Acción al confirmar
            document.getElementById('confirmar-agregar').onclick = () => {
                if (maquinaSeleccionada) {
                    agregarMaquinaAlContenedor(maquinaSeleccionada); // 👇 Función para agregar
                    modal.style.display = "none";
                } else {
                    alert("⚠️ Selecciona una máquina primero.");
                }
            };
        }
    });
}


function agregarMaquinaAlContenedor(maquina) {
    const container = document.getElementById("contenedor-online");

    // ⚠️ Verificar si ya existe
    const yaExiste = container.querySelector(`summary[data-id="${maquina.id}"]`);
    if (yaExiste) {
        alert(`⚠️ La máquina "${maquina.nombre}" ya está en la lista.`);
        return;
    }

    const detalles = document.createElement("details");
    const summary = document.createElement("summary");
    summary.setAttribute("data-nombre", maquina.nombre);
    summary.setAttribute("data-id", maquina.id);
    summary.style.cursor = "pointer";
    summary.addEventListener("dblclick", function () {
        maquinaAEliminar = summary.closest("details");
        document.getElementById('modal-eliminar').style.display = "block";
    });
    summary.innerHTML = `
        ${maquina.nombre}
        <i class="fas fa-cog icono-clic" onclick="enviarNombrePorAjax(this, event)"></i>
    `;

    detalles.appendChild(summary);
    const ul = document.createElement("ul");

    if (maquina.modulos && maquina.modulos.length > 0) {
        maquina.modulos.forEach(modulo => {
            const li = document.createElement("li");
            li.textContent = modulo.charAt(0).toUpperCase() + modulo.slice(1);
            li.style.cursor = "pointer";
            li.addEventListener("click", () => {
                console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                cargarContenidoModulo(maquina.nombre, modulo);
            });
            ul.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.innerHTML = "<em>Sin módulos aún</em>";
        ul.appendChild(li);
    }

    detalles.appendChild(ul);
    container.appendChild(detalles);
}




function abrirModalEliminarMaquina(summaryElement) {
    maquinaAEliminar = summaryElement.closest("details"); // Guarda el bloque completo
    document.getElementById('modal-eliminar').style.display = "block";
}