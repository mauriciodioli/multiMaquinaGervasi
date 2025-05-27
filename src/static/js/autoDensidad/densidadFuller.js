
  document.getElementById("selector-norma").addEventListener("change", () => {
    const seleccion = document.getElementById("selector-norma").value;
    const fullerDiv = document.getElementById("configuracion-fuller");
    fullerDiv.style.display = seleccion === "personalizado" ? "block" : "none";
  });

  document.getElementById("guardar-configuracion").addEventListener("click", () => {
    const norma = document.getElementById("selector-norma").value;
    localStorage.setItem("perfil_norma", norma);

     if (norma === "personalizado") {
    const d_max = parseFloat(document.getElementById("input-dmax").value);
    const n = parseFloat(document.getElementById("input-n").value);

    // Setear parámetros base de Fuller
    localStorage.setItem("d_max", d_max);
    localStorage.setItem("n", n);

    // 🔽 Agregá límites personalizados si vas a manejarlos
    const limites_personalizados = {
      grueso: {
        umbral_min: 4.75,
        limites: { ok: 40 }
      },
      medio: {
        umbral_min: 0.6,
        umbral_max: 4.75,
        limites: {
          exceso_grave: 70,
          limite_superior: 50,
          ok: 0
        }
      },
      fino: {
        umbral_max: 0.6,
        limites: {
          exceso_grave: 60,
          exceso: 40,
          ok: 0
        }
      }
    };
    localStorage.setItem("parametros_personalizados", JSON.stringify(limites_personalizados));
  }
    alert("✅ Configuración guardada correctamente.");
    
    document.getElementById('modal-configuracion').style.display = "none";
  });




function modalConfiguracionParametrosEntradaFuller() {
  // Mostrar el modal de configuración
    document.getElementById('modal-configuracion').style.display = "block";
};



document.addEventListener("DOMContentLoaded", () => {
  inicializarConfiguracionFuller();

});


function inicializarConfiguracionFuller() {
  if (!localStorage.getItem("perfil_norma")) {
    localStorage.setItem("perfil_norma", "hormigon_argentino");
  }
  if (!localStorage.getItem("d_max")) {
    localStorage.setItem("d_max", "25");
  }
  if (!localStorage.getItem("n")) {
    localStorage.setItem("n", "0.5");
  }

  // Si tenés campos en un modal, actualizalos también visualmente
  const selectorNorma = document.getElementById("selector-norma");
  const inputDmax = document.getElementById("input-dmax");
  const inputN = document.getElementById("input-n");

  if (selectorNorma) {
    selectorNorma.value = localStorage.getItem("perfil_norma");
  }
  if (inputDmax) {
    inputDmax.value = localStorage.getItem("d_max");
  }
  if (inputN) {
    inputN.value = localStorage.getItem("n");
  }
}


















document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("selector-norma");

  // Cargar si ya estaba guardado
  const guardado = localStorage.getItem("perfil_norma");
  if (guardado) {
    selector.value = guardado;
  }

  // Escuchar cambios y guardar
  selector.addEventListener("change", () => {
    const valor = selector.value;
    localStorage.setItem("perfil_norma", valor);
    console.log(`🔧 Perfil de norma seleccionado: ${valor}`);
  });
});





//*********************************************************************/
// Función para calcular la densidad de Fuller simple****************/
//*********************************************************************/
 
 
 function agregarFila() {
      const tamiz = parseFloat(document.getElementById("tamiz").value);
      const porcentaje = parseFloat(document.getElementById("porcentaje").value);

      if (isNaN(tamiz) || isNaN(porcentaje)) {
        alert("Completa ambos campos con números válidos.");
        return;
      }

      const tabla = document.getElementById("tabla").getElementsByTagName('tbody')[0];
      const fila = tabla.insertRow();
      fila.innerHTML = `
        <td contenteditable="true">${tamiz}</td>
        <td contenteditable="true">${porcentaje}</td>
        <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminare</button></td>
        `;



      document.getElementById("tamiz").value = '';
      document.getElementById("porcentaje").value = '';
    }

