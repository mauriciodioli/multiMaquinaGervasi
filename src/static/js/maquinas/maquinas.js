const resizer = document.getElementById('resizer');
const sidebar = document.getElementById('sidebar');
const container = document.querySelector('.contenedor-flex');

let isResizing = false;

// Cargar tamaño guardado al iniciar
window.addEventListener('load', () => {
    const savedWidth = localStorage.getItem('sidebarWidth');
    if (savedWidth) {
        sidebar.style.width = savedWidth + 'px';
    }
});

resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.body.style.cursor = 'ew-resize';
});

document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;

    let newWidth = e.clientX - container.offsetLeft;

    if (newWidth < 50) newWidth = 50; // Ahora permitimos hacerlo bien chico
    if (newWidth > 400) newWidth = 400;

    sidebar.style.width = newWidth + 'px';
});

document.addEventListener('mouseup', () => {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = 'default';
        localStorage.setItem('sidebarWidth', parseInt(sidebar.style.width)); // Guardamos
    }
});





// MODAL AGREGAR
document.querySelector('.btn-agregar').onclick = function() {
    document.getElementById('modal-agregar').style.display = "block";
};
document.querySelector('.close').onclick = function() {
    document.getElementById('modal-agregar').style.display = "none";
};

// MODAL ELIMINAR
document.querySelector('.btn-eliminar').onclick = function() {
    document.getElementById('modal-eliminar').style.display = "block";
};
document.querySelector('.close-eliminar').onclick = function() {
    document.getElementById('modal-eliminar').style.display = "none";
};

// MODAL MODIFICAR
document.querySelector('.btn-modificar').onclick = function() {
    document.getElementById('modal-modificar').style.display = "block";
};
document.querySelector('.close-modificar').onclick = function() {
    document.getElementById('modal-modificar').style.display = "none";
};

// Cerrar modales clickeando fuera del contenido
window.onclick = function(event) {
    const modals = ['modal-agregar', 'modal-eliminar', 'modal-modificar'];
    modals.forEach(function(id) {
        if (event.target == document.getElementById(id)) {
            document.getElementById(id).style.display = "none";
        }
    });
};