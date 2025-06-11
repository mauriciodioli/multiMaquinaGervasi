document.addEventListener("DOMContentLoaded", () => {
  // 🔁 Toggle de sección de componentes
  const toggleComponentes = document.getElementById("toggle-componentes");
  const seccionComponentes = document.getElementById("seccion-componentes");

  if (toggleComponentes && seccionComponentes) {
    toggleComponentes.addEventListener("click", () => {
      const visible = seccionComponentes.style.display === "block";
      seccionComponentes.style.display = visible ? "none" : "block";
      toggleComponentes.innerHTML = visible ? "🔽 Mostrar" : "🔼 Ocultar";
    });
  }

  // 🧪 Abrir modal
  document.body.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-modalAgregarComponente-agregado")) {
      document.getElementById('modalAgregarComponente').style.display = "block";
    }
  });

  // ➕ Agregar componente químico
  const form = document.querySelector("#modalAgregarComponente form");
  const modalElement = document.getElementById("modalAgregarComponente");

  const tablaComponentes = document.getElementById("tabla-componentes");

  if (form && tablaComponentes) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      fetch(form.action, {
        method: "POST",
        body: new FormData(form)
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${data.nombre}</td>
            <td>${data.porcentaje}</td>
            <td>${data.orden}</td>
            <td>
              <button class="btn btn-sm btn-warning">✏️</button>
              <button class="btn btn-sm btn-danger btn-eliminar-componente" data-id="${data.id}">🗑️</button>
            </td>
          `;
          tablaComponentes.appendChild(row);
          form.reset();
           document.getElementById('modalAgregarComponente').style.display = "none";
        } else {
          alert("⚠️ Error: " + (data.error || "No se pudo agregar el componente"));
        }
      })
      .catch(err => {
        console.error(err);
        alert("❌ Error inesperado al guardar el componente");
      });
    });
  }
});
