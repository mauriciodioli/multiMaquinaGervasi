
 
 
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
            window.ultimaCurvaPromedio = r;

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
                    <button class="btn btn-secondary" onclick="exportarPDF()">Exportar a PDF</button>
                    <button class="btn btn-secondary" onclick="exportarCSV()">Exportar a CSV</button>
                </div>
            `;

            resultadosDiv.innerHTML = finalHTML;


   
        
    
    });
}













function generarMezclaCorregida() {
  alert("🚧 Próximamente: Generación automática de mezcla corregida basada en recomendaciones.");
  // Aquí iría la lógica para aplicar los ajustes e inferir una nueva curva corregida
}

function exportarPDF() {
  const contenido = document.getElementById("resultados").innerHTML;
  const ventana = window.open('', '_blank');
  ventana.document.write(`
    <html>
    <head><title>Informe de Curva de Fuller</title></head>
    <body>${contenido}</body>
    </html>
  `);
  ventana.document.close();
  ventana.print();
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