function enviarDatos() {
    const d_max = parseFloat(document.getElementById("dmax").value);
    const n = parseFloat(document.getElementById("n").value);

    const filas = document.querySelectorAll("#tabla tbody tr");
    const tamices = [];
    const porcentajes = [];

    filas.forEach(fila => {
    const celdas = fila.getElementsByTagName("td");
    tamices.push(parseFloat(celdas[0].textContent));
    porcentajes.push(parseFloat(celdas[1].textContent));
    });

    const payload = {
    d_max: d_max,
    n: n,
    tamices: tamices,
    porcentajes_reales: porcentajes
    };

    fetch("/densidadFuller/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      debugger;
    document.getElementById("resultado").innerHTML = `
        <h3>Risultato</h3>
        <img src="${data.grafico}" alt="Grafico della curva di Fuller">
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;

    })
    .catch(err => {
    console.error("Error:", err);
    alert("Hubo un error al procesar los datos.");
    });
}







//*********************************************************************/
// Función para calcular la densidad de Fuller multiple****************/
//*********************************************************************/
let mezclaId = 0;
function agregarMezcla() {
    const container = document.getElementById("mezclasContainer");

    const mezclaDiv = document.createElement("div");
    mezclaDiv.className = "mezcla";
    mezclaDiv.dataset.id = mezclaId++;

    const tamices = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15];

    const filasHTML = tamices.map(t => `
        <tr>
            <td contenteditable="true">${t}</td>
            <td contenteditable="true"></td>
            <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
        </tr>
    `).join("");

    mezclaDiv.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3>Producto</h3>
          <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Eliminar mezcla</button>
        </div>
        <input type="text" placeholder="Nombre del producto" class="nombreProducto">
        <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Agregar Fila</button>
        <table class="tabla">
            <thead>
                <tr><th>Tamiz </th><th>% Real</th><th>Acción</th></tr>
            </thead>
            <tbody>
                ${filasHTML}
            </tbody>
        </table>
        <hr>
    `;

    container.appendChild(mezclaDiv);
}
function eliminarMezcla(boton) {
    const mezclaDiv = boton.closest('.mezcla');
    mezclaDiv.remove();
}






function agregarFilaMultiple(btn) {
    const tbody = btn.nextElementSibling.querySelector("tbody");
    const fila = document.createElement("tr");

    fila.innerHTML = `
        <td contenteditable="true">0</td>
        <td contenteditable="true">0</td>
        <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
    `;
    tbody.appendChild(fila);
}



let curvas = []; // guardar aquí
let pesos = [];
let nombreProductos = [];
let tamices = [];
function calcularTodas() { 
    const mezclasDivs = document.querySelectorAll(".mezcla");
    const payload = [];

    let dMaxFinal = null;

    mezclasDivs.forEach(mezcla => {
        const nombre = mezcla.querySelector(".nombreProducto").value || "Sin nombre";
        const filas = mezcla.querySelectorAll("tbody tr");

        const tamices = [];
        const porcentajes = [];

        for (let fila of filas) {
            const celdas = fila.querySelectorAll("td");
            const tamiz = parseFloat(celdas[0].textContent);
            const porcentaje = parseFloat(celdas[1].textContent);

            if (!isNaN(tamiz) && !isNaN(porcentaje)) {
                tamices.push(tamiz);
                porcentajes.push(porcentaje);

                // Buscar primer tamiz con < 100% pasante → posible d_max
                if (porcentaje < 100 && (dMaxFinal === null || tamiz > dMaxFinal)) {
                    dMaxFinal = tamiz;
                }
            }
        }

        if (tamices.length > 0 && porcentajes.length > 0) {
            payload.push({
                nombre: nombre,
                tamices: tamices,
                porcentajes_reales: porcentajes
            });
        }
    });

    if (payload.length === 0) {
        alert("Debe ingresar al menos una mezcla con datos válidos (tamiz y % real).");
        return;
    }

    // Guardar d_max calculado si corresponde
    if (dMaxFinal !== null) {
        localStorage.setItem("d_max", dMaxFinal.toFixed(2));
        console.log("✅ d_max calculado automáticamente:", dMaxFinal.toFixed(2));
    } else {
        console.warn("⚠️ No se detectó retención en ningún tamiz. Se usará el valor por defecto (25 mm)");
    }

    const perfil_norma = localStorage.getItem("perfil_norma") || "hormigon_argentino";
    const d_max = parseFloat(localStorage.getItem("d_max")) || 25;
    const n = parseFloat(localStorage.getItem("n")) || 0.5;

    let parametros_personalizados = null;
    if (perfil_norma === "personalizado") {
        parametros_personalizados = JSON.parse(localStorage.getItem("parametros_personalizados")) || {};
    }

    // 🔽 Enviar al backend
    fetch("/densidadFullerMultiple/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            mezclas: payload,
            d_max: d_max,
            n: n,
            perfil: perfil_norma,
            parametros_personalizados: parametros_personalizados
        })
    })
    .then(res => res.json())
          .then(data => {
             debugger;
             curvas = data.resultados.map(r => r.reales); 
             pesos = data.resultados.map(r => r.proporcion_optima);
             nombreProductos = data.resultados.map(r => r.nombre);
             tamices = data.tamices_res;
             console.log(data);
            
            const resumenProporciones = generarResumenProporciones(data.mezcla_optima.pesos, data.resultados);
            const resultadosDiv = document.getElementById("resultados");
            let finalHTML = "<h2>Resultados</h2>";
            data.resultados.forEach(resultado => {
                finalHTML += `
                    <h4>${resultado.nombre}</h4>
                    <img src="${resultado.grafico}" alt="Curva de ${resultado.nombre}">
                    <pre>${JSON.stringify(resultado, null, 2)}</pre>
                    <hr>
                `;
            });

            const r = data.curva_resultante;

            if (!r || !r.tamices || !r.promedios) {
                resultadosDiv.innerHTML += "<p style='color:red;'>❌ No se pudo generar el análisis final.</p>";
                return;
            }

            window.ultimaCurvaPromedio = {
                                          ...r,
                                          mezcla_optima: data.mezcla_optima,
                                          resultados: data.resultados
                                        };


            let diagnosticoHTML = `
                            <div style="padding: 16px; background-color: #e6f4ea; border-left: 6px solid #2e7d32; margin-top: 1rem;">
                                <h3>🧾 Diagnóstico general</h3>
                                <ul>
                                    <li><strong>Evaluación:</strong> ${r.evaluacion}</li>
                                    <li><strong>Error promedio:</strong> ${r.error_promedio.toFixed(2)}%</li>
                                    <li><strong>Recomendaciones clave:</strong>
                                        <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>
                                    </li>
                                </ul>
                                ${resumenProporciones}
                                <li>✅ Se generó una mezcla corregida y una mezcla óptima automáticamente.</li>
                                <li>📄 Puedes exportar este informe como CSV.</li>
                                <details style="margin-top: 1rem;">
                                <summary style="cursor:pointer; color:#0d47a1; font-weight:bold;">📊 Ver gráfico de proporciones óptimas</summary>
                                <canvas id="graficoProporciones" width="400" height="250" style="margin-top: 1rem;"></canvas>
                                                      <div id="bloqueOptimo"></div>
                              </details>
                            </div>
                        `;

              // Cargar HTML inicial
            document.getElementById("diagnosticoModal").innerHTML = diagnosticoHTML;

            calcularMezclaOptima().then(mezcla => {
                const pesos = mezcla.proporciones;
                const nombres = mezcla.nombres_mezclas || [];

                diagnosticoHTML += `
                <details style="margin-top: 1rem;">
                      <summary style="cursor: pointer; color:#0d47a1; font-weight: bold; font-size: 1.1rem;">
                        🧠 Ver detalles de mezcla óptima calculada
                      </summary>
                        <div style="margin-top: 2rem; padding: 16px; background-color: #e3f2fd; border-left: 6px solid #1976d2; border-radius: 8px;">
                                  <h3 style="color: #0d47a1;">🧠 Mezcla Óptima Calculada</h3>

                                  <p><strong>📉 Error promedio:</strong> <span style="color:#d32f2f;">${mezcla.error_promedio.toFixed(2)}%</span></p>

                                  <p><strong>📊 Interpretación de proporciones:</strong></p>
                                  <ul style="padding-left: 1.2rem;">
                                    ${
                                      pesos.map((p, i) => {
                                        const nombre = nombres[i] || `Mezcla ${i + 1}`;
                                        let explicacion = '';
                                        if (p === 0) {
                                          explicacion = ' (❌ descartada por no aportar mejora)';
                                        } else if (p < 20) {
                                          explicacion = ' (🔧 aporte menor, ajuste fino)';
                                        } else if (p >= 20 && p <= 50) {
                                          explicacion = ' (⚖️ contribución equilibrada)';
                                        } else {
                                          explicacion = ' (💪 componente principal)';
                                        }
                                        return `<li><strong>${nombre}</strong>: ${p.toFixed(2)}% ${explicacion}</li>`;
                                      }).join("")
                                    }
                                  </ul>

                                  <details style="margin-top: 1rem;">
                                    <summary style="cursor:pointer; color:#1976d2;">📄 Ver detalles técnicos</summary>
                                    <pre style="background:#f1f1f1; padding:10px; border-radius:5px;">${JSON.stringify({
                                      tamices: mezcla.tamices,
                                      curva_optima: mezcla.curva_optima
                                    }, null, 2)}</pre>
                                  </details>
                                </div>
                    
                    </details>
                    
                `;

                document.getElementById("diagnosticoModal").innerHTML = diagnosticoHTML;
                setTimeout(() => {
                    generarGraficoProporciones(mezcla.proporciones, mezcla.nombres_mezclas);
                }, 0);

                abrirModalExportar();
            });



            
            
            
            finalHTML += `
                <h2 style="color: #b30000;">🔎 Análisis final: Curva promedio del conjunto</h2>

                <div style="border: 2px solid #b30000; padding: 16px; border-radius: 10px; background-color: #fff4f4;">
                    <img src="${r.grafico}" alt="Curva Promedio" style="max-width: 100%; margin-bottom: 12px;">
                    <p><strong>Evaluación general:</strong> <span style="color: #000;">${r.evaluacion}</span> 
                    <em>(Error promedio: ${r.error_promedio.toFixed(2)}%)</em></p>

                    <p><strong>Recomendaciones automáticas:</strong></p>
                    <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>
                    ${resumenProporciones}
                    <p><strong>Datos base:</strong></p>
                    <pre>${JSON.stringify({ tamices: r.tamices, promedios: r.promedios }, null, 2)}</pre>
                  
                </div>

                <div id="accionesFinales" style="margin-top: 2rem;">
                    <h3>📌 Acciones</h3>
                    <button class="btn btn-primary" onclick="generarMezclaCorregida()">Generar mezcla corregida</button>
                    <button class="btn btn-primary" onclick="abrirModalExportar()">Mostrar resumen</button>
                    <button class="btn btn-secondary" onclick="exportarCSV()">Exportar a CSV</button>
                </div>
            `;
          
            resultadosDiv.innerHTML = finalHTML;
        });

}



