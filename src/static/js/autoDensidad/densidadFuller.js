
    let mezclaId = 0;
    function cerrarModalConfiguracionParametros() {
    document.getElementById('modal-configuracion').style.display = 'none';
  }
  
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
    localStorage.setItem("d_max", "9.5");
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
      const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
      fila.innerHTML = `
        <td contenteditable="true">${tamiz}</td>
        <td contenteditable="true">${porcentaje}</td>
        <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
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

function agregarMezcla() {
    const container = document.getElementById("mezclasContainer");

    const mezclaDiv = document.createElement("div");
    mezclaDiv.className = "mezcla";

    // 🔴 ESTE es el ID que después vamos a usar para guardar y restaurar
    mezclaDiv.setAttribute("data-mezcla-id", `mezcla-${mezclaId}`);

    const tamices = [9.5, 4.75, 2.36, 1.18, 0.6, 0.3, 0.15];
    const btnEliminarLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
    const nuevoProductoLabel = typeof I18N !== 'undefined' ? I18N.t('sim.nuevo_producto') : 'Nuevo Producto';

    const filasHTML = tamices.map(t => `
        <tr>
            <td contenteditable="true">${t}</td>
            <td contenteditable="true"></td>
            <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnEliminarLabel}</button></td>
        </tr>
    `).join("");

    mezclaDiv.innerHTML = `
        <div class="contenedor-producto">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>Aggregato</h3>
                <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Rimuovere il aggregato</button>
            </div>
            <h3>${nuevoProductoLabel}</h3>
            <input type="text" value="${nuevoProductoLabel}" class="nombreProducto" data-original="${nuevoProductoLabel}">
            <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Aggiungi Riga</button>
            <button class="btn btn-danger" onclick="agregarAgredadosPreCardados(this)">select precargados</button>
            <button class="btn btn-danger" onclick="agregarTablaAlocalStorage(this)">save</button>
            <table class="tabla">
                <thead>
                    <tr><th>Tamiz</th><th>% Real</th><th>Acción</th></tr>
                </thead>
                <tbody>
                    ${filasHTML}
                </tbody>
            </table>
            <hr>
        </div>
    `;

    container.appendChild(mezclaDiv);

    // 👇 lo incrementás al final para la próxima mezcla
    mezclaId++;
}
function agregarTablaAlocalStorage(btn) {
    const mezclaEl = btn.closest(".mezcla");
    if (!mezclaEl) {
        console.error("❌ No encontré la mezcla del botón save");
        return;
    }

    // 1) id de la mezcla
    let mezclaId = mezclaEl.getAttribute("data-mezcla-id") || mezclaEl.id;
    if (!mezclaId) {
        const todas = Array.from(document.querySelectorAll(".mezcla"));
        const idx = todas.indexOf(mezclaEl);
        mezclaId = `mezcla-${idx}`;
        mezclaEl.setAttribute("data-mezcla-id", mezclaId);
    }

    // 2) nombre
    const inputNombre = mezclaEl.querySelector(".nombreProducto");
    const nombre = inputNombre ? (inputNombre.value || "").trim() : "";

    // 3) filas
    const filas = [];
    const tbody = mezclaEl.querySelector("table.tabla tbody");
    if (tbody) {
        tbody.querySelectorAll("tr").forEach(tr => {
            const celdas = tr.querySelectorAll("td");
            const tamiz = (celdas[0]?.textContent || "").trim();
            const porcentaje = (celdas[1]?.textContent || "").trim();
            filas.push({ tamiz, porcentaje });
        });
    }

    // 4) leer lo que había
    let tablas = [];
    const raw = localStorage.getItem("tablasCargadas");
    if (raw) {
        try {
            tablas = JSON.parse(raw);
        } catch (e) {
            console.warn("⚠️ tablasCargadas estaba corrupto, lo reinicio");
            tablas = [];
        }
    }

    // 5) objeto actual
    const tablaActual = {
        mezclaId,
        nombre,
        filas
    };

    // 6) upsert
    const idx = tablas.findIndex(t => t.mezclaId === mezclaId);
    if (idx >= 0) {
        tablas[idx] = tablaActual;
    } else {
        tablas.push(tablaActual);
    }

    // 7) guardar
    localStorage.setItem("tablasCargadas", JSON.stringify(tablas));

    // 8) ✅ feedback visual en el botón
    const originalText = btn.textContent;
    btn.textContent = "✅ guardado";
    btn.disabled = true;
    setTimeout(() => {
        btn.textContent = originalText || "save";
        btn.disabled = false;
    }, 1500);

    console.log(`✅ Mezcla ${mezclaId} guardada en localStorage`);
}


function eliminarMezcla(boton) {
    const mezclaDiv = boton.closest('.mezcla');
    const inputNombre = mezclaDiv.querySelector('.nombreProducto');
    const nombre = inputNombre?.value?.trim();
    const mezclaId = mezclaDiv.getAttribute('data-mezcla-id');

    if (!nombre) {
        alert("❌ No se pudo identificar el nombre del producto.");
        return;
    }

    console.log("🔧 Nombre a eliminar:", nombre);
    console.log("🔧 MezclaId a eliminar:", mezclaId);

    // ==============================
    // 🔍 Paso 0: Eliminar de localStorage.tablasCargadas
    // ==============================
    if (mezclaId) {
        let tablasCargadas = [];
        try {
            const raw = localStorage.getItem("tablasCargadas");
            if (raw) {
                tablasCargadas = JSON.parse(raw);
            }
        } catch (e) {
            console.error("❌ Error al parsear tablasCargadas:", e);
            tablasCargadas = [];
        }

        console.log("📦 tablasCargadas antes:", tablasCargadas);

        const tablasActualizadas = tablasCargadas.filter(t => t.mezclaId !== mezclaId);

        console.log("✅ tablasCargadas después:", tablasActualizadas);

        localStorage.setItem("tablasCargadas", JSON.stringify(tablasActualizadas));
    }

    // 🧹 Eliminar visualmente
    mezclaDiv.remove();

    // ==============================
    // 🔍 Paso 1: Eliminar de nombres_productos
    // ==============================
    let productos = [];
    const matchNombres = document.cookie.match(/(?:^|; )nombres_productos=([^;]*)/);
    if (matchNombres) {
        try {
            productos = JSON.parse(decodeURIComponent(matchNombres[1]));
        } catch (e) {
            console.error("❌ Error al parsear nombres_productos:", e);
            productos = [];
        }
    }

    console.log("📦 nombres_productos actuales:", productos);

    const nombreNormalizado = nombre.toLowerCase().replace(/\s+/g, "_");

    const productosActualizados = productos.filter(p => {
        const pNormalizado = p.toLowerCase().replace(/\s+/g, "_");
        const coincide = pNormalizado === nombreNormalizado;
        console.log(`👉 Comparando: "${p}" → normalizado: "${pNormalizado}" vs "${nombreNormalizado}" → Match: ${coincide ? '✅' : '❌'}`);
        return !coincide;
    });

    console.log("🧹 nombres_productos actualizados:", productosActualizados);

    document.cookie = `nombres_productos=${encodeURIComponent(JSON.stringify(productosActualizados))}; path=/`;

    // ==============================
    // 🔍 Paso 2: Eliminar de mezclas_guardadas
    // ==============================
    let mezclas = {};
    const matchMezclas = document.cookie.match(/(?:^|; )mezclas_guardadas=([^;]*)/);
    if (matchMezclas) {
        try {
            mezclas = JSON.parse(decodeURIComponent(matchMezclas[1]));
        } catch (e) {
            console.error("❌ Error al parsear mezclas_guardadas:", e);
            mezclas = {};
        }
    }

    console.log("📦 mezclas_guardadas antes:", mezclas);

    const clave = nombreNormalizado;
    if (mezclas[clave]) {
        console.log(`🗑 Eliminando clave "${clave}" de mezclas_guardadas`);
        delete mezclas[clave];
    } else {
        console.warn(`⚠️ Clave "${clave}" no encontrada en mezclas_guardadas`);
    }

    console.log("✅ mezclas_guardadas después:", mezclas);

    document.cookie = `mezclas_guardadas=${encodeURIComponent(JSON.stringify(mezclas))}; path=/`;

    // Mostrar notificación internacionalizada
    const mensaje = typeof I18N !== 'undefined' ? I18N.t('sim.mezcla_eliminada').replace('{nombre}', nombre) : `🗑 Mezcla "${nombre}" eliminada completamente.`;
    showToast(mensaje);
}







function agregarFilaMultiple(btn) {
    

    // 1. encontrar el contenedor de ESTA mezcla
    const mezcla = btn.closest(".mezcla");
    if (!mezcla) {
        console.error("❌ No encontré .mezcla desde este botón");
        return;
    }
    console.log("✅ Mezcla encontrada:", mezcla);

    // 2. dentro de esa mezcla, buscar su tabla
    const tbody = mezcla.querySelector("table.tabla > tbody");
    if (!tbody) {
        console.error("❌ No encontré <tbody> dentro de esta mezcla");
        return;
    }
    console.log("✅ tbody encontrado:", tbody);

    // 3. crear la fila
    const fila = document.createElement("tr");
    const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
    fila.innerHTML = `
        <td contenteditable="true">0</td>
        <td contenteditable="true">0</td>
        <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
    `;
    tbody.appendChild(fila);
    console.log("✅ Fila agregada a ESTA tabla");
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
       // localStorage.setItem("d_max", dMaxFinal.toFixed(2));
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
            
             curvas = data.resultados.map(r => r.reales); 
             pesos = data.resultados.map(r => r.proporcion_optima);
             nombreProductos = data.resultados.map(r => r.nombre);
             tamices = data.tamices_res;
             console.log(data);

            const resumenProporciones = generarResumenProporciones(data.mezcla_optima.pesos, data.resultados);
            const resultadosDiv = document.getElementById("resultados");
            let finalHTML = "<h2>Risultati</h2>";
            data.resultados.forEach(resultado => {
                finalHTML += `

                <details>
                           <summary style="cursor:pointer; color:#0d47a1; font-weight:bold;">🔍 Ver análisis técnico completo</summary>
                             <h4>${resultado.nombre}</h4>
                              <img src="${resultado.grafico}" alt="Curva de ${resultado.nombre}">

                              <p style="margin-top:0.5rem; font-style: italic; color: #333;">
                                  🧠 <strong>Comentario:</strong> ${resultado.comentario}
                              </p>

                              <details style="margin-top: 0.5rem;">
                                <summary style="cursor: pointer; color: #1976d2;">📄 Ver datos técnicos</summary>
                                <pre style="background:#f1f1f1; padding:10px; border-radius:5px; overflow-x:auto;">
                                      ${JSON.stringify(resultado, null, 2)}
                                </pre>
                              </details>

                              <hr>
                </details>
                  
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

            // obtenés las proporciones normalizadas
              const pesosPct = calcularProporcionesMezcla(data, nombreProductos);

              // ahora podés generar el bloque HTML
              const mejorCombinacionHTML = `
                <div style="margin-bottom: 1rem;">
                  <h3>📌 Mejor combinación encontrada</h3>
                  <ul>
                    ${nombreProductos.map((n, i) => `
                      <li><strong>${n}:</strong> ${pesosPct[i].toFixed(2)}%</li>
                    `).join("")}
                  </ul>
                  <p><strong>🧪 Error medio respecto a la curva ideal:</strong> 
                    <span style="color: green;">${r.error_promedio.toFixed(2)}%</span>
                  </p>
                </div>
              `;
            


            let diagnosticoHTML = `
                            <div style="padding: 16px; background-color: #e6f4ea; border-left: 6px solid #2e7d32; margin-top: 1rem;">
                               
                              <details>
                                  <summary style="cursor:pointer; color:#0d47a1; font-weight:bold;">🔍 Ver diagnostico técnico completo</summary>
                   
                                            
                                            
                                            <h3>🧾 Diagnóstico general</h3>
                                                <ul>
                                                    <li><strong>Evaluación:</strong> ${r.evaluacion}</li>
                                                    <li><strong>Error promedio:</strong> ${r.error_promedio.toFixed(2)}%</li>
                                                    <li><strong>Recomendaciones clave:</strong>
                                                        <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>
                                                    </li>
                                                </ul>

                                                <!-- 📌 Mejor combinación encontrada -->
                                                ${mejorCombinacionHTML}
                                                <!-- 📊 Interpretación de proporciones óptimas -->

                                                
                                                ${resumenProporciones}
                                                <li>✅ Se generó una mezcla corregida y una mezcla óptima automáticamente.</li>
                                                <li>📄 Puedes exportar este informe como CSV.</li>
                                                <details style="margin-top: 1rem;">
                                                <summary style="cursor:pointer; color:#0d47a1; font-weight:bold;">📊 Ver gráfico de proporciones óptimas</summary>
                                                <canvas id="graficoProporciones" width="400" height="250" style="margin-top: 1rem;"></canvas>
                                                                      <div id="bloqueOptimo"></div>
                                              </details>
                              </details>
                            </div>
                        `;

              // Cargar HTML inicial
            document.getElementById("diagnosticoModal").innerHTML = diagnosticoHTML;

            calcularMezclaOptima().then(mezcla => {
                const pesos = mezcla.proporciones;
                const nombres = mezcla.nombres_mezclas || [];

             
                 const r = window.ultimaCurvaPromedio || {};

                const tamices = (data.tamices_res || data.mezcla_optima?.tamices || r?.tamices || []);
                const curvaSugerida = (data.mezcla_optima?.curva_resultante || r?.curva_resultante || []);


                diagnosticoHTML += `
               
                  <div style="margin-top: 1rem; padding: 16px; background-color: #e3f2fd; border-left: 6px solid #1976d2; border-radius: 8px;">
                    
                    <details>
                      <summary style="cursor:pointer; color:#0d47a1; font-weight:bold;">🔍 Ver análisis técnico completo</summary>
                      <!-- 📊 Tabla comparativa -->
                          <div style="overflow-x:auto; margin-bottom: 1rem;">
                            <table style="width:100%; border-collapse: collapse;">
                              <thead style="background: #f1f1f1;">
                                <tr>
                                  <th>Tamiz (mm)</th>
                                  <th>Curva resultante (%)</th>
                                  <th>Curva ideal (%)</th>
                                  <th>Diferencia (%)</th>
                                </tr>
                              </thead>
                              <tbody>
                               ${renderTablaComparativa(r)}
                              
                              </tbody>
                            </table>
                          </div>
                    </details>

                   

                    <!-- 📉 Recomendaciones -->
                    <div style="margin-top: 1rem; padding: 12px; background-color: #fff3cd; border-left: 6px solid #ff9800;" >
                      <h4>📉 Recomendaciones para mejorar la mezcla</h4>
                      <ul>
                        <ul id="recomendaciones-list">${renderRecomendacionesByDiffs(r.tamices, r.diferencias)}</ul>
                       
                      </ul>
                    </div>

                    <!-- 🧪 Curva sugerida -->
                    <div style="margin-top: 1rem; background:#e8f5e9; padding:16px; border-left:6px solid #388e3c;">
                      <h4>🧪 Curva sugerida de mezcla</h4>
                      <ul>
                        ${renderListaCurva(tamices, curvaSugerida)}
                      </ul>
                    </div>

                  </div>
                
                `;

                document.getElementById("diagnosticoModal").innerHTML = diagnosticoHTML;




                setTimeout(() => {
                    generarGraficoProporciones(mezcla.proporciones, mezcla.nombres_mezclas);
                }, 0);

                abrirModalExportar();
            });



            
            
            
            finalHTML += `
                <h2 style="color: #b30000;">🔎 Analisi finale: curva media dell'insieme</h2>

                <div style="border: 2px solid #b30000; padding: 16px; border-radius: 10px; background-color: #fff4f4;">
                    <img src="${r.grafico}" alt="Curva Promedio" style="max-width: 100%; margin-bottom: 12px;">
                    <p><strong>Evaluación general:</strong> <span style="color: #000;">${r.evaluacion}</span> 
                    <em>(Error promedio: ${r.error_promedio.toFixed(2)}%)</em></p>

                    <p><strong>Recomendaciones automáticas:</strong></p>
                    <ul>${r.ajustes.map(a => `<li>${a}</li>`).join("")}</ul>
                    ${resumenProporciones}
                    <p><strong>Datos base:</strong></p>
                    <details style="margin-top: 0.5rem;">
                      <summary style="cursor: pointer; color: #1976d2;">📄 Ver datos técnicos</summary>
                      <pre style="background:#f1f1f1; padding:10px; border-radius:5px; overflow-x:auto;">${JSON.stringify({ tamices: r.tamices, promedios: r.promedios }, null, 2)}</pre>
                    </details>
                
                  
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



function calcularProporcionesMezcla(data, nombreProductos) {
  // Tomamos solo los primeros N pesos (ej: N = número de mezclas)
  let pesos = (data.mezcla_optima?.pesos_optimos_mezcla || []).slice(0, nombreProductos.length);

  // Normalizar a porcentajes (0..1 → %, y que sumen 100)
  let suma = pesos.reduce((a, b) => a + b, 0);
  const pesosPct = pesos.map(v => {
    const num = Number(v);
    if (!Number.isFinite(num)) return 0;
    return num <= 1 ? (num * 100) : num;
  }).map(v => (suma > 0 ? (v / suma) * 100 : 0));

  // Loguear
  console.log("📊 Proporciones por mezcla:");
  nombreProductos.forEach((n, i) => {
    console.log(`${n}: ${pesosPct[i].toFixed(2)}%`);
  });

  return pesosPct; // lo devolvés para usarlo en tu HTML
}






function renderTablaComparativa(r, tolerancia = 2) {
  const tamices = r.tamices || [];
  const resultante = r.promedios || r.curva_resultante || []; // soporte por si viene con otro nombre
  const ideal = r.curva_ideal || [];
  const diffs = r.diferencias || resultante.map((v, i) => (v - (ideal[i] ?? 0)));

  const filas = tamices.map((t, i) => {
    const res = Number(resultante[i] ?? 0);
    const ide = Number(ideal[i] ?? 0);
    const d   = Number(diffs[i] ?? (res - ide));
    const flag = Math.abs(d) <= tolerancia ? "✅" : "⚠️";
    const signo = d >= 0 ? "+" : "";
    return `
      <tr>
        <td>${t}</td>
        <td>${res.toFixed(2)}</td>
        <td>${ide.toFixed(2)}</td>
        <td>${signo}${d.toFixed(2)} ${flag}</td>
      </tr>`;
  }).join("");

  return filas;
}

// Uso (ejemplo):
// const r = data.curva_resultante;  // como en tu código
// document.querySelector('#tabla-comparativa tbody').innerHTML = renderTablaComparativa(r);


function renderListaCurva(tamices = [], valores = []) {
  return tamices.map((t, i) => `
    <li>Tamiz ${t} mm: ${(Number(valores[i] ?? 0)).toFixed(2)}%</li>
  `).join("");
}



function renderRecomendacionesByDiffs(tamices = [], diffs = [], tolerancia = 2) {
  return tamices.map((t, i) => {
    const d = Number(diffs[i] ?? 0);
    if (!Number.isFinite(d) || Math.abs(d) <= tolerancia) return ""; // en rango aceptable

    const exceso   = d > 0;
    const icon     = exceso ? "🔻" : "🔺";
    const accion   = exceso ? "reducir" : "aumentar";
    const etiqueta = exceso ? "exceso de" : "déficit de";
    const pct      = d >= 0 ? `+${d.toFixed(2)}` : d.toFixed(2); // +5.46 / -5.33

    return `<li>${icon} Tamiz ${t} mm: ${accion} este rango (${etiqueta} <strong>${pct}%</strong>)</li>`;
  }).filter(Boolean).join("");
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

   let input = prompt(
                      "Ingresar un número entre 0 y 1 (dejar vacío para usar 1):\n\n" +
                      "📌 factor controla la intensidad del ajuste hacia la curva objetivo.\n" +
                      "• factor = 0 → no aplicás corrección (curva = promedio)\n" +
                      "• factor = 1 → corrección completa (curva = Fuller)\n" +
                      "• 0 < factor < 1 → corrección parcial\n" +
                      "• factor > 1 → sobreajuste (te pasás de Fuller)\n" +
                      "• factor < 0 → te alejás de Fuller",
                      "1"
                    );





   let tipo_objetivo = localStorage.getItem('tipo_objetivo')
    // Si el usuario aprieta "Cancelar" o deja vacío, se usa 1
    if (input === null || input.trim() === "") {
        input = "1";
    }

    const factor = parseFloat(input);

    if (isNaN(factor) || factor < 0 || factor > 1) {
        alert("❌ Número inválido. Ingresá un valor entre 0 y 1.");
        return;
    }

    fetch('/calcularCurvaCorregida/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            curvas: curvas,
            pesos: pesos,
            nombreProductos: nombreProductos,
            tamices: tamices,
            factor: factor,
            tipo_objetivo:tipo_objetivo
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


function inspeccionarCurva(curva = window.ultimaCurvaPromedio){
  if (!curva) { console.warn('No hay curva'); return; }
  const peek = (a,n=5)=>Array.isArray(a)?a.slice(0,n):a;
  console.log('keys:', Object.keys(curva));
  console.log('evaluacion:', curva.evaluacion);
  console.log('error_promedio:', curva.error_promedio);
  console.log('tamices (len):', curva?.tamices?.length, 'muestra:', peek(curva?.tamices));
  console.log('promedios (len):', curva?.promedios?.length, 'muestra:', peek(curva?.promedios));
  console.log('curva_ideal (len):', curva?.curva_ideal?.length, 'muestra:', peek(curva?.curva_ideal));
  console.log('diferencias (len):', curva?.diferencias?.length, 'muestra:', peek(curva?.diferencias));
  console.log('mezcla_optima:', curva?.mezcla_optima);
  console.log('resultados:', Array.isArray(curva?.resultados) ? curva.resultados.length : curva?.resultados);
}

// --- helper: redondea porcentaje y lo muestra sin basura ---
function formatPercent(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "0";
  // si el valor es muy chico, mostrar 2 decimales
  if (Math.abs(n) < 1) return n.toFixed(2).replace('.', ',');
  // si tiene decimales, máximo 2
  return (Math.round(n * 100) / 100).toString().replace('.', ',');
}

const buildClasificaciones = (tamices, clas) => {
  if (Array.isArray(clas) && clas.length) return clas;
  return (tamices || []).map(t => (t ?? "").toString());
};

function exportarCSV() {
  const curva = window.ultimaCurvaPromedio;
  if (!curva || !Array.isArray(curva.tamices) || !Array.isArray(curva.promedios)) {
    alert("❌ No hay datos para exportar");
    return;
  }

  inspeccionarCurva(curva);

  const tam  = curva.tamices;
  const prom = curva.promedios;
  const clas = buildClasificaciones(tam, curva.clasificaciones);
  const n = Math.min(tam.length, prom.length, clas.length);

  let csv = "Tamiz (mm);% Promedio;Abertura (mm)\n";
  for (let i = 0; i < n; i++) {
    csv += `${tam[i] ?? ""};${formatPercent(prom[i])};${clas[i] ?? ""}\n`;
  }

  const mo = curva?.mezcla_optima;
  const pesos = mo?.pesos;

  let resultadosArray = [];
  if (Array.isArray(curva?.resultados)) {
    resultadosArray = curva.resultados;
  } else if (Number.isFinite(curva?.resultados)) {
    resultadosArray = Array.from({length: curva.resultados}, (_, i) => ({ nombre: `Producto ${i+1}` }));
  }

  let pesosArray = [];
  if (Array.isArray(pesos)) {
    pesosArray = pesos.map(x =>
      (typeof x === 'number') ? x :
      (Number.isFinite(x?.porcentaje) ? x.porcentaje :
       Number.isFinite(x?.valor) ? x.valor : 0)
    );
  } else if (pesos && typeof pesos === 'object') {
    const entries = Object.entries(pesos);
    pesosArray = entries.map(([_, v]) => Number(v) || 0);
    if (!resultadosArray.length) resultadosArray = entries.map(([k, _]) => ({ nombre: k }));
  }

  if (pesosArray.length || resultadosArray.length) {
    csv += "\nProducto;Porcentaje;Comentario\n";
    const m = Math.max(pesosArray.length, resultadosArray.length);
    for (let i = 0; i < m; i++) {
      const nombre = resultadosArray[i]?.nombre ?? `Producto ${i+1}`;
      const peso   = Number.isFinite(pesosArray[i]) ? pesosArray[i] : 0;
      let comentario = "";
      if (peso < 1) comentario = "descartada por no aportar mejora";
      else if (peso < 10) comentario = "aporte menor, ajuste fino";
      else if (peso > 50) comentario = "componente principal";
      else comentario = "contribucion equilibrada";
      csv += `${nombre};${formatPercent(peso)};${comentario}\n`;
    }
  }

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "curva_promedio.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

window.exportarCSV = exportarCSV;
window.inspeccionarCurva = inspeccionarCurva;


















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

    const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
    mezclaDiv.innerHTML = `
    <div class="contenedor-producto">
        <div style="display: flex; justify-content: space-between; align-items: center;">
              <h3>Aggregato</h3>
              <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Rimuovere il aggregato</button>
            </div>
          <h3>${m.nombre}</h3>     
        <input type="text" value="${m.nombre}" class="nombreProducto" data-original="${m.nombre}">
          <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Aggiungi Riga</button>
          <table class="tabla">
            <thead>
              <tr><th>Tamiz</th><th>% Real</th><th>Acción</th></tr>
            </thead>
            <tbody>
              ${m.tamices.map((t, i) => `
                <tr>
                  <td contenteditable="true">${t}</td>
                  <td contenteditable="true">${m.porcentajes[i]}</td>
                  <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
          <hr>
    </div>
    `;

    container.appendChild(mezclaDiv);
  });
}



