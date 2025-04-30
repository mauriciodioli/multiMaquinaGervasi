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

function enviarNombrePorAjax1(iconoClicado, event) {
  event.stopPropagation();

  const summaryElement = iconoClicado.parentNode;
  const nombreMaquina = summaryElement.getAttribute('data-nombre');
  const idMaquina = summaryElement.getAttribute('data-id');
  const userMaquina = summaryElement.getAttribute('data-user_id');

  const confirmacion = confirm('¿Estás seguro de enviar los datos de: ' + nombreMaquina + '?');

  if (confirmacion) {
      fetch('/copiar_origen_destino/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `nombre_maquina=${encodeURIComponent(nombreMaquina)}&id=${encodeURIComponent(idMaquina)}&user_id=${encodeURIComponent(userMaquina)}`
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





  function enviarNombrePorAjax(iconoClicado, event) {
    event.stopPropagation();
  
    const summaryElement = iconoClicado.parentNode;
    const nombre_archivo = 'si-cam';
    const idMaquina = summaryElement.getAttribute('data-id');
    const userMaquina = summaryElement.getAttribute('data-user_id');
    //\\192.168.1.38\\
    const origen = 'C:\\Users\\Tecnico03\\Downloads';
    const destino = 'C:\\Users\\Tecnico03\\Documents';
  
    const confirmacion = confirm('¿Estás seguro de enviar los datos de: ' + nombre_archivo + '?');
  
    if (confirmacion) {
      const params = new URLSearchParams();
      params.append('nombre_archivo', nombre_archivo);
      params.append('origen', origen);
      params.append('destino', destino);
  
      fetch("http://localhost:5001/copiar_origen_destino/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: params.toString()
      })
      .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
              throw new Error(text || `HTTP error! status: ${response.status}`);
            });
          }
          return response.json();
      })
      .then(data => {
        console.log('✅ Respuesta del servidor local:', data);
        alert(data.mensaje || '✅ Archivo copiado correctamente.');
      })
      .catch(error => {
        console.error('✅ Archivo copiado correctamente. capturado por catch en enviarNombrePorAjax ', error);
         alert('✅ Archivo copiado correctamente.');
      });
      
    } else {
      console.log('⛔ Envío cancelado por el usuario.');
      alert('Envío cancelado.');
    }
  }
  
  














  fetch("/maquinas_online/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ user_id: localStorage.getItem("user_id") })
})
.then(res => res.json())
.then(data => {
    if (data.success) {
        const container = document.getElementById("contenedor-online");
        container.innerHTML = ""; // Limpiar

        data.maquinas.forEach(maquina => {
            const detalles = document.createElement("details");
            const summary = document.createElement("summary");
            summary.setAttribute("data-nombre", maquina.nombre);
            summary.setAttribute("data-id", maquina.id);
            summary.setAttribute("data-user_id", maquina.user_id);
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

                    // ✅ Agregamos el evento click por módulo
                    li.addEventListener("click", () => {
                        console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                        // Acá podés hacer lo que quieras: redirigir, abrir modal, etc.
                        // Por ejemplo:
                        // cargarContenidoModulo(maquina.nombre, modulo);
                    });

                    ul.appendChild(li);
                });
            } else {
                const li = document.createElement("li");
                li.innerHTML = "<em>Sin módulos configurados</em>";
                ul.appendChild(li);
            }

            detalles.appendChild(ul);
            container.appendChild(detalles);
        });

    } else {
        alert("⚠️ Error cargando máquinas: " + data.message);
    }
})
.catch(err => {
    console.error("🔥 Error de red:", err);
});