function generarResumenProporciones(pesos, resultados) {
    if (!pesos || !Array.isArray(pesos)) return "<p><em>No hay proporciones óptimas para mostrar.</em></p>";

    let html = "<p><strong>📊 Interpretación de las proporciones óptimas:</strong></p><ul>";

    pesos.forEach((peso, i) => {
        const nombre = resultados[i]?.nombre;

        if (!nombre) return; // 🛑 si no hay nombre, no mostrar nada

        let comentario = "";
        if (peso < 1) comentario = "❌ descartada por no aportar mejora";
        else if (peso < 10) comentario = "🔧 aporte menor, ajuste fino";
        else if (peso > 50) comentario = "💪 componente principal";
        else comentario = "⚖️ contribución equilibrada";

        html += `<li>${nombre}: ${peso.toFixed(2)}% (${comentario})</li>`;
    });

    html += "</ul>";
    return html;
}






function generarGraficoProporciones(pesos, nombres) {
    console.log("📊 Datos para graficar proporciones:");
    nombres.forEach((nombre, i) => {
        console.log(`${nombre}: ${pesos[i].toFixed(2)}%`);
    });

    const ctx = document.getElementById("graficoProporciones").getContext("2d");

    const comentarios = pesos.map(p => {
        if (p < 1) return "❌ Descartada";
        if (p < 10) return "🔧 Ajuste fino";
        if (p > 50) return "💪 Principal";
        return "⚖️ Equilibrada";
    });

    const colores = pesos.map(p => {
        if (p < 1) return "#ccc";
        if (p < 10) return "#f4c542";
        if (p > 50) return "#28a745";
        return "#007bff";
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: nombres,
            datasets: [{
                label: "% proporción óptima",
                data: pesos,
                backgroundColor: colores
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const i = ctx.dataIndex;
                            return `${pesos[i].toFixed(2)}% - ${comentarios[i]}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: "% proporción óptima"
                    }
                }
            }
        }
    });
}













function generarMezclaCorregida() {
    fetch('/calcularCurvaCorregida/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            curvas: curvas,
            pesos: pesos,
            nombreProductos: nombreProductos,
            tamices: tamices
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.grafico_base64) {
              const contenedor = document.getElementById("contenedorGraficoCurva");
              
              // Insertar imagen y tabla vacía
              contenedor.innerHTML = `
                 <img src="${data.grafico_base64}" style="max-width:100%; height:auto; margin-bottom: 15px;">
                   <h6>⚖️ Pesos proporcionales por zona y mezcla:</h6>
                  <table class="tabla-interpretacion">
                      <thead>
                          <tr>
                              <th>Mezcla</th>
                                <th>Gruesos (%)</th>
                                <th>Medios (%)</th>
                                <th>Finos (%)</th>
                              </tr>
                      </thead>
                      <tbody id="tablaInterpretacionCuerpo"></tbody>
                  </table>
              `;

              // Cargar datos en la tabla
              const cuerpo = document.getElementById("tablaInterpretacionCuerpo");
              Object.entries(data.pesos_por_zona).forEach(([mezcla, zonas]) => {
              const filaZona = `
                  <tr>
                      <td>${mezcla}</td>
                      <td>${zonas.gruesos?.toFixed(2) ?? "0.00"}</td>
                      <td>${zonas.medios?.toFixed(2) ?? "0.00"}</td>
                      <td>${zonas.finos?.toFixed(2) ?? "0.00"}</td>
                  </tr>
                  `;
                  cuerpo.innerHTML += filaZona;
              });

              // Insertar recomendaciones automáticas si hay
              if (data.acciones_recomendadas && data.acciones_recomendadas.length > 0) {
                 let tablaRecomendaciones = `
                                              <h6>🛠️ Automatic recommendations:</h6>
                                              <table class="tabla-interpretacion">
                                                <thead>
                                                  <tr>
                                                    <th>#</th>
                                                    <th>Recomendación</th>
                                                  </tr>
                                                </thead>
                                                <tbody>
                                            `;

                                            data.acciones_recomendadas.forEach((rec, index) => {
                                                tablaRecomendaciones += `
                                                  <tr>
                                                    <td>${index + 1}</td>
                                                    <td>${rec}</td>
                                                  </tr>
                                                `;
                                            });

                                            tablaRecomendaciones += `
                                                </tbody>
                                              </table>
                                            `;

                  contenedor.innerHTML += tablaRecomendaciones;

              }

          // Mostrar modal
          abrirModalGraficoCorreccion();


        } else if (data.error) {
            alert("Error: " + data.error);
        }
    })
    .catch(err => {
        console.error("Error al obtener curva corregida:", err);
    });
}











function abrirModalExportar() {   

    document.getElementById("modalExportar").style.display = "block";
}




function cerrarModalExportar() {
    document.getElementById("modalExportar").style.display = "none";
}








function exportarCSV() {
  const curva = window.ultimaCurvaPromedio;
  if (!curva || !curva.tamices || !curva.promedios) {
    alert("❌ No hay datos para exportar");
    return;
  }

  let csv = "Tamiz (mm);% Promedio;ASTM C136 o IRAM 1505\n";
  for (let i = 0; i < curva.tamices.length; i++) {
    csv += `${curva.tamices[i]};${curva.promedios[i]}%;${curva.clasificaciones[i]}\n`;
  }

  // Añadir encabezado para separarlo visualmente
  if (curva.mezcla_optima?.pesos && curva.resultados?.length) {
    csv += "\nProducto;Porcentaje;Comentario\n";

    for (let i = 0; i < curva.resultados.length; i++) {
      const peso = curva.mezcla_optima.pesos[i];
      const nombre = curva.resultados[i]?.nombre;
      if (!nombre) continue;

      let comentario = "";
      if (peso < 1) comentario = "descartada por no aportar mejora";
      else if (peso < 10) comentario = "aporte menor, ajuste fino";
      else if (peso > 50) comentario = "componente principal";
      else comentario = "contribucion equilibrada";

      csv += `${nombre};${peso.toFixed(2)}%;${comentario}\n`;
    }
  }

  //console.log("📤 CSV generado para exportar:\n", csv);

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "curva_promedio.csv";
  a.click();
}

















function calcularMezclaOptima() {
  return new Promise((resolve, reject) => {
    const mezclasDivs = document.querySelectorAll(".mezcla");
    const payload = [];

    mezclasDivs.forEach(mezcla => {
      const nombre = mezcla.querySelector(".nombreProducto").value || "Sin nombre";
      const filas = mezcla.querySelectorAll("tbody tr");

      const tamices = [];
      const porcentajes = [];

      filas.forEach(fila => {
        const celdas = fila.querySelectorAll("td");
        const tamiz = parseFloat(celdas[0].textContent);
        const porcentaje = parseFloat(celdas[1].textContent);

        if (!isNaN(tamiz) && !isNaN(porcentaje)) {
          tamices.push(tamiz);
          porcentajes.push(porcentaje);
        }
      });

      // Solo agregamos si tiene datos válidos
      if (tamices.length > 0 && porcentajes.length > 0) {
        payload.push({ nombre, tamices, porcentajes_reales: porcentajes });
      }
    });

    // Prevención si no hay mezclas válidas
    if (payload.length === 0) {
      alert("Debe agregar al menos una mezcla con datos válidos.");
      return reject("Sin mezclas válidas");
    }

    
    fetch("/densidadFullerOptimo/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mezclas: payload, d_max: 25, n: 0.5 })
    })
    .then(res => res.json())
    .then(data => {
      // Renderizar mezcla óptima
      const html = `
       
       
      `;

      const contenedor = document.getElementById("contenidoOptimo");
      contenedor.innerHTML = html;

      generarMezclaCorregida(); // Mostrar modal

      

      // Guardar en variable global
      const mezclaFinal = {
        error_promedio: data.error_promedio,
        proporciones: data.pesos,
        nombres_mezclas: data.nombres_mezclas,
        tamices: data.tamices,
        curva_optima: data.curva_optima,
        curva_ideal: data.curva_ideal
      };

      window.ultimaMezclaOptima = mezclaFinal;

      resolve(mezclaFinal); // Devuelve los datos
    })
    .catch(error => {
      console.error("Error al calcular mezcla óptima:", error);
      reject(error);
    });
  });
}
















function cargarDatosPorDefecto() {
  const mezclas = [
    {
      nombre: "Telares 2",
      tamices: [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074],
      porcentajes: [99.67,94.22,67.18,42.86,23.88,11.78,3.6,0.65]
    },
    {
      nombre: "Piedra Negra",
      tamices: [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074],
      porcentajes: [100,89.36,54,31.13,18.73,12.49,6.24,0.88]
    },
    {
      nombre: "Telares 1",
      tamices: [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15, 0.074],
      porcentajes: [100,98.76,67.02,41.33,24.62,14.58,6.31,1.6]
    }
  ];

  mezclas.forEach(m => {
    const container = document.getElementById("mezclasContainer");

    const mezclaDiv = document.createElement("div");
    mezclaDiv.className = "mezcla";

    mezclaDiv.innerHTML = `
     <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3>Producto</h3>
          <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Eliminar mezcla</button>
        </div>
      <h3>${m.nombre}</h3>
      <input type="text" value="${m.nombre}" class="nombreProducto">
      <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Agregar Fila</button>
      <table class="tabla">
        <thead>
          <tr><th>Tamiz</th><th>% Real</th><th>Acción</th></tr>
        </thead>
        <tbody>
          ${m.tamices.map((t, i) => `
            <tr>
              <td contenteditable="true">${t}</td>
              <td contenteditable="true">${m.porcentajes[i]}</td>
              <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">Eliminar</button></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
      <hr>
    `;

    container.appendChild(mezclaDiv);
  });
}



window.addEventListener("DOMContentLoaded", cargarDatosPorDefecto);
















document.addEventListener("keydown", function (e) {
    const isEnter = e.key === "Enter";
    const isTab = e.key === "Tab";

    const active = document.activeElement;
    if (!active || !active.isContentEditable) return;

    if (isEnter || isTab) {
      e.preventDefault();

      const editables = Array.from(document.querySelectorAll("td[contenteditable='true']"));
      const index = editables.indexOf(active);

      if (index !== -1) {
        let nextIndex;

        if (isTab) {
          nextIndex = index + 1;
        } else if (isEnter) {
          const currentCell = active;
          const currentRow = currentCell.parentElement;
          const colIndex = Array.from(currentRow.children).indexOf(currentCell);
          const nextRow = currentRow.nextElementSibling;

          if (nextRow) {
            const targetCell = nextRow.children[colIndex];
            if (targetCell && targetCell.isContentEditable) {
              // 👉 Selecciona todo el texto automáticamente
              setTimeout(() => {
                targetCell.focus();
                const range = document.createRange();
                range.selectNodeContents(targetCell);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
              }, 0);
              return;
            }
          }
          return;
        }

        // Enfocar la siguiente celda con Tab
        if (editables[nextIndex]) {
          editables[nextIndex].focus();
        }
      }
    }
  });

  // Si escribe en celda ya con valor, reemplazarlo todo
  document.addEventListener("beforeinput", function (e) {
    const el = document.activeElement;
    if (el && el.isContentEditable && window.getSelection().toString() === el.innerText) {
      // si el texto está todo seleccionado, se reemplaza directamente
      el.innerText = '';
    }
  });




















function abrirModalGraficoCorreccion() {
  document.getElementById('ModalGraficoCorreccion').style.display = "block";
}

function cerrarModalGraficoCorreccion() {
  
  document.getElementById('ModalGraficoCorreccion').style.display = "none";
}

// Opcional: cerrar con Escape
  document.addEventListener('keydown', function (event) {
    if (event.key === "Escape") cerrarModalGraficoCorreccion();
  });



