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

function enviarNombrePorAjax(iconoClicado, event) {
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



/*************************************************************************************************/
/*************************************************************************************************/
/****************copia las bases de datos desde las maquinas exteriores***************************/
/****************utiliza archivos .py externos al proyectos como servicio*************************/
/*************************************************************************************************/
/*************************************************************************************************/

  function Copiar_Origen_Destino_fuera_Data_Base(iconoClicado, event) {
    event.stopPropagation();
  
    const summaryElement = iconoClicado.parentNode;
    //const nombre_archivo = 'si-cam';
    const idMaquina = summaryElement.getAttribute('data-id');
    const userMaquina = summaryElement.getAttribute('data-user_id');
    const nombreMaquina = summaryElement.getAttribute('data-nombre');
   
    const origen = summaryElement.dataset.ruta;
    const nombre_archivo = summaryElement.dataset.nombre_db;
    const estado = summaryElement.dataset.estado;

    const match = origen.match(/^\\\\([^\\]+)/);
    const ip = localStorage.getItem('ipSqlServer'); // ✅ Esto debe ser la IP donde corre SQL Server
    const port = localStorage.getItem('portSqlServer'); // Cambia esto si es necesario
    const userSqlServer = localStorage.getItem('userSqlServer'); // Cambia esto si es necesario
    const passwordSqlServer = localStorage.getItem('pasSqlServer'); // Cambia esto si es necesario
    console.log(ip);  // 👉 "192.168.1.38".
    console.log(port); // 👉 "1433".
    const tablas = ["Lamiere_Tempi", "Lamiere_Icone"];
    //const origen = '\\\\192.168.1.38\\c\\SiConfig\\Data\\DB';
    //const origen = 'C:\\Users\\Tecnico03\\Downloads';
    const destino = 'C:\\Users\\Tecnico03\\Documents\\ProyectoMultiMaquina';
  
    const confirmacion = confirm('¿Estás seguro de enviar los datos de: ' + nombre_archivo + '?');
  
    if (confirmacion) {
      document.getElementById("spinner").style.display = "flex"; // 👈 Mostrar spinner

      const params = new URLSearchParams();
      params.append('nombreMaquina', nombreMaquina);
      params.append('nombre_archivo', nombre_archivo);
      params.append('origen', origen);
      params.append('destino', destino);
      params.append('estado', estado);
      params.append('ip',ip);
      params.append('port',port);
      params.append('userSqlServer',userSqlServer);
      params.append('passwordSqlServer',passwordSqlServer);
      params.append('tablas', JSON.stringify(tablas));
    
  
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
        console.error('✅ Archivo copiado correctamente. capturado por catch en Copiar_Origen_Destino_fuera_Data_Base ', error);
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
            summary.dataset.ruta = maquina.ruta;
            summary.dataset.nombre_db = maquina.nombreDb;
            summary.dataset.estado = maquina.estado;

            summary.innerHTML = `
                ${maquina.nombre}
             
                <i class="fas fa-cog icono-clic" onclick="Copiar_Origen_Destino_fuera_Data_Base(this, event)"></i>
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
                          cargarContenidoModuloHistory(maquina.nombre, modulo, maquina.clfile);
                        }
                        else if (modulo === "jobs") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                          cargarContenidoModuloJobs(maquina.nombre, modulo, maquina.clfile);
                                                  
                        }
                        else if (modulo === "lamiere") {
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                          let precioKwh= localStorage.getItem("precio_kwh"); 
                          let filtro_clfile ="";
                        
                          cargarContenidoModuloLamiere(maquina.nombre, modulo, filtro_clfile, precioKwh,maquina.potencia);
                                                  
                        }
                        else if (modulo === "cost") {
                       
                          console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                          let filtro_clfile ="";
                         
                          if (localStorage.getItem("precio_kwh")) {             
                              let precioKwh= localStorage.getItem("precio_kwh");          
                              cargarContenidoModulo(maquina.nombre, modulo, filtro_clfile, precioKwh,maquina.potencia);
                          } else {
                              alert("⚠️ No se ha configurado el precio del kWh");
                          }
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





function cargarContenidoModuloHistory(nombreMaquina, modulo, clfile, precioKwh, potencia) {
  const tablaContainer = document.querySelector(".tabla-container");
  const spinner = document.getElementById("spinner");
  const ip = localStorage.getItem("ipSqlServer"); // Cambia esto si es necesario
  const port = localStorage.getItem("portSqlServer"); // Cambia esto si es necesario
  const userSqlServer = localStorage.getItem("userSqlServer"); // Cambia esto si es necesario
  const passwordSqlServer = localStorage.getItem("pasSqlServer"); // Cambia esto si es necesario
  console.log(ip);  // 👉 "
  if (spinner) spinner.style.display = "flex";

  fetch("/maquinas_sql_histoy/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      clfile:clfile,
      ip:ip,
      port:port,
      user:userSqlServer,
      password:passwordSqlServer,
      nombre_maquina: nombreMaquina,
      modulo,
      precioKwh,
      potencia
    })
  })
    .then(res => res.json())
    .then(data => {
      if (spinner) spinner.style.display = "none";

      if (!data.success) {
        tablaContainer.innerHTML = `<p style='color:red;'>❌ Error: ${data.error || "no se pudo cargar el historial"}</p>`;
        return;
      }

      const { columnas, trabajos } = data;
      let html = "<table class='table table-bordered'><thead><tr>";

      columnas.forEach(col => {
        html += `<th>${col}</th>`;
      });

      html += "</tr></thead><tbody>";

      trabajos.forEach((fila, index) => {
        const rowClass = index % 2 === 0 ? "fila-par" : "fila-impar";
        html += `<tr class="${rowClass}">`;
      
        columnas.forEach(col => {
          const claseEspecial = col === "CLFileName" ? "no-resize" : "";
          let valor = fila[col];
            if (col === "DataOraReg" && valor) {
              valor = valor.split(".")[0]; // elimina .0000000
            }
            html += `<td class="${claseEspecial}">${valor}</td>`;

        });
        
      
        html += "</tr>";
      });
      

      html += "</tbody></table>";
      tablaContainer.innerHTML = html;
    })
    .catch(err => {
      if (spinner) spinner.style.display = "none";
      console.error("❌ Error al cargar datos importados:", err);
      tablaContainer.innerHTML = "<p style='color:red;'>❌ Error al cargar datos</p>";
    });
}



















function cargarContenidoModuloJobs(nombreMaquina, modulo, clfile, precioKwh, potencia) {
  const tablaContainer = document.querySelector(".tabla-container");
  const spinner = document.getElementById("spinner");
  const ip = localStorage.getItem("ipSqlServer"); // Cambia esto si es necesario
  const port = localStorage.getItem("portSqlServer"); // Cambia esto si es necesario
  const userSqlServer = localStorage.getItem("userSqlServer"); // Cambia esto si es necesario
  const passwordSqlServer = localStorage.getItem("pasSqlServer"); // Cambia esto si es necesario
  if (spinner) spinner.style.display = "flex";


  fetch("/resumen_trabajos/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      clfile:clfile,
      ip:ip,
      port:port,
      user:userSqlServer,
      password:passwordSqlServer,
      nombre_maquina: nombreMaquina,
      modulo,
      precioKwh,
      potencia
    })
  })
    .then(res => res.json())
    .then(data => {
      if (spinner) spinner.style.display = "none";

      if (!data.success) {
        tablaContainer.innerHTML = `<p style='color:red;'>❌ Error: ${data.error || "No se pudo cargar el resumen de trabajos"}</p>`;
        return;
      }

      const trabajos = data.resumen;
      if (trabajos.length === 0) {
        tablaContainer.innerHTML = "<p>No hay trabajos para mostrar.</p>";
        return;
      }

      const columnas = [
        "ID_CLF",        
        "STZFileName",
        "CodMacchina",
        "DataOraReg",
        "TempTotale"
      ];
      
      const nombresColumnas = {
        "ID_CLF": "🔢 ID",
        "STZFileName": "📁 Archivo STZ",
        "CodMacchina": "Macchina", 
        "TempTotale": "⏱ Tiempo trajado",
        "DataOraReg": "📅 Fecha y Hora"
      };

      let html = "<table class='table table-bordered'><thead><tr>";

      columnas.forEach(col => {
        html += `<th>${nombresColumnas[col] || col}</th>`;
      });


      html += "</tr></thead><tbody>";

      trabajos.forEach((fila, index) => {
        const rowClass = index % 2 === 0 ? "fila-par" : "fila-impar";
        html += `<tr class="${rowClass}">`;
      
        columnas.forEach(col => {
          const claseEspecial = col === "CLFileName" ? "no-resize" : "";
          let valor = fila[col];
            if (col === "DataOraReg" && valor) {
              valor = valor.split(".")[0]; // elimina .0000000
            }
            html += `<td class="${claseEspecial}">${valor}</td>`;

        });
        
      
        html += "</tr>";
      });
      

      html += "</tbody></table>";
      tablaContainer.innerHTML = html;
    })
    .catch(err => {
      if (spinner) spinner.style.display = "none";
      console.error("❌ Error al cargar datos:", err);
      tablaContainer.innerHTML = "<p style='color:red;'>❌ Error al cargar los trabajos</p>";
    });
}
















function cargarContenidoModuloLamiere(nombreMaquina, modulo, clfile, precioKwh, potencia) {
    
  const tablaContainer = document.querySelector(".tabla-container");
  const spinner = document.getElementById("spinner");
  const ip = localStorage.getItem("ipSqlServer"); // Cambia esto si es necesario
  const port = localStorage.getItem("portSqlServer"); // Cambia esto si es necesario
  const userSqlServer = localStorage.getItem("userSqlServer"); // Cambia esto si es necesario
  const passwordSqlServer = localStorage.getItem("pasSqlServer"); // Cambia esto si es necesario
  if (spinner) spinner.style.display = "flex";


  fetch("/resumen_lamiere/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      clfile:clfile,
      ip:ip,
      port:port,
      user:userSqlServer,
      password:passwordSqlServer,
      nombre_maquina: nombreMaquina,
      modulo,
      precioKwh,
      potencia
    })
  })
    .then(res => res.json())
    .then(data => {
      if (spinner) spinner.style.display = "none";

      if (!data.success) {
        tablaContainer.innerHTML = `<p style='color:red;'>❌ Error: ${data.error || "No se pudo cargar el resumen de trabajos"}</p>`;
        return;
      }

      const trabajos = data.resumen;
      if (trabajos.length === 0) {
        tablaContainer.innerHTML = "<p>No hay trabajos para mostrar.</p>";
        return;
      }

      const columnas = [
        "ID_CLF",
        "STZFileName",
        "TempTotale",  
        "FileIcona",
        "NumIconCLF",
        "TIconTaglio",
        "Consumo_kWh",
        "Costo_Euro",
        "DataOraReg"
      ];
      
      const nombresColumnas = {
        "ID_CLF": "🔢 ID",
        "STZFileName": "📁 Archivo STZ",
        "TempTotale": "⏱ Tiempo real",
        "FileIcona": "🧩 Pieza",
        "NumIconCLF": "🔢 Cant. piezas",
        "TIconTaglio": "⏱ Tiempo estimado",
        "Consumo_kWh": "⚡ kWh",
        "Costo_Euro": "💶 Costo (€)",
        "DataOraReg": "📅 Fecha"
      };

      let html = "<table class='table table-bordered'><thead><tr>";

      columnas.forEach(col => {
        html += `<th>${nombresColumnas[col] || col}</th>`;
      });

      html += "</tr></thead><tbody>";
      let ultimoID_CLF = null;
      trabajos.forEach((fila, index) => {
        const rowClass = index % 2 === 0 ? "fila-par" : "fila-impar";
        html += `<tr class="${rowClass}">`;
      
        columnas.forEach(col => {
          const claseEspecial = col === "CLFileName" ? "no-resize" : "";
      
          // 🔥 Comparar y colorear ID_CLF si es distinto al anterior
          if (col === "ID_CLF") {
            const estilo =
              fila[col] !== ultimoID_CLF
                ? "style='background-color: #ffeeba; font-weight: bold;'"
                : "";
            html += `<td ${estilo}>${fila[col]}</td>`;
            ultimoID_CLF = fila[col]; // Actualizar valor
          } else {
            let valor = fila[col];
            if (col === "DataOraReg" && valor) {
              valor = valor.split(".")[0]; // elimina .0000000
            }
            html += `<td class="${claseEspecial}">${valor}</td>`;
            
          }
        });
      
        html += "</tr>";
      });
      
      html += "</tbody></table>";
      tablaContainer.innerHTML = html;
    })
    .catch(err => {
      if (spinner) spinner.style.display = "none";
      console.error("❌ Error al cargar datos:", err);
      tablaContainer.innerHTML = "<p style='color:red;'>❌ Error al cargar los trabajos</p>";
    });
}





























function cargarContenidoModulo(nombreMaquina, modulo, clfile,precioKwh,potencia ) {
  const tablaContainer = document.querySelector(".tabla-container");
  const spinner = document.getElementById("spinner");
  const ip = localStorage.getItem("ipSqlServer"); // Cambia esto si es necesario
  const port = localStorage.getItem("portSqlServer"); // Cambia esto si es necesario
  const userSqlServer = localStorage.getItem("userSqlServer"); // Cambia esto si es necesario
  const passwordSqlServer = localStorage.getItem("pasSqlServer"); // Cambia esto si es necesario
  if (spinner) {
    spinner.style.display = "flex";
  }
  
  fetch("/maquinas_sql_cost/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
      clfile:clfile,
      ip:ip,
      port:port,
      user:userSqlServer,
      password:passwordSqlServer,
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

      trabajos.forEach((fila, index) => {
        const rowClass = index % 2 === 0 ? "fila-par" : "fila-impar";
        html += `<tr class="${rowClass}">`;
    
        columnas.forEach(col => {
            let cellClass = "";
    
            if (col === "Costo_Euro") {
                const costo = parseFloat(fila[col]) || 0;
    
                if (costo > 2) cellClass = "costo-alto";
                else if (costo > 1) cellClass = "costo-medio";
                else cellClass = "costo-bajo";
            }
    
            html += `<td class="${cellClass}">${fila[col]}</td>`;
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






