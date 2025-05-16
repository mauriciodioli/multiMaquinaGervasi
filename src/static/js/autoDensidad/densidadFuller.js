
  document.getElementById("selector-norma").addEventListener("change", () => {
    const seleccion = document.getElementById("selector-norma").value;
    const fullerDiv = document.getElementById("configuracion-fuller");
    fullerDiv.style.display = seleccion === "personalizado" ? "block" : "none";
  });

  document.getElementById("guardar-configuracion").addEventListener("click", () => {
    const norma = document.getElementById("selector-norma").value;
    localStorage.setItem("perfil_norma", norma);

    if (norma === "personalizado") {
      const dmax = parseFloat(document.getElementById("input-dmax").value);
      const n = parseFloat(document.getElementById("input-n").value);
      localStorage.setItem("d_max", dmax);
      localStorage.setItem("n", n);
    }

    alert("✅ Configuración guardada correctamente.");
    
    document.getElementById('modal-configuracion').style.display = "none";
  });




function modalConfiguracionParametrosEntradaFuller() {
    
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

    mezclaDiv.innerHTML = `
        <h3>Producto</h3>
        <input type="text" placeholder="Nombre del producto" class="nombreProducto">
        <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Agregar Fila</button>
        <table class="tabla">
            <thead>
                <tr><th>Tamiz (mm)</th><th>% Real</th><th>Acción</th></tr>
            </thead>
            <tbody></tbody>
        </table>
        <hr>
    `;

    container.appendChild(mezclaDiv);
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

function calcularTodas() {
    const mezclasDivs = document.querySelectorAll(".mezcla");
    const payload = [];

    mezclasDivs.forEach(mezcla => {
        const nombre = mezcla.querySelector(".nombreProducto").value || "Sin nombre";
        const filas = mezcla.querySelectorAll("tbody tr");

        const tamices = [];
        const porcentajes = [];

        filas.forEach(fila => {
            const celdas = fila.querySelectorAll("td");
            tamices.push(parseFloat(celdas[0].textContent));
            porcentajes.push(parseFloat(celdas[1].textContent));
        });

        payload.push({
            nombre: nombre,
            tamices: tamices,
            porcentajes_reales: porcentajes
        });
    });
    const perfil_norma = localStorage.getItem("perfil_norma") || "hormigon_argentino";
    const d_max = parseFloat(localStorage.getItem("d_max")) || 25;
    const n = parseFloat(localStorage.getItem("n")) || 0.5;
    // 🔽 Enviar al backend
    fetch("/densidadFullerMultiple/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            mezclas: payload,
            d_max: d_max,
            n: n,
            perfil:perfil_norma
            
        })
    })
    .then(res => res.json())
    .then(data => {
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

       // Bloque final con curva promedio
            const r = data.curva_resultante;
           

            if (!r || !r.tamices || !r.promedios) {
            resultadosDiv.innerHTML += "<p style='color:red;'>❌ No se pudo generar el análisis final.</p>";
            return;
            }            
            window.ultimaCurvaPromedio = r;
            
            //generarMezclaCorregida(); //sirvqa para calcular la mezcla optima
           
            
            
            setTimeout(() =>   calcularMezclaOptima(), 100);

           
            setTimeout(() => abrirModalExportar(), 100);

            finalHTML += `
                <h2 style="color: #b30000;">🔎 Análisis final: Curva promedio del conjunto</h2>

                <div style="border: 2px solid #b30000; padding: 16px; border-radius: 10px; background-color: #fff4f4;">
                    <img src="${r.grafico}" alt="Curva Promedio" style="max-width: 100%; margin-bottom: 12px;">
                    <p><strong>Evaluación general:</strong> <span style="color: #000;">${r.evaluacion}</span> 
                    <em>(Error promedio: ${r.error_promedio.toFixed(2)}%)</em></p>

                    <p><strong>Recomendaciones automáticas:</strong></p>
                    <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>

                    <p><strong>Datos base:</strong></p>
                    <pre>${JSON.stringify({ tamices: r.tamices, promedios: r.promedios }, null, 2)}</pre>
                </div>

                <div id="accionesFinales" style="margin-top: 2rem;">
                    <h3>📌 Acciones</h3>
                    <button class="btn btn-primary" onclick="generarMezclaCorregida()">Generar mezcla corregida</button>
                    <button class="btn btn-primary" onclick="abrirModalExportar()">Mostrar resumen</button>
                    <button class="btn btn-primary" onclick="abrirModalOptimo()">Calculo Optimo</button>
                     <button class="btn btn-secondary" onclick="exportarCSV()">Exportar a CSV</button>
                    </div>
            `;
                // Diagnóstico para el modal
                
                    let diagnosticoHTML = `
                    <div style="padding: 16px; background-color: #e6f4ea; border-left: 6px solid #2e7d32; margin-top: 1rem;">
                        <h3>🧾 Diagnóstico general</h3>
                        <ul>
                        <li><strong>Evaluación:</strong> ${r.evaluacion}</li>
                        <li><strong>Error promedio:</strong> ${r.error_promedio.toFixed(2)}%</li>
                        <li><strong>Recomendaciones clave:</strong>
                            <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>
                        </li>
                        <li>✅ Se generó una mezcla corregida y una mezcla óptima automáticamente.</li>
                        <li>📄 Puedes exportar este informe como CSV.</li>
                        </ul>
                    </div>
                    `;

                    // Mezcla óptima calculada
                    if (window.ultimaMezclaOptima) {
  const mezcla = window.ultimaMezclaOptima;
  const pesos = mezcla.proporciones;
  const nombres = mezcla.nombres_mezclas || [];

  diagnosticoHTML += `
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
  `;
}


                    // Ahora sí, insertamos el bloque completo en el modal
                    document.getElementById("diagnosticoModal").innerHTML = diagnosticoHTML;


                
            resultadosDiv.innerHTML = finalHTML;


   
        
    
    });
}













