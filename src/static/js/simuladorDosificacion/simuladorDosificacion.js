document.getElementById("simulador-form").addEventListener("submit", function(event) {
  event.preventDefault();

  const formData = new FormData(this);
  const proporciones = {};
  const curvas = {};
  let suma = 0;

  for (let [key, value] of formData.entries()) {
    const val = parseFloat(value) || 0;
    const normalizedKey = key.trim().toLowerCase().replace(/\s+/g, "_");
    proporciones[normalizedKey] = val;
    suma += val;
    debugger;
    // 🔁 Intentar cargar mezcla guardada en cookie para cada producto
    const mezcla = cargarMezclaDesdeCookie(normalizedKey);
    if (mezcla && mezcla.tamices && mezcla.reales) {
      curvas[normalizedKey] = mezcla;
    } else {
      console.warn(`⚠️ No se encontró curva para "${normalizedKey}"`);
    }
  }

  if (Math.abs(suma - 100) > 0.01) {
    alert("⚠️ Las proporciones deben sumar 100%");
    return;
  }

  const payload = {
    proporciones: proporciones,
    curvas: curvas
  };

  fetch("/simular_mezcla_manual/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => {
    if (!res.ok) throw new Error("Respuesta no válida del servidor");
    return res.json();
  })
  .then(data => {
      console.log("🔍 DATA RECIBIDA:", data);
      // 👇 Agrega el gráfico
      const img = document.getElementById("plotFuller");
      if (img && data.grafico_base64) {
        img.src = data.grafico_base64;
        img.alt = "Curva resultante vs Fuller";
        img.style.display = "";
      }
      // lo que ya tenías
      mostrarResultadosSimulador(data);
})

  .catch(err => {
    console.error("Error al simular mezcla:", err);
    alert("❌ Error al procesar la mezcla");
  });
});





function cargarMezclaDesdeCookie(nombreProducto) {
  const match = document.cookie.match(/(?:^|; )mezclas_guardadas=([^;]*)/);
  if (!match) return null;

  try {
    const datos = JSON.parse(decodeURIComponent(match[1]));
    return datos[nombreProducto] || null;
  } catch (e) {
    console.warn("❌ Error al leer cookie de mezclas:", e);
    return null;
  }
}






function mostrarResultadosSimulador(data) {
  const div = document.getElementById("resultadoSimulador");
  const zonas = data.zonas?.error_por_zona;

  if (
    !zonas ||
    typeof zonas.gruesos !== "number" ||
    typeof zonas.medios !== "number" ||
    typeof zonas.finos !== "number"
  ) {
    div.innerHTML = `<p style="color:red;">❌ Error: datos incompletos o mal formateados.</p>`;
    return;
  }

  let html = `
    <div class="simulacion-header">
      <span class="icono-check">✅</span>
      <h4 class="titulo-simulacion">Resultado de simulación</h4>
    </div>
    <ul>
      <li><strong>Zona gruesa:</strong> ${zonas.gruesos.toFixed(2)}%</li>
      <li><strong>Zona media:</strong> ${zonas.medios.toFixed(2)}%</li>
      <li><strong>Zona fina:</strong> ${zonas.finos.toFixed(2)}%</li>
    </ul>
  `;

  if (data.recomendacion) {
    html += `<p><strong>🔎 Recomendación:</strong> ${data.recomendacion}</p>`;
  }

  html += `
    <button id="btnOcultarResultado" class="btn-ocultar-resultado">❌ Ocultar resultado</button>
  `;

  div.innerHTML = html;
  div.classList.add("resultado-simulacion");

  // 💥 Asegurate de que esto va justo después del innerHTML
  setTimeout(() => {
    const btnOcultar = document.getElementById("btnOcultarResultado");
    if (btnOcultar) {
      btnOcultar.addEventListener("click", () => {
        div.classList.add("desaparecer");
        setTimeout(() => {
          div.innerHTML = "";
          div.classList.remove("resultado-simulacion", "desaparecer");
        }, 300);
      });
    } else {
      console.warn("❌ Botón ocultar no encontrado");
    }
  }, 10); // micro delay para asegurar que se renderice el DOM
}



 function volverAFullerMultiple() {
    fetch("/pantalla_densidad_fuller_multiple/")
      .then(res => res.text())
      .then(html => {
        document.body.innerHTML = html;  // ⚠️ reemplaza todo el body (si querés más control, usá un div contenedor)
        history.pushState(null, "", "/pantalla_densidad_fuller_multiple/");
        cargarMezclasDesdeCookies();
      })
      .catch(err => {
        alert("❌ Error al volver: " + err.message);
      });
  }