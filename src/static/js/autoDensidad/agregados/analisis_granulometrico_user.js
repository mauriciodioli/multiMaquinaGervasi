document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/autoDensidad/perfil_usuario/analisis_granulometrico/")
    .then(res => {
      if (!res.ok) throw new Error("Error cargando el HTML");
      return res.text();
    })
    .then(html => {
      document.getElementById("contenedor-analisis").innerHTML = html;
    })
    .catch(err => {
      document.getElementById("contenedor-analisis").innerHTML = `<p class="text-danger">❌ Error al cargar análisis: ${err.message}</p>`;
    });
});