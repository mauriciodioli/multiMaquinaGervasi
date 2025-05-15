
 
 
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

    fetch("/densidadFullerMultiple/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mezclas: payload, d_max: 25, n: 0.5 })  // d_max y n por ahora globales
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
           
            
            calcularMezclaOptima();    


           
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
  
                     <button class="btn btn-secondary" onclick="exportarCSV()">Exportar a CSV</button>
                    </div>
            `;
                finalHTML += `
                <div style="margin-top: 2rem; padding: 16px; background-color: #e6f4ea; border-left: 6px solid #2e7d32;">
                    <h3>🧾 Diagnóstico general</h3>
                    <ul>
                    <li><strong>Evaluación:</strong> ${r.evaluacion}</li>
                    <li><strong>Error promedio:</strong> ${r.error_promedio.toFixed(2)}%</li>
                    <li><strong>Recomendaciones clave:</strong>
                        <ul>
                        ${r.ajustes.map(a => `<li>${a}</li>`).join("")}
                        </ul>
                    </li>
                    <li>✅ Se generó una mezcla corregida y una mezcla óptima automáticamente.</li>
                    <li>📄 Puedes exportar este informe como PDF o CSV.</li>
                    </ul>
                </div>
                `;

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







function asegurarModalExportar() {
    if (!document.getElementById("modalExportar")) {
        const modalHTML = `
        <div id="modalExportar" class="modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background-color: rgba(0,0,0,0.7); z-index: 9999;">
          <div style="background:white; padding:2rem; margin:5% auto; width:90%; max-width:800px; border-radius:10px; position:relative;">
              <span onclick="cerrarModalExportar()" style="position:absolute; top:10px; right:20px; cursor:pointer; font-weight:bold; font-size:18px;">✖</span>
              <h3>📋 Exportar análisis</h3>
                <!-- 👇 Aca va el resumen dinámico -->
                <div id="resumenModal" style="max-height:300px; overflow:auto;"></div>
              <p>Podés descargar el análisis actual como PDF o CSV.</p>
               <button class="btn btn-secondary" onclick="exportarCSV()">📊 Exportar CSV</button>
          </div>
        </div>`;
        document.body.insertAdjacentHTML("beforeend", modalHTML);
    }
}

function abrirModalExportar() {
   
    asegurarModalExportar();
    document.getElementById("modalExportar").style.display = "block";
}




function cerrarModalExportar() {
    document.getElementById("modalExportar").style.display = "none";
}








function exportarCSV() {
  const r = window.ultimaCurvaPromedio; // asumimos que guardamos esto al generar
  if (!r) return alert("No hay curva promedio para exportar");

  const rows = [["Tamiz (mm)", "% Promedio"]];
  r.tamices.forEach((t, i) => {
    rows.push([t, r.promedios[i]]);
  });

  let csvContent = "data:text/csv;charset=utf-8,"
    + rows.map(e => e.join(",")).join("\n");

  const link = document.createElement("a");
  link.setAttribute("href", encodeURI(csvContent));
  link.setAttribute("download", "curva_promedio.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
        const contenedor = document.createElement("div");
        contenedor.innerHTML = `
            <h2 style="color:green;">🧠 Mezcla Óptima Calculada</h2>
            <canvas id="graficoOptimo" height="300"></canvas>
            <p><strong>Error promedio:</strong> ${data.error_promedio}%</p>
            <p><strong>Proporciones óptimas:</strong></p>
            <ul>
                ${data.pesos.map((p, i) => `<li>Mezcla ${i + 1}: ${p}%</li>`).join("")}
            </ul>
            <pre>${JSON.stringify({ tamices: data.tamices, curva: data.curva_optima }, null, 2)}</pre>
        `;
        document.getElementById("resultados").appendChild(contenedor);

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














