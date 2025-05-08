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
    
    nombreMaquina = localStorage.getItem("nombre_maquina");
    // Mostrar el nombre de la máquina en el modal
    if (nombreMaquina) {
        document.getElementById('modal-nombre-maquina').textContent = `${nombreMaquina}`;
    }
    document.getElementById('modal-eliminar').style.display = "block";
    // El modal de eliminar ya está abierto, la máquina seleccionada ya está guardada en maquinaAEliminar
   
};
document.querySelector('.close-eliminar').onclick = function() {
    maquinaAEliminar = null;
    document.getElementById('modal-eliminar').style.display = "none";
};






// Abrir modal para agregar máquinas
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

            // Agregar eventos a los elementos de la lista
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
            
                        // 👇 Setear el id en el input oculto
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

// Agregar máquina al contenedor
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






document.getElementById("confirmar-eliminar").addEventListener("click", () => {
    const dataId = localStorage.getItem("id_maquina");  // Obtiene el ID almacenado en localStorage

    // Log para verificar el data-id obtenido
    console.log("data-id de la máquina seleccionada:", dataId);

    if (dataId) {
        // Selecciona el contenedor que contiene los elementos 'details'
        const container = document.getElementById("contenedor-online");

        // Busca el elemento <details> con el data-id correspondiente
        const maquinaEliminada = container.querySelector(`details summary[data-id="${dataId}"]`);

        if (maquinaEliminada) {
            // Elimina el <details> completo que contiene ese <summary> con el data-id
            maquinaEliminada.closest('details').remove();

            console.log(`Elemento con data-id ${dataId} eliminado.`);
        } else {
            console.log(`No se encontró un elemento con data-id: ${dataId}`);
        }
    } else {
        console.log("No se encontró el data-id en localStorage");
    }

    // Cierra el modal después de la eliminación
    document.getElementById('modal-eliminar').style.display = "none"; // Cierra el modal
});



