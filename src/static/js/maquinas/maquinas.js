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


function enviarNombrePorAjax(iconoClicado, event) {
    // Detiene la propagación del evento click
    event.stopPropagation();
  
    // Obtiene el elemento <summary> padre del icono
    const summaryElement = iconoClicado.parentNode;
    // Obtiene el valor del atributo data-nombre
    const nombreMaquina = summaryElement.getAttribute('data-nombre');
  
    // Muestra el cuadro de confirmación
    const confirmacion = confirm('¿Estás seguro de enviar los datos de: ' + nombreMaquina + '?');
  
    // Si el usuario hace clic en "Aceptar" (confirmación es true), realiza la llamada AJAX
    if (confirmacion) {
      fetch('/copiar_origen_destino/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `nombre_maquina=${encodeURIComponent(nombreMaquina)}`,
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text(); // O response.json()
      })
      .then(data => {
        console.log('Respuesta del servidor:', data);
        alert('Datos enviados correctamente.'); // Opcional: mostrar un mensaje de éxito
      })
      .catch(error => {
        console.error('Error al enviar la petición AJAX:', error);
        alert('Error al enviar los datos.'); // Opcional: mostrar un mensaje de error
      });
    } else {
      // Si el usuario hace clic en "Cancelar", no se realiza la llamada AJAX
      console.log('Envío cancelado por el usuario.');
      alert('Envío cancelado.'); // Opcional: mostrar un mensaje de cancelación
    }
  }