function generarMezclaCorregida() {
    const r = window.ultimaCurvaPromedio;
    if (!r) {
        alert("No hay curva promedio cargada.");
        return;
    }

    const corregida = [];

    r.tamices.forEach((tamiz, i) => {
        let valor = r.promedios[i];
        let ajuste = 0;

        if (tamiz < 0.3 && r.ajustes.some(a => a.includes("finos"))) {
            ajuste = r.ajustes.find(a => a.includes("Reducir material finos")) ? -0.1 * valor : 0.1 * valor;
        } else if (tamiz <= 4.75 && tamiz >= 0.3 && r.ajustes.some(a => a.includes("medios"))) {
            ajuste = r.ajustes.find(a => a.includes("Reducir material medios")) ? -0.1 * valor : 0.1 * valor;
        } else if (tamiz > 4.75 && r.ajustes.some(a => a.includes("gruesos"))) {
            ajuste = r.ajustes.find(a => a.includes("Reducir material gruesos")) ? -0.1 * valor : 0.1 * valor;
        }

        const nuevo_valor = Math.max(0, Math.min(100, valor + ajuste));
        corregida.push(nuevo_valor);
    });

    // Crear contenedor y canvas para el gráfico
    const container = document.createElement("div");
    container.innerHTML = `
        <h3 style="color: #007bff;">🛠️ Mezcla Corregida Simulada</h3>
        <canvas id="graficoCorregido" height="300"></canvas>
        <pre>${JSON.stringify({ tamices: r.tamices, corregidos: corregida }, null, 2)}</pre>
    `;
    document.getElementById("resultados").appendChild(container);

    // Calcular curva ideal de Fuller
    const curvaIdeal = r.tamices.map(t => Math.pow(t / 25, 0.5) * 100); // usando dmax=25 y n=0.5

    // Crear gráfico
    new Chart(document.getElementById("graficoCorregido"), {
        type: 'line',
        data: {
            labels: r.tamices.map(t => t.toFixed(2) + " mm"),
            datasets: [
                {
                    label: "Curva Promedio Original",
                    data: r.promedios,
                    borderColor: "blue",
                    fill: false
                },
                {
                    label: "Curva de Fuller Ideal",
                    data: curvaIdeal,
                    borderColor: "orange",
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: "Curva Corregida Simulada",
                    data: corregida,
                    borderColor: "green",
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "% que pasa"
                    },
                    min: 0,
                    max: 100
                },
                x: {
                    title: {
                        display: true,
                        text: "Tamiz (mm)"
                    }
                }
            }
        }
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

  let csv = "Tamiz (mm);% Promedio; ASTM C136 o IRAM 1505\n";
  for (let i = 0; i < curva.tamices.length; i++) {
    csv += `${curva.tamices[i]};${curva.promedios[i]};${curva.clasificaciones[i]}\n`;
  }

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "curva_promedio.csv";
  a.click();
}














function calcularMezclaOptima() {
    const mezclasDivs = document.querySelectorAll(".mezcla");
    const payload = [];

    mezclasDivs.forEach(mezcla => {
        const nombre = mezcla.querySelector(".nombreProducto").value || "Sin nombre";
        const filas = mezcla.querySelectorAll("tbody tr");

        const tamices = [];
        const porcentajes = [];

        filas.forEach(fila => {
            const celdas = fila.querySelectorAll("td");
            tamices.push(parseFloat(celdas[0].textContent));
            porcentajes.push(parseFloat(celdas[1].textContent));
        });

        payload.push({ nombre, tamices, porcentajes_reales: porcentajes });
    });

    fetch("/densidadFullerOptimo/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mezclas: payload, d_max: 25, n: 0.5 })
    })
    .then(res => res.json())
        .then(data => {
          const html = `
                <h2 style="color: green;">🧠 Mezcla Óptima Calculada</h2>
                <canvas id="graficoOptimo" height="300"></canvas>

                <p><strong>Error promedio:</strong> ${data.error_promedio}%</p>
                <p>📉 Se redujo significativamente el error, ajustando la mezcla a una curva más cercana a la distribución ideal.</p>

                <p><strong>Interpretación de las proporciones óptimas:</strong></p>
                <ul>
                  ${ 
                     data.pesos.map((p, i) => {
                      const nombre = data.nombres_mezclas[i];
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

                <details>
                  <summary style="cursor:pointer; color:#007bff;">🔧 Ver datos técnicos (tamices y curva óptima)</summary>
                  <pre style="background:#f8f9fa; padding:10px; border-radius:5px;">${JSON.stringify({
                    tamices: data.tamices,
                    curva: data.curva_optima
                  }, null, 2)}</pre>
                </details>
              `;


          const contenedor = document.getElementById("contenidoOptimo");
          contenedor.innerHTML = html;

          abrirModalOptimo(); // Mostrar el modal

          new Chart(document.getElementById("graficoOptimo"), {
            type: 'line',
            data: {
              labels: data.tamices.map(t => t.toFixed(2) + " mm"),
              datasets: [
                {
                  label: "Curva Ideal de Fuller",
                  data: data.curva_ideal,
                  borderColor: "orange",
                  borderDash: [5, 5],
                  fill: false
                },
                {
                  label: "Curva Óptima Combinada",
                  data: data.curva_optima,
                  borderColor: "green",
                  fill: false
                }
              ]
            },
            options: {
              scales: {
                y: {
                  title: { display: true, text: "% que pasa" },
                  min: 0,
                  max: 100
                },
                x: {
                  title: { display: true, text: "Tamiz (mm)" }
                }
              }
            }
          });

          // Guardar para diagnóstico o exportación
          window.ultimaMezclaOptima = {
            error_promedio: data.error_promedio,
            proporciones: data.pesos,
            nombres_mezclas: data.nombres_mezclas,
            tamizes: data.tamices,
            curva_optima: data.curva_optima,
            curva_ideal: data.curva_ideal
          };
      });

}















function cargarDatosPorDefecto() {
  const mezclas = [
    {
      nombre: "Cemento Portland",
      tamices: [0.3, 0.15, 0.075],
      porcentajes: [100, 97, 90]
    },
    {
      nombre: "Arena fina",
      tamices: [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15],
      porcentajes: [100, 97, 90, 68, 45, 20, 6]
    },
    {
      nombre: "Grava 3/4\"",
      tamices: [25.0, 19.0, 12.5, 9.5],
      porcentajes: [100, 95, 40, 8]
    }
  ];

  mezclas.forEach(m => {
    const container = document.getElementById("mezclasContainer");

    const mezclaDiv = document.createElement("div");
    mezclaDiv.className = "mezcla";

    mezclaDiv.innerHTML = `
      <h3>${m.nombre}</h3>
      <input type="text" value="${m.nombre}" class="nombreProducto">
      <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Agregar Fila</button>
      <table class="tabla">
        <thead>
          <tr><th>Tamiz (mm)</th><th>% Real</th><th>Acción</th></tr>
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















function abrirModalOptimo() {
  document.getElementById("modalOptimo").style.display = "block";
}

function cerrarModalOptimo() {
  document.getElementById("modalOptimo").style.display = "none";
}