//window.addEventListener("DOMContentLoaded", cargarDatosPorDefecto);
















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







  //esto sieve para abrir el modal de cuarvas objetivos tipo de 
  //material bloques, hormigon, relleno ypersonalizada
function abrirModalTipoCurva() {
  document.getElementById("modalCurvaObjetivo").style.display = "block";
}

function cerrarModalCurvaObjetivo() {
  document.getElementById("modalCurvaObjetivo").style.display = "none";
}

function guardarTipoCurva() {
  const seleccion = document.getElementById("tipoCurvaObjetivo").value;
  localStorage.setItem("tipo_objetivo", seleccion);
  console.log("✅ Tipo de curva objetivo guardado en localStorage:", seleccion);
  cerrarModalCurvaObjetivo();
}















document.addEventListener("keydown", function(event) {
  if (event.target.classList.contains("nombreProducto") && event.key === "Enter") {
    event.preventDefault();
debugger; // 👈 Pausa para inspección manual
    const input = event.target;
    const nuevoNombre = input.value.trim();
    const original = input.dataset.original;
    if (!nuevoNombre) return;

    let productos = [];

    // Leer desde cookie
    const match = document.cookie.match(/(?:^|; )nombres_productos=([^;]*)/);
    if (match) {
      productos = JSON.parse(decodeURIComponent(match[1]));
    }

    if (nuevoNombre === original) {
      alert(`ℹ️ El nombre no cambió.`);
      return;
    }

    if (productos.includes(nuevoNombre)) {
      alert(`⚠️ El producto "${nuevoNombre}" ya existe.`);
      input.value = original;
      return;
    }

    const index = productos.indexOf(original);
    if (index !== -1) {
      productos[index] = nuevoNombre;
    } else {
      productos.push(nuevoNombre);
    }

    // Guardar en cookie
    document.cookie = "nombres_productos=" + encodeURIComponent(JSON.stringify(productos)) + "; path=/";
    input.dataset.original = nuevoNombre;
    alert(`✅ Nombre actualizado a "${nuevoNombre}".`);
    input.blur();





     // Buscar tabla asociada al producto
      const contenedor = input.closest(".contenedor-producto");
      console.log("🔍 Contenedor .contenedor-producto encontrado:", contenedor);

      if (!contenedor) {
        console.warn("⚠️ No se encontró el contenedor .contenedor-producto desde el input", input);
      }

      const tabla = contenedor?.querySelector("table");
      console.log("📊 Tabla encontrada:", tabla);

      const tamices = [];
      const reales = [];

      debugger; // 👈 Pausa para inspección manual

      if (tabla) {
        tabla.querySelectorAll("tbody tr").forEach((fila, i) => {
          const celdas = fila.querySelectorAll("td");
          console.log(`📦 Fila ${i}:`, fila);
          console.log(`➡️ Celdas[0]:`, celdas[0]?.textContent, "➡️ Celdas[1]:", celdas[1]?.textContent);

          const tamiz = parseFloat(celdas[0]?.textContent);
          const real = parseFloat(celdas[1]?.textContent);

          if (!isNaN(tamiz) && !isNaN(real)) {
            tamices.push(tamiz);
            reales.push(real);
          } else {
            console.warn(`⚠️ Datos inválidos en fila ${i}:`, { tamiz: celdas[0]?.textContent, real: celdas[1]?.textContent });
          }
        });
      } else {
        console.warn("⚠️ No se encontró la tabla dentro del contenedor.");
      }

      console.log("✅ Tamices extraídos:", tamices);
      console.log("✅ Porcentajes reales extraídos:", reales);

      guardarMezclaEnCookie(nuevoNombre, tamices, reales);








  }
});








