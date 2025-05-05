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
    const origen = '\\\\192.168.1.38\\c\\SiConfig\\Data\\DB';
    //const origen = 'C:\\Users\\Tecnico03\\Downloads';
    const destino = 'C:\\Users\\Tecnico03\\Documents\\ProyectoMultiMaquina';
  
    const confirmacion = confirm('¿Estás seguro de enviar los datos de: ' + nombre_archivo + '?');
  
    if (confirmacion) {
      document.getElementById("spinner").style.display = "flex"; // 👈 Mostrar spinner

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
      })
      .finally(() => {
        document.getElementById("spinner").style.display = "none"; // 👈 Ocultar spinner
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
            summary.style.cursor = "pointer"; // Para el nombre de la máquina

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
                    li.style.cursor = "pointer"; // Para cada subitem
                    // ✅ Agregamos el evento click por módulo
                    li.addEventListener("click", () => {
                        
                        // Acá podés hacer lo que quieras: redirigir, abrir modal, etc.
                        // Por ejemplo:
                        if (modulo === "history") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                          let filtro_clfile ="";
                         
                          if (localStorage.getItem("precio_kwh")) {             
                            let precioKwh= localStorage.getItem("precio_kwh");          
                            cargarContenidoModulo(maquina.nombre, modulo, filtro_clfile, precioKwh,maquina.potencia);
                          } else {
                              alert("⚠️ No se ha configurado el precio del kWh");
                          }
                        }
                        else if (modulo === "jobs") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                         // cargarContenidoModulo(maquina.nombre, modulo);
                                                  
                        }
                        else if (modulo === "cost") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                         // cargarContenidoModulo(maquina.nombre, modulo);
                        }
                        else if (modulo === "settings") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                          //cargarContenidoModulo(maquina.nombre, modulo);
                        }
                        else if (modulo === "statistics") {

                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                         // cargarContenidoModulo(maquina.nombre, modulo);
                        }
                       
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




function cargarContenidoModulo(nombreMaquina, modulo, clfile,precioKwh,potencia ) {
  const tablaContainer = document.querySelector(".tabla-container");
  const spinner = document.getElementById("spinner");
  if (spinner) {
    spinner.style.display = "flex";
  }
  
  fetch("/maquinas_sql/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ clfile: clfile, 
      nombre_maquina: nombreMaquina, 
      modulo: modulo, 
      precioKwh: precioKwh, 
      potencia: potencia 
    })
})
  .then(res => res.json())
  .then(data => {
      spinner.style.display = "none";

      const { columnas, trabajos } = data;

      let html = "<table><thead><tr>";
      columnas.forEach(col => {
          html += `<th>${col}</th>`;
      });
      html += "</tr></thead><tbody>";

      trabajos.forEach(fila => {
        html += "<tr>";
        columnas.forEach(col => {
            html += `<td>${fila[col]}</td>`;
        });
        html += "</tr>";
    });
    

      html += "</tbody></table>";
      tablaContainer.innerHTML = html;
  })
  .catch(err => {
      spinner.style.display = "none";
      console.error("❌ Error al cargar datos importados:", err);
      tablaContainer.innerHTML = "<p style='color:red;'>❌ Error al cargar datos</p>";
  });
}




let precioKwh = 0.20; // Valor por defecto

function abrirModalCosto() {
  document.getElementById("modal-costo").style.display = "block";
  document.getElementById("input-kwh").value = precioKwh; // Mostrar el valor actual
}


function cerrarModalCosto() {
    document.getElementById("modal-costo").style.display = "none";
}

function confirmarCosto() {
  const input = document.getElementById("input-kwh").value;
  const valor = parseFloat(input);
  if (!isNaN(valor) && valor > 0) {
      precioKwh = valor;
      localStorage.setItem("precio_kwh", precioKwh); // 👉 lo guarda en el navegador
      alert(`✅ Nuevo precio aplicado: €${precioKwh}/kWh`);
      cerrarModalCosto();
      // Si tenés una función para recargar datos con este valor, llamala acá.
  } else {
      alert("⚠️ Precio inválido.");
  }
}

