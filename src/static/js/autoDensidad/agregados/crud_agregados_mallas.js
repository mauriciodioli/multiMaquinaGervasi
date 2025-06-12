document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-modalAgregarMalla-agregado")) {
      document.getElementById('modalAgregarMalla').style.display = "block";
    }
  });

  const form = document.querySelector("#modalAgregarMalla form");
  const tabla = document.querySelector("table tbody");

  if (!form) return;

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
          <td>${data.nombre_comercial}</td>
          <td>${data.diametro_mm}</td>
         <td>
            <button class="btn btn-sm btn-danger btn-eliminar-malla" data-id="${data.id }">🗑️</button>
            </td>

        `;
        tabla.appendChild(row);
        // Mostrar la sección si estaba oculta
        document.getElementById("seccion-mallas").style.display = "block";
        form.reset();
        document.getElementById('modalAgregarMalla').style.display = "none"; // cerramos el modal manualmente
      } else {
        alert("⚠️ Error: " + (data.error || "No se pudo agregar la malla"));
      }
    })
    .catch(err => {
      console.error(err);
      alert("❌ Error inesperado al guardar la malla");
    });
  });
});






document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("click", function (e) {
    if (e.target.classList.contains("btn-eliminar-malla")) {
      const btn = e.target;
      const fila = btn.closest("tr");
      const id = btn.dataset.id;

      if (confirm("¿Seguro que querés quitar esta malla del agregado?")) {
        fetch(`/mixFamiliari_crud_agregado_agregados_mallas/${id}/eliminar`, {
          method: "DELETE"
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            fila.remove();
          } else {
            alert("⚠️ Error: " + (data.error || "No se pudo eliminar"));
          }
        })
        .catch(err => {
          console.error(err);
          alert("❌ Error inesperado al eliminar la malla");
        });
      }
    }
  });
});




document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("toggle-mallas");
  const seccion = document.getElementById("seccion-mallas");

  if (toggleBtn && seccion) {
    toggleBtn.addEventListener("click", () => {
      const visible = seccion.style.display === "block";
      seccion.style.display = visible ? "none" : "block";
      toggleBtn.innerHTML = visible ? "🔽 Mostrar" : "🔼 Ocultar";
    });
  }
});