function guardarMezclaEnCookie(nombreProducto, tamices, porcentajesReales) {
  if (!nombreProducto || tamices.length !== porcentajesReales.length) return;
  debugger;
  const normalizedKey = nombreProducto.trim().toLowerCase().replace(/\s+/g, "_");

  let datosGuardados = {};
  const match = document.cookie.match(/(?:^|; )mezclas_guardadas=([^;]*)/);
  if (match) {
    try {
      datosGuardados = JSON.parse(decodeURIComponent(match[1]));
    } catch (e) {
      console.warn("❌ Error al parsear cookie de mezclas:", e);
    }
  }

  datosGuardados[normalizedKey] = {
    tamices: tamices,
    reales: porcentajesReales
  };

  document.cookie = "mezclas_guardadas=" + encodeURIComponent(JSON.stringify(datosGuardados)) + "; path=/";
  console.log(`✅ Mezcla "${nombreProducto}" guardada como "${normalizedKey}"`);
}


window.addEventListener("unhandledrejection", function(event) {
  console.warn("❗ Rechazo no controlado:", event.reason);
});



































document.addEventListener("DOMContentLoaded", () => {
  cargarMezclasDesdeCookies();
});

function getCookie(nombre) {
  const valor = `; ${document.cookie}`;
  const partes = valor.split(`; ${nombre}=`);
  if (partes.length === 2) return decodeURIComponent(partes.pop().split(';').shift());
  return null;
}function cargarMezclasDesdeCookies() {
  const mezclasJSON = getCookie("mezclas_guardadas");
  const nombresJSON = getCookie("nombres_productos");

  if (!mezclasJSON || !nombresJSON) return;

  const mezclas = JSON.parse(decodeURIComponent(mezclasJSON));
  const nombres = JSON.parse(decodeURIComponent(nombresJSON));
  console.log("Cargando mezclas desde cookies:", mezclas, nombres);

  const container = document.getElementById("mezclasContainer");
  if (!container) return;

  Object.entries(mezclas).forEach(([clave, datos]) => {
    if (!Array.isArray(datos.tamices) || !Array.isArray(datos.reales) || datos.tamices.length !== datos.reales.length) {
      console.warn("Datos inválidos para mezcla:", clave, datos);
      return;
    }

    const mezclaDiv = document.createElement("div");
    mezclaDiv.className = "mezcla";

    const btnLabel = typeof I18N !== 'undefined' ? I18N.t('sim.btn_eliminar') : 'Eliminar';
    const filas = datos.tamices.map((t, i) => `
      <tr>
        <td contenteditable="true">${t}</td>
        <td contenteditable="true">${datos.reales[i]}</td>
        <td><button class="btn btn-danger" onclick="this.closest('tr').remove()">${btnLabel}</button></td>
      </tr>`).join("");

    const nombreVisible = nombres.find(n => n.toLowerCase().replace(/\s/g, "") === clave.toLowerCase()) || clave;

    mezclaDiv.innerHTML = `
      <div class="contenedor-producto">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h3>Aggregato</h3>
          <button class="btn btn-outline-danger btn-sm" onclick="eliminarMezcla(this)">🗑 Rimuovere il aggregato</button>
        </div>
        <h3>${nombreVisible}</h3>
        <input type="text" value="${nombreVisible}" class="nombreProducto" data-original="${nombreVisible}">
        <button class="btn btn-danger" onclick="agregarFilaMultiple(this)">Aggiungi Riga</button>
        <table class="tabla">
          <thead>
            <tr><th>Tamiz</th><th>% Real</th><th>Acción</th></tr>
          </thead>
          <tbody>
            ${filas}
          </tbody>
        </table>
        <hr>
      </div>`;

    container.appendChild(mezclaDiv);
  });
}












