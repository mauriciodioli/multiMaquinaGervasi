//inicializacion de variables localStorage
if (!localStorage.getItem("user_id")) {
    localStorage.setItem("user_id", "1");
 }
if (!localStorage.getItem("precio_kwh")) {
    localStorage.setItem("precio_kwh", "0.2");
 }




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
    
    const confirmacion = confirm('Sei sicuro di voler inviare i dati: ' + nombre_archivo + '?');
  
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
    
  
      fetch("http://localhost:5010/copiar_origen_destino/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: params.toString()
      })
      .then(response => {
         // console.log('📥 Respuesta cruda:', response);
         
          if (!response.ok) {
            return response.text().then(text => {
              throw new Error(text || `HTTP error! status: ${response.status}`);
            });
          }
          return response.json();
        })
        .then(data => {
        //  console.log('✅ Respuesta del servidor local:', data);
          //alert(data.mensaje || '✅ Archivo copiado correctamente.');
          alert(`✅ File copiato correttamente.`);
        })
        .catch(error => {
            console.error('❌ Error:', error); 
            let data = {};
            try {
              data = JSON.parse(error.message);
            } catch (e) {
              // No era JSON, lo dejamos vacío
            }

            if (data.ruta_existe === false) {
              alert("❌ La macchina è spenta.");
            } else {
              alert(`❌ Errore durante la copia del file: ${data.mensaje || error.message}`);
            }
        })
        .finally(() => {
          document.getElementById("spinner").style.display = "none"; // 👈 Ocultar spinner
        });

    } else {
      console.log('⛔ Envío cancelado por el usuario.');
      alert('Spedizione annullata.');
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
        container.innerHTML = ""; // Limpiar el contenedor antes de agregar las nuevas máquinas

        data.maquinas.forEach(maquina => {
            const detalles = document.createElement("details");
            const summary = document.createElement("summary");
            
            // Asignación de los atributos de la máquina
            summary.setAttribute("data-nombre", maquina.nombre);
            summary.setAttribute("data-id", maquina.id);
            summary.setAttribute("data-user_id", maquina.user_id);
            summary.setAttribute('data-ruta', maquina.ruta);
            summary.style.cursor = "pointer"; // Para que el nombre de la máquina sea clickeable
            summary.dataset.ruta = maquina.ruta;
            summary.dataset.nombre_db = maquina.nombreDb;
            summary.dataset.estado = maquina.estado;

            // Asignamos el contenido HTML dentro del summary
            summary.innerHTML = `${maquina.nombre} <i class="fas fa-cog icono-clic" onclick="Copiar_Origen_Destino_fuera_Data_Base(this, event)"></i>`;

            // Agregar el evento de clic al summary
            summary.addEventListener("click", function(event) {
                const clickedSummary = event.target;

                // Obtener los atributos del summary clickeado
                const dataId = clickedSummary.getAttribute('data-id');
                const dataNombre = clickedSummary.getAttribute('data-nombre');
                const dataUserId = clickedSummary.getAttribute('data-user_id');
                const dataRuta = clickedSummary.getAttribute('data-ruta');
                const dataNombreDb = clickedSummary.getAttribute('data-nombre_db');
                const dataEstado = clickedSummary.getAttribute('data-estado');
          
                // Log para verificar los datos obtenidos
                console.log('data-id:', dataId);
                console.log('data-nombre:', dataNombre);
                console.log('data-user_id:', dataUserId);
                console.log('data-ruta:', dataRuta);
                console.log('data-nombre_db:', dataNombreDb);
                console.log('data-estado:', dataEstado);
                // Al hacer clic en el <summary> (por ejemplo, en el evento 'dblclick' o 'click')
                localStorage.setItem("nombre_maquina", dataNombre);
                localStorage.setItem("id_maquina", dataId);
                localStorage.setItem("user_id", dataUserId);
                localStorage.setItem("ruta", dataRuta);
                localStorage.setItem("nombre_db", dataNombreDb);
                localStorage.setItem("estado", dataEstado);
            

            });

            detalles.appendChild(summary);

            const ul = document.createElement("ul");

            if (maquina.modulos && maquina.modulos.length > 0) {
                maquina.modulos.forEach(modulo => {
                    const li = document.createElement("li");
                    li.textContent = modulo.charAt(0).toUpperCase() + modulo.slice(1);
                    li.style.cursor = "pointer"; // Para cada subitem

                    // Evento click por módulo
                    li.addEventListener("click", () => {
                        console.log(`🔍 Click en ${modulo} de ${maquina.nombre}`);
                       // Cambiar el fondo del elemento clickeado
                       // Primero, eliminar la clase 'activo' de todos los elementos
                        document.querySelectorAll('.modulo').forEach(el => {
                            el.classList.remove('activo');
                        });

                        // Añadir la clase 'activo' al elemento clickeado
                        li.classList.add('activo');
                        // Lógica para manejar cada módulo
                        switch(modulo) {
                            case "history":
                                cargarContenidoModuloHistory(maquina.nombre, modulo, maquina.clfile);
                                break;
                            case "jobs":
                                cargarContenidoModuloJobs(maquina.nombre, modulo, maquina.clfile);
                                break;
                            case "lamiere":
                                let precioKwh = localStorage.getItem("precio_kwh");
                                cargarContenidoModuloLamiere(maquina.nombre, modulo, "", precioKwh, maquina.potencia);
                                break;
                            case "cost":
                                if (localStorage.getItem("precio_kwh")) {
                                    let precioKwh = localStorage.getItem("precio_kwh");
                                    cargarContenidoModuloCosto(maquina.nombre, modulo, "", precioKwh, maquina.potencia);
                                } else {
                                    alert("⚠️ Il prezzo del kWh non è ancora stato fissato.");
                                }
                                break;
                            case "settings":
                                // Aquí iría la lógica para settings
                                break;
                            case "statistics":
                                // Aquí iría la lógica para statistics
                                break;
                        }
                    });
              // Añadir la clase 'modulo' para poder seleccionarlo más tarde
                    li.classList.add('modulo');
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
        alert("⚠️ Errore nel caricamento delle macchine: " + data.message);
    }
})
.catch(err => {
    console.error("🔥 Error de red:", err);
});












function cargarContenidoModuloHistory(nombreMaquina, modulo, clfile, precioKwh, potencia) {
  debugger;
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
        "STZFileName": "📁 Archivio STZ",
        "CodMacchina": "Macchina", 
        "TempTotale": "⏱ Il tempo ha portato",
        "DataOraReg": "📅 Data e ora"
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
        "STZFileName": "📁 Archivio STZ",
        "TempTotale": "⏱ Tempo reale",
        "FileIcona": "🧩 Parte",
        "NumIconCLF": "🔢 Numero di pezzi",
        "TIconTaglio": "⏱ Tempo stimato",
        "Consumo_kWh": "⚡ kWh",
        "Costo_Euro": "💶 Costo (€)",
        "DataOraReg": "📅 Data"
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





























function cargarContenidoModuloCosto(nombreMaquina, modulo, clfile,precioKwh,potencia ) {
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


        const nombresColumnas = {
          "ID_CLF": "🔢 ID",
          "CLFileName": "📁 Archivio STZ",
          "CodMacchina": "🏭 Macchina",
          "TempTotale": "⏱ Tempo lavorato (s)",
          "DataOraReg": "📅 Data e ora",
          "Consumo_kWh": "⚡ kWh",
          "Costo_Euro": "💶 Costo (€)"
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
            let cellClass = "";
    
            if (col === "Costo_Euro") {
                const costo = parseFloat(fila[col]) || 0;
    
                if (costo > 2) cellClass = "costo-alto";
                else if (costo > 1) cellClass = "costo-medio";
                else cellClass = "costo-bajo";
            }
             let valor = fila[col];
            if (col === "DataOraReg" && valor) {
              valor = valor.split(".")[0]; // elimina .0000000
            }
          
            html += `<td class="${cellClass}">${valor}</td>`;
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
      alert(`✅ Nuovo prezzo applicato: €${precioKwh}/kWh`);
      cerrarModalCosto();
      // Si tenés una función para recargar datos con este valor, llamala acá.
  } else {
      alert("⚠️ Prezzo non valido.");
  }
}






